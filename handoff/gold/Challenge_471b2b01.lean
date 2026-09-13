import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ domination_number ≤ independent_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.dominationNumber G ≤ GraphCalc.independentDominationNumber G

theorem prove_471b2b01 : Candidate := by
  sorry

theorem refute_471b2b01 : ¬ Candidate := by
  sorry
