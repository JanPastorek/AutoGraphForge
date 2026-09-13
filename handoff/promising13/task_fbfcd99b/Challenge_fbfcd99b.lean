import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ sub_total_domination_number ≤ roman_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasSubTotalDominationNumber G → GraphCalc.subTotalDominationNumber G ≤ GraphCalc.romanDominationNumber G

theorem prove_fbfcd99b : Candidate := by
  sorry

theorem refute_fbfcd99b : ¬ Candidate := by
  sorry
