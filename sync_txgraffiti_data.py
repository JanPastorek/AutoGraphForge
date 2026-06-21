#!/usr/bin/env python3
"""
sync_txgraffiti_data.py — import the graph datasets bundled with the TxGraffiti
package and synchronise them into our exact-or-blank database.

TxGraffiti ships several example datasets; only the *graph* ones are relevant
here (the polytope / qubit / NBA / Calabi-Yau tables are other domains). Those
graph tables are invariant vectors only (no graph6 / edge list), so we ingest
them the same way the HoG export and the n<=9 census are ingested: as rows of
invariant values, with column names mapped onto our canonical invariant keys
(graphs.invariants.INVARIANTS / BOOLEANS). Unmapped exotic invariants are
dropped; booleans become 1/0; missing values stay blank (the generator's
finite-mask skips them).

Re-run this whenever the installed ``txgraffiti`` version changes; it is
idempotent and rewrites ``database/txgraffiti_data.csv`` from scratch.

Usage
-----
    python sync_txgraffiti_data.py
"""
from __future__ import annotations

import csv
import os

import pandas as pd

from graphs.invariants import INVARIANTS, BOOLEANS

OUT = "database/txgraffiti_data.csv"

# TxGraffiti column name -> our canonical numeric invariant key
NUM_MAP = {
    "order": "n", "size": "m",
    "maximum_degree": "Delta", "max_degree": "Delta",
    "minimum_degree": "delta", "min_degree": "delta",
    "diameter": "diam", "radius": "rad",
    "clique_number": "omega", "chromatic_number": "chi",
    "independence_number": "alpha", "vertex_cover_number": "vertex_cover",
    "matching_number": "nu", "domination_number": "gamma",
    "independent_domination_number": "ind_dom",
    "spectral_radius": "spectral_radius",
    "largest_laplacian_eigenvalue": "lap_max",
    "second_largest_adjacency_eigenvalue": "eig2",
}
# TxGraffiti column name -> our canonical boolean key
BOOL_MAP = {
    "connected": "connected", "bipartite": "bipartite", "chordal": "chordal",
    "cubic": "cubic", "eulerian": "eulerian", "planar": "planar",
    "regular": "regular", "tree": "tree", "triangle_free": "triangle_free",
    "claw_free": "claw_free", "cograph": "cograph",
}

# the bundled datasets that are actually graphs (in priority order: the first
# file with a given graph's standard-invariant signature wins, so the richer
# graph_data.csv — which carries spectral data — is preferred over duplicates)
GRAPH_FILES = ["graph_data.csv", "expressive_graph_data.csv"]

# columns that define "the same graph" for cross-file de-duplication
SIG_KEYS = ["n", "m", "Delta", "delta", "diam", "rad",
            "omega", "chi", "alpha", "nu", "gamma"]


def _txgraffiti_data_dir() -> str:
    import txgraffiti
    return os.path.join(os.path.dirname(txgraffiti.__file__), "example_data")


def _to_float(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    s = str(v).strip()
    if s in ("", "nan", "None"):
        return None
    if s in ("True", "TRUE"):
        return 1.0
    if s in ("False", "FALSE"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return None


def main() -> None:
    data_dir = _txgraffiti_data_dir()
    out_keys = list(INVARIANTS.keys()) + list(BOOLEANS.keys())
    rows = []
    seen_sigs: set = set()
    per_file = {}

    for fname in GRAPH_FILES:
        path = os.path.join(data_dir, fname)
        if not os.path.isfile(path):
            print(f"  skip (missing): {fname}")
            continue
        df = pd.read_csv(path)
        kept = 0
        this_file_sigs: set = set()      # collected per-file so we never collapse
        for i, src in df.iterrows():      # distinct graphs *within* one file
            rec = {}
            for tx_col, our in NUM_MAP.items():
                if tx_col in df.columns:
                    val = _to_float(src[tx_col])
                    if val is not None:
                        rec[our] = val
            for tx_col, our in BOOL_MAP.items():
                if tx_col in df.columns:
                    val = _to_float(src[tx_col])
                    if val is not None:
                        rec[our] = val
            if not rec:
                continue
            sig = tuple(rec.get(k) for k in SIG_KEYS)
            if sig in seen_sigs:           # same graph already imported from an
                continue                    # *earlier* file → synchronise (skip)
            this_file_sigs.add(sig)
            rec["name"] = f"txgraffiti:{os.path.splitext(fname)[0]}:{i}"
            rows.append(rec)
            kept += 1
        seen_sigs |= this_file_sigs        # only block cross-file duplicates
        per_file[fname] = kept

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    header = ["name"] + out_keys
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for rec in rows:
            w.writerow([rec.get("name")] + [rec.get(k, "") for k in out_keys])

    print(f"  source: {data_dir}")
    for f, k in per_file.items():
        print(f"    {f:30s} -> {k} graphs imported")
    mapped = sorted(set(NUM_MAP.values()) | set(BOOL_MAP.values()))
    print(f"  mapped {len(mapped)} invariant columns: {mapped}")
    print(f"  wrote {len(rows)} graphs -> {OUT}")


if __name__ == "__main__":
    main()
