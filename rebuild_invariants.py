#!/usr/bin/env python3
"""
rebuild_invariants.py — make the enriched dataset "exact or blank".

Validation against House of Graphs showed our code is correct; the only stale
values are the *greedy fallbacks* that earlier invariant code used on large
graphs (χ for n>15, α for n>20, γ for n>14). Those are unreliable
upper/lower bounds, so for rigorous conjecturing we recompute them exactly where
feasible and BLANK them otherwise (the generator's finite-mask then skips them).

HoG rows are authoritative (exact from the export) and are left untouched.
The original file is backed up to *.bak.

  python rebuild_invariants.py
"""
import csv
import os
import shutil
import sys

import networkx as nx
from networkx.algorithms.clique import max_weight_clique

import graphs.invariants as I

csv.field_size_limit(sys.maxsize)
SRC = "database/graph_database_enriched.csv"
BAK = SRC + ".bak"

# exact-feasibility caps (above these, exact computation is too slow → blank)
CHI_EXACT_N = 17
ALPHA_EXACT_N = 20
GAMMA_EXACT_N = 14


def exact_gamma(G):
    import itertools
    nodes = list(G); n = len(nodes)
    for k in range(1, n + 1):
        for s in itertools.combinations(nodes, k):
            dom = set(s)
            for v in s:
                dom.update(G.neighbors(v))
            if len(dom) == n:
                return k
    return n


def main():
    with open(SRC) as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = list(reader)
    col = {name: i for i, name in enumerate(header)}
    gi, ni, si = col["g6"], col["n"], col["source"]
    ci, ai, gmi = col.get("chi"), col.get("alpha"), col.get("gamma")

    stats = dict(chi_fixed=0, chi_blank=0, alpha_exact=0, alpha_blank=0,
                 gamma_exact=0, gamma_blank=0, hog_skipped=0)

    for r in rows:
        if (r[si] or "").startswith("hog"):       # HoG values are authoritative
            stats["hog_skipped"] += 1
            continue
        try:
            n = int(float(r[ni]))
        except Exception:
            continue
        G = None

        def graph():
            nonlocal G
            if G is None:
                G = nx.from_graph6_bytes(r[gi].encode())
            return G

        # χ : exact only via bipartite short-circuit or small-n backtracking
        if ci is not None and n > 15 and r[ci] not in ("", None):
            g = graph()
            if g.number_of_edges() == 0:
                r[ci] = "1.0"; stats["chi_fixed"] += 1
            elif nx.is_bipartite(g):
                r[ci] = "2.0"; stats["chi_fixed"] += 1
            elif n <= CHI_EXACT_N:
                r[ci] = f"{I.chromatic_number(g):.1f}"; stats["chi_fixed"] += 1
            else:
                r[ci] = ""; stats["chi_blank"] += 1

        # α : exact via max-clique on complement up to a safe size
        if ai is not None and n > ALPHA_EXACT_N and r[ai] not in ("", None):
            r[ai] = ""; stats["alpha_blank"] += 1
        elif ai is not None and ALPHA_EXACT_N >= n > 15 and r[ai] not in ("", None):
            r[ai] = f"{max_weight_clique(nx.complement(graph()), weight=None)[1]:.1f}"
            stats["alpha_exact"] += 1

        # γ : exact brute force only for small n
        if gmi is not None and n > GAMMA_EXACT_N and r[gmi] not in ("", None):
            r[gmi] = ""; stats["gamma_blank"] += 1

    shutil.copy2(SRC, BAK)
    with open(SRC, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)

    print("Rebuild complete (backup at %s)\n" % BAK)
    for k, v in stats.items():
        print(f"  {k:14s}: {v}")
    print("\nDataset is now exact-or-blank for χ / α / γ on non-HoG rows.")


if __name__ == "__main__":
    main()
