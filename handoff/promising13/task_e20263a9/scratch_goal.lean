import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph
open GraphCalc

lemma minUpTo_le {n : ℕ} {p : ℕ → Prop} [DecidablePred p] (k : ℕ) (hk : k ≤ n) (hp : p k) :
    minUpTo n p ≤ k := by
  unfold minUpTo
  have hmem : k ∈ (Finset.range (n + 1)).filter p := by
    rw [Finset.mem_filter, Finset.mem_range]
    exact ⟨Nat.lt_succ_of_le hk, hp⟩
  have hmin := Finset.min_le hmem
  generalize hmin_eq : ((Finset.range (n + 1)).filter p).min = m
  rw [hmin_eq] at hmin
  cases m with
  | top => contradiction
  | coe val =>
    simp only [WithTop.coe_le_coe] at hmin
    exact hmin

theorem radius_le_eccentricity {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    GraphCalc.radius G ≤ GraphCalc.eccentricity G v := by
  unfold GraphCalc.radius
  have hmem : GraphCalc.eccentricity G v ∈ Finset.image (GraphCalc.eccentricity G) Finset.univ := by
    apply Finset.mem_image_of_mem
    exact Finset.mem_univ v
  obtain ⟨b, hb⟩ := Finset.min_of_mem hmem
  rw [hb]
  have hle : (Finset.image (GraphCalc.eccentricity G) Finset.univ).min ≤ ↑(GraphCalc.eccentricity G v) :=
    Finset.min_le hmem
  rw [hb] at hle
  exact WithTop.coe_le_coe.mp hle

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
  have h_ne_self : ballWithin G (k + 1) v ≠ ballWithin G k v := by
    intro h_eq
    have h_univ := ballWithin_succ_eq_self_implies_univ G k v hrad h_eq
    exact hne h_univ
  have h_sub := ballWithin_subset_succ G k v
  have h_ssub : ballWithin G k v ⊂ ballWithin G (k + 1) v :=
    Finset.ssubset_iff_subset_ne.mpr ⟨h_sub, Ne.symm h_ne_self⟩
  exact Finset.card_lt_card h_ssub

lemma card_ballWithin_add {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (k m : ℕ) :
    ballWithin G (k + m) v = Finset.univ ∨ (ballWithin G k v).card + m ≤ (ballWithin G (k + m) v).card := by
  induction m with
  | zero => right; simp only [add_zero]; exact le_rfl
  | succ m ih =>
    cases ih with
    | inl h_univ =>
      left
      have hsub := ballWithin_subset_succ G (k + m) v
      rw [h_univ] at hsub
      ext x
      exact ⟨fun _ => Finset.mem_univ x, fun _ => hsub (Finset.mem_univ x)⟩
    | inr h_card =>
      by_cases hne : ballWithin G (k + m) v = Finset.univ
      · left
        have hsub := ballWithin_subset_succ G (k + m) v
        rw [hne] at hsub
        ext x
        exact ⟨fun _ => Finset.mem_univ x, fun _ => hsub (Finset.mem_univ x)⟩
      · right
        have heq : k + (m + 1) = (k + m) + 1 := by omega
        rw [heq]
        have hstep := card_ballWithin_succ_of_ne_univ G (k + m) v hrad hne
        omega

lemma ballWithin_eq_univ_of_card_add {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (k m : ℕ)
    (h : Fintype.card V ≤ (ballWithin G k v).card + m) :
    ballWithin G (k + m) v = Finset.univ := by
  have h_cases := card_ballWithin_add G v hrad k m
  cases h_cases with
  | inl h_univ => exact h_univ
  | inr h_card =>
    by_contra hc
    have h_ssub : ballWithin G (k + m) v ⊂ Finset.univ := Finset.ssubset_univ_iff.mpr hc
    have h_lt := Finset.card_lt_card h_ssub
    rw [Finset.card_univ] at h_lt
    omega

lemma ballWithin_univ_or_card_ge {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (k : ℕ) :
    ballWithin G k v = Finset.univ ∨ k + 1 ≤ (ballWithin G k v).card := by
  have h_add := card_ballWithin_add G v hrad 0 k
  have heq : 0 + k = k := by omega
  rw [heq] at h_add
  cases h_add with
  | inl h_univ => left; exact h_univ
  | inr h_card =>
    right
    have h0 : (ballWithin G 0 v).card = 1 := by
      dsimp [ballWithin]
      exact Finset.card_singleton v
    omega

lemma ballWithin_card_pred_eq_univ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (hnt : GraphCalc.IsNontrivialClass G) :
    ballWithin G (Fintype.card V - 1) v = Finset.univ := by
  unfold GraphCalc.IsNontrivialClass at hnt
  unfold GraphCalc.order at hnt
  have h_cases := ballWithin_univ_or_card_ge G v hrad (Fintype.card V - 1)
  cases h_cases with
  | inl h_univ => exact h_univ
  | inr h_card =>
    have h2 : (Fintype.card V - 1) + 1 ≤ (ballWithin G (Fintype.card V - 1) v).card := h_card
    have h_card_eq : (Fintype.card V - 1) + 1 = Fintype.card V := by omega
    rw [h_card_eq] at h2
    by_contra hc
    have h_ssub : ballWithin G (Fintype.card V - 1) v ⊂ Finset.univ :=
      Finset.ssubset_univ_iff.mpr hc
    have h_lt := Finset.card_lt_card h_ssub
    rw [Finset.card_univ] at h_lt
    omega

lemma eccentricity_le_card_pred {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (hnt : GraphCalc.IsNontrivialClass G) :
    GraphCalc.eccentricity G v ≤ Fintype.card V - 1 := by
  unfold GraphCalc.eccentricity
  unfold GraphCalc.IsNontrivialClass at hnt
  unfold GraphCalc.order at hnt
  apply minUpTo_le (Fintype.card V - 1) (by omega) (ballWithin_card_pred_eq_univ G v hrad hnt)

lemma radius_add_one_le_of_card_compl {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hrad : GraphCalc.HasRadius G) (hnt : GraphCalc.IsNontrivialClass G)
    (v : V) (k : ℕ) (W : ℕ)
    (h : k + (Finset.univ \ ballWithin G k v).card + 1 ≤ W) :
    GraphCalc.radius G + 1 ≤ W := by
  have h_split : Fintype.card V ≤ (ballWithin G k v).card + (Finset.univ \ ballWithin G k v).card := by
    have h_diff : (Finset.univ \ ballWithin G k v).card = (Finset.univ : Finset V).card - (ballWithin G k v ∩ Finset.univ).card := Finset.card_sdiff
    rw [Finset.inter_univ, Finset.card_univ] at h_diff
    have hsub : ballWithin G k v ⊆ Finset.univ := Finset.subset_univ _
    have hcard := Finset.card_le_card hsub
    rw [Finset.card_univ] at hcard
    omega
  have h_univ := ballWithin_eq_univ_of_card_add G v hrad k (Finset.univ \ ballWithin G k v).card h_split
  have hecc : GraphCalc.eccentricity G v ≤ k + (Finset.univ \ ballWithin G k v).card := by
    by_cases h_le : k + (Finset.univ \ ballWithin G k v).card ≤ Fintype.card V
    · exact minUpTo_le (k + (Finset.univ \ ballWithin G k v).card) h_le h_univ
    · have hpred := eccentricity_le_card_pred G v hrad hnt
      omega
  have hrad_le := radius_le_eccentricity G v
  omega
