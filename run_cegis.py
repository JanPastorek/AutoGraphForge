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

from config import CONFIG
from conjecture import Conjecture
from pipeline.cegis import CEGIS
from pipeline.reporting import annotate_complexity, print_conjectures, sort_conjectures

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("run_cegis")


def _lean_for(g3, natives):
    """Best-effort Lean export aligned to ``natives`` (conjectures only)."""
    try:
        return g3.conjectures_as_lean(natives, prefix="CEGIS")
    except Exception:
        return [None] * len(natives)


def wrap_survivors(result) -> list:
    """Native graffiti3 survivors → pipeline Conjecture objects (+ Lean, touch)."""
    natives = result.survivors
    leans = _lean_for(result.g3, natives) if result.g3 is not None else [None] * len(natives)
    out = []
    for nc, touch, lean in zip(natives, result.touches, leans):
        try:
            stmt = nc.pretty()
        except Exception:
            stmt = str(nc)
        c = Conjecture(
            statement=stmt, inequality=None, generation_method="cegis-graffiti3",
            lean_statement=lean, score=float(touch or 0),
            metadata={"novel": True, "touches": int(touch or 0),
                      "fixed_point": result.fixed_point},
        )
        # reporting reads tightness_witnesses for the touch column
        c.tightness_witnesses = [""] * int(touch or 0)
        out.append(c)
    annotate_complexity(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=CONFIG.cegis_rounds)
    ap.add_argument("--top", type=int, default=CONFIG.cegis_report_top)
    ap.add_argument("--prove-top", type=int, default=15)
    ap.add_argument("--no-prove", action="store_true")
    ap.add_argument("--no-rl", action="store_true", help="skip the RL searcher")
    args = ap.parse_args(argv)

    CONFIG.cegis_rounds = args.rounds
    if args.no_rl:
        CONFIG.cegis_searchers = tuple(s for s in CONFIG.cegis_searchers if s != "rl")

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

    # ----- autoformalize + kernel-verify the simplest survivors -------------
    proved = 0
    if not args.no_prove and conjs:
        from pipeline.theorem_prover import NeuralProverClient
        prover = NeuralProverClient(CONFIG)
        to_prove = [c for c in sort_conjectures(conjs, by="complexity")
                    if c.lean_statement][: args.prove_top]
        log.info("[prove] attempting %d simplest survivors via %s",
                 len(to_prove), CONFIG.prover_backends)
        for c in to_prove:
            try:
                r = prover.prove(c)
                if r.success:
                    proved += 1
                    c.metadata["proved_by"] = r.model_name
                    c.lean_proof = r.proof_tactics
            except Exception as e:
                log.debug("[prove] %s failed: %s", c.id, e)
        log.info("[prove] kernel-verified %d / %d", proved, len(to_prove))

    # ----- report -----------------------------------------------------------
    print_conjectures(conjs, sort_by=CONFIG.report_sort_by, top=args.top,
                      show_lean=True,
                      title="CEGIS SURVIVORS (theorems = kernel-verified)")

    os.makedirs(CONFIG.output_dir, exist_ok=True)
    out_path = os.path.join(CONFIG.output_dir, "cegis_results.json")
    with open(out_path, "w") as fh:
        json.dump({
            "history": result.history,
            "rounds_run": result.rounds_run,
            "fixed_point": result.fixed_point,
            "seed_final_size": len(result.seed.graphs),
            "survivors": len(conjs),
            "proved": proved,
            "conjectures": [c.to_dict() for c in
                            sort_conjectures(conjs, by=CONFIG.report_sort_by)],
        }, fh, indent=2)
    log.info("[cegis] wrote %s", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
