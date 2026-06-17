#!/usr/bin/env python3
"""
validate_against_hog.py — verify our invariant code against House of Graphs'
independently-computed values. Samples HoG rows small enough to compute exactly,
rebuilds each graph from g6, recomputes every shared invariant, and reports any
mismatch per invariant. This is an at-scale correctness check (thousands of
graphs) on an authoritative reference.

  python validate_against_hog.py [sample] [max_n]
"""
import csv
import random
import sys
from collections import defaultdict

import networkx as nx

import graphs.invariants as I

csv.field_size_limit(sys.maxsize)
SAMPLE = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
MAX_N = int(sys.argv[2]) if len(sys.argv) > 2 else 13

# stored-column → our callable
NUM = {
    "chi": I.chromatic_number, "alpha": I.independence_number,
    "omega": I.clique_number, "gamma": I.domination_number,
    "nu": I.matching_number, "Delta": I.max_degree, "delta": I.min_degree,
    "kappa": I.vertex_connectivity, "lambda": I.edge_connectivity,
    "diam": I.diameter, "rad": I.radius, "tri": I.number_of_triangles,
}
BOOL = {k: I.BOOLEANS[k] for k in ("bipartite", "planar", "regular", "eulerian")}

rng = random.Random(0)
hog_rows = []
with open("database/graph_database_enriched.csv") as fh:
    for r in csv.DictReader(fh):
        if (r.get("source") or "").startswith("hog") and r.get("g6"):
            try:
                if int(float(r["n"])) <= MAX_N:
                    hog_rows.append(r)
            except Exception:
                pass
rng.shuffle(hog_rows)
hog_rows = hog_rows[:SAMPLE]
print(f"Validating {len(hog_rows)} HoG graphs (n ≤ {MAX_N}) against our code\n")

mism = defaultdict(int)
examples = defaultdict(list)
total = defaultdict(int)
for r in hog_rows:
    G = nx.from_graph6_bytes(r["g6"].encode())
    for key, fn in NUM.items():
        ref = r.get(key, "")
        if ref in ("", None):
            continue
        try:
            ref = float(ref)
        except ValueError:
            continue
        total[key] += 1
        got = fn(G)
        if abs(got - ref) > 1e-6:
            mism[key] += 1
            if len(examples[key]) < 3:
                examples[key].append(f"g6={r['g6']} ours={got} hog={ref}")
    for key, fn in BOOL.items():
        ref = r.get(key, "")
        if ref in ("", None):
            continue
        total[key] += 1
        got = 1.0 if fn(G) else 0.0
        if abs(got - float(ref)) > 1e-6:
            mism[key] += 1
            if len(examples[key]) < 3:
                examples[key].append(f"g6={r['g6']} ours={got} hog={ref}")

print(f"{'invariant':12s} {'checked':>8s} {'mismatch':>9s}")
print("-" * 32)
any_bad = False
for key in list(NUM) + list(BOOL):
    if total[key]:
        flag = "  <-- BUG" if mism[key] else ""
        if mism[key]:
            any_bad = True
        print(f"{key:12s} {total[key]:8d} {mism[key]:9d}{flag}")
for key in list(NUM) + list(BOOL):
    for ex in examples[key]:
        print(f"   {key}: {ex}")
print("\nRESULT:", "MISMATCHES FOUND" if any_bad else "all invariants agree with HoG ✓")
