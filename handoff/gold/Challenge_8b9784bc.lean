import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (order = (3 · independence_number)) ⇒ ¬triangle_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.order G = 3 * GraphCalc.indepNum G → ¬ GraphCalc.IsTriangleFreeClass G

theorem prove_8b9784bc : Candidate := by
  sorry

theorem refute_8b9784bc : ¬ Candidate := by
  sorry
