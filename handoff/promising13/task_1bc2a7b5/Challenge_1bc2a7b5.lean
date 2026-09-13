import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ ((1/2) · sub_total_domination_number) ≤ slater
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasSubTotalDominationNumber G → GraphCalc.subTotalDominationNumber G ≤ 2 * GraphCalc.slaterNumber G

theorem prove_1bc2a7b5 : Candidate := by
  sorry

theorem refute_1bc2a7b5 : ¬ Candidate := by
  sorry
