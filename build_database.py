#!/usr/bin/env python
"""
build_database.py — assemble the conjecture-pipeline graph database.

Streams every configured graph source through the invariant battery in
``graphs.invariants`` and writes one CSV row per graph to
``database/graph_database.csv``.  Large classes are sampled (see ``--*-cap``
flags) so the build stays tractable; small/medium classes are taken whole.

Sources
-------
* named graphs        (graphs.generators.named_graphs)
* nauty corpus        (generated_nauty/, geng output, n = 1..9)
* cographs, minimal Cayley, cages, minimal Ramsey, strongly-regular (Spence)
* House of Graphs     (hog_all_28859_graphs.g6)
* minimally rigid     (zipped g6, sampled per member)

Run::

    python build_database.py                  # default caps
    python build_database.py --hog-cap 0      # include all 28859 HoG graphs
    python build_database.py --out custom.csv
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import time
from typing import Iterator, Optional, Tuple

import networkx as nx

from graphs import loaders as L
from graphs.generators import named_graphs
from graphs.invariants import (
    INVARIANTS, BOOLEANS, FAST_INVARIANTS, evaluate_all,
)

logger = logging.getLogger("build_database")

Pair = Tuple[str, nx.Graph]

# Fixed column order: metadata first, then every invariant/boolean key.
INV_KEYS = list(INVARIANTS.keys()) + list(BOOLEANS.keys())
META_KEYS = ["idx", "source", "name", "n", "m", "g6"]


def _g6(G: nx.Graph) -> str:
    """Canonical-ish graph6 string (relabelled 0..n-1 for safety)."""
    H = nx.convert_node_labels_to_integers(G)
    return nx.to_graph6_bytes(H, header=False).strip().decode("ascii")


def _named() -> Iterator[Pair]:
    for name, G in named_graphs():
        yield (f"named:{name}", G)


def collect_sources(args) -> Iterator[Tuple[str, Iterator[Pair]]]:
    """Yield (label, pair-iterator) for each enabled source."""
    def none_if_zero(v):
        return None if v in (0, None) else v

    yield ("named", _named())
    # nauty: take n<=8 whole, sample n=9
    yield ("nauty<=8", L.load_nauty(max_vertices=8))
    yield ("nauty9", _nauty9_only(none_if_zero(args.nauty9_cap)))
    yield ("cographs", L.load_cographs())
    yield ("minimal_cayley", L.load_minimal_cayley())
    yield ("cages", L.load_cages(cap_per_file=none_if_zero(args.cages_cap)))
    yield ("minimal_ramsey",
           L.load_minimal_ramsey(cap_per_file=none_if_zero(args.ramsey_cap)))
    yield ("srg", L.load_srg(cap_per_file=none_if_zero(args.srg_cap)))
    yield ("hog", L.load_hog(cap=none_if_zero(args.hog_cap)))
    if not args.no_rigid:
        yield ("minimally_rigid", L.load_minimally_rigid(
            cap_per_member=none_if_zero(args.rigid_cap),
            max_n=args.rigid_max_n))


def _nauty9_only(cap: Optional[int]) -> Iterator[Pair]:
    """Just the 9-vertex slice of the nauty corpus (sampled)."""
    d = os.path.join(L.GRAPHS_DIR, "generated_nauty")
    path = os.path.join(d, "graphs_9v_all.g6")
    if not os.path.isfile(path):
        return
    for i, g in enumerate(L.load_g6_file(path, cap=cap, seed=51)):
        yield (f"nauty:9v_all#{i}", g)


def build(args) -> None:
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    t0 = time.perf_counter()
    idx = 0
    per_source: dict[str, int] = {}

    with open(args.out, "w", newline="", encoding="ascii") as fh:
        writer = csv.writer(fh)
        writer.writerow(META_KEYS + INV_KEYS)

        for label, it in collect_sources(args):
            s0 = time.perf_counter()
            count = 0
            for source, G in it:
                if G.number_of_nodes() == 0:
                    continue
                # Full invariants for small graphs; for large graphs fall back
                # to the fast subset (skips O(n)-maxflow connectivity and the
                # spectral invariants that crawl on 100s-of-vertex graphs).
                if G.number_of_nodes() <= args.full_invariant_max:
                    inv = evaluate_all(G)
                else:
                    inv = evaluate_all(G, {**FAST_INVARIANTS, **BOOLEANS})
                row = [
                    idx, source, source, G.number_of_nodes(),
                    G.number_of_edges(), _g6(G),
                ]
                row += [inv.get(k, "") for k in INV_KEYS]
                writer.writerow(row)
                idx += 1
                count += 1
                if count % 2000 == 0:
                    logger.info("  %s: %d graphs...", label, count)
            per_source[label] = count
            logger.info("%-16s %7d graphs  (%.1fs)",
                        label, count, time.perf_counter() - s0)

    logger.info("-" * 48)
    logger.info("TOTAL %d graphs in %.1fs -> %s",
                idx, time.perf_counter() - t0, args.out)
    for k, v in per_source.items():
        logger.info("  %-16s %7d", k, v)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=os.path.join("database",
                   "graph_database.csv"))
    p.add_argument("--nauty9-cap", type=int, default=5000,
                   help="sample size for 9-vertex graphs (0 = all 274668)")
    p.add_argument("--hog-cap", type=int, default=5000,
                   help="sample size for House of Graphs (0 = all 28859)")
    p.add_argument("--cages-cap", type=int, default=0,
                   help="per-file cap for cages (0 = all)")
    p.add_argument("--ramsey-cap", type=int, default=2000,
                   help="per-file cap for minimal Ramsey (0 = all)")
    p.add_argument("--srg-cap", type=int, default=500,
                   help="per-file cap for strongly-regular (0 = all)")
    p.add_argument("--rigid-cap", type=int, default=200,
                   help="per-archive-member cap for minimally rigid (0 = all)")
    p.add_argument("--rigid-max-n", type=int, default=11,
                   help="skip rigid members with more than this many vertices")
    p.add_argument("--no-rigid", action="store_true",
                   help="skip the minimally rigid class entirely")
    p.add_argument("--full-invariant-max", type=int, default=40,
                   help="graphs with more vertices get only the fast invariant "
                        "subset (full set is too slow on large graphs)")
    p.add_argument("-q", "--quiet", action="store_true")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(message)s",
    )
    build(args)


if __name__ == "__main__":
    main()
