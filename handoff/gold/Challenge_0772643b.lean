import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (K_4_free)) ⇒ clique_number ≤ 3
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.cliqueNum G ≤ 3

theorem prove_0772643b : Candidate := by
  sorry

theorem refute_0772643b : ¬ Candidate := by
  sorry
