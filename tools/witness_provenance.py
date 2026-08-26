#!/usr/bin/env python
"""tools/witness_provenance.py — which pool actually kills conjectures?

The refutation tiers are very unequal in size: the HoG+census pool is ~291k
graphs, the parametric families ~1.1k, the random models ~200, the degenerate
tier ~390. Cost is dominated by the big pool, so it matters whether the
counterexamples come from there or from the small structured pools -- if the
small pools do most of the killing, the search is not really exploring 291k
graphs, it is looking up a handful of families.

Attribution is by membership: each refutation records the graph6 of its witness,
and each tier cache is indexed by graph6.
"""
from __future__ import annotations
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import networkx as nx

TIERS = [("degenerate", "battery_degenerate.parquet"),
         ("families",   "battery_families.parquet"),
         ("random",     "battery_random.parquet"),
         ("bigdb (HoG + census n<=9)", "battery_bigdb.parquet"),
         ("seed snapshot T", "seed_battery.parquet")]

def main() -> int:
    ref = json.load(open("results/cegis_refuted.json"))
    idx = {}
    for name, f in TIERS:
        p = os.path.join("database", "cache", f)
        if os.path.exists(p):
            idx[name] = set(pd.read_parquet(p).index.astype(str))
            print(f"  tier {name:28s} {len(idx[name]):7d} graphs")
    print()

    hits = collections.Counter()
    orders = collections.Counter()
    unattributed = 0
    for r in ref:
        g6 = r.get("witness_g6")
        if not g6:
            continue
        where = [n for n in idx if g6 in idx[n]]
        if not where:
            unattributed += 1
            hits["(not in any cached tier)"] += 1
        else:
            # smallest/cheapest tier that contains it gets the credit
            for name, _ in TIERS:
                if name in where:
                    hits[name] += 1
                    break
        try:
            orders[nx.from_graph6_bytes(g6.encode()).number_of_nodes()] += 1
        except Exception:
            pass

    total = sum(hits.values())
    print(f"witnesses attributed ({total} refutations with a witness):")
    for name, n in hits.most_common():
        print(f"  {name:28s} {n:5d}  ({100*n/total:5.1f}%)")
    print()
    print("witness order distribution:")
    for o in sorted(orders):
        print(f"  n={o:3d}  {orders[o]:5d}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
