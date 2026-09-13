import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((((9/14) · annihilation_number) + (17/14)) < independent_domination_number) ⇒ ¬tree
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 9 * GraphCalc.annihilationNumber G + 17 < 14 * GraphCalc.independentDominationNumber G → ¬ GraphCalc.IsTreeClass G

theorem prove_f894ab15 : Candidate := by
  sorry

theorem refute_f894ab15 : ¬ Candidate := by
  sorry
