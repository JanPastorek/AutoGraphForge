import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (claw_free)) ∧ (cograph)) ⇒ connected_zero_forcing_number ≤ ((6/5) · maximum_degree)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsClawFreeClass G → GraphCalc.IsCographClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → 5 * GraphCalc.connectedZeroForcingNumber G ≤ 6 * G.maxDegree

theorem prove_32d69c46 : Candidate := by
  sorry

theorem refute_32d69c46 : ¬ Candidate := by
  sorry
