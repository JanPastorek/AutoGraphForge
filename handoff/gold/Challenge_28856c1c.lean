import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((((18/7) · slater) + (3/7)) < independence_number) ⇒ ¬subcubic
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 18 * GraphCalc.slaterNumber G + 3 < 7 * GraphCalc.indepNum G → ¬ GraphCalc.IsSubcubicClass G

theorem prove_28856c1c : Candidate := by
  sorry

theorem refute_28856c1c : ¬ Candidate := by
  sorry
