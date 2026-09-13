import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph
open GraphCalc

example {V : Type} [Fintype V] [DecidableEq V] (s : Finset V) :
    Fintype.card V = s.card + (Finset.univ \ s).card := by
  exact?

