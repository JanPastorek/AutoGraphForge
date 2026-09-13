import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ 2 ≤ sub_total_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasSubTotalDominationNumber G → 2 ≤ GraphCalc.subTotalDominationNumber G

theorem prove_8ca1b27c : Candidate := by
  sorry

theorem refute_8ca1b27c : ¬ Candidate := by
  sorry
