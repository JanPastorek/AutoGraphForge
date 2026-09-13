import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (eulerian)) ∧ (triangle_free)) ⇒ connected_zero_forcing_number ≤ ((3 · maximum_degree) + -4)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsEulerianClass G → GraphCalc.IsTriangleFreeClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → GraphCalc.connectedZeroForcingNumber G + 4 ≤ 3 * G.maxDegree

theorem prove_f9ba8f29 : Candidate := by
  sorry

theorem refute_f9ba8f29 : ¬ Candidate := by
  sorry
