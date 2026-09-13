import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (subcubic)) ⇒ zero_forcing_number ≤ 8
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsSubcubicClass G → GraphCalc.IsNontrivialClass G → GraphCalc.zeroForcingNumber G ≤ 8

theorem prove_e5e4cd84 : Candidate := by
  sorry

theorem refute_e5e4cd84 : ¬ Candidate := by
  sorry
