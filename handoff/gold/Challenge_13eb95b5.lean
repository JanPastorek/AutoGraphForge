import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (K_4_free)) ∧ (claw_free)) ⇒ zero_forcing_number ≤ 7
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsK4FreeClass G → GraphCalc.IsClawFreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.zeroForcingNumber G ≤ 7

theorem prove_13eb95b5 : Candidate := by
  sorry

theorem refute_13eb95b5 : ¬ Candidate := by
  sorry
