import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (K_4_free)) ∧ (connected)) ⇒ total_zero_forcing_number ≤ (((3/2) · annihilation_number) + 1)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsConnectedClass G → GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → 2 * GraphCalc.totalZeroForcingNumber G ≤ 3 * GraphCalc.annihilationNumber G + 2

theorem prove_912f761d : Candidate := by
  sorry

theorem refute_912f761d : ¬ Candidate := by
  sorry
