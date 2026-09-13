import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((nontrivial) ∧ (regular)) ⇒ maximum_degree = minimum_degree
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsRegularClass G → GraphCalc.IsNontrivialClass G → G.maxDegree = G.minDegree

theorem prove_b2c2702c : Candidate := by
  sorry

theorem refute_b2c2702c : ¬ Candidate := by
  sorry
