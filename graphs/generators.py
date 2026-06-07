"""
graphs/generators.py — factory functions for standard and random graph families.

All functions return nx.Graph instances.
"""

from __future__ import annotations

import random
from typing import List, Tuple

import networkx as nx


# ---------------------------------------------------------------------------
# Named / classical graphs
# ---------------------------------------------------------------------------

def named_graphs() -> List[Tuple[str, nx.Graph]]:
    """Return (name, graph) pairs for a curated set of named graphs."""
    pairs: List[Tuple[str, nx.Graph]] = []

    # Complete graphs
    for k in range(1, 8):
        pairs.append((f"K{k}", nx.complete_graph(k)))

    # Paths
    for k in range(2, 9):
        pairs.append((f"P{k}", nx.path_graph(k)))

    # Cycles
    for k in range(3, 10):
        pairs.append((f"C{k}", nx.cycle_graph(k)))

    # Complete bipartite
    for a, b in [(1, 3), (2, 2), (2, 3), (2, 4), (3, 3), (3, 4)]:
        pairs.append((f"K{a},{b}", nx.complete_bipartite_graph(a, b)))

    # Wheel graphs (hub + cycle)
    for k in range(4, 8):
        pairs.append((f"W{k}", nx.wheel_graph(k + 1)))

    # Hypercubes
    pairs.append(("Q3", nx.hypercube_graph(3)))

    # Platonic / famous
    pairs.append(("Petersen",     nx.petersen_graph()))
    pairs.append(("Heawood",      nx.heawood_graph()))
    pairs.append(("Pappus",       nx.pappus_graph()))
    pairs.append(("Desargues",    nx.desargues_graph()))
    pairs.append(("Dodecahedron", nx.dodecahedral_graph()))
    pairs.append(("Icosahedron",  nx.icosahedral_graph()))
    pairs.append(("Octahedron",   nx.octahedral_graph()))
    pairs.append(("Cubical",      nx.cubical_graph()))

    # Small named graphs
    pairs.append(("Bull",     _bull()))
    pairs.append(("Cricket",  _cricket()))
    pairs.append(("Diamond",  _diamond()))
    pairs.append(("House",    nx.house_graph()))
    pairs.append(("Butterfly", _butterfly()))
    pairs.append(("Gem",      _gem()))
    pairs.append(("Kite",     _kite()))

    # Trees
    pairs.append(("Star4",   nx.star_graph(4)))
    pairs.append(("Star6",   nx.star_graph(6)))
    pairs.append(("Caterpillar6", _caterpillar(6)))

    return pairs


# ---------------------------------------------------------------------------
# Small named constructions
# ---------------------------------------------------------------------------

def _bull() -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 4)])
    return G


def _cricket() -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (3, 4)])
    return G


def _diamond() -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (0, 3), (0, 2)])
    return G


def _butterfly() -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)])
    return G


def _gem() -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4),
                      (0, 2), (0, 3), (0, 4)])
    return G


def _kite() -> nx.Graph:
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (3, 4)])
    return G


def _caterpillar(n: int) -> nx.Graph:
    G = nx.path_graph(n)
    for i in range(1, n - 1):
        leaf = n + i - 1
        G.add_edge(i, leaf)
    return G


# ---------------------------------------------------------------------------
# Random graph families
# ---------------------------------------------------------------------------

def random_connected_er(n: int, p: float, seed: int) -> nx.Graph:
    """Erdős–Rényi G(n, p) conditioned on connectivity (retry until connected)."""
    rng = random.Random(seed)
    for _ in range(200):
        G = nx.erdos_renyi_graph(n, p, seed=rng.randint(0, 2**31))
        if nx.is_connected(G):
            return G
    # Fallback: spanning tree + ER edges
    G = nx.erdos_renyi_graph(n, p, seed=seed)
    T = nx.minimum_spanning_tree(G if G.number_of_edges() > 0 else nx.path_graph(n))
    G2 = nx.erdos_renyi_graph(n, p, seed=seed + 1)
    G2.add_edges_from(T.edges())
    return G2


def random_regular(n: int, d: int, seed: int) -> nx.Graph:
    """Random d-regular graph on n vertices (n·d must be even)."""
    try:
        return nx.random_regular_graph(d, n, seed=seed)
    except Exception:
        return nx.cycle_graph(n)  # fallback


def random_tree(n: int, seed: int) -> nx.Graph:
    return nx.random_labeled_tree(n, seed=seed)


def random_bipartite(n1: int, n2: int, p: float, seed: int) -> nx.Graph:
    return nx.bipartite.random_graph(n1, n2, p, seed=seed)


def generate_random_batch(
    count: int,
    min_n: int = 5,
    max_n: int = 12,
    seed: int = 42,
) -> List[Tuple[str, nx.Graph]]:
    """Generate a mixed batch of random connected graphs."""
    rng = random.Random(seed)
    batch = []
    for i in range(count):
        n = rng.randint(min_n, max_n)
        kind = rng.choice(["er", "regular", "tree", "bipartite"])
        s = rng.randint(0, 2**31)
        try:
            if kind == "er":
                p = rng.uniform(0.25, 0.75)
                G = random_connected_er(n, p, s)
                name = f"ER({n},{p:.2f})_{i}"
            elif kind == "regular":
                d = rng.choice([2, 3] if n >= 4 else [2])
                G = random_regular(n, d, s)
                name = f"Reg({n},{d})_{i}"
            elif kind == "tree":
                G = random_tree(n, s)
                name = f"Tree({n})_{i}"
            else:
                n2 = rng.randint(2, max(3, n - 2))
                p = rng.uniform(0.3, 0.8)
                G = random_bipartite(n, n2, p, s)
                name = f"Bip({n},{n2})_{i}"
            batch.append((name, G))
        except Exception:
            batch.append((f"fallback_{i}", nx.cycle_graph(n)))
    return batch
