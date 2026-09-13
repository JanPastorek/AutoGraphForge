import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (bipartite)) ∧ (cubic)) ⇒ 2 = clique_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsBipartiteClass G → GraphCalc.IsCubicClass G → GraphCalc.IsNontrivialClass G → 2 = GraphCalc.cliqueNum G

theorem prove_5cce7bef : Candidate := by
  sorry

theorem refute_5cce7bef : ¬ Candidate := by
  sorry
