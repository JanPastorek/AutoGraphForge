import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (slater = (((2/5) · independence_number) + (-1/5))) ⇒ ¬claw_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 5 * GraphCalc.slaterNumber G + 1 = 2 * GraphCalc.indepNum G → ¬ GraphCalc.IsClawFreeClass G

theorem prove_408b44c1 : Candidate := by
  sorry

theorem refute_408b44c1 : ¬ Candidate := by
  sorry
