import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (size = ((3 · zero_forcing_number) + 6)) ⇒ connected
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.size G = 3 * GraphCalc.zeroForcingNumber G + 6 → GraphCalc.IsConnectedClass G

theorem prove_7541b759 : Candidate := by
  sorry

theorem refute_7541b759 : ¬ Candidate := by
  sorry
