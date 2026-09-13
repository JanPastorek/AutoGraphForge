import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (K_4_free)) ∧ (regular)) ⇒ minimum_degree ≤ 6
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsRegularClass G → GraphCalc.IsK4FreeClass G → GraphCalc.IsNontrivialClass G → G.minDegree ≤ 6

theorem prove_ffe76e98 : Candidate := by
  sorry

theorem refute_ffe76e98 : ¬ Candidate := by
  sorry
