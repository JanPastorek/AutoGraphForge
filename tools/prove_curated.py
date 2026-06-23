#!/usr/bin/env python3
"""
tools/prove_curated.py — validate the full chain (preamble + export header +
local DeepSeek-Prover-V2 + kernel verify) on a few universally-true theorems over
mathlib-native invariants, exactly as the pipeline would export them.
"""
from __future__ import annotations
import logging, sys
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("prove_curated")

from config import CONFIG
from conjecture import Conjecture
from pipeline.lean_export import _PREAMBLE, _HEADER_BINDERS

def thm(name: str, body: str) -> str:
    return (f"{_PREAMBLE}\ntheorem {name} {_HEADER_BINDERS}\n  : {body} :=\nsorry")

CASES = [
    ("delta_le_Delta", "δ ≤ Δ  (minimum_degree ≤ maximum_degree)",
     "(G.minDegree : ℝ) ≤ (G.maxDegree : ℝ)"),
    ("omega_le_order", "ω ≤ n  (clique_number ≤ order)",
     "(G.cliqueNum : ℝ) ≤ (G.order : ℝ)"),
    ("alpha_le_order", "α ≤ n  (independence_number ≤ order)",
     "(G.indepNum : ℝ) ≤ (G.order : ℝ)"),
]

def main():
    from pipeline.theorem_prover import NeuralProverClient
    prover = NeuralProverClient(CONFIG)
    proved = []
    for name, informal, body in CASES:
        c = Conjecture(statement=informal, inequality=None,
                       generation_method="curated", lean_statement=thm(name, body))
        log.info("[prove] %s", informal)
        r = prover.prove(c)
        if r.success:
            proved.append((informal, r))
            log.info("[prove] ✓ KERNEL-VERIFIED by %s (%.1fs)", r.model_name, r.elapsed_s or 0)
        else:
            log.info("[prove] ✗ %s", r.error)
    print("\n" + "=" * 70)
    print("KERNEL-VERIFIED: %d / %d" % (len(proved), len(CASES)))
    for informal, r in proved:
        print("-" * 70); print(informal); print(r.proof_tactics)
    return 0

if __name__ == "__main__":
    sys.exit(main())
