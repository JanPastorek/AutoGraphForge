import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (order ≤ ((4/3) · independence_number)) ⇒ K_4_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 3 * GraphCalc.order G ≤ 4 * GraphCalc.indepNum G → GraphCalc.IsK4FreeClass G

theorem prove_2e2fe54e : Candidate := by
  sorry

theorem refute_2e2fe54e : ¬ Candidate := by
  sorry
