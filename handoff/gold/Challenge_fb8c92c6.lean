import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (size < annihilation_number) ⇒ K_4_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.size G < GraphCalc.annihilationNumber G → GraphCalc.IsK4FreeClass G

theorem prove_fb8c92c6 : Candidate := by
  sorry

theorem refute_fb8c92c6 : ¬ Candidate := by
  sorry
