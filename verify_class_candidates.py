#!/usr/bin/env python3
"""
verify_class_candidates.py — novel conjectures *specific to graph classes*.

Same flow as verify_candidates.py but keeps the class-conditioned survivors
("for all bipartite/regular/planar/… G: …"), grouped by class. Generation is
restricted to computable invariants so the falsifiers can test them; every
reported bound is verified on the full enriched database. A representative
candidate from each of a few interesting classes is then pushed through the
real falsification → Lean → prover pipeline.
"""
import csv
import logging
import random
import sys
from collections import defaultdict

import numpy as np
import networkx as nx

csv.field_size_limit(sys.maxsize)
logging.basicConfig(level=logging.WARNING, format="%(message)s")

import graphs.invariants as I
from config import Config
from conjecture import ConjectureStatus
from graphs.database import GraphDatabase, GraphEntry
from pipeline.hypothesis_gen import TxGraffitiGenerator
from pipeline.novelty import annotate
from pipeline.falsification import FalsificationOrchestrator
from pipeline.autoformalization import GraphOfThoughtFormalizer
from pipeline.theorem_prover import NeuralProverClient

CSV_PATH = "database/graph_database_enriched.csv"
SAMPLE = 5000
TOL = 1e-6
PER_CLASS = 5                       # how many to list per class
PUSH_CLASSES = ["regular", "planar", "chordal", "bipartite", "claw_free", "eulerian"]

COMPUTABLE = {k for k, fn in {**I.INVARIANTS, **I.BOOLEANS}.items() if fn is not I._data_only}
ALL_KEYS = list(I.INVARIANTS.keys()) + list(I.BOOLEANS.keys())


def load_rows(path):
    rows = []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            inv = {}
            for k in ALL_KEYS:
                v = row.get(k, "")
                if v not in ("", None):
                    try:
                        inv[k] = float(v)
                    except ValueError:
                        pass
            rows.append((row["name"], inv))
    return rows


full = load_rows(CSV_PATH)
full_vals = {k: np.array([inv.get(k, np.nan) for _, inv in full], float) for k in ALL_KEYS}
print(f"Loaded {len(full)} graphs")


def verify_full(conj):
    iq = conj.inequality
    mask = full_vals[iq.hypothesis] >= 0.5
    for k in [iq.inv_a, iq.inv_b] + [n for _, n in iq.extra_terms]:
        mask &= np.isfinite(full_vals[k])
    if not mask.any():
        return None
    a = full_vals[iq.inv_a][mask]
    rhs = iq.coeff_b * full_vals[iq.inv_b][mask] + iq.offset
    for c, nm in iq.extra_terms:
        rhs += c * full_vals[nm][mask]
    slack = rhs - a
    return float(slack.min()), int((np.abs(slack) < TOL).sum()), int(mask.sum())


# ── generate over computable invariants on a sample ───────────────────────
rng = random.Random(13)
sample = rng.sample(full, min(SAMPLE, len(full)))
db = GraphDatabase()
for name, inv in sample:
    e = GraphEntry(name, nx.Graph(), {k: v for k, v in inv.items() if k in COMPUTABLE})
    db._name_index[e.name] = len(db._entries)
    db._entries.append(e)

cfg = Config(txgraffiti_max_conjectures=10**9, txgraffiti_filter_known=False,
             txgraffiti_multivariable=True)
allc = TxGraffitiGenerator(db, cfg).generate()
novel, known = annotate(allc)
print(f"Generated {len(allc)} | known {len(known)} | novel {len(novel)}\n")

# ── keep class-conditioned, computable, verified-on-full ──────────────────
by_class = defaultdict(list)
for c in novel:
    iq = c.inequality
    if iq.hypothesis is None or not iq.referenced_invariants() <= COMPUTABLE:
        continue
    res = verify_full(c)
    if res is None:
        continue
    mn, nt, sup = res
    if mn < -TOL or nt == 0 or sup < 20:
        continue
    c.metadata["full"] = (nt, sup)
    by_class[iq.hypothesis].append(c)

for cls in by_class:
    by_class[cls].sort(key=lambda c: c.metadata["full"][0] / c.metadata["full"][1], reverse=True)

print("=" * 80)
print("  NOVEL CONJECTURES BY GRAPH CLASS  (verified on full DB)")
print("=" * 80)
for cls in sorted(by_class, key=lambda c: -len(by_class[c])):
    conjs = by_class[cls]
    print(f"\n── {cls}  ({len(conjs)} novel) ──")
    for c in conjs[:PER_CLASS]:
        nt, sup = c.metadata["full"]
        base = c.statement.split("  (for")[0]
        print(f"   [{100*nt/sup:3.0f}% tight, {sup:5d} graphs]  {base}")

# ── push one per selected class through the real pipeline ─────────────────
falsifier = FalsificationOrchestrator(cfg)
formalizer = GraphOfThoughtFormalizer(cfg)
prover = NeuralProverClient(cfg)

print("\n" + "=" * 80)
print("  PIPELINE RUN  (falsification → Lean → prover) — best per class")
print("=" * 80)
for cls in PUSH_CLASSES:
    if not by_class.get(cls):
        continue
    c = by_class[cls][0]
    nt, sup = c.metadata["full"]
    print("=" * 78)
    print(f"[{cls}] {c.statement}")
    print(f"    DB: tight on {nt}/{sup} ({100*nt/sup:.0f}%)")
    res = falsifier.test(c)
    if res.falsified:
        g = res.counterexample_graph
        print(f"    FALSIFICATION: ✗ counterexample by {res.strategy_used} "
              f"(n={g.number_of_nodes()}, m={g.number_of_edges()})")
        continue
    print("    FALSIFICATION: ✓ survived (note: random search rarely hits rare classes)")
    lean = formalizer.formalize(c)
    if c.status == ConjectureStatus.FORMALIZED and lean:
        print("    LEAN 4:")
        for ln in lean.splitlines():
            print(f"        {ln}")
        resp = prover.prove(c)
        print(f"    PROVER: {'✓ proved' if resp.success else '✗ not proved (stub)'}")
    else:
        print("    LEAN 4: — not auto-formalizable")
