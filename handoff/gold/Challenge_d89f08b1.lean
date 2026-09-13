import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: ((((3/2) · zero_forcing_number) + (3/2)) < annihilation_number) ⇒ ¬cograph
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → 3 * GraphCalc.zeroForcingNumber G + 3 < 2 * GraphCalc.annihilationNumber G → ¬ GraphCalc.IsCographClass G

theorem prove_d89f08b1 : Candidate := by
  sorry

theorem refute_d89f08b1 : ¬ Candidate := by
  sorry
