#!/usr/bin/env python3
"""
verify_candidates.py — take the top GENERAL novel conjectures and run them
through the real pipeline: falsification (actual graph search) → Lean 4
autoformalization → theorem-prover stub.

Generation is restricted to the *computable* invariants (those with a real
networkx implementation) so the falsifiers can genuinely evaluate candidate
graphs. Candidates are fit on a sample, verified on the full enriched database,
then the strongest general ones are pushed through the pipeline.
"""
import csv
import logging
import random
import sys

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
SAMPLE = 4000
TOPK = 8
TOL = 1e-6

# Invariants we can actually compute on a fresh graph (exclude data-only ones).
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
print(f"Loaded {len(full)} graphs; {len(COMPUTABLE)} computable invariants")
full_vals = {k: np.array([inv.get(k, np.nan) for _, inv in full], float) for k in ALL_KEYS}


def verify_full(conj):
    iq = conj.inequality
    mask = np.ones(len(full), bool)
    if iq.hypothesis is not None:
        mask &= full_vals[iq.hypothesis] >= 0.5
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


# ── generate on a computable-only sample ──────────────────────────────────
rng = random.Random(11)
sample = rng.sample(full, min(SAMPLE, len(full)))
db = GraphDatabase()
for name, inv in sample:
    inv_c = {k: v for k, v in inv.items() if k in COMPUTABLE}
    e = GraphEntry(name, nx.Graph(), inv_c)
    db._name_index[e.name] = len(db._entries)
    db._entries.append(e)

cfg = Config(txgraffiti_max_conjectures=10**9, txgraffiti_filter_known=False,
             txgraffiti_multivariable=True)
allc = TxGraffitiGenerator(db, cfg).generate()
novel, known = annotate(allc)
print(f"Generated {len(allc)} | known {len(known)} | novel {len(novel)}")

# general + computable + verified on full DB
cands = []
for c in novel:
    iq = c.inequality
    if iq.hypothesis is not None:
        continue
    if not c.inequality.referenced_invariants() <= COMPUTABLE:
        continue
    res = verify_full(c)
    if res is None:
        continue
    mn, nt, sup = res
    if mn < -TOL or nt == 0 or sup < 20:
        continue
    c.metadata["ratio"] = nt / sup
    c.metadata["full"] = (nt, sup)
    cands.append(c)
cands.sort(key=lambda c: c.metadata["ratio"], reverse=True)
cands = cands[:TOPK]
print(f"Selected {len(cands)} top general candidates to push through the pipeline\n")

# ── run the real pipeline stages ──────────────────────────────────────────
falsifier = FalsificationOrchestrator(cfg)
formalizer = GraphOfThoughtFormalizer(cfg)
prover = NeuralProverClient(cfg)

for i, c in enumerate(cands, 1):
    nt, sup = c.metadata["full"]
    print("=" * 78)
    print(f"[{i}] {c.statement}")
    print(f"    DB: tight on {nt}/{sup} ({100*nt/sup:.0f}%)")

    res = falsifier.test(c)   # real graph search; updates c.status
    if res.falsified:
        g = res.counterexample_graph
        print(f"    FALSIFICATION: ✗ counterexample found by {res.strategy_used} "
              f"(n={g.number_of_nodes()}, m={g.number_of_edges()}, "
              f"violation={res.violation:.3f}) — was a finite-DB artifact")
        continue
    print("    FALSIFICATION: ✓ survived Z3/MCTS/VNS/CE search")

    lean = formalizer.formalize(c)
    if c.status == ConjectureStatus.FORMALIZED and lean:
        print("    LEAN 4:")
        for ln in lean.splitlines():
            print(f"        {ln}")
        resp = prover.prove(c)
        verdict = "✓ proved" if resp.success else f"✗ not proved ({(resp.error or 'stub')[:50]})"
        print(f"    PROVER ({getattr(resp, 'model_name', 'stub')}): {verdict}")
    else:
        print("    LEAN 4: — not auto-formalizable (invariants outside the heuristic map)")
