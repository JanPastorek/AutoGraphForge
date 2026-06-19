#!/usr/bin/env python3
"""
run_parallel.py — the full unified graph-conjecturing pipeline, parallelised,
run as a multi-round dynamic-database loop.

Each round:
  1. (re)build the per-invariant arrays from the CURRENT database
  2. parallel TxGraffiti generation, sharded by LHS (target) invariant
     (the Dalmatian filter buckets by LHS invariant, so shards are independent)
  3. + cached Sage expression-tree / property conjectures (round 1 only)
  4. novelty filter (drop linear rediscoveries of known theorems)
  5. parallel counterexample attack on the NEW conjectures of this round
  6. every refuting graph is persisted back into the database (in-memory +
     CSV), so the next round regenerates on a strictly tighter feasible region
     — the dynamic-database principle.

Conjectures already resolved (refuted or survived) in an earlier round are not
re-attacked; only conjectures that newly appear after the database grew are.

Memory: the 348k-graph DB and arrays load once in the parent and are shared
copy-on-write by forked workers. Each generation shard peaks ~12-16 GB, so
generation concurrency is bounded by --gen-workers (default 3).

Usage
-----
    python run_parallel.py [--rounds 3] [--max-conjectures 200]
                           [--gen-workers 3] [--attack-workers 12] [--search-n 12]
"""
from __future__ import annotations

import argparse
import json
import logging
import multiprocessing as mp
import time
from pathlib import Path

import networkx as nx

from config import CONFIG
from conjecture import ConjectureStatus
from pipeline.novelty import annotate
from pipeline.unified import UnifiedPipeline, _lean_skeleton

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("parallel")

# globals inherited by forked workers (set in parent before each Pool is created)
PIPE: UnifiedPipeline = None      # type: ignore
SEARCH_N = 12
KEEP_PER_LHS = 200                 # top novel survivors kept per LHS shard


# --------------------------------------------------------------- workers --

def gen_worker(lhs: str):
    """Enumerate + Dalmatian-filter + novelty-filter one LHS-invariant shard."""
    g = PIPE.txg
    g.lhs_subset = {lhs}
    cands = g._enumerate_candidates()
    survived = g._dalmatian_filter(cands)
    novel, known = annotate(survived)            # annotate returns (novel, known)
    novel.sort(key=lambda c: c.score, reverse=True)
    keep = novel[:KEEP_PER_LHS]
    for c in keep:                               # trim heavy witness lists for IPC
        c.tightness_witnesses = c.tightness_witnesses[:25]
    return lhs, len(cands), len(survived), len(known), keep


def attack_worker(c):
    """Attack one conjecture; return (id, refuting-edge-list|None, n)."""
    G = PIPE._attack(c, SEARCH_N)
    if G is None:
        return c.id, None, 0
    return c.id, list(G.edges()), G.number_of_nodes()


# --------------------------------------------------------------- stages --

def generate_round(numeric, gen_workers, max_conj, ctx):
    """Parallel sharded TxGraffiti generation over the current database."""
    PIPE.txg._arrays = None                       # rebuild from the grown DB
    PIPE.txg._load_arrays()                       # preload once in parent (COW)
    txg = []
    with ctx.Pool(gen_workers, maxtasksperchild=1) as pool:
        for lhs, nraw, nsurv, nknown, keep in pool.imap_unordered(gen_worker, numeric):
            log.info("    LHS=%-14s raw=%7d dalmatian=%6d known=%5d novel_kept=%d",
                     lhs, nraw, nsurv, nknown, len(keep))
            txg.extend(keep)
    txg.sort(key=lambda c: c.score, reverse=True)
    txg = txg[:max_conj]
    for c in txg:
        c.generation_method = "txgraffiti"
    return txg


def attack_round(active, attack_workers, ctx):
    """Parallel counterexample attack; persist every refuting graph into the DB."""
    byid = {c.id: c for c in active}
    refuted = 0
    with ctx.Pool(attack_workers, maxtasksperchild=25) as pool:
        for cid, edges, nn in pool.imap_unordered(attack_worker, active):
            if edges is not None:
                G = nx.Graph()
                G.add_nodes_from(range(nn))
                G.add_edges_from(edges)
                PIPE._persist(byid[cid], G)       # marks falsified + grows DB
                refuted += 1
    return refuted


# ------------------------------------------------------------------ main --

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--max-conjectures", type=int, default=200)
    ap.add_argument("--gen-workers", type=int, default=3)
    ap.add_argument("--attack-workers", type=int, default=12)
    ap.add_argument("--search-n", type=int, default=12)
    args = ap.parse_args(argv)

    global PIPE, SEARCH_N
    SEARCH_N = args.search_n
    t0 = time.time()
    cfg = CONFIG
    cfg.txgraffiti_max_conjectures = args.max_conjectures

    log.info("Building pipeline (loading full database)…")
    PIPE = UnifiedPipeline.build(cfg)
    names, numeric, bools, vals, bvals = PIPE.txg._load_arrays()
    n_ctx = 1 + sum(1 for b in bools
                    if (bvals[b] >= 0.5).sum() >= cfg.txgraffiti_min_support)
    log.info("DB ready: %d graphs, %d numeric invariants, %d contexts; "
             "max_conjectures=%d, rounds=%d",
             len(names), len(numeric), n_ctx, args.max_conjectures, args.rounds)

    ctx = mp.get_context("fork")

    seen: set = set()           # statements already generated (dedup across rounds)
    all_cands: list = []        # every distinct conjecture ever produced
    sage_added = False
    total_refuted = 0

    for rnd in range(1, args.rounds + 1):
        db0 = len(PIPE.db)
        log.info("=" * 60)
        log.info("[ROUND %d/%d]  database = %d graphs", rnd, args.rounds, db0)

        # ---- generation (on the current, possibly augmented, DB) ----------
        log.info("  [gen] parallel TxGraffiti — %d shards, %d workers",
                 len(numeric), args.gen_workers)
        txg = generate_round(numeric, args.gen_workers, args.max_conjectures, ctx)
        round_cands = list(txg)
        if not sage_added:
            round_cands += PIPE._gen_sage(run_sage=False, max_geng=7, t=8)
            sage_added = True

        # ---- dedup against everything seen before -------------------------
        new = []
        for c in round_cands:
            key = (c.statement, c.generation_method)
            if key in seen:
                continue
            seen.add(key)
            new.append(c)
            all_cands.append(c)
        log.info("  [gen] %d candidates this round, %d new (total distinct %d)",
                 len(round_cands), len(new), len(all_cands))

        # ---- novelty filter on the new linear conjectures -----------------
        novel, known = annotate([c for c in new if c.inequality is not None])
        known_ids = {id(c) for c in known}
        for c in new:
            c.metadata["novel"] = (c.inequality is None) or (id(c) not in known_ids)
        active = [c for c in new if c.inequality is None or id(c) not in known_ids]
        log.info("  [novelty] %d novel, %d known (linear); %d active to attack",
                 len(novel), len(known), len(active))

        if not active:
            log.info("  [round %d] no new conjectures to attack — loop converged", rnd)
            break

        # ---- parallel counterexample attack -------------------------------
        log.info("  [attack] %d conjectures, %d workers", len(active), args.attack_workers)
        refuted = attack_round(active, args.attack_workers, ctx)
        total_refuted += refuted
        log.info("  [attack] refuted %d; database grew %d → %d graphs",
                 refuted, db0, len(PIPE.db))

    # ---- finalise: survivors = novel/nonlinear never refuted --------------
    survivors = [c for c in all_cands
                 if c.status == ConjectureStatus.PROPOSED
                 and (c.inequality is None or c.metadata.get("novel"))]
    for c in survivors:
        c.mark_survived()
    log.info("=" * 60)
    log.info("[final] %d distinct generated, %d refuted, %d survivors",
             len(all_cands), total_refuted, len(survivors))

    # ---- autoformalization ----------------------------------------------
    for c in survivors:
        try:
            if c.inequality is not None:
                PIPE.formalizer.formalize(c)
            else:
                c.mark_formalized(_lean_skeleton(c))
        except Exception as e:
            log.debug("formalize failed %s: %s", c.id, e)
    formalized = sum(1 for c in survivors if c.lean_statement)
    log.info("[final] formalized %d/%d", formalized, len(survivors))

    # ---- report ----------------------------------------------------------
    rep = PIPE._report(all_cands, survivors, total_refuted, time.time() - t0)
    rep["rounds"] = args.rounds
    rep["final_db_graphs"] = len(PIPE.db)
    outdir = Path(cfg.output_dir)
    (outdir / "parallel_report.json").write_text(json.dumps(rep, indent=2))

    print("\n" + "=" * 64)
    print("  PARALLEL MULTI-ROUND PIPELINE REPORT")
    print("=" * 64)
    print(f"  rounds         : {args.rounds}")
    print(f"  generated      : {rep['generated_total']}  {rep['generated_by_method']}")
    print(f"  refuted (loop) : {rep['refuted']}")
    print(f"  survivors      : {rep['survivors']}  (novel: {rep['novel_survivors']})")
    print(f"  final DB       : {rep['final_db_graphs']} graphs")
    print(f"  elapsed        : {rep['elapsed_s']}s")
    print("=" * 64)
    print("  Survivors:")
    for r in rep["results"][:120]:
        tag = "NOVEL" if r["novel"] else "known"
        print(f"   [{tag:5s}] ({r['method']}) {r['statement']}")
    print(f"\n  report -> {outdir/'parallel_report.json'}")


if __name__ == "__main__":
    main()
