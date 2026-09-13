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

lemma le_romanDominationNumber {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ)
    (h : ∀ f : V → Fin 3, GraphCalc.IsRomanDominatingFunction G f → k ≤ GraphCalc.romanWeight f) :
    k ≤ GraphCalc.romanDominationNumber G := by
  unfold GraphCalc.romanDominationNumber
  have h_ex : ∃ f : V → Fin 3, GraphCalc.IsRomanDominatingFunction G f := by
    use (fun _ => 2)
    intro v hv
    dsimp at hv
    have h_false : False := by
      revert hv
      decide
    contradiction
  rcases h_ex with ⟨f₀, hf₀⟩
  have h_mem : GraphCalc.romanWeight f₀ ∈ (Finset.univ.filter (GraphCalc.IsRomanDominatingFunction G)).image GraphCalc.romanWeight := by
    rw [Finset.mem_image]
    exact ⟨f₀, Finset.mem_filter.mpr ⟨Finset.mem_univ f₀, hf₀⟩, rfl⟩
  have h_nonempty : ((Finset.univ.filter (GraphCalc.IsRomanDominatingFunction G)).image GraphCalc.romanWeight).Nonempty :=
    ⟨GraphCalc.romanWeight f₀, h_mem⟩
  obtain ⟨m, hm⟩ := Finset.min_of_nonempty h_nonempty
  rw [hm]
  dsimp
  have hm_in := Finset.mem_of_min hm
  rw [Finset.mem_image] at hm_in
  rcases hm_in with ⟨f_min, hf_min, rfl⟩
  rw [Finset.mem_filter] at hf_min
  exact h f_min hf_min.2

lemma two_le_romanWeight {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hnt : GraphCalc.IsNontrivialClass G) (f : V → Fin 3)
    (hf : GraphCalc.IsRomanDominatingFunction G f) :
    2 ≤ GraphCalc.romanWeight f := by
  unfold GraphCalc.romanWeight
  unfold GraphCalc.IsNontrivialClass at hnt
  unfold GraphCalc.order at hnt
  by_contra hc
  have h_le1 : ∑ v : V, (f v : ℕ) ≤ 1 := by omega
  have h_no2 : ∀ v : V, (f v : ℕ) ≠ 2 := by
    intro v hv
    have h_mem := Finset.single_le_sum (fun u _ => Nat.zero_le (f u : ℕ)) (Finset.mem_univ v)
    rw [hv] at h_mem
    omega
  have h_no0 : ∀ v : V, (f v : ℕ) ≠ 0 := by
    intro v hv
    have h_f0 : f v = 0 := by
      ext
      exact hv
    obtain ⟨u, _, hu2⟩ := hf v h_f0
    have hu2_nat : (f u : ℕ) = 2 := by
      rw [hu2]
      rfl
    exact h_no2 u hu2_nat
  have h_ge1 : ∀ v : V, 1 ≤ (f v : ℕ) := by
    intro v
    have h0 := h_no0 v
    omega
  have h_sum_ge : ∑ v : V, 1 ≤ ∑ v : V, (f v : ℕ) :=
    Finset.sum_le_sum (fun v _ => h_ge1 v)
  rw [Finset.sum_const, nsmul_eq_mul, mul_one] at h_sum_ge
  rw [Finset.card_univ] at h_sum_ge
  have h2 : 2 ≤ ∑ v : V, (f v : ℕ) := hnt.trans h_sum_ge
  omega

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

lemma ballWithin_univ_or_card_ge {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (k : ℕ) :
    ballWithin G k v = Finset.univ ∨ k + 1 ≤ (ballWithin G k v).card := by
  induction k with
  | zero =>
    right
    dsimp [ballWithin]
    simp
  | succ k ih =>
    cases ih with
    | inl h_univ =>
      left
      have hsub := ballWithin_subset_succ G k v
      rw [h_univ] at hsub
      ext x
      exact ⟨fun _ => Finset.mem_univ x, fun _ => hsub (Finset.mem_univ x)⟩
    | inr h_card =>
      by_cases hne : ballWithin G k v = Finset.univ
      · left
        have hsub := ballWithin_subset_succ G k v
        rw [hne] at hsub
        ext x
        exact ⟨fun _ => Finset.mem_univ x, fun _ => hsub (Finset.mem_univ x)⟩
      · right
        have hstep := card_ballWithin_succ_of_ne_univ G k v hrad hne
        omega

lemma ballWithin_card_pred_eq_univ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hrad : GraphCalc.HasRadius G) (hnt : GraphCalc.IsNontrivialClass G) :
    ballWithin G (Fintype.card V - 1) v = Finset.univ := by
  have h := ballWithin_univ_or_card_ge G v hrad (Fintype.card V - 1)
  cases h with
  | inl h1 => exact h1
  | inr h2 =>
    unfold GraphCalc.IsNontrivialClass at hnt
    unfold GraphCalc.order at hnt
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

lemma radius_add_one_le_card {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hrad : GraphCalc.HasRadius G) (hnt : GraphCalc.IsNontrivialClass G) :
    GraphCalc.radius G + 1 ≤ Fintype.card V := by
  unfold GraphCalc.IsNontrivialClass at hnt
  unfold GraphCalc.order at hnt
  obtain ⟨v⟩ := Fintype.card_pos_iff.mp (by omega : 0 < Fintype.card V)
  have h_rad_le := radius_le_eccentricity G v
  have h_ecc_le := eccentricity_le_card_pred G v hrad hnt
  omega

lemma mem_ballWithin_of_walk {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] {v w : V} (p : G.Walk v w) :
    w ∈ ballWithin G p.length v := by
  induction p using SimpleGraph.Walk.concatRec with
  | Hnil =>
    dsimp [ballWithin]
    exact Finset.mem_singleton_self _
  | Hconcat p hadj ih =>
    rw [SimpleGraph.Walk.length_concat]
    dsimp [ballWithin]
    rw [Finset.mem_union]
    right
    rw [Finset.mem_biUnion]
    refine ⟨_, ih, ?_⟩
    rw [Finset.mem_filter]
    exact ⟨Finset.mem_univ _, hadj⟩

lemma mem_ballWithin_of_walk_le {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] {v w : V} (p : G.Walk v w) {k : ℕ} (hk : p.length ≤ k) :
    w ∈ ballWithin G k v := by
  have hmem := mem_ballWithin_of_walk G p
  obtain ⟨m, rfl⟩ := Nat.exists_eq_add_of_le hk
  exact ballWithin_subset_add G p.length m v hmem

lemma ballWithin_eq_univ_of_forall_walk {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (k : ℕ)
    (h : ∀ w : V, ∃ p : G.Walk v w, p.length ≤ k) :
    ballWithin G k v = Finset.univ := by
  ext w
  simp only [Finset.mem_univ, iff_true]
  obtain ⟨p, hp⟩ := h w
  exact mem_ballWithin_of_walk_le G p hp

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

lemma radius_add_one_le_romanWeight_of_card_le {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hrad : GraphCalc.HasRadius G) (hnt : GraphCalc.IsNontrivialClass G)
    (f : V → Fin 3) (hcard : Fintype.card V ≤ GraphCalc.romanWeight f) :
    GraphCalc.radius G + 1 ≤ GraphCalc.romanWeight f :=
  (radius_add_one_le_card G hrad hnt).trans hcard

lemma card_le_romanWeight_of_no_two {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (f : V → Fin 3) (hf : GraphCalc.IsRomanDominatingFunction G f)
    (h_no2 : ∀ v : V, (f v : ℕ) ≠ 2) :
    Fintype.card V ≤ GraphCalc.romanWeight f := by
  unfold GraphCalc.romanWeight
  have h_no0 : ∀ v : V, (f v : ℕ) ≠ 0 := by
    intro v hv
    have h_f0 : f v = 0 := by ext; exact hv
    obtain ⟨u, _, hu2⟩ := hf v h_f0
    have hu2_nat : (f u : ℕ) = 2 := by rw [hu2]; rfl
    exact h_no2 u hu2_nat
  have h_ge1 : ∀ v : V, 1 ≤ (f v : ℕ) := by
    intro v
    have h0 := h_no0 v
    omega
  have h_sum : ∑ v : V, 1 ≤ ∑ v : V, (f v : ℕ) :=
    Finset.sum_le_sum (fun v _ => h_ge1 v)
  rw [Finset.sum_const, nsmul_eq_mul, mul_one] at h_sum
  rw [Finset.card_univ] at h_sum
  exact h_sum

lemma mem_ballWithin_one_of_adj {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (c u : V) (hadj : G.Adj c u) :
    u ∈ ballWithin G 1 c :=
  mem_ballWithin_of_walk G (SimpleGraph.Walk.cons hadj SimpleGraph.Walk.nil)

lemma mem_ballWithin_one_self {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (c : V) :
    c ∈ ballWithin G 1 c :=
  ballWithin_subset_succ G 0 c (Finset.mem_singleton_self c)






