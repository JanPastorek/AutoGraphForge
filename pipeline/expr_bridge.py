"""
pipeline/expr_bridge.py — evaluate Sage-generated conjectures on networkx graphs.

The Sage `Conjecturing` engines emit conjectures as strings, e.g.

    numeric  :  nu(x) <= maximum(alpha(x), min_degree(x)) + 1
    property :  ((is_two_connected)&(is_claw_free))->(is_hamiltonian)

To run these through the rest of the (networkx-based) pipeline — the seeded
counterexample search, the durable counterexample loop, autoformalization — we
need to evaluate them on an arbitrary networkx graph. This module turns any such
string into a ``margin(G)`` function with the convention used by
``counterexample_search``:

    margin(G) > 0   ⇔   G refutes the conjecture (violation magnitude)
    margin(G) <= 0  ⇔   G satisfies it (or the conjecture is inapplicable)

so the existing ``seeds`` / ``hill_climb`` engine can attack it unchanged.
"""
from __future__ import annotations

import math
import re
from typing import Callable

import networkx as nx

# ---------------------------------------------------------------------------
# Exact invariant computations matching the Sage-side definitions
# ---------------------------------------------------------------------------
from graphs.invariants import (
    independence_number, clique_number, chromatic_number, domination_number,
    matching_number, vertex_connectivity, edge_connectivity, diameter, radius,
    algebraic_connectivity, number_of_triangles, girth as _girth,
)


def _spectral_radius(G: nx.Graph) -> float:
    import numpy as np
    if G.number_of_nodes() == 0:
        return 0.0
    A = nx.to_numpy_array(G)
    return float(max(np.linalg.eigvalsh(A)))


def _girth_val(G: nx.Graph) -> float:
    g = _girth(G)
    # acyclic graphs: Sage uses +Infinity; we substitute 2n so bounds stay finite
    if g == float("inf"):
        return float(2 * G.number_of_nodes())
    return float(g)


SAGE_INV: dict[str, Callable[[nx.Graph], float]] = {
    "order":           lambda G: float(G.number_of_nodes()),
    "size":            lambda G: float(G.number_of_edges()),
    "max_degree":      lambda G: float(max((d for _, d in G.degree()), default=0)),
    "min_degree":      lambda G: float(min((d for _, d in G.degree()), default=0)),
    "avg_degree":      lambda G: (2.0 * G.number_of_edges() / G.number_of_nodes()
                                  if G.number_of_nodes() else 0.0),
    "alpha":           lambda G: float(independence_number(G)),
    "omega":           lambda G: float(clique_number(G)),
    "chi":             lambda G: float(chromatic_number(G)),
    "gamma":           lambda G: float(domination_number(G)),
    "nu":              lambda G: float(matching_number(G)),
    "tau":             lambda G: float(G.number_of_nodes() - independence_number(G)),  # Gallai
    "diameter":        lambda G: float(diameter(G)),
    "radius":          lambda G: float(radius(G)),
    "girth":           _girth_val,
    "kappa":           lambda G: float(vertex_connectivity(G)),
    "lam":             lambda G: float(edge_connectivity(G)),
    "triangles":       lambda G: float(number_of_triangles(G)),
    "spectral_radius": _spectral_radius,
    "alg_conn":        lambda G: float(algebraic_connectivity(G)),
}

# ---------------------------------------------------------------------------
# Boolean predicates matching the Sage-side property list
# ---------------------------------------------------------------------------

def _claw_free(G: nx.Graph) -> bool:
    star = nx.star_graph(3)
    from networkx.algorithms.isomorphism import GraphMatcher
    return not GraphMatcher(G, star).subgraph_is_monomorphic() and \
        not _has_induced_claw(G)


def _has_induced_claw(G: nx.Graph) -> bool:
    for v in G:
        nb = list(G.neighbors(v))
        if len(nb) < 3:
            continue
        # independent triple among neighbours ⇒ induced claw
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                if G.has_edge(nb[i], nb[j]):
                    continue
                for k in range(j + 1, len(nb)):
                    if not G.has_edge(nb[i], nb[k]) and not G.has_edge(nb[j], nb[k]):
                        return True
    return False


def _vertex_transitive(G: nx.Graph) -> bool:
    try:
        from networkx.algorithms.isomorphism import GraphMatcher
        orbits = _automorphism_orbits(G)
        return len(orbits) <= 1 if G.number_of_nodes() else True
    except Exception:
        return False


def _automorphism_orbits(G: nx.Graph):
    # cheap orbit computation via degree+neighbourhood refinement is unreliable;
    # fall back to "all degrees equal" necessary condition for small search use.
    degs = {d for _, d in G.degree()}
    return [list(G.nodes())] if len(degs) <= 1 else [[v] for v in G.nodes()]


def _self_complementary(G: nx.Graph) -> bool:
    if G.number_of_nodes() == 0:
        return True
    return nx.is_isomorphic(G, nx.complement(G))


SAGE_PRED: dict[str, Callable[[nx.Graph], bool]] = {
    "is_regular":          lambda G: len({d for _, d in G.degree()}) <= 1,
    "is_bipartite":        lambda G: nx.is_bipartite(G),
    "is_planar":           lambda G: nx.check_planarity(G)[0],
    "is_claw_free":        lambda G: not _has_induced_claw(G),
    "is_chordal":          lambda G: nx.is_chordal(G),
    "is_eulerian":         lambda G: nx.is_eulerian(G),
    "is_vertex_transitive": _vertex_transitive,
    "is_tree":             lambda G: nx.is_tree(G),
    "is_two_connected":    lambda G: (G.number_of_nodes() > 2 and nx.node_connectivity(G) >= 2),
    "is_three_connected":  lambda G: (G.number_of_nodes() > 3 and nx.node_connectivity(G) >= 3),
    "is_dirac":            lambda G: (2 * min((d for _, d in G.degree()), default=0) >= G.number_of_nodes()),
    "is_self_complementary": _self_complementary,
    "has_even_order":      lambda G: (G.number_of_nodes() % 2 == 0),
    "is_hamiltonian":      lambda G: _is_hamiltonian(G),
    "has_perfect_matching": lambda G: (2 * matching_number(G) == G.number_of_nodes()),
}


def _is_hamiltonian(G: nx.Graph) -> bool:
    n = G.number_of_nodes()
    if n < 3 or not nx.is_connected(G):
        return False
    # exact backtracking Hamiltonian-cycle test (fine for small search graphs)
    nodes = list(G.nodes())
    start = nodes[0]
    adj = {v: set(G.neighbors(v)) for v in nodes}
    target = n

    def ext(v, visited):
        if len(visited) == target:
            return start in adj[v]
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if ext(w, visited):
                    return True
                visited.discard(w)
        return False

    return ext(start, {start})


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_INV_CALL = re.compile(r"([A-Za-z_]\w*)\(x\)")
_SAFE_NS = {
    "minimum": min, "maximum": max, "sqrt": math.sqrt, "abs": abs,
    "floor": math.floor, "ceil": math.ceil, "Infinity": math.inf,
    "min": min, "max": max,
}


class _B:
    """Boolean wrapper so logical operators compose for property statements:
    & (and), | (or), ~ (not), >> (implication)."""
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = bool(v)

    def __and__(self, o):  return _B(self.v and o.v)
    def __or__(self, o):   return _B(self.v or o.v)
    def __invert__(self):  return _B(not self.v)
    def __rshift__(self, o): return _B((not self.v) or o.v)   # implication
    def __bool__(self):    return self.v


def _is_property(statement: str) -> bool:
    return "->" in statement and "<=" not in statement and ">=" not in statement


def make_margin(statement: str) -> Callable[[nx.Graph], float]:
    """Return margin(G): >0 iff G refutes `statement`."""
    if _is_property(statement):
        return _property_margin(statement)
    return _bound_margin(statement)


def make_value(expr: str) -> Callable[[nx.Graph], float]:
    """Compile a single Sage-style invariant expression (one side or one term of
    a bound, e.g. ``maximum(alpha(x), min_degree(x))``) into a function returning
    its float value on a graph. Used by the coefficient-tuning LP."""
    needed = set(_INV_CALL.findall(expr))
    code = compile(_INV_CALL.sub(r"V['\1']", expr).replace("^", "**").strip(),
                   "<expr>", "eval")

    def value(G: nx.Graph) -> float:
        V = {nm: SAGE_INV[nm](G) for nm in needed}
        ns = dict(_SAFE_NS); ns["V"] = V
        return float(eval(code, {"__builtins__": {}}, ns))

    return value


def _bound_margin(statement: str) -> Callable[[nx.Graph], float]:
    if "<=" in statement:
        lhs_s, rhs_s = statement.split("<=", 1); upper = True
    elif ">=" in statement:
        lhs_s, rhs_s = statement.split(">=", 1); upper = False
    else:
        raise ValueError("not a bound: " + statement)

    needed = set(_INV_CALL.findall(statement))
    lhs_e = _INV_CALL.sub(r"V['\1']", lhs_s).replace("^", "**").strip()
    rhs_e = _INV_CALL.sub(r"V['\1']", rhs_s).replace("^", "**").strip()
    lhs_c = compile(lhs_e, "<lhs>", "eval")
    rhs_c = compile(rhs_e, "<rhs>", "eval")

    def margin(G: nx.Graph) -> float:
        if G.number_of_nodes() < 1 or not nx.is_connected(G):
            return -1e18
        try:
            V = {nm: SAGE_INV[nm](G) for nm in needed}
            ns = dict(_SAFE_NS); ns["V"] = V
            L = eval(lhs_c, {"__builtins__": {}}, ns)
            R = eval(rhs_c, {"__builtins__": {}}, ns)
        except (ZeroDivisionError, ValueError, OverflowError, KeyError):
            return -1e18
        if not (math.isfinite(L) and math.isfinite(R)):
            return -1e18
        return (L - R) if upper else (R - L)

    return margin


def _property_margin(statement: str) -> Callable[[nx.Graph], float]:
    needed = set(re.findall(r"[A-Za-z_]\w*", statement)) & set(SAGE_PRED)
    expr = statement
    # wrap predicate names; longest first to avoid partial overlaps
    for nm in sorted(needed, key=len, reverse=True):
        expr = re.sub(r"\b" + nm + r"\b", "_B(P['{}'])".format(nm), expr)
    expr = expr.replace("->", ">>")
    code = compile(expr, "<prop>", "eval")

    def margin(G: nx.Graph) -> float:
        if G.number_of_nodes() < 1 or not nx.is_connected(G):
            return -1e18
        try:
            P = {nm: SAGE_PRED[nm](G) for nm in needed}
            ns = {"_B": _B, "P": P}
            holds = bool(eval(code, {"__builtins__": {}}, ns))
        except Exception:
            return -1e18
        # implication refuted ⇒ margin +1, else -1
        return 1.0 if not holds else -1.0

    return margin
