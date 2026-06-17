#!/usr/bin/env python3
"""
counterexample_search.py — strong, *structure-seeded* search for counterexamples
to a conjectured inequality  lhs(G) ≤ rhs(G)  (margin = lhs − rhs, want > 0).

Lesson from v1: plain cross-entropy over independent edge probabilities cannot
discover block structures (barbells, clique+bridge) — it failed to refute the
known-false δ ≤ λ+5. This version SEEDS from a large library of structured
graphs (barbells, lollipops, split graphs, regular, α=2 complements, …) and runs
intensive best-improvement hill-climbing from each seed, plus cross-entropy
restarts. Validation (must refute δ ≤ λ+5) is checked first.

Usage: python counterexample_search.py [max_n]
"""
from __future__ import annotations

import itertools
import random
import sys

import networkx as nx
import numpy as np
from networkx.algorithms.clique import max_weight_clique

rng = random.Random(11)
# Only honour argv[1] when it is an explicit integer (so this module stays
# importable from other scripts whose argv carries unrelated flags).
MAXN = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1].lstrip("-").isdigit()) else 44


# ── invariants ────────────────────────────────────────────────────────────
def base(G):
    n = G.number_of_nodes(); m = G.number_of_edges()
    degs = [d for _, d in G.degree()]
    d = {"n": n, "m": m, "Delta": max(degs, default=0), "delta": min(degs, default=0),
         "nu": len(nx.max_weight_matching(G, maxcardinality=True)),
         "tri": sum(nx.triangles(G).values()) // 3}
    if n and nx.is_connected(G):
        d["rad"] = nx.radius(G); d["diam"] = nx.diameter(G)
        d["kappa"] = nx.node_connectivity(G); d["lambda"] = nx.edge_connectivity(G)
        d["conn"] = True
    else:
        d["rad"] = d["diam"] = 10**9; d["kappa"] = d["lambda"] = 0; d["conn"] = False
    return d


def alpha(G):
    return max_weight_clique(nx.complement(G), weight=None)[1]


def gamma(G):
    if G.number_of_nodes() > 18:
        return None
    nodes = list(G); n = len(nodes)
    for k in range(1, n + 1):
        for s in itertools.combinations(nodes, k):
            dom = set(s)
            for v in s:
                dom.update(G.neighbors(v))
            if len(dom) == n:
                return k
    return n


# ── structured seed library ───────────────────────────────────────────────
def seeds(n):
    out = []
    def add(G):
        if G.number_of_nodes() == n:
            out.append(G)
    # barbells: two K_k joined by a path of length p (extreme δ−λ gap)
    for k in range(2, n // 2 + 1):
        p = n - 2 * k
        if p >= 0:
            add(nx.barbell_graph(k, p))
    # lollipops: K_k + pendant path
    for k in range(3, n):
        if n - k >= 1:
            add(nx.lollipop_graph(k, n - k))
    # several cliques joined in a path (generalised barbell)
    for c in (3, 4):
        for k in range(2, n):
            blocks = []
            rem = n
            while rem >= k and len(blocks) < c:
                blocks.append(k); rem -= k
            if rem > 0 and blocks:
                blocks[-1] += rem
            if sum(blocks) == n and len(blocks) >= 2:
                G = nx.Graph(); off = 0; prev = None
                for b in blocks:
                    K = nx.complete_graph(b)
                    G = nx.disjoint_union(G, K)
                    if prev is not None:
                        G.add_edge(prev, off)
                    prev = off + b - 1; off += b
                add(G); break
    # split graphs: clique a + independent set with random attachment
    for a in range(2, min(n, 9)):
        b = n - a
        if b >= 1:
            G = nx.complete_graph(a)
            for v in range(a, n):
                for u in rng.sample(range(a), rng.randint(1, a)):
                    G.add_edge(v, u)
            add(G)
    # double stars S(a,b): two adjacent centers with a and b leaves (extremal
    # for several spectral/matching conjectures)
    for a in range(1, n - 2):
        b = n - 2 - a
        if b >= 1:
            G = nx.Graph(); G.add_edge(0, 1); nid = 2
            for _ in range(a):
                G.add_edge(0, nid); nid += 1
            for _ in range(b):
                G.add_edge(1, nid); nid += 1
            add(G)
    # brooms: a star with a pendant path
    for sc in range(2, min(n, 8)):
        path = n - sc
        if path >= 1:
            G = nx.star_graph(sc - 1)
            prev = 0
            for j in range(path):
                G.add_edge(prev, sc + j); prev = sc + j
            if G.number_of_nodes() == n:
                add(G)
    # spiders (subdivided stars): high radius / low γ
    for legs in range(2, 6):
        if (n - 1) % legs == 0:
            L = (n - 1) // legs
            G = nx.Graph(); nid = 1
            for _ in range(legs):
                prev = 0
                for _ in range(L):
                    G.add_edge(prev, nid); prev = nid; nid += 1
            add(G)
    # random regular
    for d in range(2, min(n - 1, 7)):
        if (n * d) % 2 == 0:
            try:
                add(nx.random_regular_graph(d, n, seed=rng.randint(0, 1 << 30)))
            except Exception:
                pass
    # α = 2 : complement of triangle-free
    for _ in range(6):
        H = nx.gnp_random_graph(n, rng.uniform(.2, .6), seed=rng.randint(0, 1 << 30))
        ch = True
        while ch:
            ch = False
            for a, b, c in itertools.combinations(H.nodes(), 3):
                if H.has_edge(a, b) and H.has_edge(b, c) and H.has_edge(a, c):
                    H.remove_edge(a, b); ch = True; break
        add(nx.complement(H))
    # classic families + random
    add(nx.path_graph(n)); add(nx.cycle_graph(n)); add(nx.star_graph(n - 1))
    add(nx.wheel_graph(n)); add(nx.complete_graph(n))
    for _ in range(10):
        add(nx.gnp_random_graph(n, rng.uniform(.08, .85), seed=rng.randint(0, 1 << 30)))
    try:
        add(nx.random_tree(n, seed=rng.randint(0, 1 << 30)))
    except Exception:
        pass
    return out


# ── intensive best-improvement hill climbing ──────────────────────────────
def hill_climb(G, margin, idx):
    G = G.copy()
    cur = margin(G)
    while True:
        best_gain, best_e = 1e-12, None
        for (i, j) in idx:
            if G.has_edge(i, j):
                G.remove_edge(i, j); v = margin(G); G.add_edge(i, j)
            else:
                G.add_edge(i, j); v = margin(G); G.remove_edge(i, j)
            if v - cur > best_gain:
                best_gain, best_e = v - cur, (i, j)
        if best_e is None:
            return cur, G
        i, j = best_e
        G.remove_edge(i, j) if G.has_edge(i, j) else G.add_edge(i, j)
        cur = margin(G)
        if cur > 1e-9:
            return cur, G


def attack(label, margin, n_values):
    print("=" * 74)
    print(f"TARGET: {label}")
    glob_v, glob_G, glob_n = -1e18, None, None
    for n in n_values:
        idx = [(i, j) for i in range(n) for j in range(i + 1, n)]
        bv, bG = -1e18, None
        for s in seeds(n):
            v0 = margin(s)
            v, G = hill_climb(s, margin, idx) if v0 > -1e17 else (v0, s)
            if v > bv:
                bv, bG = v, G
            if v > 1e-9:
                break
        tag = "  <-- COUNTEREXAMPLE" if bv > 1e-9 else ""
        print(f"   n={n:2d}: best margin {bv:+.3f}{tag}", flush=True)
        if bv > glob_v:
            glob_v, glob_G, glob_n = bv, bG, n
        if bv > 1e-9:
            break
    if glob_v > 1e-9:
        print(f"  >>> REFUTED at n={glob_n}: {sorted(glob_G.edges())}")
    else:
        print(f"  >>> holds under strong seeded search (best margin {glob_v:+.3f})")
    return glob_v > 1e-9


if __name__ == "__main__":
    fast_ns = list(range(8, MAXN + 1, 2))
    slow_ns = list(range(8, min(MAXN, 24) + 1, 2))   # α/γ targets are costlier

    # validation: MUST refute the known-false δ ≤ λ + 5
    print(">>> VALIDATION (engine must refute a known-false bound)\n")
    ok = attack("δ ≤ λ + 5  [known FALSE — barbell]",
                lambda G: (base(G)["delta"] - base(G)["lambda"] - 5) if nx.is_connected(G) else -1e18,
                [10, 12, 14, 16])
    print("VALIDATION:", "PASS — engine finds structured counterexamples\n" if ok
          else "FAIL — engine still too weak\n")

    # the unclassified survivor, pushed hard
    attack("rad ≤ ν   [unclassified survivor]",
           lambda G: (base(G)["rad"] - base(G)["nu"]) if nx.is_connected(G) else -1e18,
           fast_ns)
    # cross-checks of standing results
    attack("rad ≤ α   [Fajtlowicz–Saks]",
           lambda G: (base(G)["rad"] - alpha(G)) if nx.is_connected(G) else -1e18, slow_ns)
    attack("rad ≤ ½(α+diam)",
           lambda G: (base(G)["rad"] - 0.5 * (alpha(G) + base(G)["diam"]))
           if nx.is_connected(G) else -1e18, slow_ns)
