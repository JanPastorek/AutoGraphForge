"""
pipeline/degenerate_graphs.py — the refutation tier the census forgets.

Measured on this repo's caches, only 774 of 279,614 usable pool graphs (0.28%)
are disconnected and 27 are edgeless with at least two vertices: the large tier
comes from a connected census, and the families and random tiers are connected
by construction. A conjecture false only on a disconnected graph, on one with
an isolated vertex, or on an edgeless graph therefore has almost no chance of
being refuted — it survives for want of a witness rather than because it is
true. Re-refuting the 6,637 survivors against the graphs built here killed 115
of them.

These are cheap (small orders) and are exactly the shapes that break lower
bounds such as ``2 <= total_domination_number`` or ``2 <= chromatic_number``.
"""
from __future__ import annotations

import itertools

import networkx as nx

from pipeline.seed_corpus import graph6_id


def degenerate_graphs(max_n: int = 10) -> list:
    """Disconnected / isolate-bearing / edgeless graphs up to ``max_n`` vertices."""
    out: list = []

    # edgeless graphs — the extreme case: chromatic number 1, no domination
    for n in range(2, max_n + 1):
        out.append(nx.empty_graph(n))

    # connected building blocks, then every disjoint union that fits
    blocks = []
    for n in range(1, max_n):
        blocks += [nx.path_graph(n), nx.complete_graph(n)]
        if n >= 3:
            blocks += [nx.cycle_graph(n), nx.star_graph(n - 1)]
    blocks = [b for b in blocks if 1 <= b.number_of_nodes() <= max_n]

    for a, b in itertools.combinations_with_replacement(range(len(blocks)), 2):
        g = nx.disjoint_union(blocks[a], blocks[b])
        if 2 <= g.number_of_nodes() <= max_n:
            out.append(g)

    # three components, and a connected graph carrying isolated vertices
    for a, b, c in itertools.combinations_with_replacement(range(len(blocks)), 3):
        g = nx.disjoint_union(nx.disjoint_union(blocks[a], blocks[b]), blocks[c])
        if 3 <= g.number_of_nodes() <= max_n:
            out.append(g)
    for n in range(2, max_n):
        for isolates in range(1, min(3, max_n - n) + 1):
            g = nx.disjoint_union(nx.path_graph(n), nx.empty_graph(isolates))
            if g.number_of_nodes() <= max_n:
                out.append(g)

    seen, uniq = set(), []
    for g in out:
        if g.number_of_nodes() < 2:
            continue
        gid = graph6_id(g)
        if gid not in seen:
            seen.add(gid)
            uniq.append(g)
    return uniq
