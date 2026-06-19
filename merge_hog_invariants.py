#!/usr/bin/env python3
"""
merge_hog_invariants.py — enrich the graph database with the House of Graphs
invariant export (graphs/hog_invariant_values_all.txt).

The export already carries every basic invariant *plus* ~30 richer ones
(treewidth, girth, spectral data, vertex cover, …), all pre-computed — so this
just merges, it does not recompute. The result keeps every non-HoG source from
the existing CSV and replaces the sampled HoG rows with the full HoG set,
filled out with the extra invariant columns.

    python merge_hog_invariants.py
    python merge_hog_invariants.py --in database/graph_database.csv \
                                   --out database/graph_database_enriched.csv
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import sys
import time

from graphs.invariants import INVARIANTS, BOOLEANS
from graphs.loaders import load_hog_invariants, HOG_INVARIANTS_FILE

try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(2147483647)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("merge_hog")

META_KEYS = ["idx", "source", "name", "n", "m", "g6"]
INV_KEYS = list(INVARIANTS.keys()) + list(BOOLEANS.keys())   # includes new keys


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--in", dest="inp", default=os.path.join("database", "graph_database.csv"))
    p.add_argument("--out", default=os.path.join("database", "graph_database_enriched.csv"))
    p.add_argument("--hog-txt", default=HOG_INVARIANTS_FILE)
    args = p.parse_args()

    t0 = time.perf_counter()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    with open(args.out, "w", newline="", encoding="utf-8") as out_fh:
        writer = csv.writer(out_fh)
        writer.writerow(META_KEYS + INV_KEYS)
        idx = 0

        # 1) Carry over every non-HoG row, widening to the new column set.
        kept = 0
        with open(args.inp, newline="") as in_fh:
            reader = csv.DictReader(in_fh)
            for row in reader:
                if (row.get("source") or "").startswith("hog"):
                    continue
                meta = [idx, row.get("source", ""), row.get("name", ""),
                        row.get("n", ""), row.get("m", ""), row.get("g6", "")]
                writer.writerow(meta + [row.get(k, "") for k in INV_KEYS])
                idx += 1
                kept += 1
        logger.info("Carried over %d non-HoG rows", kept)

        # 2) Append the full HoG set with the enriched invariants.
        hog = 0
        for G, g6, inv in load_hog_invariants(args.hog_txt):
            name = f"hog:#{hog}"
            meta = [idx, "hog", name,
                    int(inv.get("n", G.number_of_nodes())),
                    int(inv.get("m", G.number_of_edges())), g6]
            writer.writerow(meta + [inv.get(k, "") for k in INV_KEYS])
            idx += 1
            hog += 1
            if hog % 5000 == 0:
                logger.info("  …%d HoG graphs", hog)
        logger.info("Added %d HoG graphs from %s", hog, args.hog_txt)

    logger.info("-" * 52)
    logger.info("TOTAL %d rows, %d invariant columns -> %s  (%.1fs)",
                idx, len(INV_KEYS), args.out, time.perf_counter() - t0)


if __name__ == "__main__":
    main()
