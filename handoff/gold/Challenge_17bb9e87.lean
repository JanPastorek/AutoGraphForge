import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (K_4_free)) ∧ (regular)) ⇒ connected_zero_forcing_number ≤ 10
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsRegularClass G → GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → GraphCalc.connectedZeroForcingNumber G ≤ 10

theorem prove_17bb9e87 : Candidate := by
  sorry

theorem refute_17bb9e87 : ¬ Candidate := by
  sorry
