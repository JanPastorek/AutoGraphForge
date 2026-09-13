import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (87 < size) ⇒ ¬cubic
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 87 < GraphCalc.size G → ¬ GraphCalc.IsCubicClass G

theorem prove_bdacaed1 : Candidate := by
  sorry

theorem refute_bdacaed1 : ¬ Candidate := by
  sorry
