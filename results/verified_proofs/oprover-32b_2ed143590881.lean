-- prover: oprover-32b
-- statement: import Mathlib
import LeanProject.GraphInvariants

open SimpleGraph

theorem delta_le_Delta {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
  : (G.minDegree : ℝ) ≤ (G.maxDegree : ℝ) :=
sorry

import Mathlib
import LeanProject.GraphInvariants

set_option maxHeartbeats 4000000
open SimpleGraph

theorem delta_le_Delta {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
  : (G.minDegree : ℝ) ≤ (G.maxDegree : ℝ) := 
by
  have h_main : G.minDegree ≤ G.maxDegree := by
    apply SimpleGraph.minDegree_le_maxDegree
  
  have h_final : (G.minDegree : ℝ) ≤ (G.maxDegree : ℝ) := by
    norm_cast at h_main ⊢
    <;>
    (try simp_all) <;>
    (try linarith) <;>
    (try norm_num) <;>
    (try omega)
    <;>
    (try
      {
        simp_all [Nat.cast_le]
        <;>
        linarith
      })
  
  exact h_final
