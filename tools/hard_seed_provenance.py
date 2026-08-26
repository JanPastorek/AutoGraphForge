#!/usr/bin/env python
"""tools/hard_seed_provenance.py — where do the hard-seed graphs come from?

`database/hard_seed/graphs.g6` is the pipeline's memory: every graph that ever
refuted a conjecture is appended to it, and it is reloaded as part of the seed
snapshot `T` on the next run (pipeline/seed_corpus.py). It dominates the
counterexample attribution, so "where did *it* come from" is the real question
behind "which tier does the killing".

Two attributions are reported, because they answer different questions.

  exact graph6      — the pipeline's own notion of identity. `graph6_id` only
                      relabels to 0..n-1; it is NOT isomorphism-canonical, so
                      this is "is this literally the object that tier holds".
                      This is the notion `SeedCorpus.add` dedups by, hence the
                      one that governs what actually happened.

  WL fingerprint    — Weisfeiler-Lehman hash, isomorphism-invariant. Catches a
                      searcher that *rediscovered* a family graph under a
                      different labelling. It is a hash, not a canonical form:
                      equal hashes are near-certain but not proven isomorphic,
                      so treat the WL column as an upper bound on rediscovery.

Anything in neither was constructed by the active searchers (z3, cross_entropy,
vns, sa, mcts, rl) — there is no other producer of witness graphs.

Usage:
    python tools/hard_seed_provenance.py [--seed-file database/hard_seed/graphs.g6]
"""
from __future__ import annotations

import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings  # noqa: E402

import networkx as nx  # noqa: E402

# The WL hash changed in networkx 3.5; the warning fires once per call and would
# bury the report. Attribution only compares hashes computed by this same run,
# so the change is irrelevant here.
warnings.filterwarnings("ignore", message=".*hashes produced for graphs.*")
import pandas as pd  # noqa: E402

from config import CONFIG  # noqa: E402

# Ordered cheapest/most-specific first: a graph present in several tiers is
# credited to the first, so the big pool never absorbs credit for a graph the
# small structured pools also hold.
TIERS = [
    ("degenerate",   "battery_degenerate.parquet"),
    ("families",     "battery_families.parquet"),
    ("random",       "battery_random.parquet"),
    ("seed T (TxGraffiti)", "seed_battery.parquet"),
    ("bigdb (HoG + census n<=9)", "battery_bigdb.parquet"),
]


def wl(g6: str) -> str:
    return nx.weisfeiler_lehman_graph_hash(nx.from_graph6_bytes(g6.encode()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-file", default=os.path.join(CONFIG.hard_seed_dir,
                                                        "graphs.g6"))
    ap.add_argument("--cache-dir", default=os.path.join("database", "cache"))
    ap.add_argument("--no-wl", action="store_true",
                    help="skip the isomorphism-invariant pass (slow on big graphs)")
    args = ap.parse_args()

    seed = [ln.strip() for ln in open(args.seed_file) if ln.strip()]
    print(f"hard seed: {len(seed)} graph6 lines "
          f"({len(set(seed))} distinct)\n")

    exact, wlidx = {}, {}
    for name, fname in TIERS:
        p = os.path.join(args.cache_dir, fname)
        if not os.path.exists(p):
            print(f"  tier {name:28s} MISSING ({p})")
            continue
        ids = [str(i) for i in pd.read_parquet(p).index]
        exact[name] = set(ids)
        print(f"  tier {name:28s} {len(ids):7d} graphs")
        if not args.no_wl:
            wlidx[name] = {wl(i) for i in ids}
    print()

    def attribute(index, key):
        hits = collections.Counter()
        for g6 in seed:
            k = key(g6)
            for name, _ in TIERS:
                if name in index and k in index[name]:
                    hits[name] += 1
                    break
            else:
                hits["searcher-constructed"] += 1
        return hits

    def report(title, hits):
        print(title)
        total = sum(hits.values())
        for name, n in hits.most_common():
            print(f"  {name:34s} {n:6d}  {100.0 * n / total:5.1f}%")
        print()

    report("attribution by exact graph6 (the pipeline's own identity):",
           attribute(exact, lambda g: g))
    if not args.no_wl:
        report("attribution up to isomorphism (WL hash — upper bound):",
               attribute(wlidx, wl))

    # Where the searchers actually contribute is a question about *order*: every
    # tier is capped (families n<=7 plus parametric, bigdb n<=14), so above that
    # cap a witness can only have been constructed. Bucketing the exact-graph6
    # attribution by order shows whether the searchers are doing anything the
    # pools could not have done.
    def bucket(n):
        return "n<=9" if n <= 9 else ("10<=n<=14" if n <= 14 else "n>=15")

    grid = collections.Counter()
    orders = collections.Counter()
    for g6 in seed:
        n = nx.from_graph6_bytes(g6.encode()).number_of_nodes()
        orders[n] += 1
        src = next((name for name, _ in TIERS
                    if name in exact and g6 in exact[name]), "searcher-constructed")
        grid[(bucket(n), src)] += 1

    buckets = ["n<=9", "10<=n<=14", "n>=15"]
    names = [n for n, _ in TIERS] + ["searcher-constructed"]
    print("exact attribution x order:")
    print(f"  {'':34s}" + "".join(f"{b:>12s}" for b in buckets))
    for name in names:
        row = [grid[(b, name)] for b in buckets]
        if any(row):
            print(f"  {name:34s}" + "".join(f"{v:12d}" for v in row))
    print(f"  {'TOTAL':34s}" +
          "".join(f"{sum(grid[(b, n)] for n in names):12d}" for b in buckets))
    print()

    print("hard-seed graphs by order:")
    for n in sorted(orders):
        print(f"  n={n:3d}  {orders[n]:6d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
