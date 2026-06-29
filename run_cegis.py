#!/usr/bin/env python3
"""
run_cegis.py — headline CEGIS experiment.

Generate on the TxGraffiti expressive seed (full graphcalc battery), refute
against tiered pools + active search (SA + rlgt deep-CE/REINFORCE), grow the seed
with witnesses to a fixed point, then rank survivors, autoformalize them to Lean
and kernel-verify with the real Lean+mathlib prover.

Usage:
    python run_cegis.py [--rounds N] [--top N] [--prove-top N] [--no-prove]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time

from config import CONFIG
from conjecture import Conjecture
from pipeline.cegis import CEGIS
from pipeline.reporting import annotate_complexity, print_conjectures, sort_conjectures

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("run_cegis")


def _lean_for(g3, natives, columns):
    """Self-contained, kernel-checkable Lean export for the *supported* subset of
    survivors (see pipeline.lean_export). Survivors whose invariants have no
    faithful mathlib/preamble definition, or which are conditioned on a
    graph-class predicate, get ``None`` (reported, not formalized incorrectly)."""
    from pipeline.lean_export import export_supported
    leans = export_supported(g3, natives, columns)
    n_ok = sum(1 for x in leans if x)
    log.info("[prove] %d/%d survivors export to well-formed Lean (supported invariants)",
             n_ok, len(natives))
    return leans


def wrap_survivors(result) -> list:
    """Native graffiti3 survivors → pipeline Conjecture objects (+ Lean, touch)."""
    natives = result.survivors
    columns = list(result.seed.frame.columns) if getattr(result, "seed", None) is not None else []
    leans = _lean_for(result.g3, natives, columns) \
        if result.g3 is not None else [None] * len(natives)
    # Known-theorem filter (legacy parity): flag survivors that rediscover a
    # classical/trivial bound (ω≤χ, König–Egerváry, diam≤2·rad, …).
    from pipeline.cegis_novelty import classify_native
    out = []
    for nc, touch, lean in zip(natives, result.touches, leans):
        # Sophie sufficient-conditions have no pretty(); render as "hyp ⇒ property".
        if hasattr(nc, "hyp_relation") and hasattr(nc, "property_name"):
            try:
                hyp = nc.hyp_relation.pretty()
            except Exception:
                hyp = getattr(nc, "hyp_name", "?")
            stmt = f"({hyp}) ⇒ {nc.property_name}"
        else:
            try:
                stmt = nc.pretty()
            except Exception:
                stmt = str(nc)
        is_known, why = (False, None)
        if CONFIG.cegis_filter_known:
            try:
                is_known, why = classify_native(nc, columns)
            except Exception:
                pass
        c = Conjecture(
            statement=stmt, inequality=None, generation_method="cegis-graffiti3",
            lean_statement=lean, score=float(touch or 0),
            metadata={"novel": not is_known, "touches": int(touch or 0),
                      "fixed_point": result.fixed_point,
                      "known_as": why},
        )
        # reporting reads tightness_witnesses for the touch column
        c.tightness_witnesses = [""] * int(touch or 0)
        out.append(c)
    n_known = sum(1 for c in out if not c.metadata.get("novel", True))
    if n_known:
        log.info("[novelty] %d/%d survivors rediscover a known theorem", n_known, len(out))
    annotate_complexity(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=CONFIG.cegis_rounds)
    ap.add_argument("--top", type=int, default=CONFIG.cegis_report_top)
    ap.add_argument("--prove-top", type=int, default=15)
    ap.add_argument("--no-prove", action="store_true")
    ap.add_argument("--no-rl", action="store_true", help="skip the RL searcher")
    ap.add_argument("--reprove", action="store_true",
                    help="skip the search; reload persisted survivors and only "
                         "re-run the wrap+prove+report stage")
    args = ap.parse_args(argv)

    CONFIG.cegis_rounds = args.rounds
    if args.no_rl:
        CONFIG.cegis_searchers = tuple(s for s in CONFIG.cegis_searchers if s != "rl")

    survivors_path = os.path.join(CONFIG.output_dir, "cegis_survivors.dill")

    if args.reprove:
        import dill
        with open(survivors_path, "rb") as fh:
            conjs = dill.load(fh)
        log.info("[cegis] reprove: loaded %d persisted survivors from %s",
                 len(conjs), survivors_path)
    else:
        log.info("=" * 70)
        log.info("CEGIS run: rounds=%d searchers=%s exact_tier_max_n=%d",
                 args.rounds, CONFIG.cegis_searchers, CONFIG.exact_tier_max_n)
        log.info("=" * 70)

        cegis = CEGIS(CONFIG)
        result = cegis.run()

        conjs = wrap_survivors(result)
        log.info("[cegis] %d survivors after %d round(s)%s",
                 len(conjs), result.rounds_run,
                 " (FIXED POINT)" if result.fixed_point else "")

        # Persist the wrapped survivors (with Lean exports) so the wrap+prove
        # stage can be re-run cheaply via --reprove without repeating the search.
        os.makedirs(CONFIG.output_dir, exist_ok=True)
        try:
            import dill
            with open(survivors_path, "wb") as fh:
                dill.dump(conjs, fh)
            log.info("[cegis] persisted %d survivors → %s", len(conjs), survivors_path)
        except Exception as e:
            log.warning("[cegis] survivor persistence failed: %s", e)

    # ----- autoformalize + kernel-verify the simplest survivors -------------
    proved = 0
    if not args.no_prove and conjs:
        from pipeline.theorem_prover import NeuralProverClient
        prover = NeuralProverClient(CONFIG)
        to_prove = [c for c in sort_conjectures(conjs, by="complexity")
                    if c.lean_statement][: args.prove_top]
        log.info("[prove] attempting %d simplest survivors via %s",
                 len(to_prove), CONFIG.prover_backends)
        t_prove_start = time.time()
        n_workers = max(1, int(getattr(CONFIG, "prove_concurrency", 1) or 1))

        def _attempt(c):
            try:
                return c, prover.prove(c)
            except Exception as e:                       # pragma: no cover
                log.debug("[prove] %s failed: %s", c.id, e)
                return c, None

        if n_workers > 1:
            # Parallel: vLLM batches the concurrent requests, so each completes
            # inside the shim timeout while aggregate throughput stays high.
            from concurrent.futures import ThreadPoolExecutor, as_completed
            log.info("[prove] proving %d survivors with concurrency=%d", len(to_prove), n_workers)
            with ThreadPoolExecutor(max_workers=n_workers) as ex:
                futs = [ex.submit(_attempt, c) for c in to_prove]
                for fut in as_completed(futs):
                    c, r = fut.result()
                    if r is not None and r.success:
                        proved += 1
                        c.metadata["proved_by"] = r.model_name
                        c.lean_proof = r.proof_tactics
                        log.info("[prove] ✓ %s verified by %s (%d so far)",
                                 c.id, r.model_name, proved)
        else:
            for c in to_prove:
                if CONFIG.prove_time_budget_s and \
                   (time.time() - t_prove_start) > CONFIG.prove_time_budget_s:
                    log.info("[prove] wall-clock budget (%ds) reached — stopping with %d/%d attempted",
                             CONFIG.prove_time_budget_s, proved, len(to_prove))
                    break
                _, r = _attempt(c)
                if r is not None and r.success:
                    proved += 1
                    c.metadata["proved_by"] = r.model_name
                    c.lean_proof = r.proof_tactics
        log.info("[prove] kernel-verified %d / %d", proved, len(to_prove))

    # ----- report -----------------------------------------------------------
    print_conjectures(conjs, sort_by=CONFIG.report_sort_by, top=args.top,
                      show_lean=True,
                      title="CEGIS SURVIVORS (theorems = kernel-verified)")

    os.makedirs(CONFIG.output_dir, exist_ok=True)
    out_path = os.path.join(CONFIG.output_dir, "cegis_results.json")
    payload = {
        "survivors": len(conjs),
        "proved": proved,
        "conjectures": [c.to_dict() for c in
                        sort_conjectures(conjs, by=CONFIG.report_sort_by)],
    }
    if not args.reprove:
        payload.update({
            "history": result.history,
            "rounds_run": result.rounds_run,
            "fixed_point": result.fixed_point,
            "seed_final_size": len(result.seed.graphs),
        })
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2)
    log.info("[cegis] wrote %s", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
