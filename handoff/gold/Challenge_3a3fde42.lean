import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (zero_forcing_number < (connected_zero_forcing_number + -1)) ⇒ ¬eulerian
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → GraphCalc.zeroForcingNumber G + 1 < GraphCalc.connectedZeroForcingNumber G → ¬ GraphCalc.IsEulerianClass G

theorem prove_3a3fde42 : Candidate := by
  sorry

theorem refute_3a3fde42 : ¬ Candidate := by
  sorry
