-- prover: oprover-32b
-- statement: import Mathlib
import LeanProject.GraphInvariants

open SimpleGraph

theorem omega_le_order {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
  : (G.cliqueNum : ℝ) ≤ (G.order : ℝ) :=
sorry

import Mathlib
import LeanProject.GraphInvariants

set_option maxHeartbeats 4000000
open SimpleGraph

theorem omega_le_order {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
  : (G.cliqueNum : ℝ) ≤ (G.order : ℝ) := 
by
  have h_main : G.cliqueNum ≤ G.order := by
    have h₁ : ∃ (s : Finset V), G.IsNClique G.cliqueNum s ∧ s.card = G.cliqueNum := by
      obtain ⟨s, hs⟩ := G.exists_isNClique_cliqueNum
      refine' ⟨s, _⟩
      <;> simp_all [hs.card_eq]
      <;> aesop
    obtain ⟨s, hs_clique, hs_card⟩ := h₁
    have h₂ : s.card ≤ Fintype.card V := by
      apply Finset.card_le_univ
    have h₃ : G.cliqueNum ≤ Fintype.card V := by
      have h₄ : G.cliqueNum = s.card := by
        linarith
      rw [h₄]
      <;> linarith
    have h₄ : G.cliqueNum ≤ G.order := by
      have h₅ : G.order = Fintype.card V := rfl
      rw [h₅]
      <;> linarith
    exact h₄
  
  have h_final : (G.cliqueNum : ℝ) ≤ (G.order : ℝ) := by
    norm_cast at h_main ⊢
    <;>
    (try simp_all) <;>
    (try linarith) <;>
    (try norm_num) <;>
    (try norm_cast) <;>
    (try simp_all [Nat.cast_le]) <;>
    (try linarith)
    <;>
    (try
      {
        simpa [Nat.cast_le] using h_main
      })
    <;>
    (try
      {
        exact by
          exact_mod_cast h_main
      })
  
  exact h_final
