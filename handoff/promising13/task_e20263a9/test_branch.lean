import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph
open GraphCalc

-- Let's test what Lean says about the remaining branch
theorem test_goal {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hnt : GraphCalc.IsNontrivialClass G)
    (hrad : GraphCalc.HasRadius G)
    (f : V → Fin 3)
    (hf : GraphCalc.IsRomanDominatingFunction G f)
    (h_two : 2 ≤ GraphCalc.romanWeight f)
    (h_card : GraphCalc.radius G + 1 ≤ Fintype.card V)
    (hle : ¬ Fintype.card V ≤ GraphCalc.romanWeight f)
    (hrad1 : ¬ GraphCalc.radius G ≤ 1) :
    GraphCalc.radius G + 1 ≤ GraphCalc.romanWeight f := by
  sorry
