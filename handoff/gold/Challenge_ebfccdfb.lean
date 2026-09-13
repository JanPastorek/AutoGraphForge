import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (cograph)) ⇒ connected_zero_forcing_number ≤ (((1/2) · maximum_degree) + 7)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsCographClass G → GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → 2 * GraphCalc.connectedZeroForcingNumber G ≤ G.maxDegree + 14

theorem prove_ebfccdfb : Candidate := by
  sorry

theorem refute_ebfccdfb : ¬ Candidate := by
  sorry
