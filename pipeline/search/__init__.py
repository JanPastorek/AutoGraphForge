"""
pipeline/search — active counterexample search for CEGIS.

All searchers share one objective (``GraphSearchProblem``: maximise the
conjecture's violation = -slack, computed via graphcalc). ``find_counterexample``
runs the configured searchers cheapest-first and returns the first witness graph.

Searchers (config ``cegis_searchers``, tried in the given order):
  z3            exact SMT, encodable linear bounds only (fast, early)
  vns           variable-neighborhood search (black-box, full battery)
  sa            simulated annealing            (black-box)
  cross_entropy linear cross-entropy (Wagner without the net)
  mcts          UCT over edge toggles
  rl            rlgt deep-CE / REINFORCE (torch)
Per-order trial budgets shrink ∝ ref/n (``search_order_ref``), so big graphs get
proportionally fewer trials.
"""
from __future__ import annotations

import logging
from typing import List, Optional

import networkx as nx

from config import Config, CONFIG
from pipeline.search.problem import GraphSearchProblem
from pipeline.search.simulated_annealing import simulated_annealing
from pipeline.search.metaheuristics import vns, mcts, cross_entropy
from pipeline.search.rlgt_adapter import rl_search
from pipeline.search.z3_adapter import z3_search

logger = logging.getLogger(__name__)


def find_counterexample(native, all_cols: List[str], cfg: Config = CONFIG,
                        hypothesis_class: Optional[str] = None,
                        seed: int = 0) -> Optional[nx.Graph]:
    """Run the configured active searchers; return the first counterexample.

    A per-candidate wall-clock budget (``search_time_budget_s``) bounds total
    search time regardless of how expensive the conjecture's invariants are, so
    big graph orders can be probed safely — a slow candidate simply runs out of
    budget rather than stalling the round."""
    import time
    problem = GraphSearchProblem(native, all_cols, hypothesis_class,
                                 eval_cap_s=cfg.search_eval_cap_s)
    orders = tuple(cfg.search_orders)
    ref, floor = cfg.search_order_ref, cfg.search_min_trials
    deadline = time.time() + cfg.search_time_budget_s

    for kind in cfg.cegis_searchers:
        if kind == "rl":
            continue                       # RL is a bounded post-phase (see cegis.py)
        if time.time() > deadline:
            break
        try:
            if kind == "z3":
                g = z3_search(native, all_cols, cfg,
                              verify=problem.is_counterexample)
            elif kind == "vns":
                g = vns(problem, orders=orders, k_max=cfg.vns_k_max,
                        iterations=min(cfg.vns_iterations, 80),
                        seed=seed, ref=ref, floor=floor, deadline=deadline)
            elif kind == "sa":
                g = simulated_annealing(problem, orders=orders,
                                        iterations=cfg.sa_iterations,
                                        restarts=cfg.sa_restarts, seed=seed,
                                        ref=ref, floor=floor, deadline=deadline)
            elif kind == "cross_entropy":
                g = cross_entropy(problem, orders=orders,
                                  population=min(cfg.ce_population, 30),
                                  elite_frac=cfg.ce_elite_frac,
                                  iterations=min(cfg.ce_iterations, 12),
                                  seed=seed, ref=ref, floor=max(6, floor // 2),
                                  deadline=deadline)
            elif kind == "mcts":
                g = mcts(problem, orders=orders,
                         iterations=min(cfg.mcts_iterations, 200), c=cfg.mcts_c,
                         seed=seed, ref=ref, floor=floor, deadline=deadline)
            else:
                continue
        except Exception as e:
            logger.debug("[search] %s failed: %s", kind, e)
            g = None
        if g is not None:
            logger.info("[search] %s found a counterexample (n=%d)",
                        kind, g.number_of_nodes())
            return g

    if problem.best_graph is not None:
        logger.debug("[search] no counterexample; best violation %.4f",
                     problem.best_violation)
    return None
