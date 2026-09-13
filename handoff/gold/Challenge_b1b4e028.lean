import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (slater < (((1/4) · independence_number) + (1/2))) ⇒ ¬claw_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 4 * GraphCalc.slaterNumber G < GraphCalc.indepNum G + 2 → ¬ GraphCalc.IsClawFreeClass G

theorem prove_b1b4e028 : Candidate := by
  sorry

theorem refute_b1b4e028 : ¬ Candidate := by
  sorry
