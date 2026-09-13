import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (size < (((17/8) · total_zero_forcing_number) + (-5/4))) ⇒ ¬eulerian
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → 8 * GraphCalc.size G + 10 < 17 * GraphCalc.totalZeroForcingNumber G → ¬ GraphCalc.IsEulerianClass G

theorem prove_5c492e66 : Candidate := by
  sorry

theorem refute_5c492e66 : ¬ Candidate := by
  sorry
