"""
pipeline/search/problem.py — the shared objective for active counterexample search.

Every searcher (SA, rlgt deep-CE/REINFORCE, …) optimises the same scalar:

    violation(G) = -slack(G)        (slack = rhs - lhs, graffiti3's convention)

so violation > 0 ⇔ G is a counterexample. The objective respects the
conjecture's hypothesis: a graph outside the class scores ``-inf`` (the searchers
should start in-class anyway). Only the invariants the conjecture *references* are
computed per candidate graph (≈25× cheaper than the full battery), with a
full-battery fallback, and memoised by graph6.
"""
from __future__ import annotations

import logging
import math
import re
import signal
from typing import Dict, List, Optional, Set

import networkx as nx
import pandas as pd

from graphcalc.graphs import compute_knowledge_table, all_properties

from pipeline.seed_corpus import graph6_id

logger = logging.getLogger(__name__)

_NEG_INF = float("-inf")


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):            # pragma: no cover
    raise _Timeout()


def per_order_trials(base: int, n: int, *, ref: int = 6, floor: int = 30) -> int:
    """Order-adaptive trial budget: trials shrink ∝ ref/n, so big (expensive)
    graphs get proportionally fewer trials than small ones."""
    return max(floor, int(base * ref / max(n, 1)))


def _tokens(text: str) -> Set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text or ""))


class GraphSearchProblem:
    """Black-box objective wrapping one graffiti3 native conjecture."""

    def __init__(self, native, all_cols: List[str],
                 hypothesis_class: Optional[str] = None, eval_cap_s: int = 3):
        self.native = native
        self.hypothesis_class = hypothesis_class
        self.eval_cap_s = int(eval_cap_s)
        # referenced columns = battery names appearing in the (relation+condition) text
        text = ""
        for attr in ("pretty",):
            try:
                text += " " + native.pretty()
            except Exception:
                pass
        text += " " + repr(native)
        toks = _tokens(text)
        self.cols: List[str] = [c for c in all_cols if c in toks] or list(all_cols)
        self._cache: Dict[str, float] = {}
        self.best_violation = _NEG_INF
        self.best_graph: Optional[nx.Graph] = None

    # ------------------------------------------------------------ objective --
    def _row(self, G: nx.Graph) -> Optional[dict]:
        have_alarm = hasattr(signal, "SIGALRM")
        if have_alarm:
            old = signal.signal(signal.SIGALRM, _on_alarm)
            signal.alarm(self.eval_cap_s)
        try:
            return compute_knowledge_table(self.cols, [G]).iloc[0].to_dict()
        except _Timeout:
            return None                       # big-graph ILP too slow → skip
        except Exception:
            try:
                return all_properties([G]).iloc[0].to_dict()
            except Exception:
                return None
        finally:
            if have_alarm:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old)

    def violation(self, G: nx.Graph) -> float:
        if G is None or G.number_of_nodes() < 2:
            return _NEG_INF
        gid = graph6_id(G)
        if gid in self._cache:
            return self._cache[gid]
        row = self._row(G)
        if row is None:
            self._cache[gid] = _NEG_INF
            return _NEG_INF
        frame = pd.DataFrame([row])
        try:
            applicable, _holds, failures = self.native.check(frame)
            if not bool(pd.Series(applicable).iloc[0]):
                v = _NEG_INF                       # outside hypothesis class
            else:
                s = self.native.relation.slack(frame)
                v = -float(pd.Series(s).iloc[0])
        except Exception:
            v = _NEG_INF
        if math.isfinite(v) and v > self.best_violation:
            self.best_violation, self.best_graph = v, G.copy()
        self._cache[gid] = v
        return v

    def is_counterexample(self, G: nx.Graph, tol: float = 1e-9) -> bool:
        return self.violation(G) > tol

    # --------------------------------------------------------------- moves --
    def random_start(self, n: int, rng) -> nx.Graph:
        """A random connected graph of order n in the hypothesis class (best effort)."""
        from pipeline.random_models import sample_graphs
        cls = self.hypothesis_class
        try:
            gs = sample_graphs(cls, orders=(n,), per=1, seed=int(rng.integers(1 << 30)))
            if gs:
                return gs[0]
        except Exception:
            pass
        p = float(rng.uniform(0.3, 0.6))
        G = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
        if not nx.is_connected(G) and n > 1:
            G = nx.connected_watts_strogatz_graph(n, min(4, n - 1), 0.3)
        return G

    @staticmethod
    def neighbors(G: nx.Graph, rng, k: int = 1) -> nx.Graph:
        """A k-edge-flip neighbour (toggle k random pairs), kept simple/undirected."""
        H = G.copy()
        nodes = list(H.nodes())
        for _ in range(k):
            u, v = rng.choice(nodes, size=2, replace=False)
            u, v = int(u), int(v)
            if H.has_edge(u, v):
                H.remove_edge(u, v)
            else:
                H.add_edge(u, v)
        return H
