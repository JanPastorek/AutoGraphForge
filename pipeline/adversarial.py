"""
pipeline/adversarial.py — structure-targeted adversarial counterexample search.

A permanent verification resource: a fixed pool of graphs deliberately built to
break loose bounds (barbells with large δ / tiny λ, cliques with sparse tails,
spiders with large radius / small γ, class generators, …) together with their
*exact* invariant values. A conjecture is refuted the moment any pool graph
violates it — this is what stops database-only artifacts (δ ≤ λ+5, χ ≤ avg_deg+3)
from ever surviving.

Only invariants we can compute exactly and quickly are used, so a refutation is
sound. Conjectures referencing an invariant outside this set are left untested
here (the search-based falsifiers handle them).
"""
from __future__ import annotations

import itertools
import logging
import random
from typing import Dict, List, Optional

import networkx as nx
import numpy as np
from networkx.algorithms.clique import max_weight_clique

import graphs.invariants as I
from config import Config, CONFIG

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exact invariants the adversarial pool can certify against
# ---------------------------------------------------------------------------

def _spectral(G):
    """(spectral_radius λ₁, λ₂, λ_min, μ_max, algebraic connectivity a)."""
    A = nx.to_numpy_array(G)
    ev = np.linalg.eigvalsh(A)               # ascending
    lev = np.linalg.eigvalsh(np.diag(A.sum(1)) - A)
    lam2 = float(ev[-2]) if len(ev) > 1 else float(ev[-1])
    alg = float(lev[1]) if len(lev) > 1 else 0.0
    return float(ev[-1]), lam2, float(ev[0]), float(lev[-1]), alg


def _exact_gamma(G):
    nodes = list(G); n = len(nodes)
    for k in range(1, n + 1):
        for s in itertools.combinations(nodes, k):
            dom = set(s)
            for v in s:
                dom.update(G.neighbors(v))
            if len(dom) == n:
                return k
    return n


def inv_exact(G) -> Dict[str, float]:
    """Exact value of every adversarially-checkable invariant + computed class."""
    n = G.number_of_nodes(); m = G.number_of_edges()
    alpha = max_weight_clique(nx.complement(G), weight=None)[1]
    rho, eig2, eig_min, lap_max, alg = _spectral(G)
    d = {
        "n": float(n), "m": float(m),
        "alpha": float(alpha), "omega": float(max_weight_clique(G, weight=None)[1]),
        "chi": float(I.chromatic_number(G)), "nu": float(I.matching_number(G)),
        "Delta": float(I.max_degree(G)), "delta": float(I.min_degree(G)),
        "kappa": float(I.vertex_connectivity(G)), "lambda": float(I.edge_connectivity(G)),
        "diam": float(I.diameter(G)), "rad": float(I.radius(G)),
        "tri": float(I.number_of_triangles(G)),
        "degeneracy": float(max(nx.core_number(G).values()) if m else 0),
        "avg_deg": float(2 * m / n) if n else 0.0,
        "vertex_cover": float(n - alpha),
        "ind_dom": float(min(len(c) for c in nx.find_cliques(nx.complement(G)))),
        "alg": alg,
        "spectral_radius": rho, "eig2": eig2, "eig_min": eig_min, "lap_max": lap_max,
    }
    if n <= 14:
        d["gamma"] = float(_exact_gamma(G))
    # cheap graph classes — always; pricey ones (Hamiltonicity backtrack,
    # self-complement isomorphism, cograph O(n⁴), well-covered) only on small G.
    for name in _CHEAP_CLASSES:
        try:
            d[name] = 1.0 if I.BOOLEANS[name](G) else 0.0
        except Exception:
            pass
    if n <= 11:
        for name in _PRICEY_CLASSES:
            try:
                d[name] = 1.0 if I.BOOLEANS[name](G) else 0.0
            except Exception:
                pass
    return d


_CHEAP_CLASSES = [c for c in ("bipartite", "planar", "regular", "eulerian",
                              "chordal", "tree", "triangle_free", "cubic",
                              "claw_free", "split", "outerplanar")
                  if c in I.BOOLEANS]
_PRICEY_CLASSES = [c for c in ("cograph", "self_compl", "hamiltonian",
                               "well_covered") if c in I.BOOLEANS]


#: invariants the pool can certify (everything inv_exact may emit)
CHECKABLE = {
    "n", "m", "alpha", "omega", "chi", "nu", "Delta", "delta", "kappa", "lambda",
    "diam", "rad", "tri", "degeneracy", "avg_deg", "vertex_cover", "ind_dom",
    "gamma", "alg", "spectral_radius", "eig2", "eig_min", "lap_max",
} | {k for k, fn in I.BOOLEANS.items() if fn is not I._data_only}


# ---------------------------------------------------------------------------
# Pool of structure-targeted adversarial graphs
# ---------------------------------------------------------------------------

def _generators(rng: random.Random, max_n: int):
    # barbells: large δ, tiny λ  → break δ ≤ λ + c
    for k in range(3, 11):
        for p in range(0, 4):
            yield nx.barbell_graph(k, p)
    # lollipops & clique+tail: high χ/ω, low avg-deg → break χ ≤ avg_deg + c
    for k in range(3, 9):
        for tail in range(1, 12):
            yield nx.lollipop_graph(k, tail)
    # spiders: high radius, low γ → break rad ≤ c·γ
    for legs in range(3, 6):
        for L in range(2, 6):
            G = nx.Graph(); nid = 1
            for _ in range(legs):
                prev = 0
                for _ in range(L):
                    G.add_edge(prev, nid); prev = nid; nid += 1
            yield G
    # complete split graphs
    for a in range(2, 8):
        for b in range(2, 8):
            G = nx.complete_graph(a)
            for v in range(a, a + b):
                for u in rng.sample(range(a), rng.randint(1, a)):
                    G.add_edge(v, u)
            yield G
    # class generators
    for _ in range(200):
        n = rng.randint(6, max_n); dreg = rng.randint(2, min(n - 1, 6))
        if (n * dreg) % 2 == 0:
            try:
                yield nx.random_regular_graph(dreg, n, seed=rng.randint(0, 1 << 30))
            except Exception:
                pass
    for _ in range(200):
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        yield nx.bipartite.random_graph(a, b, rng.uniform(.2, .9), seed=rng.randint(0, 1 << 30))
    for _ in range(200):                       # k-trees (chordal)
        n = rng.randint(6, max_n); k = rng.randint(1, 4)
        G = nx.complete_graph(k + 1); cliques = [tuple(range(k + 1))]
        for v in range(k + 1, n):
            base = rng.choice(cliques); att = rng.sample(base, k)
            for u in att:
                G.add_edge(v, u)
            cliques.append(tuple(att) + (v,))
        yield G
    for _ in range(200):                       # complement of triangle-free → α = 2
        n = rng.randint(6, 14)
        H = nx.gnp_random_graph(n, rng.uniform(.2, .6), seed=rng.randint(0, 1 << 30))
        ch = True
        while ch:
            ch = False
            for a, b, c in itertools.combinations(H.nodes(), 3):
                if H.has_edge(a, b) and H.has_edge(b, c) and H.has_edge(a, c):
                    H.remove_edge(a, b); ch = True; break
        yield nx.complement(H)
    for _ in range(250):
        n = rng.randint(6, max_n)
        yield nx.gnp_random_graph(n, rng.uniform(.1, .8), seed=rng.randint(0, 1 << 30))
    for n in range(3, max_n + 1):
        yield nx.path_graph(n); yield nx.cycle_graph(n)
    for n in range(3, 12):
        yield nx.complete_graph(n); yield nx.wheel_graph(n); yield nx.star_graph(n)


class AdversarialPool:
    """Lazily-built singleton pool of (graph, exact-invariants) pairs."""

    _shared: Optional["AdversarialPool"] = None

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        rng = random.Random(cfg.adversarial_seed)
        self.entries: List[tuple] = []           # (nx.Graph, inv-dict)
        seen = set()
        for G in _generators(rng, cfg.adversarial_max_n):
            if G.number_of_nodes() < 2 or G.number_of_nodes() > cfg.adversarial_max_n:
                continue
            if not nx.is_connected(G):
                continue
            h = nx.weisfeiler_lehman_graph_hash(G)
            if h in seen:
                continue
            seen.add(h)
            self.entries.append((G, inv_exact(G)))
        logger.info("[Adversarial] pool of %d structure-targeted graphs", len(self.entries))

    @classmethod
    def shared(cls, cfg: Config = CONFIG) -> "AdversarialPool":
        if cls._shared is None:
            cls._shared = cls(cfg)
        return cls._shared

    def refute(self, inequality) -> Optional[nx.Graph]:
        """Return a pool graph violating the inequality, or None (incl. when the
        conjecture uses an invariant the pool cannot certify)."""
        if not inequality.referenced_invariants() <= CHECKABLE:
            return None
        for G, vals in self.entries:
            s = inequality.slack(vals)            # None when outside the hypothesis class
            if s is not None and s < -1e-9:
                return G
        return None
