import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (order < (3 · slater)) ⇒ subcubic
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.order G < 3 * GraphCalc.slaterNumber G → GraphCalc.IsSubcubicClass G

theorem prove_1bc29ecb : Candidate := by
  sorry

theorem refute_1bc29ecb : ¬ Candidate := by
  sorry
