"""
graphs/invariants.py — graph invariant implementations using networkx.

Every function accepts a networkx.Graph and returns a numeric value (int or
float).  Float('inf') signals "undefined" (e.g., diameter of disconnected G).

INVARIANTS : dict[str, callable]  — numerical invariants
BOOLEANS   : dict[str, callable]  — Boolean properties (return 0 or 1)
"""

from __future__ import annotations

import itertools
import math
from typing import Dict

import networkx as nx


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _backtrack_coloring(G: nx.Graph, k: int) -> bool:
    """Return True iff G is k-colourable (DSatur-style backtracker)."""
    nodes = list(G.nodes())
    color: Dict = {}

    def bt(idx: int) -> bool:
        if idx == len(nodes):
            return True
        v = nodes[idx]
        used = {color[u] for u in G.neighbors(v) if u in color}
        for c in range(k):
            if c not in used:
                color[v] = c
                if bt(idx + 1):
                    return True
                del color[v]
        return False

    return bt(0)


# ---------------------------------------------------------------------------
# Bounded greedy fallbacks (O(n log n + m), never hang) for the NP-hard
# invariants on large graphs, where exact / heuristic library routines either
# blow up exponentially or fail to scale.
# ---------------------------------------------------------------------------

def _greedy_independent_set(G: nx.Graph) -> int:
    """Size of a maximal independent set via static min-degree order.

    Returns a *lower bound* on the independence number α(G); exact for many
    sparse graphs.  Pure O(n log n + m), so it can never hang.
    """
    blocked: set = set()
    size = 0
    for v in sorted(G.nodes(), key=lambda x: G.degree(x)):
        if v not in blocked:
            size += 1
            blocked.add(v)
            blocked.update(G.neighbors(v))
    return size


def _greedy_clique(G: nx.Graph) -> int:
    """Size of a clique grown greedily from each vertex within its own
    neighbourhood.  Returns a *lower bound* on the clique number ω(G).

    Only neighbours of the seed are ever considered, so the cost is
    O(Σ_v deg(v)·ω) — near-linear on sparse graphs and safe on large ones.
    """
    best = 1
    adj = G.adj
    for v in G.nodes():
        if G.degree(v) + 1 <= best:
            continue  # this seed cannot beat the current best
        clique = [v]
        for u in sorted(adj[v], key=lambda x: G.degree(x), reverse=True):
            if all(u in adj[w] for w in clique):
                clique.append(u)
        if len(clique) > best:
            best = len(clique)
    return best


def _greedy_domination(G: nx.Graph) -> int:
    """Greedy minimum dominating set size (an *upper bound* on γ(G)).

    Repeatedly picks the vertex covering the most still-undominated vertices,
    using a lazy ``gain`` heap so the whole routine is near-linear and cannot
    stall on large graphs.
    """
    import heapq

    closed = {v: set(G.neighbors(v)) | {v} for v in G.nodes()}
    undominated = set(G.nodes())
    # max-heap on current gain (negated) with lazy invalidation
    heap = [(-len(closed[v]), v) for v in G.nodes()]
    heapq.heapify(heap)
    chosen = 0
    while undominated:
        neg_gain, v = heapq.heappop(heap)
        gain = len(closed[v] & undominated)
        if gain == 0:
            continue
        if -neg_gain != gain:           # stale entry: re-insert with true gain
            heapq.heappush(heap, (-gain, v))
            continue
        chosen += 1
        undominated -= closed[v]
    return chosen


# ---------------------------------------------------------------------------
# Numerical invariants
# ---------------------------------------------------------------------------

def number_of_vertices(G: nx.Graph) -> int:
    return G.number_of_nodes()


def number_of_edges(G: nx.Graph) -> int:
    return G.number_of_edges()


def max_degree(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return max(d for _, d in G.degree())


def min_degree(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return min(d for _, d in G.degree())


def average_degree(G: nx.Graph) -> float:
    n = G.number_of_nodes()
    if n == 0:
        return 0.0
    return 2.0 * G.number_of_edges() / n


def chromatic_number(G: nx.Graph) -> int:
    """
    Exact chromatic number via iterative k-colouring check.
    Falls back to greedy upper-bound for n > 25 (for speed).
    """
    n = G.number_of_nodes()
    if n == 0:
        return 0
    if G.number_of_edges() == 0:
        return 1
    # Exact, fast short-circuit: a graph with an edge is 2-chromatic iff bipartite
    # (covers trees, forests, even cycles, …). This is exact at any size.
    if nx.is_bipartite(G):
        return 2

    if n > 24:
        # Greedy upper bound only (exact search too slow for large n).
        # NB: compute greedy *directly* — do not call clique_number first, as
        # find_cliques can blow up on large dense graphs.
        c = nx.coloring.greedy_color(G, strategy="largest_first")
        return max(c.values()) + 1

    # Exact: search up from the clique-number lower bound.
    lb = clique_number(G)
    for k in range(lb, n + 1):
        if _backtrack_coloring(G, k):
            return k
    return n


def independence_number(G: nx.Graph) -> int:
    """
    Maximum independent set via complement clique.
    Exact for connected graphs ≤ 25 vertices; approximation otherwise.
    """
    n = G.number_of_nodes()
    if n == 0:
        return 0
    if G.number_of_edges() == 0:
        return n

    if n <= 20:
        # Exact: α(G) = ω(complement); find_cliques is safe at this size.
        comp = nx.complement(G)
        try:
            return max(len(c) for c in nx.find_cliques(comp))
        except Exception:
            pass

    # Large graphs: bounded greedy lower bound.  (networkx's
    # approximation.maximum_independent_set does not scale and can hang on
    # graphs with thousands of vertices.)
    return _greedy_independent_set(G)


def clique_number(G: nx.Graph) -> int:
    """Maximum clique size (Bron–Kerbosch via networkx).

    Exact for graphs up to 64 vertices; for larger graphs a bounded greedy
    lower bound is used, since enumerating all maximal cliques can blow up
    exponentially on large dense graphs.
    """
    n = G.number_of_nodes()
    if n == 0:
        return 0
    if G.number_of_edges() == 0:
        return 1
    if n <= 64:
        try:
            return max(len(c) for c in nx.find_cliques(G))
        except Exception:
            pass
    return _greedy_clique(G)


def domination_number(G: nx.Graph) -> int:
    """
    Minimum dominating set size.
    Exact for n ≤ 20 via brute-force; greedy approximation otherwise.
    """
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        return 0

    if n <= 14:
        for k in range(1, n + 1):
            for subset in itertools.combinations(nodes, k):
                dominated = set(subset)
                for v in subset:
                    dominated.update(G.neighbors(v))
                if len(dominated) == n:
                    return k
        return n

    # Larger graphs: lazy-gain greedy (upper bound on γ), near-linear.
    return _greedy_domination(G)


def matching_number(G: nx.Graph) -> int:
    """Maximum matching cardinality (Blossom algorithm via networkx)."""
    return len(nx.max_weight_matching(G, maxcardinality=True))


def vertex_connectivity(G: nx.Graph) -> int:
    if G.number_of_nodes() <= 1:
        return 0
    try:
        return nx.node_connectivity(G)
    except Exception:
        return 0


def edge_connectivity(G: nx.Graph) -> int:
    if G.number_of_nodes() <= 1:
        return 0
    try:
        return nx.edge_connectivity(G)
    except Exception:
        return 0


def diameter(G: nx.Graph) -> float:
    if not nx.is_connected(G):
        return float("inf")
    try:
        return nx.diameter(G)
    except Exception:
        return float("inf")


def radius(G: nx.Graph) -> float:
    if not nx.is_connected(G):
        return float("inf")
    try:
        return nx.radius(G)
    except Exception:
        return float("inf")


def algebraic_connectivity(G: nx.Graph) -> float:
    """
    Second smallest Laplacian eigenvalue (Fiedler value).

    Uses a direct dense eigensolve (numpy) for graphs up to a few thousand
    vertices: it is both far faster and far more robust than networkx's default
    iterative ``tracemin_pcg`` solver, which can stall for seconds — or fail to
    converge — even on small dense graphs.
    """
    n = G.number_of_nodes()
    if n < 2 or not nx.is_connected(G):
        return 0.0
    if n <= 2000:
        import numpy as np
        L = nx.laplacian_matrix(G).toarray().astype(float)
        eigvals = np.linalg.eigvalsh(L)          # ascending, eigvals[0] ~ 0
        return float(eigvals[1])
    try:
        return float(nx.algebraic_connectivity(G))
    except Exception:
        return 0.0


def clique_cover_number(G: nx.Graph) -> int:
    """Minimum clique cover = χ(complement of G)."""
    return chromatic_number(nx.complement(G))


def number_of_triangles(G: nx.Graph) -> int:
    t = sum(nx.triangles(G).values())
    return t // 3


def girth(G: nx.Graph) -> float:
    """Length of shortest cycle; inf for acyclic graphs."""
    try:
        return nx.girth(G)
    except Exception:
        return float("inf")


# ---------------------------------------------------------------------------
# Boolean properties  (return 0 or 1 for compatibility with invariant math)
# ---------------------------------------------------------------------------

def is_bipartite(G: nx.Graph) -> int:
    return int(nx.is_bipartite(G))


def is_planar(G: nx.Graph) -> int:
    return int(nx.is_planar(G))


def is_regular(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 1
    degrees = {d for _, d in G.degree()}
    return int(len(degrees) == 1)


def is_eulerian(G: nx.Graph) -> int:
    return int(nx.is_eulerian(G))


def is_chordal(G: nx.Graph) -> int:
    return int(nx.is_chordal(G))


def is_tree(G: nx.Graph) -> int:
    return int(nx.is_tree(G))


# ---------------------------------------------------------------------------
# Registries
# ---------------------------------------------------------------------------

#: Numerical invariants used by hypothesis generation and falsification.
INVARIANTS: Dict[str, callable] = {
    "n":       number_of_vertices,
    "m":       number_of_edges,
    "chi":     chromatic_number,      # χ
    "alpha":   independence_number,   # α
    "omega":   clique_number,         # ω
    "gamma":   domination_number,     # γ
    "nu":      matching_number,       # ν  (matching number)
    "Delta":   max_degree,            # Δ
    "delta":   min_degree,            # δ
    "kappa":   vertex_connectivity,   # κ
    "lambda":  edge_connectivity,     # λ
    "diam":    diameter,
    "rad":     radius,
    "alg":     algebraic_connectivity,
    "tri":     number_of_triangles,
}

#: Subset whose values are always finite and fast to compute.
FAST_INVARIANTS: Dict[str, callable] = {
    k: v for k, v in INVARIANTS.items()
    if k in {"n", "m", "Delta", "delta", "nu", "chi", "alpha", "omega", "gamma"}
}

BOOLEANS: Dict[str, callable] = {
    "bipartite": is_bipartite,
    "planar":    is_planar,
    "regular":   is_regular,
    "eulerian":  is_eulerian,
    "chordal":   is_chordal,
    "tree":      is_tree,
}


# ---------------------------------------------------------------------------
# Additional computed graph classes (cheap on small graphs; used as hypotheses)
# ---------------------------------------------------------------------------

def is_triangle_free(G: nx.Graph) -> bool:
    return number_of_triangles(G) == 0


def is_cubic(G: nx.Graph) -> bool:
    return G.number_of_nodes() > 0 and all(d == 3 for _, d in G.degree())


def is_claw_free(G: nx.Graph) -> bool:
    """No induced K_{1,3}: every vertex's neighbourhood has independence ≤ 2."""
    for v in G:
        nbrs = list(G.neighbors(v))
        if len(nbrs) >= 3:
            H = G.subgraph(nbrs)
            # a claw centred at v ⟺ 3 pairwise non-adjacent neighbours
            comp = nx.complement(H)
            try:
                if max((len(c) for c in nx.find_cliques(comp)), default=0) >= 3:
                    return False
            except Exception:
                return False
    return True


def is_cograph(G: nx.Graph) -> bool:
    """P4-free (no induced path on 4 vertices)."""
    nodes = list(G)
    for quad in itertools.combinations(nodes, 4):
        H = G.subgraph(quad)
        degs = sorted(d for _, d in H.degree())
        if degs == [1, 1, 2, 2] and nx.is_connected(H):
            return False   # induced P4
    return True


def is_split(G: nx.Graph) -> bool:
    """Vertices partition into a clique and an independent set (chordal + co-chordal)."""
    try:
        return nx.is_chordal(G) and nx.is_chordal(nx.complement(G))
    except Exception:
        return False


def is_outerplanar(G: nx.Graph) -> bool:
    """G is outerplanar ⟺ G plus a universal vertex is planar."""
    H = G.copy()
    u = ("apex",)
    H.add_node(u)
    H.add_edges_from((u, v) for v in G)
    try:
        return nx.check_planarity(H, counterexample=False)[0]
    except Exception:
        return False


def is_self_complementary(G: nx.Graph) -> bool:
    n = G.number_of_nodes()
    if (n * (n - 1) // 2) % 2 != 0:
        return False               # needs an even number of edge slots
    if G.number_of_edges() != n * (n - 1) // 4:
        return False
    return nx.is_isomorphic(G, nx.complement(G))


def is_hamiltonian(G: nx.Graph) -> bool:
    n = G.number_of_nodes()
    if n < 3 or not nx.is_connected(G):
        return False
    if min((d for _, d in G.degree()), default=0) < 2:
        return False
    nodes = list(G)
    start = nodes[0]
    adj = {v: set(G.neighbors(v)) for v in nodes}
    target = n

    def extend(v, visited):
        if len(visited) == target:
            return start in adj[v]
        for w in adj[v]:
            if w not in visited:
                visited.add(w)
                if extend(w, visited):
                    return True
                visited.discard(w)
        return False

    return extend(start, {start})


def is_well_covered(G: nx.Graph) -> bool:
    """Every maximal independent set has the same size (so γ = i(G) = α).

    Maximal independent sets of G are exactly the maximal cliques of the
    complement, so the class holds iff those all share one size.
    """
    try:
        first = None
        for clique in nx.find_cliques(nx.complement(G)):
            if first is None:
                first = len(clique)
            elif len(clique) != first:
                return False
        return True
    except Exception:
        return False


for _name, _fn in [
    ("triangle_free", is_triangle_free), ("cubic", is_cubic),
    ("claw_free", is_claw_free), ("cograph", is_cograph), ("split", is_split),
    ("outerplanar", is_outerplanar), ("self_compl", is_self_complementary),
    ("hamiltonian", is_hamiltonian), ("well_covered", is_well_covered),
]:
    BOOLEANS.setdefault(_name, _fn)


# ---------------------------------------------------------------------------
# Externally-sourced invariants
# ---------------------------------------------------------------------------
# Values for these are loaded from the House of Graphs export
# (graphs/hog_invariant_values_all.txt via graphs.loaders.load_hog_invariants);
# they are NOT computed on the fly here. They are registered so hypothesis
# generation sweeps them like any other invariant. The placeholder compute
# function returns None, so evaluate_all / falsification simply skip them on
# graphs whose value was not supplied from the database.

def _data_only(_G):  # pragma: no cover - intentionally returns nothing
    return None


#: HoG invariant name → (short key, "num" | "bool").  Keys that coincide with an
#: existing INVARIANT/BOOLEAN reuse that key; the rest are new.
HOG_INVARIANT_MAP: Dict[str, tuple] = {
    # existing numeric
    "Number of Vertices": ("n", "num"),
    "Number of Edges": ("m", "num"),
    "Chromatic Number": ("chi", "num"),
    "Independence Number": ("alpha", "num"),
    "Clique Number": ("omega", "num"),
    "Domination Number": ("gamma", "num"),
    "Matching Number": ("nu", "num"),
    "Maximum Degree": ("Delta", "num"),
    "Minimum Degree": ("delta", "num"),
    "Vertex Connectivity": ("kappa", "num"),
    "Edge Connectivity": ("lambda", "num"),
    "Diameter": ("diam", "num"),
    "Radius": ("rad", "num"),
    "Algebraic Connectivity": ("alg", "num"),
    "Number of Triangles": ("tri", "num"),
    # existing boolean
    "Bipartite": ("bipartite", "bool"),
    "Planar": ("planar", "bool"),
    "Regular": ("regular", "bool"),
    "Eulerian": ("eulerian", "bool"),
    # new numeric
    "Average Degree": ("avg_deg", "num"),
    "Chromatic Index": ("chi_e", "num"),
    "Circumference": ("circumference", "num"),
    "Degeneracy": ("degeneracy", "num"),
    "Density": ("density", "num"),
    "Feedback Vertex Set Number": ("fvs", "num"),
    "Genus": ("genus", "num"),
    "Girth": ("girth", "num"),
    "Group Size": ("aut_group", "num"),
    "Independent Domination Number": ("ind_dom", "num"),
    "Index": ("spectral_radius", "num"),
    "Laplacian Largest Eigenvalue": ("lap_max", "num"),
    "Length of Longest Induced Cycle": ("longest_induced_cycle", "num"),
    "Length of Longest Induced Path": ("longest_induced_path", "num"),
    "Length of Longest Path": ("longest_path", "num"),
    "Number of Arc Orbits": ("arc_orbits", "num"),
    "Number of Components": ("components", "num"),
    "Number of Edge Orbits": ("edge_orbits", "num"),
    "Number of Spanning Trees": ("spanning_trees", "num"),
    "Number of Vertex Orbits": ("vertex_orbits", "num"),
    "Number of Zero Eigenvalues": ("zero_eigenvalues", "num"),
    "Second Largest Eigenvalue": ("eig2", "num"),
    "Smallest Eigenvalue": ("eig_min", "num"),
    "Treewidth": ("treewidth", "num"),
    "Vertex Cover Number": ("vertex_cover", "num"),
    # new boolean
    "Acyclic": ("acyclic", "bool"),
    "Claw-Free": ("claw_free", "bool"),
    "Connected": ("connected", "bool"),
    "Hamiltonian": ("hamiltonian", "bool"),
    "Hypohamiltonian": ("hypohamiltonian", "bool"),
    "Hypotraceable": ("hypotraceable", "bool"),
    "Traceable": ("traceable", "bool"),
    "Twin-Free": ("twin_free", "bool"),
}

# Register the externally-sourced keys so generation treats them as invariants.
for _name, (_key, _kind) in HOG_INVARIANT_MAP.items():
    if _kind == "num":
        INVARIANTS.setdefault(_key, _data_only)
    else:
        BOOLEANS.setdefault(_key, _data_only)


# ---------------------------------------------------------------------------
# Evaluation helper
# ---------------------------------------------------------------------------

def evaluate_all(G: nx.Graph, invariant_set=None) -> Dict[str, float]:
    """
    Evaluate all (or a chosen subset of) invariants on G.
    Skips any that raise or return infinity.
    """
    inv_set = invariant_set or {**INVARIANTS, **BOOLEANS}
    result: Dict[str, float] = {}
    for name, fn in inv_set.items():
        try:
            val = fn(G)
            if val is not None and not (isinstance(val, float) and math.isinf(val)):
                result[name] = float(val)
        except Exception:
            pass
    return result


def evaluate_fast(G: nx.Graph) -> Dict[str, float]:
    """Evaluate only the fast invariant subset."""
    return evaluate_all(G, invariant_set=FAST_INVARIANTS)


#: Combined registry of every numeric invariant and boolean property.
ALL_INVARIANTS: Dict[str, callable] = {**INVARIANTS, **BOOLEANS}


def evaluate_named(G: nx.Graph, names) -> Dict[str, float]:
    """Evaluate exactly the named invariants/booleans on G (skips unknown names)."""
    subset = {k: ALL_INVARIANTS[k] for k in names if k in ALL_INVARIANTS}
    return evaluate_all(G, subset)
