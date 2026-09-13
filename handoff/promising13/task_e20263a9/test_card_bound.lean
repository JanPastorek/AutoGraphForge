import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph
open GraphCalc

lemma ballWithin_subset_succ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V) :
    ballWithin G k v ⊆ ballWithin G (k + 1) v := by
  intro x hx
  dsimp [ballWithin]
  exact Finset.mem_union_left _ hx

lemma ballWithin_subset_add {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k m : ℕ) (v : V) :
    ballWithin G k v ⊆ ballWithin G (k + m) v := by
  induction m with
  | zero => exact Finset.Subset.refl _
  | succ m ih =>
    have h1 := ballWithin_subset_succ G (k + m) v
    exact Finset.Subset.trans ih h1

lemma ballWithin_succ_eq_self_implies_add {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V)
    (h : ballWithin G (k + 1) v = ballWithin G k v) (m : ℕ) :
    ballWithin G (k + m) v = ballWithin G k v := by
  induction m with
  | zero => rfl
  | succ m ih =>
    have heq : k + (m + 1) = (k + m) + 1 := by omega
    rw [heq]
    dsimp [ballWithin]
    rw [ih]
    exact h

lemma ballWithin_succ_eq_self_implies_univ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V)
    (hrad : GraphCalc.HasRadius G)
    (h : ballWithin G (k + 1) v = ballWithin G k v) :
    ballWithin G k v = Finset.univ := by
  have h_add := ballWithin_succ_eq_self_implies_add G k v h (Fintype.card V)
  have h_sub : ballWithin G (Fintype.card V) v ⊆ ballWithin G (k + Fintype.card V) v := by
    have heq : k + Fintype.card V = Fintype.card V + k := by omega
    rw [heq]
    exact ballWithin_subset_add G (Fintype.card V) k v
  rw [hrad v] at h_sub
  rw [h_add] at h_sub
  ext x
  exact ⟨fun _ => Finset.mem_univ x, fun _ => h_sub (Finset.mem_univ x)⟩

lemma card_ballWithin_succ_of_ne_univ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V)
    (hrad : GraphCalc.HasRadius G)
    (hne : ballWithin G k v ≠ Finset.univ) :
    (ballWithin G k v).card + 1 ≤ (ballWithin G (k + 1) v).card := by
  have h_not_eq : ballWithin G (k + 1) v ≠ ballWithin G k v := by
    intro heq
    exact hne (ballWithin_succ_eq_self_implies_univ G k v hrad heq)
  have h_sub := ballWithin_subset_succ G k v
  have h_ssub : ballWithin G k v ⊂ ballWithin G (k + 1) v :=
    Finset.ssubset_iff_subset_ne.mpr ⟨h_sub, h_not_eq.symm⟩
  exact Finset.card_lt_card h_ssub
