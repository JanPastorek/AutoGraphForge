#!/usr/bin/env python
"""tools/hypothesis_selectivity.py — how much of the pool can a class conjecture even touch?

A class-conditioned conjecture `(cubic AND triangle-free) => B` says nothing about
a graph that is not cubic and triangle-free: on those the implication is vacuously
true. So a refutation search that walks the whole pool spends its budget where no
counterexample can exist. This measures, per surviving conjecture, the fraction of
the refutation pool that satisfies its hypothesis -- i.e. the fraction of the
search that is not wasted by construction.
"""
from __future__ import annotations
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from pipeline import conjecture_lattice as cl

def main() -> int:
    frames = []
    for f in ["battery_bigdb", "battery_families", "battery_random",
              "battery_degenerate", "seed_battery"]:
        p = f"database/cache/{f}.parquet"
        if os.path.exists(p):
            frames.append(pd.read_parquet(p))
    pool = pd.concat(frames)
    pool = pool[~pool.index.duplicated(keep="first")]
    n = len(pool)
    print(f"pool: {n} graphs\n")

    conj = json.load(open("results/cegis_results.json"))["conjectures"]
    surv = cl.parse_survivors(conj)

    sel = []
    per_class = {}
    for s in surv:
        cls = [c for c in s.classes if c in pool.columns]
        if not cls:
            continue
        mask = pd.Series(True, index=pool.index)
        for c in cls:
            mask &= pool[c].fillna(False).astype(bool)
        frac = mask.sum() / n
        sel.append((frac, tuple(sorted(s.classes))))
        per_class.setdefault(tuple(sorted(cls)), frac)

    sel.sort()
    print(f"{len(sel)} class-conditioned survivors\n")
    import statistics
    fr = [f for f, _ in sel]
    print(f"  median fraction of pool satisfying the hypothesis: {statistics.median(fr)*100:.2f}%")
    print(f"  mean:   {statistics.mean(fr)*100:.2f}%")
    print(f"  under 1% of the pool:  {sum(1 for f in fr if f < 0.01)} conjectures "
          f"({100*sum(1 for f in fr if f<0.01)/len(fr):.0f}%)")
    print(f"  under 0.1% of the pool:{sum(1 for f in fr if f < 0.001)} conjectures "
          f"({100*sum(1 for f in fr if f<0.001)/len(fr):.0f}%)")
    print("\n  tightest hypotheses (smallest feasible region):")
    seen = set()
    for f, c in sel:
        if c in seen:
            continue
        seen.add(c)
        print(f"    {f*100:7.3f}%  ({int(f*n):6d} graphs)  {' & '.join(c)}")
        if len(seen) >= 12:
            break
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
