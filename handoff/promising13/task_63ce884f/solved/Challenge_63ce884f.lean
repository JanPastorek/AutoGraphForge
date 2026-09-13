import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ (roman_domination_number + 1) ≤ double_roman_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.romanDominationNumber G + 1 ≤ GraphCalc.doubleRomanDominationNumber G

theorem prove_63ce884f : Candidate := by
  sorry

theorem refute_63ce884f : ¬ Candidate := by
  sorry
