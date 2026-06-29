#!/usr/bin/env python3
"""
tools/merge_shards.py — reconcile the 5 independent CEGIS shards (see
tools/run_shard.py) into the single results/ tree the rest of the pipeline
(run_cegis.py --reprove, the prover stage) expects.

  * results/shard_{0..4}/cegis_survivors.dill → results/cegis_survivors.dill
    (concatenated, deduped by statement, sorted by complexity).
  * results/shard_{0..4}/cegis_results.json   → results/cegis_results.json
    (per-shard payloads merged; survivors/proved counts summed).
  * database/shards/{0..4}/hard_seed/graphs.g6 → database/hard_seed/graphs.g6
    (union of every shard's grown witness set, deduped, appended to the
    canonical hard seed so future runs start from a strictly bigger seed).

Usage:
    python tools/merge_shards.py [--shards 5]
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from pipeline.reporting import annotate_complexity, sort_conjectures

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("merge_shards")


def _merge_survivors(n_shards: int) -> list:
    import dill
    all_conjs = []
    for i in range(n_shards):
        p = os.path.join("results", f"shard_{i}", "cegis_survivors.dill")
        if not os.path.exists(p):
            log.warning("[merge] missing %s — skipping shard %d", p, i)
            continue
        with open(p, "rb") as fh:
            conjs = dill.load(fh)
        log.info("[merge] shard %d: %d survivors", i, len(conjs))
        all_conjs += conjs

    seen, uniq = set(), []
    for c in all_conjs:
        key = c.statement
        if key not in seen:
            seen.add(key)
            uniq.append(c)
    log.info("[merge] %d total → %d after dedup", len(all_conjs), len(uniq))
    annotate_complexity(uniq)
    return sort_conjectures(uniq, by="complexity")


def _merge_hard_seeds(n_shards: int) -> int:
    canonical = os.path.join(CONFIG.hard_seed_dir, "graphs.g6")
    existing = set()
    if os.path.exists(canonical):
        with open(canonical) as fh:
            existing = {ln.strip() for ln in fh if ln.strip()}
    new = set()
    for i in range(n_shards):
        p = os.path.join("database", "shards", str(i), "hard_seed", "graphs.g6")
        if not os.path.exists(p):
            continue
        with open(p) as fh:
            new |= {ln.strip() for ln in fh if ln.strip()}
    add = sorted(new - existing)
    if add:
        os.makedirs(CONFIG.hard_seed_dir, exist_ok=True)
        with open(canonical, "a") as fh:
            for g6 in add:
                fh.write(g6 + "\n")
    log.info("[merge] hard seed: %d existing + %d new = %d total",
             len(existing), len(add), len(existing) + len(add))
    return len(add)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", type=int, default=5)
    args = ap.parse_args(argv)

    conjs = _merge_survivors(args.shards)
    added_witnesses = _merge_hard_seeds(args.shards)

    os.makedirs(CONFIG.output_dir, exist_ok=True)
    import dill
    out_dill = os.path.join(CONFIG.output_dir, "cegis_survivors.dill")
    with open(out_dill, "wb") as fh:
        dill.dump(conjs, fh)
    log.info("[merge] wrote %s (%d survivors)", out_dill, len(conjs))

    payload = {
        "survivors": len(conjs),
        "proved": 0,
        "conjectures": [c.to_dict() for c in conjs],
        "merged_from_shards": args.shards,
        "witnesses_added_to_canonical_hard_seed": added_witnesses,
    }
    out_json = os.path.join(CONFIG.output_dir, "cegis_results.json")
    with open(out_json, "w") as fh:
        json.dump(payload, fh, indent=2)
    log.info("[merge] wrote %s", out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
