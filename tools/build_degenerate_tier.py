#!/usr/bin/env python
"""tools/build_degenerate_tier.py — a refutation tier of degenerate graphs.

Measured on the caches this repo ships, only **774 of 279,614** usable pool
graphs (0.28%) are disconnected, and just 27 are edgeless with at least two
vertices. The large tier is drawn from a connected census, and the families and
random tiers are connected by construction. A conjecture that is false only on
a disconnected graph, on a graph with an isolated vertex, or on an edgeless
graph therefore has almost no chance of being refuted — it survives for want of
a witness rather than because it is true.

This builds the missing witnesses explicitly: disjoint unions, graphs with
isolated vertices attached, edgeless graphs, and forests with several
components. They are cheap (small orders) and they are exactly the shapes that
break lower bounds such as ``2 ≤ total_domination_number`` or
``2 ≤ chromatic_number``.

Usage:
    python tools/build_degenerate_tier.py [--max-n 10] [--out PATH]
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx  # noqa: E402

from pipeline.degenerate_graphs import degenerate_graphs  # noqa: E402
from pipeline.seed_corpus import graph6_id  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--out", default=os.path.join("database", "cache",
                                                  "battery_degenerate.parquet"))
    ap.add_argument("--cap-s", type=int, default=60)
    args = ap.parse_args()

    graphs = degenerate_graphs(args.max_n)
    disconnected = sum(1 for g in graphs if not nx.is_connected(g))
    print(f"{len(graphs)} degenerate graphs up to n={args.max_n} "
          f"({disconnected} disconnected)")

    from pipeline import invariants_graphcalc as battery
    ids = [graph6_id(g) for g in graphs]
    frame = battery.cached_battery(graphs, ids, cache_path=args.out,
                                   cap_s=args.cap_s, max_n=args.max_n)
    print(f"battery: {frame.shape[0]} rows x {frame.shape[1]} columns → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
