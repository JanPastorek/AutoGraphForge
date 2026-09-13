import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (size < (((3/2) · independence_number) + (-3/2))) ⇒ K_4_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 2 * GraphCalc.size G + 3 < 3 * GraphCalc.indepNum G → GraphCalc.IsK4FreeClass G

theorem prove_13fb63dd : Candidate := by
  sorry

theorem refute_13fb63dd : ¬ Candidate := by
  sorry
