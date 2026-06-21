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

Incremental re-sweep: round 1 sweeps every LHS (target) invariant. A later
round only re-sweeps the LHS invariants whose bounds the previous round's
counterexamples actually broke (``dirty_lhs``) — the only targets whose
relevant values changed. When nothing is broken, the loop has converged and
stops early, instead of re-running the full sweep for no new conjectures.

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
from pipeline.reporting import annotate_complexity, print_conjectures
from pipeline.unified import UnifiedPipeline, _lean_skeleton


def _gen_expression_stages(cfg):
    """Nonlinear / expression-tree conjectures: Graffiti3 (native Python) and,
    optionally, the Sage Conjecturing stage with optimal-coefficient tuning."""
    out = []
    if getattr(cfg, "graffiti3_enabled", True):
        try:
            from pipeline.graffiti3_stage import Graffiti3Generator
            g3 = Graffiti3Generator(cfg=cfg).generate_candidates()
            log.info("[expr] Graffiti3: %d conjectures", len(g3))
            out += g3
        except Exception as e:
            log.warning("[expr] Graffiti3 stage failed: %s", e)
    if getattr(cfg, "sage_enabled", True):
        try:
            sage = PIPE._gen_sage(run_sage=False, max_geng=7, t=8)
            if getattr(cfg, "sage_tune_coefficients", False) and sage:
                from pipeline.tuning import tune_sage_conjectures
                sage = tune_sage_conjectures(sage)
                log.info("[expr] Sage: %d conjectures (coefficient-tuned)", len(sage))
            else:
                log.info("[expr] Sage: %d conjectures", len(sage))
            out += sage
        except Exception as e:
            log.warning("[expr] Sage stage failed: %s", e)
    return out

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
    survived = g.generate_candidates()           # txgraffiti generators + Dalmatian/Morgan
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

def generate_round(lhs_targets, gen_workers, max_conj, ctx):
    """Parallel sharded TxGraffiti generation over the current database.

    Only the LHS (target) invariants in ``lhs_targets`` are swept; the RHS still
    ranges over all invariants inside each shard.
    """
    PIPE.txg.invalidate()                         # rebuild from the grown DB
    PIPE.txg._load_arrays()                       # preload once in parent (COW)
    txg = []
    with ctx.Pool(gen_workers, maxtasksperchild=1) as pool:
        for lhs, nraw, nsurv, nknown, keep in pool.imap_unordered(gen_worker, lhs_targets):
            log.info("    LHS=%-14s raw=%7d dalmatian=%6d known=%5d novel_kept=%d",
                     lhs, nraw, nsurv, nknown, len(keep))
            txg.extend(keep)
    txg.sort(key=lambda c: c.score, reverse=True)
    txg = txg[:max_conj]
    for c in txg:
        c.generation_method = "txgraffiti"
    return txg


def attack_round(active, attack_workers, ctx):
    """Parallel counterexample attack; persist every refuting graph into the DB.

    Returns (refuted_count, dirty_lhs) where dirty_lhs is the set of LHS
    invariants whose bounds the newly-added counterexamples actually broke —
    i.e. the only LHS targets whose values changed enough to need re-sweeping.
    """
    byid = {c.id: c for c in active}
    refuted = 0
    dirty_lhs: set = set()
    with ctx.Pool(attack_workers, maxtasksperchild=25) as pool:
        for cid, edges, nn in pool.imap_unordered(attack_worker, active):
            if edges is not None:
                G = nx.Graph()
                G.add_nodes_from(range(nn))
                G.add_edges_from(edges)
                c = byid[cid]
                PIPE._persist(c, G)               # marks falsified + grows DB
                refuted += 1
                if c.inequality is not None:
                    dirty_lhs.add(c.inequality.inv_a)
    return refuted, dirty_lhs


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
    # LHS invariants to sweep this round. Round 1 sweeps all; later rounds sweep
    # only the LHS whose bounds the previous round's counterexamples broke.
    lhs_targets = list(numeric)

    for rnd in range(1, args.rounds + 1):
        db0 = len(PIPE.db)
        log.info("=" * 60)
        log.info("[ROUND %d/%d]  database = %d graphs", rnd, args.rounds, db0)
        if not lhs_targets:
            log.info("  no LHS invariant values changed last round — converged")
            break

        # ---- generation (on the current, possibly augmented, DB) ----------
        log.info("  [gen] parallel TxGraffiti — %d/%d LHS shards (%s), %d workers",
                 len(lhs_targets), len(numeric),
                 "all" if len(lhs_targets) == len(numeric) else ",".join(sorted(lhs_targets)),
                 args.gen_workers)
        txg = generate_round(lhs_targets, args.gen_workers, args.max_conjectures, ctx)
        round_cands = list(txg)
        if not sage_added:
            round_cands += _gen_expression_stages(PIPE.cfg)
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
        refuted, dirty_lhs = attack_round(active, args.attack_workers, ctx)
        total_refuted += refuted
        # next round re-sweeps only the LHS invariants whose values changed
        lhs_targets = [a for a in numeric if a in dirty_lhs]
        log.info("  [attack] refuted %d; database grew %d → %d graphs; "
                 "next round re-sweeps %d LHS (%s)",
                 refuted, db0, len(PIPE.db), len(lhs_targets),
                 ",".join(sorted(lhs_targets)) or "none")

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
    annotate_complexity(all_cands)                       # store op-count metric
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
    print_conjectures(survivors, sort_by=getattr(cfg, "report_sort_by", "score"),
                      top=120, show_lean=False, title="SURVIVORS")
    print(f"\n  report -> {outdir/'parallel_report.json'}")


if __name__ == "__main__":
    main()
