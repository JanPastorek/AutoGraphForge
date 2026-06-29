"""
pipeline/cegis.py — the counterexample-guided conjecturing loop.

    generate on the seed  →  refute (tiers + active search)  →  add witnesses
    to the seed  →  regenerate … until a round refutes nothing (fixed point).

Generation is graffiti3 (FAST) over the seed's full graphcalc battery. Refutation
is the tiered NaN-aware `Refuter` followed, for pool-survivors, by active
counterexample search (SA + rlgt deep-CE/REINFORCE). Witnesses grow the seed
(and are persisted), so each round's conjectures are tighter and validated
against strictly more graphs. Survivors of a fixed-point round hold on everything
tried.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import networkx as nx

from config import Config, CONFIG
from pipeline.seed_corpus import SeedCorpus
from pipeline.refute_matrix import Refuter
from pipeline.search import find_counterexample

from txgraffiti.graffiti3.graffiti3 import Graffiti3, Mode
from txgraffiti.graffiti3.heuristics.dalmatian import dalmatian_filter
from txgraffiti.graffiti3.heuristics.morgan import morgan_filter

logger = logging.getLogger(__name__)

# Shared handles for forked refute/search workers. Populated in-place before each
# pool is created, so the children inherit the current candidates + refuter via
# copy-on-write (the graffiti3 conjectures carry unpicklable lambda predicates —
# fork avoids ever pickling them; only integer indices cross the boundary).
_W: dict = {}


def _refute_worker(idx: int):
    try:
        ref, wits, tier = _W["refuter"].refute(_W["cands"][idx])
        return idx, bool(ref), tier, [w for w in wits if w is not None]
    except Exception:
        return idx, False, None, []


def _search_worker(idx: int):
    try:
        g = find_counterexample(_W["cands"][idx], _W["allcols"], _W["cfg"], seed=idx)
        return idx, g
    except Exception:
        return idx, None


@dataclass
class CegisResult:
    survivors: List = field(default_factory=list)       # native graffiti3 conjectures
    touches: List[int] = field(default_factory=list)
    g3: Optional[Graffiti3] = None                      # for Lean export of survivors
    seed: Optional[SeedCorpus] = None
    rounds_run: int = 0
    fixed_point: bool = False
    history: List[dict] = field(default_factory=list)


class CEGIS:
    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        logger.info("[cegis] loading seed (TxGraffiti expressive graphs + battery)…")
        self.seed = SeedCorpus.from_txgraffiti(cfg)
        logger.info("[cegis] building refutation tiers…")
        self.refuter = Refuter(cfg)

    # ---------------------------------------------------------- generation --
    def _targets(self) -> List[str]:
        nums = self.seed.numeric_targets()
        if self.cfg.cegis_targets:
            nums = [t for t in nums if t in set(self.cfg.cegis_targets)]
        if self.cfg.cegis_max_targets:
            nums = nums[: self.cfg.cegis_max_targets]
        return nums

    def _gen_kwargs(self, mode: Optional[str] = None, complexity: Optional[int] = None) -> dict:
        """graffiti3.conjecture() kwargs from config (mode preset + per-feature
        overrides). ``mode``/``complexity`` args let the one-shot final pass run
        a deeper preset than the per-round loop."""
        m = mode or self.cfg.cegis_gen_mode
        comp = complexity if complexity is not None else self.cfg.cegis_gen_complexity
        kw = {"mode": Mode(m), "enable_sophie": self.cfg.graffiti3_sophie}
        if comp is not None:
            kw["complexity"] = comp
        if self.cfg.cegis_gen_products is not None:
            kw["include_invariant_products"] = self.cfg.cegis_gen_products
        if self.cfg.cegis_gen_abs is not None:
            kw["include_abs"] = self.cfg.cegis_gen_abs
        if self.cfg.cegis_gen_min_max is not None:
            kw["include_min_max"] = self.cfg.cegis_gen_min_max
        if self.cfg.cegis_gen_log is not None:
            kw["include_log"] = self.cfg.cegis_gen_log
        if self.cfg.cegis_gen_quick is not None:
            kw["quick"] = self.cfg.cegis_gen_quick
        return kw

    def _gen_cache_key(self, targets, gen_kwargs: dict) -> str:
        """Stable key for the (seed, targets, gen-config) → raw candidates map.
        The generation config (mode/complexity/feature flags) is part of the key
        so changing depth invalidates a stale cache instead of reusing it."""
        import hashlib
        ids = ",".join(sorted(self.seed.graphs.keys()))
        cfg_sig = "|".join(f"{k}={gen_kwargs.get(k)}" for k in sorted(
            ("mode", "complexity", "include_invariant_products", "include_abs",
             "include_min_max", "include_log", "enable_sophie")))
        sig = f"{ids}|{','.join(targets)}|{cfg_sig}"
        return hashlib.sha1(sig.encode()).hexdigest()[:16]

    def _generate(self, mode: Optional[str] = None,
                  complexity: Optional[int] = None) -> Tuple[list, Graffiti3]:
        import os
        from pipeline.lean_export import make_lean_label
        frame = self.seed.frame
        targets = self._targets()
        gen_kwargs = self._gen_kwargs(mode, complexity)
        # Map the supported invariants to their real Lean (mathlib + preamble)
        # names so survivor exports are kernel-checkable, not stubs over undefined
        # symbols; unsupported columns get a placeholder and are filtered later.
        lean_label = make_lean_label(frame.columns)
        g3 = Graffiti3(frame, lean_label=lean_label)   # cheap; .conjecture() is not

        # Generation cache: graffiti3's .conjecture() is the ~13-min cost and is
        # deterministic in (seed, targets, config). Cache the *raw* output (via
        # dill — the conjectures hold local closures pickle can't handle) so a
        # repeated dataset is restored instantly instead of regenerated.
        ckey = os.path.join(self.cfg.cache_dir,
                            f"gen_{self._gen_cache_key(targets, gen_kwargs)}.dill")
        ineqs = sophie = None
        if os.path.exists(ckey):
            try:
                import dill
                with open(ckey, "rb") as fh:
                    ineqs, sophie = dill.load(fh)
                logger.info("[cegis] generation restored from cache (%d ineq + %d sophie)",
                            len(ineqs), len(sophie))
            except Exception as e:
                logger.warning("[cegis] gen cache read failed (%s) — regenerating", e)
                ineqs = None
        if ineqs is None:
            res = g3.conjecture(targets, **gen_kwargs)
            ineqs = list(res.conjectures)
            sophie = list(getattr(res, "sophie_conditions", [])) \
                if self.cfg.graffiti3_sophie else []
            try:
                import dill
                os.makedirs(self.cfg.cache_dir, exist_ok=True)
                with open(ckey, "wb") as fh:
                    dill.dump((ineqs, sophie), fh)
                logger.info("[cegis] cached generation → %s", os.path.basename(ckey))
            except Exception as e:
                logger.warning("[cegis] gen cache write failed: %s", e)
        n_raw = len(ineqs)
        n_sophie_raw = len(sophie)
        # Sophie conditions can't go through Dalmatian/Morgan (no numeric bound);
        # rank them by significance (support of the hypothesis) and keep the top-N.
        if sophie and self.cfg.cegis_max_sophie and \
           len(sophie) > self.cfg.cegis_max_sophie:
            sophie.sort(key=lambda s: getattr(s, "support_h", 0), reverse=True)
            sophie = sophie[: self.cfg.cegis_max_sophie]

        # Freeze each conjecture's hypothesis on the SEED frame. graffiti3's
        # check() otherwise re-derives an "auto-base" (always-True booleans) from
        # whatever frame it sees, so a bound that holds on the seed would be
        # re-judged under a *different* hypothesis on the refutation pool and
        # spuriously "refuted". Freezing makes the hypothesis part of the
        # conjecture, consistent across seed / pools / search.
        for c in ineqs:
            try:
                if getattr(c, "condition", None) is None and hasattr(c, "_auto_base"):
                    c.condition = c._auto_base(frame)
            except Exception:
                pass

        # Drop degenerate invariant-vs-constant bounds (clique_number ≤ 20, 9 ≤
        # size, …): seed-specific or trivial, not real conjectures. Sophie
        # sufficient-conditions are a separate list and are NOT filtered.
        if self.cfg.cegis_drop_constant_bounds:
            from pipeline.candidate_filters import drop_constant_bounds
            before = len(ineqs)
            ineqs = drop_constant_bounds(ineqs, list(frame.columns))
            if before != len(ineqs):
                logger.info("[cegis] dropped %d invariant-vs-constant bounds "
                            "(%d → %d)", before - len(ineqs), before, len(ineqs))

        # Dalmatian significance filter on the seed: keep only conjectures that
        # are the tightest bound for at least one seed graph (per target /
        # direction / hypothesis). This makes the full graphcalc battery
        # tractable — graffiti3's product features generate ~10^5 raw candidates,
        # the Dalmatian envelope is typically a few hundred. Runs *after* the
        # condition freeze (it groups by condition).
        if self.cfg.cegis_dalmatian:
            try:
                ineqs = dalmatian_filter(frame, ineqs)
            except Exception as e:
                logger.warning("[cegis] dalmatian_filter failed (%s) — keeping raw", e)
        n_dal = len(ineqs)
        # Morgan: drop a bound asserted on a smaller class when the *same* bound
        # holds on a larger class (hypothesis-maximality).
        if self.cfg.cegis_morgan:
            try:
                ineqs = morgan_filter(frame, ineqs)
            except Exception as e:
                logger.warning("[cegis] morgan_filter failed (%s) — skipping", e)

        # dedup by pretty(); re-append the (separately handled) Sophie conditions
        seen, uniq = set(), []
        for c in ineqs + sophie:
            try:
                key = c.pretty()
            except Exception:
                key = repr(c)
            if key not in seen:
                seen.add(key); uniq.append(c)
        logger.info("[cegis] candidates: %d ineq raw → %d Dalmatian → %d Morgan "
                    "(+%d/%d sophie kept) → %d total",
                    n_raw, n_dal, len(ineqs), len(sophie), n_sophie_raw, len(uniq))
        return uniq, g3

    # ----------------------------------------------- refute + search (||) --
    def _refute_and_search(self, cands, all_cols, do_search):
        """Two embarrassingly-parallel phases over candidates:
        (A) tiered pool refutation on all; (B) active search on the capped pool
        survivors. Returns (survivors, witnesses, refuted_pool, refuted_search)."""
        import multiprocessing as mp
        n = len(cands)
        workers = max(1, int(self.cfg.cegis_workers))
        _W.clear()
        _W.update({"refuter": self.refuter, "cands": cands,
                   "allcols": all_cols, "cfg": self.cfg})
        ctx = mp.get_context("fork")

        # Hard per-phase wall-clock cap. The per-eval SIGALRM in the search
        # cannot interrupt a C-extension ILP solver (exact χ/ω/α on a big graph),
        # so a single eval can hang a worker indefinitely. We run the pool with a
        # deadline via imap_unordered; if it elapses we ``terminate()`` the pool
        # (SIGTERM *does* kill a hung native computation) and treat every
        # not-yet-returned candidate as a survivor (never a false refutation).
        phase_to = int(getattr(self.cfg, "cegis_phase_timeout_s", 0) or 0) or None

        def _run(fn, items, chunk, default):
            items = list(items)
            if workers <= 1 or len(items) <= 1:
                return [fn(i) for i in items]
            out: List = [None] * len(items)
            with ctx.Pool(workers) as pool:
                # apply_async + readiness polling (portable; avoids the
                # IMapIterator.next API). Collect every result that finishes
                # before the deadline; on timeout, terminate() (SIGTERM kills a
                # hung native ILP solver) and keep the rest as survivors.
                asyncs = [(i, pool.apply_async(fn, (it,))) for i, it in enumerate(items)]
                deadline = (time.time() + phase_to) if phase_to else None
                pending = asyncs
                while pending:
                    nxt = []
                    for i, ar in pending:
                        if ar.ready():
                            try:
                                out[i] = ar.get()
                            except Exception:
                                out[i] = default(items[i])
                        else:
                            nxt.append((i, ar))
                    pending = nxt
                    if not pending:
                        break
                    if deadline is not None and time.time() > deadline:
                        logger.warning("[cegis] phase wall-clock cap (%ss) hit: %d/%d done; "
                                       "killing hung workers, rest kept as survivors",
                                       phase_to, len(items) - len(pending), len(items))
                        pool.terminate(); pool.join()
                        for i, _ar in pending:
                            out[i] = default(items[i])
                        break
                    time.sleep(0.2)
            return out

        # Phase A — pool refutation on every candidate
        from collections import Counter
        tier_counts: Counter = Counter()
        witnesses: List[nx.Graph] = []
        refuted_pool = 0
        survivor_idx: List[int] = []
        for idx, ref, tier, wits in _run(_refute_worker, range(n), n // (workers * 4),
                                         lambda i: (i, False, None, [])):
            if ref:
                refuted_pool += 1
                tier_counts[tier or "?"] += 1
                witnesses += wits
            else:
                survivor_idx.append(idx)

        # Phase B — active search on the (capped) pool survivors
        refuted_search = 0
        survivors: List = []
        to_search = survivor_idx[: self.cfg.cegis_max_search] if do_search else []
        kept = survivor_idx[len(to_search):]
        for idx, g in _run(_search_worker, to_search, 1, lambda i: (i, None)):
            if g is not None:
                refuted_search += 1
                witnesses.append(g)
            else:
                survivors.append(cands[idx])
        survivors += [cands[i] for i in kept]

        # Phase C — RL (rlgt) as a *bounded* last resort on the top-K survivors.
        # RL spins up a torch agent per conjecture/order, far too heavy to run on
        # every survivor, so it only attacks a small subset here.
        if ("rl" in self.cfg.cegis_searchers and self.cfg.rl_enabled
                and survivors and self.cfg.rl_max_search > 0):
            from pipeline.search.problem import GraphSearchProblem
            from pipeline.search.rlgt_adapter import rl_search
            rl_orders = tuple(o for o in self.cfg.search_orders if o <= 16)[:2]
            k = min(self.cfg.rl_max_search, len(survivors))
            still = []
            rl_deadline = (time.time() + phase_to) if phase_to else None
            for ci, c in enumerate(survivors[:k]):
                if rl_deadline and time.time() > rl_deadline:
                    logger.warning("[cegis] RL phase wall-clock cap hit at %d/%d — "
                                   "keeping the rest as survivors", ci, k)
                    still += survivors[ci:k]
                    break
                prob = GraphSearchProblem(c, all_cols,
                                          eval_cap_s=self.cfg.search_eval_cap_s)
                g = rl_search(prob, orders=rl_orders,
                              episodes=min(self.cfg.rl_episodes, 5),
                              candidates=min(self.cfg.rl_candidates, 40),
                              agent_kind=self.cfg.rl_agent)
                if g is not None:
                    refuted_search += 1
                    witnesses.append(g)
                else:
                    still.append(c)
            survivors = still + survivors[k:]
        if refuted_search:
            tier_counts["search"] += refuted_search
        if tier_counts:
            logger.info("[cegis] refutation provenance: %s",
                        ", ".join(f"{t}={c}" for t, c in tier_counts.most_common()))
        self._last_tier_counts = dict(tier_counts)
        return survivors, witnesses, refuted_pool, refuted_search

    # ---------------------------------------------------------------- loop --
    def run(self) -> CegisResult:
        all_cols = self.seed.numeric_targets() + self.seed.booleans()
        do_search = any(k in ("sa", "rl") for k in self.cfg.cegis_searchers)
        result = CegisResult(seed=self.seed)
        survivors, g3 = [], None
        t_start = time.time()

        # Best healthy round's survivors, kept so a later degenerate round (where
        # generation collapses to near-zero candidates — see the guard below)
        # cannot overwrite a good result with an empty one.
        best_survivors, best_g3 = [], None
        prev_cands = 0

        for rnd in range(1, self.cfg.cegis_rounds + 1):
            if self.cfg.cegis_time_budget_s and (time.time() - t_start) > self.cfg.cegis_time_budget_s:
                logger.info("[cegis] wall-clock budget (%ds) reached before round %d — "
                            "stopping with current survivors", self.cfg.cegis_time_budget_s, rnd)
                break
            t0 = time.time()
            cands, g3 = self._generate()
            logger.info("[cegis][round %d] seed=%d graphs → %d candidate conjectures",
                        rnd, len(self.seed.graphs), len(cands))

            # Generation-collapse guard: if a round produces drastically fewer
            # candidates than the previous healthy round, generation has gone
            # degenerate (e.g. seed pathology). Stop and keep the previous
            # round's survivors rather than letting the few trivial leftovers be
            # refuted down to zero. Only triggers once we have a healthy baseline.
            if prev_cands >= 100 and len(cands) < 0.33 * prev_cands:
                logger.warning("[cegis] generation collapse at round %d (%d cands "
                               "vs %d previous) — stopping, keeping round %d survivors",
                               rnd, len(cands), prev_cands, rnd - 1)
                break

            survivors, witnesses, refuted_pool, refuted_search = \
                self._refute_and_search(cands, all_cols, do_search)

            added = self.seed.add(witnesses) if witnesses else []
            if added:
                self.seed.persist_witnesses(added)

            stat = {
                "round": rnd, "candidates": len(cands), "survivors": len(survivors),
                "refuted_pool": refuted_pool, "refuted_search": refuted_search,
                "refutation_by_tier": getattr(self, "_last_tier_counts", {}),
                "witnesses_added": len(added), "seed_size": len(self.seed.graphs),
                "seconds": round(time.time() - t0, 1),
            }
            result.history.append(stat)
            logger.info("[cegis][round %d] survivors=%d refuted(pool=%d,search=%d) "
                        "+%d witnesses → seed=%d  (%.1fs)",
                        rnd, len(survivors), refuted_pool, refuted_search,
                        len(added), len(self.seed.graphs), stat["seconds"])

            # This round is healthy → it becomes the best result so far.
            best_survivors, best_g3 = survivors, g3
            prev_cands = len(cands)

            result.rounds_run = rnd
            if (refuted_pool + refuted_search) == 0:
                result.fixed_point = True
                logger.info("[cegis] fixed point reached at round %d", rnd)
                break
            if not added:
                # refuted some, but couldn't recover structures to learn from →
                # regenerating would repeat; stop to avoid an infinite loop.
                logger.info("[cegis] refuted without new witnesses — stopping")
                break

        # One-shot deep extraction on the converged seed (optional, default off):
        # run a single richer generation pass on the hardened seed, refute it,
        # and merge its survivors — DEEP's richness once per shard rather than
        # every round (which is far too slow on a large seed).
        if self.cfg.cegis_final_deep_pass:
            logger.info("[cegis] final deep pass on converged seed (%d graphs), mode=%s",
                        len(self.seed.graphs), self.cfg.cegis_final_deep_mode)
            try:
                cands, g3d = self._generate(mode=self.cfg.cegis_final_deep_mode,
                                            complexity=self.cfg.cegis_final_deep_complexity)
                dsurv, dwit, rp, rs = self._refute_and_search(cands, all_cols, do_search)
                added = self.seed.add(dwit) if dwit else []
                if added:
                    self.seed.persist_witnesses(added)
                logger.info("[cegis] final deep pass: %d candidates → %d survivors "
                            "(refuted pool=%d search=%d)", len(cands), len(dsurv), rp, rs)
                seen, merged = set(), []
                for c in list(best_survivors) + list(dsurv):
                    try:
                        key = c.pretty()
                    except Exception:
                        key = repr(c)
                    if key not in seen:
                        seen.add(key); merged.append(c)
                best_survivors, best_g3 = merged, (g3d or best_g3)
            except Exception as e:
                logger.warning("[cegis] final deep pass failed (%s) — keeping loop survivors", e)

        result.survivors = best_survivors
        result.g3 = best_g3
        result.touches = [self.refuter.touch_count(c, self.seed.frame) for c in best_survivors]
        return result
