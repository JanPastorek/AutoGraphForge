import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ 2 ≤ total_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalDominationNumber G → 2 ≤ GraphCalc.totalDominationNumber G

theorem prove_9e476a83 : Candidate := by
  sorry

theorem refute_9e476a83 : ¬ Candidate := by
  sorry
