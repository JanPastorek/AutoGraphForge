#!/usr/bin/env python3
"""
tools/prove_demo.py — end-to-end demo of the local DeepSeek-Prover-V2 backend.

Loads the cached CEGIS candidates, keeps the *supported* (kernel-checkable)
ones, wraps the simplest few, and runs the prover ensemble
(lean tactics → DeepSeek-Prover-V2 local) — each candidate is kernel-verified
against mathlib + the GraphInvariants preamble. Prints which became theorems.

    PYTHONPATH=. python3 tools/prove_demo.py --k 5
"""
from __future__ import annotations
import argparse, glob, os, sys, logging
import dill, pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("prove_demo")

from config import CONFIG
from pipeline import invariants_graphcalc as battery
from txgraffiti.graffiti3.graffiti3 import Graffiti3
from pipeline.lean_export import make_lean_label, is_supported, SUPPORTED, _columns_used

# Invariants with an established mathlib API the prover actually knows. The
# custom domination defs in the preamble are well-formed but the model has never
# seen their lemmas, so it can't close goals over them yet — bias the demo to the
# native ones so the end-to-end chain has a real chance to verify.
NATIVE = {"order", "size", "minimum_degree", "maximum_degree",
          "clique_number", "independence_number"}
from pipeline.refute_matrix import Refuter
from pipeline.reporting import annotate_complexity, sort_conjectures
import run_cegis


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5, help="how many simplest supported survivors to prove")
    args = ap.parse_args(argv)

    frame = battery._coerce(pd.read_parquet("database/cache/seed_battery.parquet"))
    g3 = Graffiti3(frame, lean_label=make_lean_label(frame.columns))
    cache = sorted(glob.glob("database/cache/gen_*.dill"), key=os.path.getmtime)[-1]
    ineqs, _ = dill.load(open(cache, "rb"))
    log.info("loaded %d cached candidates from %s", len(ineqs), os.path.basename(cache))

    cols = list(frame.columns)
    supported = []
    for c in ineqs:
        try:
            c.condition = c._auto_base(frame)
        except Exception:
            pass
        if is_supported(c, cols) and all(u in NATIVE for u in _columns_used(c, cols)):
            supported.append(c)
    # dedup by pretty statement
    seen, uniq = set(), []
    for c in supported:
        p = c.pretty()
        if p not in seen:
            seen.add(p); uniq.append(c)
    log.info("supported, unconditioned, kernel-checkable survivors: %d unique", len(uniq))

    r = Refuter(CONFIG)
    class _R: pass
    res = _R(); res.survivors = uniq; res.g3 = g3; res.fixed_point = True; res.rounds_run = 3
    class _S: pass
    res.seed = _S(); res.seed.frame = frame
    res.touches = [r.touch_count(c, frame) for c in uniq]

    conjs = [c for c in run_cegis.wrap_survivors(res) if c.lean_statement]
    conjs = sort_conjectures(conjs, by="complexity")[: args.k]
    log.info("proving the %d simplest:", len(conjs))
    for c in conjs:
        log.info("   • %s", c.statement)

    from pipeline.theorem_prover import NeuralProverClient
    prover = NeuralProverClient(CONFIG)
    proved = []
    for c in conjs:
        log.info("[prove] %s", c.statement)
        rr = prover.prove(c)
        if rr.success:
            proved.append((c, rr))
            log.info("[prove] ✓ KERNEL-VERIFIED by %s (%.1fs)", rr.model_name, rr.elapsed_s or 0)
        else:
            log.info("[prove] ✗ %s", rr.error)

    print("\n" + "=" * 70)
    print("KERNEL-VERIFIED THEOREMS: %d / %d" % (len(proved), len(conjs)))
    for c, rr in proved:
        print("-" * 70)
        print("informal:", c.statement)
        print(rr.proof_tactics)
    return 0


if __name__ == "__main__":
    sys.exit(main())
