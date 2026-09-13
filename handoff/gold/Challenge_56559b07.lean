import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((((8/17) · size) + (10/17)) < connected_zero_forcing_number) ⇒ ¬eulerian
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasConnectedZeroForcingNumber G → 8 * GraphCalc.size G + 10 < 17 * GraphCalc.connectedZeroForcingNumber G → ¬ GraphCalc.IsEulerianClass G

theorem prove_56559b07 : Candidate := by
  sorry

theorem refute_56559b07 : ¬ Candidate := by
  sorry
