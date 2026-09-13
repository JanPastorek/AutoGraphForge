import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (annihilation_number < (((7/5) · independent_domination_number) + (-4/5))) ⇒ ¬tree
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 5 * GraphCalc.annihilationNumber G + 4 < 7 * GraphCalc.independentDominationNumber G → ¬ GraphCalc.IsTreeClass G

theorem prove_1ea0da8b : Candidate := by
  sorry

theorem refute_1ea0da8b : ¬ Candidate := by
  sorry
