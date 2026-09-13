import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (size ≤ independence_number) ⇒ K_4_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.size G ≤ GraphCalc.indepNum G → GraphCalc.IsK4FreeClass G

theorem prove_04b443b2 : Candidate := by
  sorry

theorem refute_04b443b2 : ¬ Candidate := by
  sorry
