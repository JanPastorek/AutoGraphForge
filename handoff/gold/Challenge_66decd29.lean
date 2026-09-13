import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (87 < size) ⇒ ¬subcubic
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 87 < GraphCalc.size G → ¬ GraphCalc.IsSubcubicClass G

theorem prove_66decd29 : Candidate := by
  sorry

theorem refute_66decd29 : ¬ Candidate := by
  sorry
