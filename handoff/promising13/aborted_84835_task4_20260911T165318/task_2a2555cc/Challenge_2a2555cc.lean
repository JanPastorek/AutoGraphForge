import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ radius ≤ total_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasRadius G → GraphCalc.HasTotalDominationNumber G → GraphCalc.radius G ≤ GraphCalc.totalDominationNumber G

theorem prove_2a2555cc : Candidate := by
  sorry

theorem refute_2a2555cc : ¬ Candidate := by
  sorry
