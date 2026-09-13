import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (K_4_free)) ⇒ zero_forcing_number ≤ (((3/2) · annihilation_number) + 1)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → 2 * GraphCalc.zeroForcingNumber G ≤ 3 * GraphCalc.annihilationNumber G + 2

theorem prove_f4213d91 : Candidate := by
  sorry

theorem refute_f4213d91 : ¬ Candidate := by
  sorry
