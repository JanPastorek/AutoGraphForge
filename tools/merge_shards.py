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


def _drop_cross_shard_refuted(conjs: list, n_shards: int) -> tuple:
    """Re-refute the merged survivors against the merged witness set.

    Each shard grows its own hard seed and never sees the others', so a graph
    that one shard worked hard to find cannot kill a conjecture another shard
    is keeping. Unioning the survivors without re-checking them therefore
    reports conjectures the run had the evidence to refute — the witness simply
    sat in the wrong shard.

    Evaluation only: the witnesses already exist, so this costs one pass over
    the cached batteries and no search.
    """
    import glob
    import hashlib

    from pipeline import conjecture_lattice as cl

    # Each shard runs against its own *copy* of the refutation tiers, so the
    # 18 MB bigdb battery appears six times over. Loading it once instead of
    # six times is the difference between a few hundred MB and a few GB, and
    # deduplicating by content hash keeps that safe if the copies ever diverge.
    candidates = sorted(
        glob.glob(os.path.join("database", "shards", "*", "cache", "*.parquet"))
        + glob.glob(os.path.join(CONFIG.cache_dir, "*.parquet")))
    paths, seen = [], set()
    for path in candidates:
        with open(path, "rb") as fh:
            digest = hashlib.blake2b(fh.read(), digest_size=16).hexdigest()
        if digest in seen:
            log.info("[merge] skipping duplicate cache %s", path)
            continue
        seen.add(digest)
        paths.append(path)
    frame = cl.load_pool(paths)
    if frame is None:
        log.warning("[merge] no cached batteries found — skipping the "
                    "cross-shard refutation pass")
        return conjs, 0, len(conjs)

    evaluator = cl.PoolEvaluator(frame)
    payloads = [{"statement": c.statement} for c in conjs]
    refuted, unchecked = cl.find_refuted(payloads, evaluator)
    log.info("[merge] cross-shard refutation: %d graphs, %d survivor(s) refuted, "
             "%d not checkable", evaluator.n_rows, len(refuted), unchecked)
    for i, witness in list(refuted.items())[:5]:
        log.info("[merge]   refuted by %s: %s", witness, conjs[i].statement[:90])

    # A refutation is a result, not a rejection. Each entry here is a statement
    # paired with an explicit graph on which it fails — the strongest kind of
    # answer this pipeline produces, and the only one that is decidable in Lean
    # without a proof search. Earlier runs kept only `kept` and dropped these on
    # the floor, which is why the refuted set had to be recomputed from scratch.
    record_refutations(
        [{"statement": conjs[i].statement,
          "witness_g6": witness,
          "id": getattr(conjs[i], "id", None),
          "generation_method": getattr(conjs[i], "generation_method", None),
          "refuted_by": "cross-shard merge"}
         for i, witness in refuted.items()])

    kept = [c for i, c in enumerate(conjs) if i not in refuted]
    return kept, len(refuted), unchecked


def record_refutations(rows: list, filename: str = "cegis_refuted.json") -> str:
    """Write refuted statements with their counterexample graphs.

    Published whole via atomic rename so a reader never observes a partial
    file, matching how the rest of the pipeline publishes artefacts.
    """
    os.makedirs(CONFIG.output_dir, exist_ok=True)
    path = os.path.join(CONFIG.output_dir, filename)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(rows, fh, indent=1)
    os.replace(tmp, path)
    log.info("[merge] wrote %s (%d refutation(s) with witnesses)", path, len(rows))
    return path


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", type=int, default=5)
    ap.add_argument("--keep-cross-shard-refuted", action="store_true",
                    help="skip the cross-shard refutation pass (old behaviour)")
    args = ap.parse_args(argv)

    conjs = _merge_survivors(args.shards)
    added_witnesses = _merge_hard_seeds(args.shards)
    n_refuted = n_unchecked = 0
    if not args.keep_cross_shard_refuted:
        conjs, n_refuted, n_unchecked = _drop_cross_shard_refuted(conjs, args.shards)
        log.info("[merge] %d survivors after cross-shard refutation", len(conjs))

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
        "cross_shard_refuted": n_refuted,
        "cross_shard_unchecked": n_unchecked,
    }
    out_json = os.path.join(CONFIG.output_dir, "cegis_results.json")
    with open(out_json, "w") as fh:
        json.dump(payload, fh, indent=2)
    log.info("[merge] wrote %s", out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
