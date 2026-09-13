import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (K_4_free)) ⇒ connected_zero_forcing_number ≤ (((5/2) · independence_number) + (-1/2))
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → 2 * GraphCalc.connectedZeroForcingNumber G + 1 ≤ 5 * GraphCalc.indepNum G

theorem prove_e2a73c47 : Candidate := by
  sorry

theorem refute_e2a73c47 : ¬ Candidate := by
  sorry
