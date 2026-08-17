#!/usr/bin/env python3
"""
tools/run_shard.py — depth-first CEGIS shard launcher for the SLURM array.

Splits the full numeric invariant battery into N contiguous chunks (N = the
array size) and runs one independent CEGIS pass per chunk, each against its
own isolated cache/hard_seed/output directories so concurrent shards never
race on shared state (database/hard_seed/graphs.g6, database/cache/*.parquet).
Each shard starts from a copy of the shared seed (see tools/slurm comments)
so it benefits from the already-accumulated witnesses/battery without
recomputing them.

Reads SLURM_ARRAY_TASK_ID / SLURM_ARRAY_TASK_COUNT (falls back to env
SHARD_ID / SHARD_COUNT, then to 0/1, for local testing).

Usage (normally invoked from tools/slurm/cegis_shard.sbatch):
    python tools/run_shard.py
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("run_shard")

_TARGETS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "database", "shards", "all_targets.json")


def _shard_id_and_count() -> tuple[int, int]:
    # Explicit SHARD_* env wins over SLURM's, so a partial re-run (e.g. only the
    # two headline-invariant shards) can keep the original 5-way target split:
    # submit --array=0,1 but set SHARD_COUNT=5 so the chunking is unchanged.
    sid = int(os.environ.get("SHARD_ID", os.environ.get("SLURM_ARRAY_TASK_ID", "0")))
    cnt = int(os.environ.get("SHARD_COUNT", os.environ.get("SLURM_ARRAY_TASK_COUNT", "1")))
    return sid, cnt


def _chunk(items: list, sid: int, cnt: int) -> list:
    """Contiguous, deterministic chunk sid of cnt over a sorted item list."""
    items = sorted(items)
    n = len(items)
    base, rem = divmod(n, cnt)
    start = sid * base + min(sid, rem)
    size = base + (1 if sid < rem else 0)
    return items[start: start + size]


def main():
    sid, cnt = _shard_id_and_count()
    log.info("[shard %d/%d] starting", sid, cnt)

    # Determine this shard's invariant targets from a precomputed list (see
    # tools/slurm/cegis_shard.sbatch, which generates database/shards/
    # all_targets.json once on the login node before submission) — avoids 5
    # concurrent processes each probing/writing the shared seed-battery cache.
    if os.path.exists(_TARGETS_FILE):
        import json
        with open(_TARGETS_FILE) as fh:
            all_targets = json.load(fh)
    else:
        log.warning("[shard %d/%d] %s missing — probing the shared seed directly "
                    "(fine for a single local run, racy for concurrent shards)",
                    sid, cnt, _TARGETS_FILE)
        from pipeline.seed_corpus import SeedCorpus
        all_targets = SeedCorpus.from_txgraffiti(CONFIG).numeric_targets()
    targets = _chunk(all_targets, sid, cnt)
    log.info("[shard %d/%d] %d/%d invariants assigned: %s",
             sid, cnt, len(targets), len(all_targets), targets)

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG.cegis_targets = tuple(targets)
    CONFIG.cache_dir = os.path.join(base, "database", "shards", str(sid), "cache")
    # Tier batteries are read-only and identical for every shard, so they stay
    # in the one shared directory instead of being copied per shard. Only the
    # seed battery (written every round) needs to be shard-private.
    CONFIG.tier_cache_dir = os.path.join(base, "database", "cache")
    # …and witnesses are published to a single shared log so a graph found by
    # one shard can refute every shard's conjectures in the next round.
    CONFIG.shared_witness_log = os.path.join(
        base, "database", "hard_seed", "shared_witnesses.g6")
    # …and a shared witness is measured once, by whichever shard sees it first.
    CONFIG.peer_battery_glob = os.path.join(
        base, "database", "shards", "*", "cache", "seed_battery.parquet")

    # Optional evidence gates, off unless asked for (see config.py for the
    # trade-off each one makes).
    CONFIG.cegis_min_hypothesis_support = int(os.environ.get("MIN_HYP_SUPPORT", "0"))
    CONFIG.cegis_drop_decorative = os.environ.get("DROP_DECORATIVE", "0") == "1"
    CONFIG.hard_seed_dir = os.path.join(base, "database", "shards", str(sid), "hard_seed")
    CONFIG.output_dir = os.path.join(base, "results", f"shard_{sid}")

    # Full-node depth budget: only 5 jobs total, so push hard per shard.
    CONFIG.cegis_workers = int(os.environ.get("CEGIS_WORKERS", "240"))
    CONFIG.cegis_rounds = 25
    CONFIG.cegis_max_search = 150
    CONFIG.search_time_budget_s = 90
    CONFIG.sa_iterations = 600
    CONFIG.sa_restarts = 3
    CONFIG.rl_max_search = 30
    CONFIG.rl_episodes = 100
    CONFIG.rl_candidates = 400
    CONFIG.cegis_max_sophie = 1000

    # More effort on counterexample search specifically (denser + wider orders).
    # Env-overridable: NP-hard-target shards (chromatic/clique/independence/
    # domination) should cap the ceiling where exact ILP stays feasible — search
    # above ~n=30 there just hangs the solver (now bounded by the phase timeout,
    # but better avoided). e.g. SEARCH_ORDERS="6,8,10,12,14,16,18,20,22,24,26,28".
    _so = os.environ.get("SEARCH_ORDERS")
    CONFIG.search_orders = tuple(int(x) for x in _so.split(",")) if _so else \
        (6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 40, 50, 60, 75, 100)
    CONFIG.search_min_trials = 30
    CONFIG.search_eval_cap_s = 8

    # Generation depth (env-overridable so a deeper run is just a var flip; see
    # config.py for what each preset/toggle enables). Defaults preserve the cheap
    # FAST per-round loop. Set GEN_MODE=standard|deep, or FINAL_DEEP_PASS=1 to add
    # a single rich extraction pass on the converged seed.
    CONFIG.cegis_gen_mode = os.environ.get("GEN_MODE", "fast")
    _gc = os.environ.get("GEN_COMPLEXITY")
    CONFIG.cegis_gen_complexity = int(_gc) if _gc else None
    _b = lambda v: None if v is None else v == "1"
    CONFIG.cegis_gen_products = _b(os.environ.get("GEN_PRODUCTS"))
    CONFIG.cegis_gen_abs = _b(os.environ.get("GEN_ABS"))
    CONFIG.cegis_gen_min_max = _b(os.environ.get("GEN_MIN_MAX"))
    CONFIG.cegis_gen_log = _b(os.environ.get("GEN_LOG"))
    CONFIG.cegis_final_deep_pass = os.environ.get("FINAL_DEEP_PASS", "0") == "1"
    CONFIG.cegis_final_deep_mode = os.environ.get("FINAL_DEEP_MODE", "deep")
    _fdc = os.environ.get("FINAL_DEEP_COMPLEXITY")
    CONFIG.cegis_final_deep_complexity = int(_fdc) if _fdc else None

    # Self-limit to fit the SLURM --time allocation (see cegis_shard.sbatch);
    # leaves margin so the process persists survivors before SLURM's hard kill.
    CONFIG.cegis_time_budget_s = int(os.environ.get("CEGIS_TIME_BUDGET_S", str(29 * 3600)))

    import run_cegis
    return run_cegis.main(["--rounds", str(CONFIG.cegis_rounds), "--no-prove"])


if __name__ == "__main__":
    sys.exit(main())
