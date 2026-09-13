import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (subcubic)) ⇒ maximum_degree ≤ 3
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsSubcubicClass G → GraphCalc.IsNontrivialClass G → G.maxDegree ≤ 3

theorem prove_92f15e08 : Candidate := by
  sorry

theorem refute_92f15e08 : ¬ Candidate := by
  sorry
