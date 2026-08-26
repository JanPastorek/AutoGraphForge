"""
pipeline/search/rlgt_adapter.py — RL counterexample search via the `rlgt` package.

Wraps rlgt's Deep Cross-Entropy (Wagner) / REINFORCE agents over a
``GlobalFlipEnvironment``: the agent builds a graph of fixed order by flipping
edges, and the **reward is the conjecture's violation** (= -slack, computed with
graphcalc). A reward > 0 ⇒ counterexample. Torch/rlgt are imported lazily and the
whole searcher degrades to ``None`` if unavailable, so the pipeline never hard-
depends on a GPU stack.

The environment is constrained to the conjecture's hypothesis class, in the two
ways rlgt allows:

  * ``initial_graph_generator`` — episodes start from a graph in the class
    rather than from the empty graph, which for a hypothesis satisfied by 0.07%
    of graphs is the difference between starting inside the feasible set and
    starting outside it with no gradient back in.

  * ``action_mask`` — for a class that is an edge-set restriction (bipartite:
    fix a 2-colouring, allow only cross pairs) the mask removes every other
    action. rlgt's agents set masked logits to -inf, so those flips are never
    proposed and every graph the agent can construct is bipartite by
    construction. This is the "boundary" the search never has to cross.

A degree- or subgraph-defined class (cubic, chordal, claw-free) has no static
mask that expresses it — a mask is a statement about single positions, that
constraint is not — so there the class-aware start is all this can do, and the
out-of-class reward floor still applies.
"""
from __future__ import annotations

import logging
from typing import Optional

import networkx as nx
import numpy as np

from pipeline.search.problem import GraphSearchProblem

logger = logging.getLogger(__name__)

_BAD = -1.0e6     # finite stand-in for -inf rewards (out-of-class / uncomputable)


def _rlgt_graph_to_nx(g) -> list:
    """Convert a (possibly batched) rlgt Graph into a list of networkx graphs."""
    A = np.asarray(g.adjacency_matrix_binary)
    if A.ndim == 2:
        A = A[None, ...]
    return [nx.from_numpy_array(a) for a in A]


def _masked_environment(base_cls, problem, n):
    """`base_cls` with the conjecture's class baked into starts and actions."""
    pairs = problem.allowed_pairs(n)
    mask = None
    if pairs:
        # Row-major upper triangle: pair (i, j), i < j, is at index
        # sum_{r<i}(n-1-r) + (j-i-1). Verified against rlgt's own flattening.
        length = n * (n - 1) // 2
        index = {}
        k = 0
        for i in range(n):
            for j in range(i + 1, n):
                index[(i, j)] = k
                k += 1
        allowed = np.zeros(length, dtype=bool)
        for u, v in pairs:
            allowed[index[(min(u, v), max(u, v))]] = True
        # Actions run over 2 * length when `flip_only` is False: `a % length`
        # selects the position and `a // length` decides whether to flip it, so
        # the mask has to be tiled over both halves.
        mask = np.concatenate([allowed, allowed])

    class _ConstrainedEnvironment(base_cls):
        @property
        def action_mask(self):
            return mask

    return _ConstrainedEnvironment


def _initial_graph_generator(problem, n, rng):
    """rlgt `GraphGenerator` drawing episode starts from the hypothesis class.

    Returns None when the class has no reachable member at this order, so the
    caller keeps rlgt's default (empty-graph) start rather than a fabricated one.
    """
    try:
        from rlgt.graphs.graph import Graph
    except Exception:
        return None
    if not problem.constraint:
        return None
    if problem.constraint.start(n, rng) is None:
        return None

    def generate(batch_size: int):
        rows = []
        for _ in range(batch_size):
            G = problem.constraint.start(n, rng)
            A = np.zeros((n, n), dtype=np.uint8)
            if G is not None:
                for u, v in G.edges():
                    A[u, v] = A[v, u] = 1
            rows.append(A)
        return Graph(adjacency_matrix_binary=np.stack(rows),
                     is_directed=False, allow_loops=False)

    return generate


def rl_search(problem: GraphSearchProblem, *, orders, episodes: int,
              candidates: int, agent_kind: str = "deep_cross_entropy",
              seed: int = 0) -> Optional[nx.Graph]:
    try:
        import torch
        import torch.nn as nn
        from rlgt.environments.global_environments import GlobalFlipEnvironment
        from rlgt.agents.deep_cross_entropy_agent import DeepCrossEntropyAgent
        try:
            from rlgt.agents.reinforce_agent import ReinforceAgent
        except Exception:
            ReinforceAgent = None
    except Exception as e:                                   # torch/rlgt absent
        logger.info("[rl] rlgt/torch unavailable (%s) — skipping RL searcher", e)
        return None

    rng = np.random.default_rng(seed)

    def reward(batched_graph) -> np.ndarray:
        out = []
        for G in _rlgt_graph_to_nx(batched_graph):
            v = problem.violation(G)
            out.append(v if np.isfinite(v) else _BAD)
        return np.asarray(out, dtype=np.float32)

    for n in orders:
        try:
            cls = _masked_environment(GlobalFlipEnvironment, problem, int(n))
            kwargs = {}
            gen = _initial_graph_generator(problem, int(n), rng)
            if gen is not None:
                kwargs["initial_graph_generator"] = gen
            env = cls(graph_invariant=reward, graph_order=int(n), **kwargs)
            policy = nn.Sequential(
                nn.Linear(env.state_length, 128), nn.ReLU(),
                nn.Linear(128, env.action_number),
            )
            opt = torch.optim.Adam(policy.parameters(), lr=1e-3)
            if agent_kind == "reinforce" and ReinforceAgent is not None:
                agent = ReinforceAgent(env, policy, opt)
            else:
                agent = DeepCrossEntropyAgent(
                    env, policy, opt,
                    candidates_count=candidates,
                    elite_count=max(5, candidates // 10),
                    survivors_count=max(10, candidates // 4),
                    random_generator=rng,
                )
            agent.reset()
            for _ in range(episodes):
                agent.step()
                if agent.best_score is not None and agent.best_score > 1e-9:
                    bg = agent.best_graph
                    if bg is not None:
                        cands = _rlgt_graph_to_nx(bg)
                        for G in cands:
                            if problem.is_counterexample(G):
                                logger.info("[rl] counterexample at n=%d (score %.3f)",
                                            n, agent.best_score)
                                return G
        except Exception as e:
            logger.debug("[rl] agent failed at n=%d: %s", n, e)
            continue
    return None
