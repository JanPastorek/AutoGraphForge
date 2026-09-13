import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (triangle_free)) ⇒ clique_number ≤ 2
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsTriangleFreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.cliqueNum G ≤ 2

theorem prove_2de8718a : Candidate := by
  sorry

theorem refute_2de8718a : ¬ Candidate := by
  sorry
