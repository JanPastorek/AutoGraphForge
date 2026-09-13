import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (connected)) ∧ (triangle_free)) ⇒ total_zero_forcing_number ≤ ((2 · maximum_degree) + 2)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsConnectedClass G → GraphCalc.IsTriangleFreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → GraphCalc.totalZeroForcingNumber G ≤ 2 * G.maxDegree + 2

theorem prove_369b0ce0 : Candidate := by
  sorry

theorem refute_369b0ce0 : ¬ Candidate := by
  sorry
