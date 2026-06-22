"""
pipeline/search/metaheuristics.py — VNS, MCTS, CrossEntropy counterexample search.

All three are black-box graph-construction searchers over the shared objective
``GraphSearchProblem.violation`` (= -slack; >0 ⇒ counterexample), so — unlike the
SMT/Z3 falsifier — they work for the *entire* graphcalc battery, not a hardcoded
invariant set. Trial budgets are order-adaptive (``per_order_trials``): orders are
swept small→large and the per-order budget shrinks ∝ ref/n, so expensive big
graphs get fewer trials. Each returns the first counterexample graph, or None.
"""
from __future__ import annotations

import math
from typing import Optional

import networkx as nx
import numpy as np

from pipeline.search.problem import GraphSearchProblem, per_order_trials

_HIT = 1e-9


# --------------------------------------------------------------------------- #
# Variable Neighborhood Search
# --------------------------------------------------------------------------- #
def _local_ascent(problem, G, rng, budget):
    v = problem.violation(G)
    for _ in range(budget):
        H = problem.neighbors(G, rng, k=1)
        vh = problem.violation(H)
        if vh > _HIT:
            return H, vh
        if vh > v:
            G, v = H, vh
        else:
            break
    return G, v


def vns(problem: GraphSearchProblem, *, orders, k_max: int, iterations: int,
        seed: int = 0, ref: int = 6, floor: int = 30) -> Optional[nx.Graph]:
    rng = np.random.default_rng(seed)
    for n in orders:
        budget = per_order_trials(iterations, n, ref=ref, floor=floor)
        G = problem.random_start(n, rng)
        best = problem.violation(G)
        if best > _HIT:
            return G
        it = 0
        while it < budget:
            k = 1
            while k <= k_max and it < budget:
                H = problem.neighbors(G, rng, k=k)               # shake
                H, vh = _local_ascent(problem, H, rng, budget=6)
                it += 7
                if vh > _HIT:
                    return H
                if math.isfinite(vh) and vh > best:
                    G, best, k = H, vh, 1                         # reset neighborhoods
                else:
                    k += 1
    return None


# --------------------------------------------------------------------------- #
# Monte-Carlo Tree Search (UCT over edge-toggle actions, fixed order)
# --------------------------------------------------------------------------- #
class _Node:
    __slots__ = ("G", "parent", "children", "visits", "total", "untried")

    def __init__(self, G, parent, actions):
        self.G = G
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.total = 0.0
        self.untried = list(actions)


def mcts(problem: GraphSearchProblem, *, orders, iterations: int, c: float = 1.41,
         rollout_depth: int = 6, seed: int = 0, ref: int = 6, floor: int = 30
         ) -> Optional[nx.Graph]:
    rng = np.random.default_rng(seed)
    for n in orders:
        budget = per_order_trials(iterations, n, ref=ref, floor=floor)
        actions = [(i, j) for i in range(n) for j in range(i + 1, n)]
        root = _Node(problem.random_start(n, rng), None, actions)
        if problem.violation(root.G) > _HIT:
            return root.G
        for _ in range(budget):
            node = root
            while not node.untried and node.children:            # select (UCT)
                node = max(node.children.values(),
                           key=lambda ch: (ch.total / max(ch.visits, 1))
                           + c * math.sqrt(math.log(node.visits + 1) / max(ch.visits, 1)))
            if node.untried:                                     # expand
                a = node.untried.pop(int(rng.integers(len(node.untried))))
                H = node.G.copy()
                u, v = a
                H.remove_edge(u, v) if H.has_edge(u, v) else H.add_edge(u, v)
                node = node.children.setdefault(a, _Node(H, node, actions))
            r = problem.violation(node.G)                        # evaluate
            if r > _HIT:
                return node.G
            G = node.G
            for _ in range(rollout_depth):                       # random rollout
                G = problem.neighbors(G, rng, k=1)
                rr = problem.violation(G)
                if rr > _HIT:
                    return G
                if math.isfinite(rr):
                    r = max(r, rr)
            while node is not None:                              # backprop
                node.visits += 1
                node.total += r if math.isfinite(r) else 0.0
                node = node.parent
    return None


# --------------------------------------------------------------------------- #
# Cross-Entropy (linear edge-probability model — Wagner without the deep net)
# --------------------------------------------------------------------------- #
def cross_entropy(problem: GraphSearchProblem, *, orders, population: int,
                  elite_frac: float, iterations: int, seed: int = 0,
                  ref: int = 6, floor: int = 20) -> Optional[nx.Graph]:
    rng = np.random.default_rng(seed)
    for n in orders:
        iters = per_order_trials(iterations, n, ref=ref, floor=floor)
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        p = np.full(len(pairs), 0.5)
        n_elite = max(1, int(population * elite_frac))
        for _ in range(iters):
            samples, scores = [], []
            for _s in range(population):
                bits = rng.random(len(pairs)) < p
                G = nx.Graph()
                G.add_nodes_from(range(n))
                G.add_edges_from(pairs[k] for k in range(len(pairs)) if bits[k])
                v = problem.violation(G)
                if v > _HIT:
                    return G
                samples.append(bits)
                scores.append(v if math.isfinite(v) else -1e9)
            top = np.argsort(scores)[::-1][:n_elite]
            elite = np.array([samples[i] for i in top], dtype=float)
            p = np.clip(0.7 * elite.mean(axis=0) + 0.3 * p, 0.02, 0.98)
    return None
