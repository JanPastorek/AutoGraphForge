import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (slater < (((1/8) · independence_number) + (7/8))) ⇒ ¬regular
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 8 * GraphCalc.slaterNumber G < GraphCalc.indepNum G + 7 → ¬ GraphCalc.IsRegularClass G

theorem prove_421cecba : Candidate := by
  sorry

theorem refute_421cecba : ¬ Candidate := by
  sorry
