import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (connected)) ⇒ total_zero_forcing_number ≤ (((3/2) · zero_forcing_number) + (3/2))
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsConnectedClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → 2 * GraphCalc.totalZeroForcingNumber G ≤ 3 * GraphCalc.zeroForcingNumber G + 3

theorem prove_603cb464 : Candidate := by
  sorry

theorem refute_603cb464 : ¬ Candidate := by
  sorry
