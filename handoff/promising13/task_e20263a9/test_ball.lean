import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph
open GraphCalc

lemma self_mem_ballWithin {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V) :
    v ∈ ballWithin G k v := by
  induction k with
  | zero =>
    dsimp [ballWithin]
    exact Finset.mem_singleton_self v
  | succ k ih =>
    dsimp [ballWithin]
    exact Finset.mem_union_left _ ih

lemma ballWithin_subset_succ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V) :
    ballWithin G k v ⊆ ballWithin G (k + 1) v := by
  intro x hx
  dsimp [ballWithin]
  exact Finset.mem_union_left _ hx

lemma adj_mem_ballWithin_succ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v u w : V)
    (hu : u ∈ ballWithin G k v) (hadj : G.Adj u w) :
    w ∈ ballWithin G (k + 1) v := by
  dsimp [ballWithin]
  apply Finset.mem_union_right
  rw [Finset.mem_biUnion]
  use u
  refine ⟨hu, ?_⟩
  rw [Finset.mem_filter]
  exact ⟨Finset.mem_univ w, hadj⟩

lemma ballWithin_trans {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k m : ℕ) (v u w : V)
    (hu : u ∈ ballWithin G k v) (hw : w ∈ ballWithin G m u) :
    w ∈ ballWithin G (k + m) v := by
  induction m generalizing w with
  | zero =>
    dsimp [ballWithin] at hw
    rw [Finset.mem_singleton.mp hw]
    exact hu
  | succ m ih =>
    dsimp [ballWithin] at hw
    rw [Finset.mem_union] at hw
    cases hw with
    | inl hw1 =>
      have h1 := ih w hw1
      have hsub := ballWithin_subset_succ G (k + m) v
      exact hsub h1
    | inr hw2 =>
      rw [Finset.mem_biUnion] at hw2
      rcases hw2 with ⟨z, hz, hz2⟩
      rw [Finset.mem_filter] at hz2
      have hz_in : z ∈ ballWithin G (k + m) v := ih z hz
      have := adj_mem_ballWithin_succ G (k + m) v z w hz_in hz2.2
      have heq : k + (m + 1) = (k + m) + 1 := by omega
      rw [heq]
      exact this
