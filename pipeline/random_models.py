"""
pipeline/random_models.py — class-aware random graph generators for refutation.

The fixed adversarial pool (barbells, lollipops, spiders, …) targets *specific*
loose bounds. Random models complement it by probing the typical interior of a
graph class across several orders, which often breaks bounds that only the
structured witnesses miss. Generators are class-aware: a conjecture conditioned
on "regular" graphs is tested against random regular graphs, "bipartite" against
random bipartite graphs, and so on, so every sampled graph actually satisfies
the hypothesis and is a valid potential counterexample.
"""
from __future__ import annotations

import random
from typing import List, Optional

import networkx as nx

DEFAULT_ORDERS = (6, 8, 10, 12, 15, 18, 22, 26)


def _connected(G: nx.Graph) -> bool:
    return G.number_of_nodes() > 0 and nx.is_connected(G)


def sample_graphs(hypothesis: Optional[str] = None, *,
                  orders=DEFAULT_ORDERS, per: int = 6,
                  seed: int = 2025) -> List[nx.Graph]:
    """Random connected graphs across several orders, respecting ``hypothesis``.

    ``hypothesis`` is one of our boolean-invariant names (e.g. "regular",
    "bipartite", "tree", "planar", "triangle_free", "cubic") or None for a
    general mix. Returned graphs are connected and satisfy the class.
    """
    rng = random.Random(seed)
    out: List[nx.Graph] = []

    def keep(G):
        if _connected(G):
            out.append(nx.convert_node_labels_to_integers(G))

    for n in orders:
        for _ in range(per):
            s = rng.randint(0, 2**31 - 1)
            h = hypothesis
            if h in ("regular", "cubic"):
                d = 3 if h == "cubic" else rng.choice([2, 3, 4])
                if (n * d) % 2 == 0 and d < n:
                    try:
                        keep(nx.random_regular_graph(d, n, seed=s))
                    except nx.NetworkXError:
                        pass
            elif h in ("bipartite",):
                a = max(1, n // 2)
                keep(nx.bipartite.gnmk_random_graph(a, n - a,
                     rng.randint(n - 1, a * (n - a)), seed=s))
            elif h in ("tree", "acyclic"):
                keep(nx.random_labeled_tree(n, seed=s) if hasattr(nx, "random_labeled_tree")
                     else nx.random_tree(n, seed=s))
            elif h in ("triangle_free",):
                a = rng.randint(1, n - 1)
                keep(nx.bipartite.gnmk_random_graph(a, n - a,
                     rng.randint(n - 1, a * (n - a)), seed=s))
            elif h in ("planar",):
                # random geometric graphs are usually planar-ish; keep only planar
                G = nx.random_geometric_graph(n, radius=rng.uniform(0.3, 0.6), seed=s)
                if _connected(G) and nx.check_planarity(G)[0]:
                    keep(G)
            else:
                # general mix: Erdős–Rényi at a few densities + a random regular
                p = rng.uniform(0.15, 0.7)
                keep(nx.gnp_random_graph(n, p, seed=s))
                d = rng.choice([2, 3, 4])
                if (n * d) % 2 == 0 and d < n:
                    try:
                        keep(nx.random_regular_graph(d, n, seed=s + 1))
                    except nx.NetworkXError:
                        pass
    return out
