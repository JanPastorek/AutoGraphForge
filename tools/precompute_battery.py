#!/usr/bin/env python3
"""
tools/precompute_battery.py — offline graphcalc battery for the big DB tier.

Computes the full graphcalc battery on graph structures and writes
``database/cache/battery_bigdb.parquet`` (graph6-indexed, with a ``graph6``
column so the refuter can reconstruct witnesses). The CEGIS ``Refuter`` loads
that file automatically as the 'bigdb' refutation tier when present.

Sources of structures:
  * database/graph_database_enriched.csv — has a ``g6`` column (HoG + families,
    incl. barbells etc.).
  * any extra graph6 file passed with --g6.

This is the expensive, one-time job (approved in docs/CEGIS_PLAN.md §3). It is
incremental: rerunning only computes graphs not already cached. Cap --max-n to
keep ILP invariants feasible (n≤16 ≈ 3s/graph).

Usage:
    python tools/precompute_battery.py --max-n 14 [--limit N] [--g6 FILE]
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

import networkx as nx
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from pipeline import invariants_graphcalc as battery
from pipeline.seed_corpus import graph6_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("precompute")


def _graphs_from_enriched(path: str):
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path, usecols=lambda c: c == "g6")
    out = []
    for s in df["g6"].dropna():
        try:
            out.append(nx.from_graph6_bytes(str(s).encode()))
        except Exception:
            pass
    log.info("loaded %d graphs from %s", len(out), path)
    return out


def _graphs_from_g6_file(path: str):
    out = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(nx.from_graph6_bytes(line.encode()))
                except Exception:
                    pass
    log.info("loaded %d graphs from %s", len(out), path)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=14)
    ap.add_argument("--limit", type=int, default=0, help="cap #graphs (0 = all)")
    ap.add_argument("--g6", action="append", default=[], help="extra graph6 file(s)")
    ap.add_argument("--workers", type=int, default=1,
                    help="fork-pool size for the per-graph ILP computation "
                         "(embarrassingly parallel across graphs)")
    args = ap.parse_args(argv)

    graphs = _graphs_from_enriched("database/graph_database_enriched.csv")
    for f in args.g6:
        graphs += _graphs_from_g6_file(f)
    graphs = [g for g in graphs if 2 <= g.number_of_nodes() <= args.max_n]
    if args.limit:
        graphs = graphs[: args.limit]
    if not graphs:
        log.error("no graphs to process"); return 1

    ids = [graph6_id(g) for g in graphs]
    uniq = {}
    for i, g in zip(ids, graphs):
        uniq.setdefault(i, g)
    log.info("computing battery for %d unique graphs (n≤%d)…", len(uniq), args.max_n)

    cache_path = os.path.join(CONFIG.cache_dir, "battery_bigdb.parquet")
    frame = battery.cached_battery(
        list(uniq.values()), list(uniq.keys()),
        cache_path=cache_path, cap_s=CONFIG.battery_cap_s, max_n=args.max_n,
        workers=args.workers)
    # store graph6 as a column too (the refuter reads it to rebuild witnesses)
    frame = frame.copy()
    frame["graph6"] = frame.index
    frame.to_parquet(cache_path)
    log.info("wrote %s  (%d graphs, %d cols)", cache_path, len(frame), frame.shape[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
