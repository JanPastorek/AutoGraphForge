import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (claw_free)) ∧ (triangle_free)) ⇒ maximum_degree ≤ (2 · minimum_degree)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsTriangleFreeClass G → GraphCalc.IsClawFreeClass G → GraphCalc.IsNontrivialClass G → G.maxDegree ≤ 2 * G.minDegree

theorem prove_37a9c9f7 : Candidate := by
  sorry

theorem refute_37a9c9f7 : ¬ Candidate := by
  sorry
