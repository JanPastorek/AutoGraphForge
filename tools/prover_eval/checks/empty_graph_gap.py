"""Is the frontier 'refutation' a discovery, or a degenerate counterexample?

The conjecture was generated over graphs with order >= 2 (graffiti3 attaches a
`nontrivial` base hypothesis). The class-conditioned export carries that guard;
the necessary-condition export — hypothesis is an inequality, conclusion is a
class — does not. If so, every such exported statement is refutable by the empty
graph, on which every `forall v` class predicate is vacuously true, and the
"counterexample" says nothing about the mathematics.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 900
from pipeline.theorem_prover import LeanSubprocessProver

lean = LeanSubprocessProver(CONFIG)
PRE = ("import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"
       "set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n\n"
       "open SimpleGraph\n\n")

# Exactly the frontier challenge's Candidate.
CAND = ("abbrev Candidate : Prop :=\n"
        "    ∀ {V : Type} [Fintype V] [DecidableEq V]\n"
        "    (G : SimpleGraph V) [DecidableRel G.Adj],\n"
        "      10 * GraphCalc.annihilationNumber G ≤ 3 * GraphCalc.size G + 1 →"
        " ¬ GraphCalc.IsCubicClass G\n\n")

checks = [
 ("empty graph is cubic (vacuously)",
  "example : GraphCalc.IsCubicClass (GraphCalc.ofEdges 0 []) := by decide"),
 ("empty graph satisfies the hypothesis",
  "example : 10 * GraphCalc.annihilationNumber (GraphCalc.ofEdges 0 []) ≤ "
  "3 * GraphCalc.size (GraphCalc.ofEdges 0 []) + 1 := by decide"),
 ("=> Candidate is refuted by the EMPTY graph alone",
  CAND + "theorem t : ¬ Candidate := by\n"
         "  intro h\n"
         "  have := @h (Fin 0) _ _ (GraphCalc.ofEdges 0 []) _ (by decide)\n"
         "  revert this\n  decide"),
]
for name, body in checks:
    src = PRE + (body if body.startswith("abbrev") else body)
    ok, log = lean._run_lean(src, audit_axioms=False)
    print(f"{'YES' if ok else 'no ':4s} {name}")
    if not ok:
        print("     ", log.strip()[-200:])
