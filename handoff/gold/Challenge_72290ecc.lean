import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (cubic)) ⇒ domination_number ≤ 6
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsCubicClass G → GraphCalc.IsNontrivialClass G → GraphCalc.dominationNumber G ≤ 6

theorem prove_72290ecc : Candidate := by
  sorry

theorem refute_72290ecc : ¬ Candidate := by
  sorry
