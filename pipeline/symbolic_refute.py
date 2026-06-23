"""
pipeline/symbolic_refute.py — constructive refutation of constant / degree bounds.

The active searchers sweep bounded graph orders, so a survivor like ``order ≤ 14``
or ``maximum_degree ≤ 3`` — false for *any* large enough graph — can slip through
and look "theorem-grade". This tier refutes such bounds **by construction**,
independent of the seed/pool size: it builds extremal graphs over a wide order
ladder (a handful of empty / complete / star / path / cycle / bipartite /
two-clique structures per order) and returns the first one that violates the
conjecture while satisfying its hypothesis.

It only engages when every invariant the conjecture references is **cheap**
(computable in O(n+m) at large n) — so it never tries to evaluate an NP-hard
invariant on a 1000-vertex graph. Conjectures touching expensive invariants are
left to the active searchers. Returning the *smallest* witness keeps the seed
battery cheap, since the ladder is ascending.
"""
from __future__ import annotations

import re
from typing import List, Optional, Set

import networkx as nx
import pandas as pd

from graphcalc.graphs import compute_knowledge_table

# Invariants computable in ~O(n+m) — safe to evaluate on large extremal graphs.
# Deliberately conservative: excludes distance (diameter/radius/aspl), subgraph
# (triangle_free, chordal, claw_free, …), spectral, and all NP-hard invariants.
CHEAP_COLS: Set[str] = {
    "order", "size", "average_degree", "maximum_degree", "minimum_degree",
    "connected", "bipartite", "regular", "cubic", "subcubic", "tree",
    "eulerian", "nontrivial",
}

# Ascending order ladder: small orders refute constant *lower* bounds
# (`5 ≤ order`), large orders refute constant *upper* bounds (`order ≤ 14`,
# `maximum_degree ≤ 3`). First hit wins, so witnesses come out as small as possible.
_ORDERS = (2, 3, 4, 6, 9, 15, 40, 120, 400, 1200)


def _tokens(text: str) -> Set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text or ""))


def referenced_columns(native, all_cols: List[str]) -> Set[str]:
    text = ""
    try:
        text += " " + native.pretty()
    except Exception:
        pass
    text += " " + repr(native)
    toks = _tokens(text)
    return {c for c in all_cols if c in toks}


def is_cheap(native, all_cols: List[str]) -> bool:
    refs = referenced_columns(native, all_cols)
    return bool(refs) and refs <= CHEAP_COLS


def _extremal_graphs(n: int) -> List[nx.Graph]:
    """A small spread of order-n structures hitting the extremes of each cheap
    invariant (size, degrees, regularity, connectivity, class membership)."""
    gs: List[nx.Graph] = []
    gs.append(nx.empty_graph(n))                       # size 0, Δ 0, 0-regular, disconnected
    gs.append(nx.complete_graph(n))                    # max size, Δ=δ=n-1, regular, connected
    if n >= 2:
        gs.append(nx.star_graph(n - 1))                # Δ=n-1, δ=1, tree, bipartite
        gs.append(nx.path_graph(n))                    # Δ≤2, tree, bipartite
    if n >= 3:
        gs.append(nx.cycle_graph(n))                   # 2-regular, connected, eulerian
        a = n // 2
        gs.append(nx.complete_bipartite_graph(a, n - a))   # dense bipartite
    if n >= 4 and n % 2 == 0:                          # two disjoint cliques: regular, disconnected
        h = nx.disjoint_union(nx.complete_graph(n // 2), nx.complete_graph(n // 2))
        gs.append(h)
    # normalise to integer-labelled simple graphs
    return [nx.convert_node_labels_to_integers(g) for g in gs]


def _violates(native, G: nx.Graph, cols: List[str]) -> bool:
    """True iff G is in the conjecture's hypothesis class and breaks the bound."""
    try:
        frame = compute_knowledge_table(cols, [G])
        applicable, holds, _failures = native.check(frame)
        ap = bool(pd.Series(applicable).iloc[0])
        ho = bool(pd.Series(holds).iloc[0])
        return ap and not ho
    except Exception:
        return False


def symbolic_refute(native, all_cols: List[str],
                    orders=_ORDERS) -> Optional[nx.Graph]:
    """Return the smallest extremal witness refuting ``native``, or None.

    None means "not applicable" (the conjecture references an expensive invariant)
    or "no extremal witness found" — in both cases the caller falls back to the
    pool tiers + active search."""
    refs = referenced_columns(native, all_cols)
    if not refs or not (refs <= CHEAP_COLS):
        return None
    cols = sorted(refs)
    for n in orders:
        for G in _extremal_graphs(n):
            if G.number_of_nodes() >= 2 and _violates(native, G, cols):
                return G
    return None
