import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((nontrivial) ∧ (cograph)) ∧ (subcubic)) ⇒ annihilation_number ≤ 3
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsSubcubicClass G → GraphCalc.IsCographClass G → GraphCalc.IsNontrivialClass G → GraphCalc.annihilationNumber G ≤ 3

theorem prove_0a79fd70 : Candidate := by
  sorry

theorem refute_0a79fd70 : ¬ Candidate := by
  sorry
