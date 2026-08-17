#!/usr/bin/env python
"""tools/lean_differential.py — check graphcalc against the Lean kernel.

Every conjecture the pipeline makes, keeps or refutes rests on graphcalc's
invariant values. If one of those is wrong the whole process is steered by it,
silently: a bad value cannot be caught by refutation, because refutation *uses*
it. This repository already produced one concrete instance — a boolean class
flag stored as ``False`` where it should have been ``True``, which excluded 548
graphs from hypotheses they satisfied.

This is the independent check. For each small graph it asks the Lean kernel to
*evaluate* the same invariant from ``LeanProject.GraphInvariantsComputable``
and confirm it equals the number graphcalc produced::

    example : GraphCalc.indepNum G17 = 3 := by decide

``decide`` reduces the definition to a normal form and the kernel accepts only
if the two agree, so a passing file is a machine-checked statement that the two
implementations coincide on every graph tested. One ``example`` per (graph,
invariant) so that a failure names both.

Usage:
    python tools/lean_differential.py [--max-n 6] [--limit N] [--keep FILE]
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx  # noqa: E402

from config import CONFIG  # noqa: E402

# graphcalc battery column → Lean expression over the graph. Natural-number
# invariants only: `decide` compares naturals, and a float invariant has no
# exact counterpart to compare against.
NUMERIC = {
    "order": "GraphCalc.order {G}",
    "size": "GraphCalc.size {G}",
    "minimum_degree": "SimpleGraph.minDegree {G}",
    "maximum_degree": "SimpleGraph.maxDegree {G}",
    "independence_number": "GraphCalc.indepNum {G}",
    "clique_number": "GraphCalc.cliqueNum {G}",
    "domination_number": "GraphCalc.dominationNumber {G}",
    "independent_domination_number": "GraphCalc.independentDominationNumber {G}",
    "slater": "GraphCalc.slaterNumber {G}",
    "annihilation_number": "GraphCalc.annihilationNumber {G}",
    "zero_forcing_number": "GraphCalc.zeroForcingNumber {G}",
    "total_zero_forcing_number": "GraphCalc.totalZeroForcingNumber {G}",
    "connected_zero_forcing_number": "GraphCalc.connectedZeroForcingNumber {G}",
    "vertex_cover_number": "GraphCalc.vertexCoverNumber {G}",
}

# Invariants that can be undefined: `minCard` has no witness on some graphs.
# graphcalc returns None there; Lean must report no witness rather than 0.
PARTIAL = {
    "connected_zero_forcing_number": "HasConnectedZeroForcingNumber",
    "total_zero_forcing_number":     "HasTotalZeroForcingNumber",
}

BOOLEAN = {
    "connected": "GraphCalc.IsConnectedClass {G}",
    "tree": "GraphCalc.IsTreeClass {G}",
    "claw_free": "GraphCalc.IsClawFreeClass {G}",
    "cograph": "GraphCalc.IsCographClass {G}",
    "regular": "GraphCalc.IsRegularClass {G}",
    "cubic": "GraphCalc.IsCubicClass {G}",
    "subcubic": "GraphCalc.IsSubcubicClass {G}",
    "eulerian": "GraphCalc.IsEulerianClass {G}",
    "triangle_free": "GraphCalc.IsTriangleFreeClass {G}",
    "K_4_free": "GraphCalc.IsK4FreeClass {G}",
    "nontrivial": "GraphCalc.IsNontrivialClass {G}",
    "bipartite": "GraphCalc.IsBipartiteClass {G}",
}

PREAMBLE = ("import Mathlib\n"
            "import LeanProject.GraphInvariantsComputable\n\n"
            "set_option maxRecDepth 100000\n\n")


def graphs_up_to(max_n: int):
    """Every graph on 2..max_n vertices, connected or not.

    Disconnected and edgeless graphs are deliberately included: they are where
    the two implementations are most likely to differ, because that is where
    conventions diverge — domination of an isolated vertex, the minimum degree
    of an edgeless graph, whether such a graph counts as nontrivial.
    """
    from networkx.generators.atlas import graph_atlas_g
    return [G for G in graph_atlas_g() if 2 <= G.number_of_nodes() <= max_n]


def render(graphs, rows, limit=None):
    """(lean source, [(line_number, graph6, invariant, expected)])."""
    from pipeline.seed_corpus import graph6_id

    out = [PREAMBLE]
    checks = []
    line = PREAMBLE.count("\n") + 1
    for i, G in enumerate(graphs):
        gid = graph6_id(G)
        if gid not in rows.index:
            continue
        row = rows.loc[gid]
        n = G.number_of_nodes()
        edges = ", ".join(f"({a}, {b})" for a, b in
                          sorted(tuple(sorted(e)) for e in G.edges()))
        name = f"G{i}"
        out.append(f"-- {gid}  (n={n}, m={G.number_of_edges()})\n")
        out.append(f"abbrev {name} : SimpleGraph (Fin {n}) := "
                   f"GraphCalc.ofEdges {n} [{edges}]\n")
        line += 2
        for col, template in NUMERIC.items():
            value = row.get(col)
            undefined = value is None or (isinstance(value, float) and value != value)
            if undefined:
                # Skipping here was a blind spot exactly the size of a real bug.
                # graphcalc reports no value precisely when no subset satisfies
                # the predicate, and that is where `minCard` silently returned 0.
                # Assert the definedness predicate is FALSE instead of testing
                # nothing, so "graphcalc has no value" and "Lean has no witness"
                # are checked to coincide.
                pred = PARTIAL.get(col)
                if pred is None:
                    continue
                out.append(f"example : ¬ GraphCalc.{pred} {name} := by decide\n")
                checks.append((line, gid, f"{col}:undefined", False))
                line += 1
                continue
            out.append(f"example : {template.format(G=name)} = {int(value)} "
                       f":= by decide\n")
            checks.append((line, gid, col, int(value)))
            line += 1
        for col, template in BOOLEAN.items():
            value = row.get(col)
            if value is None or (isinstance(value, float) and value != value):
                continue
            expr = template.format(G=name)
            out.append(f"example : {expr if bool(value) else '¬ ' + expr} "
                       f":= by decide\n")
            checks.append((line, gid, col, bool(value)))
            line += 1
        out.append("\n")
        line += 1
        if limit and len(checks) >= limit:
            break
    return "".join(out), checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None,
                    help="stop after this many individual checks")
    ap.add_argument("--keep", default="", help="write the generated Lean here")
    ap.add_argument("--timeout", type=int, default=1800,
                    help="seconds allowed for the Lean run (the default 180s in "
                         "config is sized for a single proof, not thousands of "
                         "`decide` evaluations)")
    args = ap.parse_args()
    CONFIG.lean_timeout_s = args.timeout

    from pipeline import invariants_graphcalc as battery
    from pipeline.seed_corpus import graph6_id

    graphs = graphs_up_to(args.max_n)
    print(f"{len(graphs)} graphs on 2..{args.max_n} vertices "
          f"({sum(1 for g in graphs if not nx.is_connected(g))} disconnected)")
    rows = battery.compute_battery(graphs, cap_s=60, max_n=args.max_n)
    rows.index = [graph6_id(g) for g in graphs]

    source, checks = render(graphs, rows, args.limit)
    print(f"{len(checks)} checks over {len(NUMERIC)} numeric + "
          f"{len(BOOLEAN)} boolean invariants")
    if args.keep:
        with open(args.keep, "w") as fh:
            fh.write(source)
        print(f"wrote {args.keep}")

    from pipeline.theorem_prover import LeanSubprocessProver
    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean available — cannot verify.")
        return 2
    ok, log = lean._run_lean(source, audit_axioms=False)

    # A failing `decide` *is* a disagreement. Map it back to its line so the
    # (graph, invariant) pair is named rather than just "the file failed".
    failures = []
    for m in re.finditer(r"^.*?:(\d+):\d+: error: (.*)$", log, re.M):
        line, message = int(m.group(1)), m.group(2)
        failures.append((next((c for c in checks if c[0] == line), None), message))
    if ok and not failures:
        print(f"\nAGREEMENT: all {len(checks)} checks kernel-verified — graphcalc "
              f"and the Lean definitions coincide on every graph tested.")
        return 0
    if not failures:
        # ok=False with nothing parseable is a run that never finished, not a
        # clean bill of health — saying "0 disagreements" here would be a lie.
        print(f"\nINCONCLUSIVE: the Lean run did not complete and reported no "
              f"per-line errors. None of the {len(checks)} checks were "
              f"established.\n  {log.strip()[-300:]}")
        return 2
    print(f"\nDISAGREEMENTS: {len(failures)}")
    for match, message in failures[:25]:
        if match:
            _, gid, col, expected = match
            print(f"  {gid:>10}  {col:32s} graphcalc={expected!r}  |  {message[:66]}")
        else:
            print(f"  (unlocated) {message[:100]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
