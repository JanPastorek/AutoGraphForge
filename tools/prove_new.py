#!/usr/bin/env python3
"""
tools/prove_new.py — try to kernel-verify the unconditioned survivors that use the
newly-formalized invariants (zero-forcing family / Slater / annihilation).

Cross-references the latest cegis_results.json so only actual survivors are tried.
"""
from __future__ import annotations
import glob, json, logging, os, sys
import dill, pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("prove_new")

from config import CONFIG
from pipeline import invariants_graphcalc as battery
from txgraffiti.graffiti3.graffiti3 import Graffiti3
from pipeline.lean_export import make_lean_label, is_supported, SUPPORTED
from pipeline.refute_matrix import Refuter
from pipeline.reporting import sort_conjectures
import run_cegis

NEW = {"slater", "annihilation_number", "zero_forcing_number",
       "total_zero_forcing_number", "connected_zero_forcing_number"}


def main(argv=None):
    k = int((argv or sys.argv[1:] or ["6"])[0])
    frame = battery._coerce(pd.read_parquet("database/cache/seed_battery.parquet"))
    cols = list(frame.columns)
    g3 = Graffiti3(frame, lean_label=make_lean_label(cols))
    cache = sorted(glob.glob("database/cache/gen_*.dill"), key=os.path.getmtime)[-1]
    ineqs, _ = dill.load(open(cache, "rb"))
    log.info("loaded %d candidates from %s", len(ineqs), os.path.basename(cache))

    survivors = set()
    if os.path.exists("results/cegis_results.json"):
        d = json.load(open("results/cegis_results.json"))
        survivors = {c["statement"] for c in d.get("conjectures", [])}
        log.info("cross-referencing %d survivor statements", len(survivors))

    picked, seen = [], set()
    for c in ineqs:
        try:
            if getattr(c, "condition", None) is None and hasattr(c, "_auto_base"):
                c.condition = c._auto_base(frame)        # don't clobber generation conditions
        except Exception:
            pass
        try:
            p = c.pretty()
        except Exception:
            continue
        used = [col for col in cols if col in p]
        is_new_or_conditioned = any(u in NEW for u in used) or "⇒" in p
        if (p not in seen and is_supported(c, cols) and is_new_or_conditioned
                and (not survivors or p in survivors)):
            seen.add(p); picked.append(c)

    r = Refuter.__new__(Refuter)
    class _R: pass
    res = _R(); res.survivors = picked; res.g3 = g3; res.fixed_point = True; res.rounds_run = 1
    class _S: pass
    res.seed = _S(); res.seed.frame = frame
    res.touches = [r.touch_count(c, frame) for c in picked]
    conjs = [c for c in run_cegis.wrap_survivors(res) if c.lean_statement]
    conjs = sort_conjectures(conjs, by="complexity")[:k]
    log.info("proving %d unconditioned new-invariant survivors:", len(conjs))
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
    print("KERNEL-VERIFIED NEW-INVARIANT THEOREMS: %d / %d" % (len(proved), len(conjs)))
    for c, rr in proved:
        print("-" * 70); print(c.statement); print(rr.proof_tactics)
    return 0


if __name__ == "__main__":
    sys.exit(main())
