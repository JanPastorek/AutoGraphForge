"""Both guards must actually block the degenerate escapes, not merely appear.

Two defects produced four fake "resolutions": statements refutable on `Fin 0`
(where every `forall v` class predicate is vacuously true), and statements where
`minCard` returned 0 for an invariant with no witness. The fix is only real if
those two moves now fail — so assert the crux of each directly, and require the
guards to be non-vacuous on a graph that should satisfy them.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 1200
from tools.prover_eval.w16 import is_timeout
from pipeline.theorem_prover import LeanSubprocessProver

lean = LeanSubprocessProver(CONFIG)
PRE = ("import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"
       "set_option maxRecDepth 100000\n\nopen SimpleGraph\n\n")
P3 = "(GraphCalc.ofEdges 3 [(0,1),(1,2)])"        # path, connected
D4 = "(GraphCalc.ofEdges 4 [(0,1)])"              # two isolated vertices

cases = [
 ("empty graph blocked by nontrivial",
  f"example : ¬ GraphCalc.IsNontrivialClass (GraphCalc.ofEdges 0 []) := by decide"),
 ("singleton blocked by nontrivial",
  f"example : ¬ GraphCalc.IsNontrivialClass (GraphCalc.ofEdges 1 []) := by decide"),
 ("guard NOT vacuous: P3 is nontrivial",
  f"example : GraphCalc.IsNontrivialClass {P3} := by decide"),
 ("disconnected graph blocked by Z_c definedness",
  f"example : ¬ GraphCalc.HasConnectedZeroForcingNumber {D4} := by decide"),
 ("definedness NOT vacuous: P3 has a connected ZF set",
  f"example : GraphCalc.HasConnectedZeroForcingNumber {P3} := by decide"),
]
fail = 0
for name, body in cases:
    ok, log = lean._run_lean(PRE + body, audit_axioms=False)
    verdict = "PASS" if ok else ("INCONCLUSIVE (timeout)" if is_timeout(log) else "FAIL")
    print(f"{verdict:22s} {name}")
    if not ok:
        fail += 1
        print("     ", log.strip()[-200:])
print("\nBOTH GUARDS HOLD AND ARE NON-VACUOUS" if not fail
      else f"\n{fail} case(s) unproven — do not resubmit")
sys.exit(1 if fail else 0)
