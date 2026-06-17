"""
pipeline/novelty.py — known-theorem novelty filter.

Classifies a generated linear-inequality Conjecture as either a rediscovery of a
classical/trivial result ("known") or genuinely "novel".

Method
------
A conjecture  C:  f(G) ≤ Σ cᵢ·gᵢ(G) + c₀   (optionally restricted to a class P)
is considered *known* if it is logically **implied** by a convex combination of
curated classical theorems with the same left-hand invariant f and a compatible
graph class.

Because graph invariants are independent non-negative quantities, a linear form
B(G) = Σ bᵢ·gᵢ + b₀ satisfies  B(G) ≤ C_rhs(G)  for every graph in the class iff

    bᵢ ≤ cᵢ          for every invariant i          (term-wise dominance)
    b₀ ≤ c₀ + Σ (cᵢ − bᵢ)·Lᵢ                         (offset, using class lower
                                                       bounds Lᵢ ≤ gᵢ)

If several known theorems  f ≤ Bⱼ  hold, then for convex weights wⱼ ≥ 0, Σ wⱼ = 1
we also have  f ≤ Σ wⱼ Bⱼ.  So C is known iff such weights exist with the combined
form dominating C_rhs — a small LP feasibility problem (scipy ``linprog``), with a
cheap single-theorem fast path checked first.

The theorem table below is intentionally conservative: it encodes only safe,
universally-true lower bounds, so the filter never *wrongly* hides a real
conjecture (it may, at worst, leave a trivial one labelled "novel"). Extend
``KNOWN_THEOREMS`` / ``LOWER_BOUNDS`` to tighten it further.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

from conjecture import Conjecture

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Class hierarchy — a theorem proved for a superclass also holds for subclasses.
# ---------------------------------------------------------------------------

SUPERCLASSES: Dict[str, set] = {
    # trees and (acyclic) forests are bipartite, chordal and planar
    "tree": {"bipartite", "chordal", "planar", "acyclic"},
    "acyclic": {"bipartite", "chordal", "planar"},
    "cubic": {"regular"},
    "split": {"chordal"},
    "outerplanar": {"planar"},
}


# ---------------------------------------------------------------------------
# Safe lower bounds Lᵢ ≤ invariant(G), true for every graph with ≥ 1 vertex.
# (Conservative on purpose — only bounds that cannot be violated.)
# ---------------------------------------------------------------------------

LOWER_BOUNDS: Dict[str, float] = {
    "n": 1.0,
    "chi": 1.0,
    "omega": 1.0,
    "alpha": 1.0,
    "gamma": 1.0,
    # everything else is ≥ 0
}


# ---------------------------------------------------------------------------
# Linear identities Σ cᵢ·invᵢ + c₀ = 0 that hold on a class (or all graphs).
# Used to *substitute* equal quantities when checking implication, e.g. on
# regular graphs Δ = δ = 2m/n = ρ = degeneracy, so a bound on one is a bound on
# any of them; or Gallai's n = α + τ and König's ν = τ on bipartite graphs.
# ---------------------------------------------------------------------------

IDENTITIES: List[Tuple[Dict[str, float], float, Optional[str]]] = [
    ({"n": 1.0, "alpha": -1.0, "vertex_cover": -1.0}, 0.0, None),     # n = α + τ
    ({"nu": 1.0, "vertex_cover": -1.0}, 0.0, "bipartite"),            # ν = τ (König)
    ({"Delta": 1.0, "delta": -1.0}, 0.0, "regular"),
    ({"Delta": 1.0, "avg_deg": -1.0}, 0.0, "regular"),
    ({"Delta": 1.0, "spectral_radius": -1.0}, 0.0, "regular"),
    ({"Delta": 1.0, "degeneracy": -1.0}, 0.0, "regular"),
    ({"alpha": 1.0, "ind_dom": -1.0}, 0.0, "well_covered"),   # i(G) = α (well-covered)
]


# ---------------------------------------------------------------------------
# Curated classical / trivial theorems.
#
# Each entry:  (lhs, {rhs_invariant: coeff, ...}, offset, class_or_None, name)
# meaning      lhs(G) ≤ Σ coeff·rhs(G) + offset   for the given class.
# ---------------------------------------------------------------------------

KNOWN_THEOREMS: List[Tuple[str, Dict[str, float], float, Optional[str], str]] = [
    # ── chromatic / clique ────────────────────────────────────────────────
    ("omega", {"chi": 1.0}, 0.0, None, "ω ≤ χ"),
    ("chi",   {"Delta": 1.0}, 1.0, None, "χ ≤ Δ + 1 (greedy/Brooks)"),
    ("omega", {"Delta": 1.0}, 1.0, None, "ω ≤ Δ + 1"),

    # ── Whitney connectivity chain  κ ≤ λ ≤ δ ≤ Δ ─────────────────────────
    ("kappa",  {"lambda": 1.0}, 0.0, None, "κ ≤ λ (Whitney)"),
    ("lambda", {"delta": 1.0},  0.0, None, "λ ≤ δ (Whitney)"),
    ("kappa",  {"delta": 1.0},  0.0, None, "κ ≤ δ (Whitney)"),
    ("kappa",  {"Delta": 1.0},  0.0, None, "κ ≤ Δ"),
    ("lambda", {"Delta": 1.0},  0.0, None, "λ ≤ Δ"),
    ("delta",  {"Delta": 1.0},  0.0, None, "δ ≤ Δ"),

    # ── algebraic (Fiedler) connectivity:  a(G) ≤ κ ≤ λ ≤ δ ───────────────
    ("alg", {"kappa": 1.0},  0.0, None, "a(G) ≤ κ (Fiedler)"),
    ("alg", {"lambda": 1.0}, 0.0, None, "a(G) ≤ λ (Fiedler)"),
    ("alg", {"delta": 1.0},  0.0, None, "a(G) ≤ δ (Fiedler)"),

    # ── distance ──────────────────────────────────────────────────────────
    ("rad",  {"diam": 1.0}, 0.0, None, "rad ≤ diam"),
    ("diam", {"rad": 2.0},  0.0, None, "diam ≤ 2·rad"),

    # ── matching ──────────────────────────────────────────────────────────
    ("nu", {"n": 0.5}, 0.0, None, "ν ≤ n/2"),

    # ── trivial order caps  (f ≤ n, Δ ≤ n−1, …) ───────────────────────────
    ("chi",    {"n": 1.0}, 0.0, None, "χ ≤ n"),
    ("omega",  {"n": 1.0}, 0.0, None, "ω ≤ n"),
    ("alpha",  {"n": 1.0}, 0.0, None, "α ≤ n"),
    ("gamma",  {"n": 1.0}, 0.0, None, "γ ≤ n"),
    ("nu",     {"n": 1.0}, 0.0, None, "ν ≤ n"),
    ("kappa",  {"n": 1.0}, 0.0, None, "κ ≤ n"),
    ("lambda", {"n": 1.0}, 0.0, None, "λ ≤ n"),
    ("Delta",  {"n": 1.0}, -1.0, None, "Δ ≤ n − 1"),
    ("delta",  {"n": 1.0}, -1.0, None, "δ ≤ n − 1"),
    ("diam",   {"n": 1.0}, -1.0, None, "diam ≤ n − 1"),
    ("rad",    {"n": 1.0}, -1.0, None, "rad ≤ n − 1"),

    # ── edge colouring (Vizing):  Δ ≤ χ′ ≤ Δ + 1 ─────────────────────────
    ("Delta", {"chi_e": 1.0}, 0.0, None, "Δ ≤ χ′ (Vizing)"),
    ("chi_e", {"Delta": 1.0}, 1.0, None, "χ′ ≤ Δ + 1 (Vizing)"),

    # ── degeneracy d:  δ ≤ d ≤ Δ,  χ,ω ≤ d + 1,  d ≤ tw ───────────────────
    ("degeneracy", {"Delta": 1.0}, 0.0, None, "degeneracy ≤ Δ"),
    ("delta", {"degeneracy": 1.0}, 0.0, None, "δ ≤ degeneracy"),
    ("chi", {"degeneracy": 1.0}, 1.0, None, "χ ≤ degeneracy + 1"),
    ("omega", {"degeneracy": 1.0}, 1.0, None, "ω ≤ degeneracy + 1"),
    ("degeneracy", {"treewidth": 1.0}, 0.0, None, "degeneracy ≤ treewidth"),

    # ── treewidth tw:  χ,ω ≤ tw + 1,  δ ≤ tw,  tw ≤ n − 1 ─────────────────
    ("chi", {"treewidth": 1.0}, 1.0, None, "χ ≤ tw + 1"),
    ("omega", {"treewidth": 1.0}, 1.0, None, "ω ≤ tw + 1"),
    ("delta", {"treewidth": 1.0}, 0.0, None, "δ ≤ tw"),
    ("treewidth", {"n": 1.0}, -1.0, None, "tw ≤ n − 1"),

    # ── vertex cover τ (Gallai τ = n − α; König–Egerváry ν ≤ τ ≤ 2ν) ──────
    ("vertex_cover", {"n": 1.0, "alpha": -1.0}, 0.0, None, "τ = n − α (Gallai)"),
    ("alpha", {"n": 1.0, "vertex_cover": -1.0}, 0.0, None, "α = n − τ (Gallai)"),
    ("nu", {"vertex_cover": 1.0}, 0.0, None, "ν ≤ τ (König–Egerváry)"),
    ("vertex_cover", {"nu": 2.0}, 0.0, None, "τ ≤ 2ν"),
    ("vertex_cover", {"n": 1.0}, -1.0, None, "τ ≤ n − 1"),
    ("nu", {"alpha": 0.5, "vertex_cover": 0.5}, 0.0, None, "ν ≤ ½(α+τ) = n/2"),

    # ── (independent) domination:  γ ≤ i(G) ≤ α ──────────────────────────
    ("gamma", {"ind_dom": 1.0}, 0.0, None, "γ ≤ i(G)"),
    ("ind_dom", {"alpha": 1.0}, 0.0, None, "i(G) ≤ α"),

    # ── degree / spectral chain:  δ ≤ 2m/n ≤ ρ ≤ Δ,  ω ≤ ρ + 1 ───────────
    ("delta", {"avg_deg": 1.0}, 0.0, None, "δ ≤ 2m/n"),
    ("avg_deg", {"Delta": 1.0}, 0.0, None, "2m/n ≤ Δ"),
    ("avg_deg", {"spectral_radius": 1.0}, 0.0, None, "2m/n ≤ ρ"),
    ("spectral_radius", {"Delta": 1.0}, 0.0, None, "ρ ≤ Δ"),
    ("delta", {"spectral_radius": 1.0}, 0.0, None, "δ ≤ ρ"),
    ("omega", {"spectral_radius": 1.0}, 1.0, None, "ω ≤ ρ + 1"),
    ("eig2", {"spectral_radius": 1.0}, 0.0, None, "λ₂ ≤ λ₁ (adjacency)"),

    # ── Laplacian largest eigenvalue μ:  a(G) ≤ μ ≤ 2Δ,  μ ≤ n ───────────
    ("lap_max", {"n": 1.0}, 0.0, None, "μ ≤ n"),
    ("lap_max", {"Delta": 2.0}, 0.0, None, "μ ≤ 2Δ"),
    ("alg", {"lap_max": 1.0}, 0.0, None, "a(G) ≤ μ"),

    # ── paths / cycles / distance ─────────────────────────────────────────
    ("longest_path", {"n": 1.0}, -1.0, None, "longest path ≤ n − 1"),
    ("circumference", {"n": 1.0}, 0.0, None, "circumference ≤ n"),
    ("circumference", {"longest_path": 1.0}, 1.0, None, "circumference ≤ longest path + 1"),
    ("diam", {"longest_path": 1.0}, 0.0, None, "diam ≤ longest path"),
    ("girth", {"circumference": 1.0}, 0.0, None, "girth ≤ circumference"),

    # ── symmetry / components ─────────────────────────────────────────────
    ("components", {"n": 1.0}, 0.0, None, "components ≤ n"),
    ("vertex_orbits", {"n": 1.0}, 0.0, None, "vertex orbits ≤ n"),
    ("edge_orbits", {"m": 1.0}, 0.0, None, "edge orbits ≤ m"),
    ("arc_orbits", {"edge_orbits": 2.0}, 0.0, None, "arc orbits ≤ 2·edge orbits"),

    # ── perfect graphs: χ = ω on bipartite & chordal graphs ───────────────
    ("chi", {"omega": 1.0}, 0.0, "bipartite", "χ ≤ ω (bipartite is perfect)"),
    ("chi", {"omega": 1.0}, 0.0, "chordal",   "χ ≤ ω (chordal is perfect)"),

    # ── bipartite ─────────────────────────────────────────────────────────
    ("chi",   {}, 2.0, "bipartite", "χ ≤ 2 (bipartite)"),
    ("omega", {}, 2.0, "bipartite", "ω ≤ 2 (bipartite)"),
    ("tri",   {}, 0.0, "bipartite", "triangle-free (bipartite)"),
    ("n", {"alpha": 2.0}, 0.0, "bipartite", "n ≤ 2α (bipartite, König/Gallai)"),

    # ── planar ────────────────────────────────────────────────────────────
    ("chi",   {}, 4.0, "planar", "χ ≤ 4 (Four-Colour Theorem)"),
    ("delta", {}, 5.0, "planar", "δ ≤ 5 (planar degeneracy)"),

    # ── regular ───────────────────────────────────────────────────────────
    ("Delta", {"delta": 1.0}, 0.0, "regular", "Δ = δ (regular)"),
    ("delta", {"Delta": 1.0}, 0.0, "regular", "Δ = δ (regular)"),

    # ── new computed classes ──────────────────────────────────────────────
    ("omega", {}, 2.0, "triangle_free", "ω ≤ 2 (triangle-free)"),
    ("tri", {}, 0.0, "triangle_free", "0 triangles (triangle-free)"),
    ("chi", {"omega": 1.0}, 0.0, "cograph", "χ ≤ ω (cographs are perfect)"),
    ("chi", {"omega": 1.0}, 0.0, "split", "χ ≤ ω (split graphs are perfect)"),
    ("alpha", {"ind_dom": 1.0}, 0.0, "well_covered", "α = i(G) (well-covered)"),

    # ── trivial / known bounds (per external review) ──────────────────────
    # universal structural & spectral facts (also subsume class-conditioned forms)
    ("treewidth", {"fvs": 1.0}, 1.0, None, "tw ≤ fvs + 1"),
    ("omega", {"fvs": 1.0}, 2.0, None, "ω ≤ fvs + 2"),
    ("chi", {"spectral_radius": 1.0}, 1.0, None, "χ ≤ ρ + 1 (Wilf)"),
    ("chi_e", {"lap_max": 1.0}, 0.0, None, "χ′ ≤ μ_max"),
    ("lap_max", {"chi_e": 2.0}, 0.0, None, "μ_max ≤ 2χ′"),
    ("diam", {"longest_induced_path": 1.0}, 0.0, None, "diam ≤ longest induced path"),
    ("longest_path", {"nu": 2.0}, 0.0, None, "longest path ≤ 2ν"),
    ("circumference", {"nu": 2.0}, 0.0, None, "circumference ≤ 2ν"),
    ("longest_induced_cycle", {"longest_induced_path": 1.0}, 1.0, None, "lic ≤ lip + 1"),
    ("longest_induced_cycle", {"alpha": 2.0}, 1.0, None, "lic ≤ 2α + 1"),
    ("components", {"gamma": 1.0}, 0.0, None, "components ≤ γ"),
    ("spectral_radius", {"Delta": 1.0}, 0.0, None, "ρ ≤ Δ"),       # also density helper
    ("density", {}, 1.0, None, "density ≤ 1 (trivial)"),
    # class-specific known/artifact bounds
    ("degeneracy", {}, 5.0, "planar", "degeneracy ≤ 5 (planar, Euler)"),
    ("degeneracy", {"treewidth": 0.5}, 2.0, "planar", "degeneracy ≤ ½tw+2 (planar artifact)"),
    ("vertex_cover", {"n": 0.5}, 0.0, "bipartite", "τ ≤ n/2 (bipartite)"),
    ("spectral_radius", {"lap_max": 0.5}, 0.0, "bipartite", "ρ ≤ ½μ (bipartite)"),
    ("rad", {"alpha": 1.0}, 0.0, "claw_free", "rad ≤ α (claw-free, known)"),
    ("lap_max", {"spectral_radius": 2.0}, 0.0, "regular", "μ ≤ 2ρ (regular)"),
    ("chi_e", {"degeneracy": 1.0}, 1.0, "regular", "χ′ ≤ degeneracy + 1 (regular)"),

    # ── round-2 triage: further provable / trivial bounds ─────────────────
    ("degeneracy", {"spectral_radius": 1.0}, 0.0, None, "degeneracy ≤ ρ"),
    ("avg_deg", {"degeneracy": 2.0}, 0.0, None, "2m/n ≤ 2·degeneracy"),
    ("chi", {"chi_e": 1.0}, 1.0, None, "χ ≤ χ′ + 1"),
    ("omega", {"chi_e": 1.0}, 1.0, None, "ω ≤ χ′ + 1"),
    ("chi_e", {"Delta": 1.5}, 0.0, None, "χ′ ≤ 1.5Δ (Vizing)"),
    ("eig_min", {}, 0.0, None, "λ_min ≤ 0 (trace 0)"),
    ("rad", {"n": 0.5}, 0.0, None, "rad ≤ n/2"),
    ("degeneracy", {"genus": 1.0}, 5.0, None, "degeneracy ≤ genus + 5 (Euler)"),
    ("delta", {"genus": 1.0}, 5.0, None, "δ ≤ genus + 5 (Euler)"),
    ("kappa", {"genus": 1.0}, 5.0, None, "κ ≤ genus + 5 (Euler)"),
    ("lambda", {"genus": 1.0}, 5.0, None, "λ ≤ genus + 5 (Euler)"),
    ("eig2", {"spectral_radius": 1.0}, 0.0, None, "λ₂ ≤ λ₁ = ρ"),
    ("circumference", {"vertex_cover": 2.0}, 0.0, None, "circumference ≤ 2τ"),

    # ── external review round 2: more classical / structural results ──────
    # rad ≤ α: Fajtlowicz–Saks; via Chung's induced-path theorem (rad r ⟹ an
    # induced path on ≥2r−1 vertices ⟹ α ≥ r). Universal ⇒ covers all classes.
    ("rad", {"alpha": 1.0}, 0.0, None, "rad ≤ α (Fajtlowicz–Saks / Chung)"),
    ("gamma", {"nu": 1.0}, 0.0, None, "γ ≤ ν (Laskar–Walikar, isolate-free)"),
    ("omega", {"tri": 1.0}, 2.0, None, "ω ≤ tri + 2 (clique has C(ω,3) triangles)"),
    ("n", {"m": 1.0}, 1.0, None, "n ≤ m + 1 (connected: m ≥ n−1)"),
    # split graphs:  diam ≤ 3, rad ≤ 2, hence the radius/diameter/domination bounds
    ("diam", {}, 3.0, "split", "diam ≤ 3 (split)"),
    ("rad", {}, 2.0, "split", "rad ≤ 2 (split)"),
    ("rad", {"gamma": 1.0}, 0.0, "split", "rad ≤ γ (split)"),
    ("rad", {"ind_dom": 1.0}, 0.0, "split", "rad ≤ i (split)"),
    ("diam", {"rad": 1.0}, 1.0, "split", "diam ≤ rad + 1 (split)"),
    ("diam", {"gamma": 1.0}, 1.0, "split", "diam ≤ γ + 1 (split)"),
    ("diam", {"ind_dom": 1.0}, 1.0, "split", "diam ≤ i + 1 (split)"),
    # well-covered: i(G) = α(G), so rad ≤ α gives rad ≤ i too (via identity below)
    ("rad", {"gamma": 1.0}, 0.0, "well_covered", "rad ≤ γ (well-covered)"),
    # chordal: perfect (χ=ω) + simplicial vertex (δ ≤ C(δ,2) ≤ tri)
    ("chi", {"tri": 1.0}, 2.0, "chordal", "χ ≤ tri + 2 (chordal, perfect)"),
    ("delta", {"tri": 1.0}, 1.0, "chordal", "δ ≤ tri + 1 (chordal, simplicial)"),
    ("kappa", {"tri": 1.0}, 1.0, "chordal", "κ ≤ tri + 1 (chordal)"),
    ("lambda", {"tri": 1.0}, 1.0, "chordal", "λ ≤ tri + 1 (chordal)"),
    # Hamiltonian: spanning cycle ⇒ diam ≤ ⌊n/2⌋ and a near-perfect matching
    ("diam", {"gamma": 2.0}, 0.0, "hamiltonian", "diam ≤ 2γ (Hamiltonian)"),
    ("diam", {"ind_dom": 2.0}, 0.0, "hamiltonian", "diam ≤ 2i (Hamiltonian)"),
    ("n", {"nu": 2.0}, 1.0, "hamiltonian", "n ≤ 2ν + 1 (Hamiltonian)"),
    ("n", {"nu": 2.0}, 1.0, "claw_free", "n ≤ 2ν + 1 (Sumner–Las Vergnas)"),
]


# ---------------------------------------------------------------------------
# Transitive closure of the simple  f ≤ g  relations
# ---------------------------------------------------------------------------
# Many true bounds are chains: κ ≤ λ ≤ δ ≤ degeneracy ≤ treewidth, or
# a(G) ≤ κ ≤ … ≤ Δ ≤ χ′.  Each link is a tabled theorem of the form
# ``f ≤ g`` (coeff 1, offset 0); their transitive composition is also true.
# We materialise the closure as extra theorems so the implication checker
# (which only combines theorems sharing the conjecture's LHS) catches the
# composed bounds too.

def _transitive_theorems(base):
    from collections import defaultdict

    universal = defaultdict(set)              # f -> {g}   (holds on all graphs)
    per_class = defaultdict(lambda: defaultdict(set))   # cls -> f -> {g}
    for lhs, rhs, off, cls, _ in base:
        if off == 0.0 and len(rhs) == 1:
            (g, c), = rhs.items()
            if c == 1.0:
                (universal if cls is None else per_class[cls])[lhs].add(g)

    def closure(adj):
        nodes = set(adj) | {g for s in adj.values() for g in s}
        reach = {f: set(adj.get(f, ())) for f in nodes}
        changed = True
        while changed:
            changed = False
            for f in nodes:
                extra = set().union(*(reach.get(g, set()) for g in reach[f])) if reach[f] else set()
                if not extra <= reach[f]:
                    reach[f] |= extra
                    changed = True
        return reach

    derived = []
    ureach = closure(universal)
    for f, gs in ureach.items():
        for g in gs:
            if f != g and g not in universal.get(f, set()):
                derived.append((f, {g: 1.0}, 0.0, None, f"transitive: {f} ≤ {g}"))

    for cls, cedges in per_class.items():
        merged = defaultdict(set)
        for f in set(universal) | set(cedges):
            merged[f] = universal.get(f, set()) | cedges.get(f, set())
        for f, gs in closure(merged).items():
            for g in gs:
                if f != g and g not in ureach.get(f, set()) and g not in cedges.get(f, set()):
                    derived.append((f, {g: 1.0}, 0.0, cls, f"transitive[{cls}]: {f} ≤ {g}"))
    return derived


KNOWN_THEOREMS += _transitive_theorems(KNOWN_THEOREMS)


# ---------------------------------------------------------------------------
# Implication checks
# ---------------------------------------------------------------------------

def _rhs_of(conj: Conjecture) -> Tuple[str, Dict[str, float], float, Optional[str]]:
    """Normalise a conjecture to  inv_a ≤ {coeffs} + offset  (coeff on lhs = 1)."""
    ineq = conj.inequality
    ca = ineq.coeff_a or 1.0
    rhs: Dict[str, float] = {}
    rhs[ineq.inv_b] = rhs.get(ineq.inv_b, 0.0) + ineq.coeff_b / ca
    for coeff, name in ineq.extra_terms:
        rhs[name] = rhs.get(name, 0.0) + coeff / ca
    return ineq.inv_a, rhs, ineq.offset / ca, ineq.hypothesis


def _single_implies(B: Dict[str, float], b0: float,
                    R: Dict[str, float], r0: float, tol: float = 1e-6) -> bool:
    """Does the single known bound (B, b0) dominate the conjecture rhs (R, r0)?"""
    invs = set(B) | set(R)
    # term-wise dominance: bᵢ ≤ cᵢ
    for i in invs:
        if B.get(i, 0.0) > R.get(i, 0.0) + tol:
            return False
    # offset, relaxed by the safe class lower bounds
    slack = r0 - b0 + sum(
        (R.get(i, 0.0) - B.get(i, 0.0)) * LOWER_BOUNDS.get(i, 0.0) for i in invs
    )
    return slack >= -tol


def _convex_implies(theorems: List[Tuple[Dict[str, float], float, str]],
                    R: Dict[str, float], r0: float,
                    identities: Optional[List[Tuple[Dict[str, float], float]]] = None,
                    tol: float = 1e-6) -> Optional[List[str]]:
    """LP feasibility (Farkas): is  f ≤ R  implied by  {f ≤ Bⱼ}, the safe lower
    bounds Lᵢ ≤ gᵢ, and the class identities Eₖ(g) = 0 ?

    We seek convex weights wⱼ ≥ 0 (Σ = 1), slacks sᵢ ≥ 0, t ≥ 0 and free
    multipliers μₖ with, identically in g,
        R(g) − Σ wⱼ Bⱼ(g) = Σ sᵢ (gᵢ − Lᵢ) + Σ μₖ Eₖ(g) + t.
    Matching coefficients gives an equality-constrained LP. Returns the names of
    the positively-weighted theorems if feasible, else None.
    """
    try:
        import numpy as np
        from scipy.optimize import linprog
    except Exception:
        return None

    identities = identities or []
    m = len(theorems)
    K = len(identities)
    invs = sorted(set(R)
                  | {i for B, _, _ in theorems for i in B}
                  | {i for E, _ in identities for i in E})
    p = len(invs)
    # variables: w(0..m-1), s(0..p-1), t, mu(0..K-1)
    nvars = m + p + 1 + K

    def col_w(j): return j
    def col_s(idx): return m + idx
    col_t = m + p
    def col_mu(k): return m + p + 1 + k

    A_eq, b_eq = [], []
    # per-invariant:  Σ wⱼ Bⱼ[i] + sᵢ + Σ μₖ Eₖ[i] = R[i]
    for idx, i in enumerate(invs):
        row = [0.0] * nvars
        for j, (B, _, _) in enumerate(theorems):
            row[col_w(j)] = B.get(i, 0.0)
        row[col_s(idx)] = 1.0
        for k, (E, _) in enumerate(identities):
            row[col_mu(k)] = E.get(i, 0.0)
        A_eq.append(row)
        b_eq.append(R.get(i, 0.0))
    # constant:  Σ wⱼ b0ⱼ − Σ sᵢ Lᵢ + t + Σ μₖ E0ₖ = r0
    row = [0.0] * nvars
    for j, (_, b0, _) in enumerate(theorems):
        row[col_w(j)] = b0
    for idx, i in enumerate(invs):
        row[col_s(idx)] = -LOWER_BOUNDS.get(i, 0.0)
    row[col_t] = 1.0
    for k, (_, e0) in enumerate(identities):
        row[col_mu(k)] = e0
    A_eq.append(row)
    b_eq.append(r0)
    # Σ wⱼ = 1
    row = [0.0] * nvars
    for j in range(m):
        row[col_w(j)] = 1.0
    A_eq.append(row)
    b_eq.append(1.0)

    bounds = [(0.0, None)] * (m + p + 1) + [(None, None)] * K
    res = linprog(c=[0.0] * nvars,
                  A_eq=np.array(A_eq, float), b_eq=np.array(b_eq, float),
                  bounds=bounds, method="highs")
    if not res.success:
        return None
    return [theorems[j][2] for j in range(m) if res.x[j] > 1e-6]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify(conj: Conjecture) -> Tuple[bool, Optional[str]]:
    """Return (is_known, matched_theorem_description).

    is_known == True  ⟹ the conjecture is implied by classical/trivial theorems.
    """
    if conj.inequality is None:
        return False, None

    lhs, R, r0, cls = _rhs_of(conj)
    applicable = {None, cls} | SUPERCLASSES.get(cls, set())
    theorems = [
        (B, b0, name)
        for (tlhs, B, b0, tcls, name) in KNOWN_THEOREMS
        if tlhs == lhs and tcls in applicable
    ]
    if not theorems:
        return False, None

    # Cheap path: a single known bound already dominates the conjecture.
    for B, b0, name in theorems:
        if _single_implies(B, b0, R, r0):
            return True, name

    # General path: convex combination of known bounds + class identities
    # (e.g. κ ≤ ½δ + ½λ via Whitney, or regular-graph degree substitutions).
    idents = [(E, e0) for (E, e0, ecls) in IDENTITIES if ecls in applicable]
    used = _convex_implies(theorems, R, r0, idents)
    if used:
        return True, " + ".join(used)

    return False, None


def annotate(conjectures: List[Conjecture]) -> Tuple[List[Conjecture], List[Conjecture]]:
    """Tag every conjecture's metadata with novelty info; return (novel, known)."""
    novel: List[Conjecture] = []
    known: List[Conjecture] = []
    for c in conjectures:
        is_known, matched = classify(c)
        c.metadata["novelty"] = "known" if is_known else "novel"
        if matched:
            c.metadata["matched_theorem"] = matched
        (known if is_known else novel).append(c)
    return novel, known
