#!/usr/bin/env python
"""Empirically validate the curated known relations against the battery.

Every relation in ``pipeline.known_relations`` claims a universal (or
class-restricted) bound between graph invariants. This script checks each one
against the precomputed invariant battery (connected, non-trivial graphs) and
reports any relation with a counterexample, so the novelty table never trusts an
unverified bound. Relations whose invariants are not in the battery are reported
as untestable (kept on the curator's authority).

Usage:  python tools/validate_known_relations.py
"""
from __future__ import annotations

import glob
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import known_relations as kr  # noqa: E402

# novelty symbol -> battery column (classical short names differ from columns)
SYM2COL = {
    "n": "order", "m": "size", "Delta": "maximum_degree", "delta": "minimum_degree",
    "avg_deg": "average_degree", "omega": "clique_number",
    "alpha": "independence_number", "chi": "chromatic_number",
    "gamma": "domination_number", "ind_dom": "independent_domination_number",
    "vertex_cover": "vertex_cover_number", "nu": "matching_number",
    "diam": "diameter", "rad": "radius", "min_edge_cover": "edge_cover_number",
}

TOL = 1e-6


def _load_battery() -> pd.DataFrame:
    paths = sorted(set(glob.glob("database/cache/battery_*.parquet")))
    if not paths:
        raise SystemExit("no battery parquet found under database/cache/")
    df = pd.concat([pd.read_parquet(p) for p in paths], ignore_index=True, sort=False)
    if "connected" in df:
        df = df[df["connected"] == True]  # noqa: E712
    if "nontrivial" in df:
        df = df[df["nontrivial"] == True]  # noqa: E712
    # derive the order-threshold predicates (older parquets predate them)
    if "order" in df.columns:
        o = pd.to_numeric(df["order"], errors="coerce")
        df["order_bigger_than_2"] = (o > 2).fillna(False)
        df["order_bigger_than_3"] = (o > 3).fillna(False)
    return df


def main() -> int:
    df = _load_battery()
    print(f"battery (connected, non-trivial): {len(df)} graphs")

    def col(sym):
        c = SYM2COL.get(sym, sym)
        return c if c in df.columns else None

    ok = untestable = 0
    false_rels = []
    for lhs, rhs, off, cls, name in kr.load_relations():
        needed = [lhs] + list(rhs)
        if any(col(x) is None for x in needed):
            untestable += 1
            continue
        sub = df if cls is None else (df[df[cls] == True] if cls in df.columns else None)  # noqa: E712
        if sub is None or len(sub) == 0:
            untestable += 1
            continue
        viol = sub[col(lhs)].astype(float) - off
        for k, c in rhs.items():
            viol = viol - c * sub[col(k)].astype(float)
        nbad = int((viol > TOL).sum())
        if nbad:
            false_rels.append((name, nbad, len(sub), float(viol.max())))
        else:
            ok += 1

    print(f"verified (no counterexample): {ok}")
    print(f"untestable (missing column) : {untestable}")
    print(f"FALSE (counterexamples)     : {len(false_rels)}")
    for name, nbad, ntot, worst in sorted(false_rels, key=lambda x: -x[1]):
        print(f"  [{nbad}/{ntot}, worst +{worst:g}]  {name}")
    return 1 if false_rels else 0


if __name__ == "__main__":
    raise SystemExit(main())
