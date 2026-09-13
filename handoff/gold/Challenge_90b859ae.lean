import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (K_4_free)) ⇒ total_zero_forcing_number ≤ (((7/4) · independence_number) + (7/4))
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → 4 * GraphCalc.totalZeroForcingNumber G ≤ 7 * GraphCalc.indepNum G + 7

theorem prove_90b859ae : Candidate := by
  sorry

theorem refute_90b859ae : ¬ Candidate := by
  sorry
