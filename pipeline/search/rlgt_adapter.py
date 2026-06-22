"""
pipeline/search/rlgt_adapter.py — RL counterexample search via the `rlgt` package.

Wraps rlgt's Deep Cross-Entropy (Wagner) / REINFORCE agents over a
``GlobalFlipEnvironment``: the agent builds a graph of fixed order by flipping
edges, and the **reward is the conjecture's violation** (= -slack, computed with
graphcalc). A reward > 0 ⇒ counterexample. Torch/rlgt are imported lazily and the
whole searcher degrades to ``None`` if unavailable, so the pipeline never hard-
depends on a GPU stack.
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
            env = GlobalFlipEnvironment(graph_invariant=reward, graph_order=int(n))
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
