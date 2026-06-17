#!/usr/bin/env python3
"""
tests/test_invariants.py — verify every invariant against graphs with
analytically known values. Runnable as a script (exit code 0 = all pass) and as
a pytest module.

Catches the class of bug found by the adversarial filter (χ falling back to a
greedy upper bound on larger graphs).
"""
import math
import sys

import networkx as nx

import graphs.invariants as I
from pipeline import adversarial as ADV

TOL = 1e-6


def _named():
    K = nx.complete_graph
    C = nx.cycle_graph
    P = nx.path_graph
    return {
        "K1": K(1), "K2": K(2), "K3": K(3), "K4": K(4), "K5": K(5),
        "C4": C(4), "C5": C(5), "C6": C(6), "C7": C(7),
        "P3": P(3), "P4": P(4), "P5": P(5),
        "claw_K13": nx.star_graph(3),
        "petersen": nx.petersen_graph(),
        "K33": nx.complete_bipartite_graph(3, 3),
        "K23": nx.complete_bipartite_graph(2, 3),
        "bull": nx.bull_graph(),
        "wheel5": nx.wheel_graph(5),
        # large graphs — exercise the χ fix (greedy fallback used to kick in n>15)
        "P20": P(20),
        "tree17": nx.from_graph6_bytes(b"PhQ?P?CA?_?_A?_??A?G?A??"),
        "C25": C(25),
        "K8_8": nx.complete_bipartite_graph(8, 8),
        "K16": K(16),
    }


# expected[name][invariant] = value ; only listed invariants are checked
EXPECTED = {
    "K1": dict(n=1, m=0, chi=1, alpha=1, omega=1, gamma=1, nu=0, Delta=0, delta=0,
               kappa=0, lam=0, diam=0, rad=0, tri=0,
               bipartite=1, planar=1, regular=1, chordal=1, tree=1, triangle_free=1),
    "K2": dict(n=2, m=1, chi=2, alpha=1, omega=2, gamma=1, nu=1, Delta=1, delta=1,
               kappa=1, lam=1, diam=1, rad=1, tri=0, alg=2,
               bipartite=1, tree=1, regular=1, eulerian=0, chordal=1, claw_free=1),
    "K3": dict(n=3, m=3, chi=3, alpha=1, omega=3, gamma=1, nu=1, Delta=2, delta=2,
               kappa=2, lam=2, diam=1, rad=1, tri=1, alg=3,
               bipartite=0, regular=1, eulerian=1, chordal=1, triangle_free=0,
               hamiltonian=1, claw_free=1),
    "K4": dict(n=4, m=6, chi=4, alpha=1, omega=4, gamma=1, nu=2, Delta=3, delta=3,
               kappa=3, lam=3, diam=1, rad=1, tri=4, alg=4,
               planar=1, outerplanar=0, cubic=1, chordal=1, eulerian=0, hamiltonian=1),
    "K5": dict(n=5, chi=5, omega=5, alpha=1, nu=2, tri=10, kappa=4, lam=4,
               planar=0, eulerian=1, regular=1),
    "C4": dict(n=4, m=4, chi=2, alpha=2, omega=2, gamma=2, nu=2, Delta=2, delta=2,
               kappa=2, lam=2, diam=2, rad=2, tri=0, alg=2,
               bipartite=1, regular=1, eulerian=1, chordal=0, triangle_free=1,
               cograph=1, hamiltonian=1, well_covered=1, outerplanar=1),
    "C5": dict(n=5, chi=3, alpha=2, omega=2, gamma=2, nu=2, diam=2, rad=2, tri=0,
               bipartite=0, chordal=0, self_compl=1, hamiltonian=1, triangle_free=1,
               well_covered=1, regular=1),
    "C6": dict(n=6, chi=2, alpha=3, gamma=2, nu=3, diam=3, rad=3,
               bipartite=1, chordal=0, regular=1, eulerian=1),
    "C7": dict(n=7, chi=3, alpha=3, gamma=3, nu=3, diam=3, rad=3, bipartite=0),
    "P3": dict(n=3, chi=2, alpha=2, omega=2, gamma=1, nu=1, Delta=2, delta=1,
               kappa=1, lam=1, diam=2, rad=1, tree=1, bipartite=1, chordal=1),
    "P4": dict(n=4, chi=2, alpha=2, gamma=2, nu=2, diam=3, rad=2,
               tree=1, self_compl=1, cograph=0, split=1, bipartite=1),
    "P5": dict(n=5, chi=2, alpha=3, gamma=2, nu=2, diam=4, rad=2, tree=1),
    "claw_K13": dict(n=4, chi=2, alpha=3, omega=2, gamma=1, nu=1, Delta=3, delta=1,
                     diam=2, rad=1, tree=1, bipartite=1,
                     claw_free=0, well_covered=0),
    "petersen": dict(n=10, chi=3, alpha=4, omega=2, gamma=3, nu=5, Delta=3, delta=3,
                     kappa=3, lam=3, diam=2, rad=2, tri=0,
                     bipartite=0, planar=0, regular=1, cubic=1, chordal=0,
                     triangle_free=1, hamiltonian=0, claw_free=0),
    "K33": dict(n=6, chi=2, alpha=3, omega=2, gamma=2, nu=3, Delta=3, delta=3,
                diam=2, rad=2, bipartite=1, planar=0, regular=1, cubic=1,
                eulerian=0, hamiltonian=1),
    "K23": dict(n=5, chi=2, alpha=3, omega=2, nu=2, diam=2, bipartite=1, planar=1),
    "bull": dict(n=5, chi=3, omega=3, alpha=3, tri=1, planar=1, chordal=1, tree=0),
    "wheel5": dict(n=5, chi=3, omega=3, tri=4, planar=1, hamiltonian=1),
    # χ on larger graphs (the bug: greedy upper bound for n>15)
    "P20": dict(n=20, chi=2, tree=1, bipartite=1),
    "tree17": dict(n=17, chi=2, tree=1, bipartite=1),
    "C25": dict(n=25, chi=3, bipartite=0, regular=1),
    "K8_8": dict(n=16, chi=2, bipartite=1, regular=1),
    "K16": dict(n=16, chi=16, omega=16, alpha=1),
}

# map check-key → invariant callable
NUM = {
    "n": I.number_of_vertices, "m": I.number_of_edges, "chi": I.chromatic_number,
    "alpha": I.independence_number, "omega": I.clique_number,
    "gamma": I.domination_number, "nu": I.matching_number,
    "Delta": I.max_degree, "delta": I.min_degree,
    "kappa": I.vertex_connectivity, "lam": I.edge_connectivity,
    "diam": I.diameter, "rad": I.radius, "tri": I.number_of_triangles,
    "alg": I.algebraic_connectivity,
}
BOOL = {k: I.BOOLEANS[k] for k in (
    "bipartite", "planar", "regular", "eulerian", "chordal", "tree",
    "triangle_free", "cubic", "claw_free", "cograph", "split", "outerplanar",
    "self_compl", "hamiltonian", "well_covered") if k in I.BOOLEANS}


def run():
    graphs = _named()
    fails = []
    checks = 0
    for name, exp in EXPECTED.items():
        G = graphs[name]
        for key, want in exp.items():
            if key in NUM:
                got = NUM[key](G)
            elif key in BOOL:
                got = 1 if BOOL[key](G) else 0
            else:
                continue
            checks += 1
            ok = abs(got - want) < TOL if isinstance(want, float) or key == "alg" \
                else got == want
            if not ok:
                fails.append(f"{name}.{key}: got {got}, want {want}")

    # cross-check: adversarial inv_exact agrees with the registry on shared keys
    xkeys = {"n", "m", "alpha", "omega", "chi", "nu", "Delta", "delta",
             "kappa", "lambda", "diam", "rad", "tri"}
    for name in ("K4", "C5", "petersen", "P5", "bull"):
        d = ADV.inv_exact(graphs[name])
        for k in xkeys:
            reg = {"lambda": "lam"}.get(k, k)
            want = NUM[reg](graphs[name]) if reg in NUM else None
            if want is None:
                continue
            checks += 1
            if abs(d[k] - want) > TOL:
                fails.append(f"inv_exact[{name}].{k}: got {d[k]}, registry {want}")

    print(f"invariant checks: {checks} run, {len(fails)} failed")
    for f in fails:
        print("  FAIL:", f)
    return len(fails) == 0


def test_invariants():
    assert run()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
