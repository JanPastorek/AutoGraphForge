"""Confirm the restored guard actually excludes degenerate graphs.

An earlier version of this check called a 900s TIMEOUT a rejection, which
established nothing — the same timeout/rejection conflation being fixed in the
scoring path. The crux is small and decidable, so test it directly instead of
inferring it from a whole failed refutation: if `IsNontrivialClass` is false on
the degenerate graphs, no proof can discharge the guard with them.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 600
from tools.prover_eval.w16 import is_timeout
from pipeline.theorem_prover import LeanSubprocessProver

lean = LeanSubprocessProver(CONFIG)
PRE = ("import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"
       "set_option maxRecDepth 100000\n\nopen SimpleGraph\n\n")

cases = [
    ("empty graph is NOT nontrivial",
     "example : ¬ GraphCalc.IsNontrivialClass (GraphCalc.ofEdges 0 []) := by decide"),
    ("singleton is NOT nontrivial",
     "example : ¬ GraphCalc.IsNontrivialClass (GraphCalc.ofEdges 1 []) := by decide"),
    ("a 2-vertex graph IS nontrivial (guard is not vacuous)",
     "example : GraphCalc.IsNontrivialClass (GraphCalc.ofEdges 2 [(0,1)]) := by decide"),
]
fail = 0
for name, body in cases:
    ok, log = lean._run_lean(PRE + body, audit_axioms=False)
    verdict = "PASS" if ok else ("INCONCLUSIVE (timeout)" if is_timeout(log) else "FAIL")
    print(f"{verdict:22s} {name}")
    if not ok:
        fail += 1
        print("     ", log.strip()[-200:])
print("\nGUARD EXCLUDES DEGENERATE GRAPHS" if not fail
      else f"\n{fail} case(s) unproven — guard NOT established")
sys.exit(1 if fail else 0)
