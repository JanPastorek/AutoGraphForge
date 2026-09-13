import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (((4/3) · maximum_degree) = total_zero_forcing_number) ⇒ K_4_free
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalZeroForcingNumber G → 4 * G.maxDegree = 3 * GraphCalc.totalZeroForcingNumber G → GraphCalc.IsK4FreeClass G

theorem prove_59f90a44 : Candidate := by
  sorry

theorem refute_59f90a44 : ¬ Candidate := by
  sorry
