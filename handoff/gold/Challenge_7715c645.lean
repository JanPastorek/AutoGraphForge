import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (subcubic)) ⇒ total_zero_forcing_number ≤ 8
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsSubcubicClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → GraphCalc.totalZeroForcingNumber G ≤ 8

theorem prove_7715c645 : Candidate := by
  sorry

theorem refute_7715c645 : ¬ Candidate := by
  sorry
