import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (cubic)) ⇒ slater ≤ 5
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsCubicClass G → GraphCalc.IsNontrivialClass G → GraphCalc.slaterNumber G ≤ 5

theorem prove_16f4763d : Candidate := by
  sorry

theorem refute_16f4763d : ¬ Candidate := by
  sorry
