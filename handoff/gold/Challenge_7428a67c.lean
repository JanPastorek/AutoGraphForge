import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((((7/9) · zero_forcing_number) + (35/9)) < annihilation_number) ⇒ ¬cograph
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 7 * GraphCalc.zeroForcingNumber G + 35 < 9 * GraphCalc.annihilationNumber G → ¬ GraphCalc.IsCographClass G

theorem prove_7428a67c : Candidate := by
  sorry

theorem refute_7428a67c : ¬ Candidate := by
  sorry
