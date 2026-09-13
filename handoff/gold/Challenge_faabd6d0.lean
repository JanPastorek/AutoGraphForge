import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (order < (((3/2) · independence_number) + (-1/2))) ⇒ K_4_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 2 * GraphCalc.order G + 1 < 3 * GraphCalc.indepNum G → GraphCalc.IsK4FreeClass G

theorem prove_faabd6d0 : Candidate := by
  sorry

theorem refute_faabd6d0 : ¬ Candidate := by
  sorry
