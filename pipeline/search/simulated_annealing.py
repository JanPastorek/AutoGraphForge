"""
pipeline/search/simulated_annealing.py — SA counterexample search.

Metropolis over k-edge-flip neighbours, maximising the conjecture's violation
(= -slack). Returns the first graph with violation > 0 (a counterexample), or
None. Several restarts over several graph orders.
"""
from __future__ import annotations

import logging
import math
import time
from typing import Optional

import networkx as nx
import numpy as np

from pipeline.search.problem import GraphSearchProblem, per_order_trials

logger = logging.getLogger(__name__)


def simulated_annealing(problem: GraphSearchProblem, *, orders, iterations: int,
                        restarts: int, seed: int = 0, ref: int = 6,
                        floor: int = 30, deadline: Optional[float] = None
                        ) -> Optional[nx.Graph]:
    rng = np.random.default_rng(seed)
    for n in orders:
        if deadline and time.time() > deadline:
            return None
        steps = per_order_trials(iterations, n, ref=ref, floor=floor)
        for r in range(restarts):
            G = problem.random_start(n, rng)
            cur = problem.violation(G)
            if cur > 1e-9:
                return G
            T0, Tmin = 1.0, 1e-3
            for it in range(steps):
                if deadline and (it & 7) == 0 and time.time() > deadline:
                    return None
                T = max(Tmin, T0 * (1.0 - it / steps))
                k = 1 if rng.random() < 0.8 else 2
                H = problem.neighbors(G, rng, k=k)
                cand = problem.violation(H)
                if cand > 1e-9:
                    return H
                if not math.isfinite(cand):
                    continue
                d = cand - cur
                if d >= 0 or rng.random() < math.exp(d / T):
                    G, cur = H, cand
    return None
