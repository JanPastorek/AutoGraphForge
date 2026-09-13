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

lemma mem_ballWithin_one_of_adj {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (c u : V) (hadj : G.Adj c u) :
    u ∈ ballWithin G 1 c :=
  mem_ballWithin_of_walk G (SimpleGraph.Walk.cons hadj SimpleGraph.Walk.nil)

lemma ballWithin_subset_succ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V) :
    ballWithin G k v ⊆ ballWithin G (k + 1) v := by
  intro x hx
  dsimp [ballWithin]
  exact Finset.mem_union_left _ hx

lemma mem_ballWithin_one_self {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (c : V) :
    c ∈ ballWithin G 1 c :=
  ballWithin_subset_succ G 0 c (Finset.mem_singleton_self c)

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

lemma radius_add_one_le_romanWeight_of_unique_two {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hrad : GraphCalc.HasRadius G)
    (hnt : GraphCalc.IsNontrivialClass G)
    (f : V → Fin 3) (hf : GraphCalc.IsRomanDominatingFunction G f)
    (u : V) (hu2 : (f u : ℕ) = 2)
    (h_unique : ∀ v : V, (f v : ℕ) = 2 → v = u) :
    GraphCalc.radius G + 1 ≤ GraphCalc.romanWeight f := by
  have h_compl_subset : Finset.univ \ (ballWithin G 1 u) ⊆ Finset.univ.filter (fun v => (f v : ℕ) = 1) := by
    intro v hv
    rw [Finset.mem_sdiff] at hv
    rw [Finset.mem_filter]
    refine ⟨Finset.mem_univ v, ?_⟩
    have h_not_in := hv.2
    have h_not_self : v ≠ u := by
      intro heq
      rw [heq] at h_not_in
      exact h_not_in (mem_ballWithin_one_self G u)
    have h_not_adj : ¬ G.Adj u v := by
      intro hadj
      exact h_not_in (mem_ballWithin_one_of_adj G u v hadj)
    by_cases h0 : (f v : ℕ) = 0
    · have h0_fin : f v = 0 := by ext; exact h0
      obtain ⟨z, hz_adj, hz2⟩ := hf v h0_fin
      have hz2_nat : (f z : ℕ) = 2 := by rw [hz2]; rfl
      have hz_eq_u := h_unique z hz2_nat
      rw [hz_eq_u] at hz_adj
      exact False.elim (h_not_adj hz_adj.symm)
    · by_cases h2 : (f v : ℕ) = 2
      · have := h_unique v h2
        exact False.elim (h_not_self this)
      · omega
  have h_card_compl : (Finset.univ \ (ballWithin G 1 u)).card ≤ (Finset.univ.filter (fun v => (f v : ℕ) = 1)).card :=
    Finset.card_le_card h_compl_subset
  have h_card_split : Fintype.card V = (ballWithin G 1 u).card + (Finset.univ \ (ballWithin G 1 u)).card := by
    have h_diff : (Finset.univ \ (ballWithin G 1 u)).card = (Finset.univ : Finset V).card - ((ballWithin G 1 u) ∩ Finset.univ).card := Finset.card_sdiff
    rw [Finset.inter_univ, Finset.card_univ] at h_diff
    have h_le : (ballWithin G 1 u).card ≤ Fintype.card V := by
      have hsub : ballWithin G 1 u ⊆ Finset.univ := Finset.subset_univ _
      have hcard := Finset.card_le_card hsub
      rw [Finset.card_univ] at hcard
      exact hcard
    omega
  have h_sum_ones : (Finset.univ.filter (fun v => (f v : ℕ) = 1)).card = ∑ v ∈ Finset.univ.filter (fun v => (f v : ℕ) = 1), (f v : ℕ) := by
    have h_ones : ∑ v ∈ Finset.univ.filter (fun v => (f v : ℕ) = 1), 1 = ∑ v ∈ Finset.univ.filter (fun v => (f v : ℕ) = 1), (f v : ℕ) := by
      apply Finset.sum_congr rfl
      intro x hx
      have hx1 : (f x : ℕ) = 1 := (Finset.mem_filter.mp hx).2
      rw [hx1]
    rw [Finset.sum_const, smul_eq_mul, mul_one] at h_ones
    exact h_ones
  have h_sum_le : (Finset.univ.filter (fun v => (f v : ℕ) = 1)).card + 2 ≤ GraphCalc.romanWeight f := by
    unfold GraphCalc.romanWeight
    have hu_not_one : u ∉ Finset.univ.filter (fun v => (f v : ℕ) = 1) := by
      rw [Finset.mem_filter]
      push Not
      intro _
      omega
    have hsub : insert u (Finset.univ.filter (fun v => (f v : ℕ) = 1)) ⊆ Finset.univ := Finset.subset_univ _
    have h2sub : ∑ v ∈ insert u (Finset.univ.filter (fun v => (f v : ℕ) = 1)), (f v : ℕ) ≤ ∑ v : V, (f v : ℕ) :=
      Finset.sum_le_sum_of_subset_of_nonneg hsub (fun _ _ _ => Nat.zero_le _)
    rw [Finset.sum_insert hu_not_one, hu2] at h2sub
    rw [h_sum_ones]
    omega
  have h_card_bound : Fintype.card V ≤ (ballWithin G 1 u).card + (GraphCalc.romanWeight f - 2) := by
    omega
  have h_ball_univ := ballWithin_eq_univ_of_card_add G u hrad 1 (GraphCalc.romanWeight f - 2) h_card_bound
  have heq : 1 + (GraphCalc.romanWeight f - 2) = GraphCalc.romanWeight f - 1 := by omega
  rw [heq] at h_ball_univ
  unfold GraphCalc.IsNontrivialClass at hnt
  unfold GraphCalc.order at hnt
  have h_ecc_le : GraphCalc.eccentricity G u ≤ GraphCalc.romanWeight f - 1 := by
    by_cases h_le_n : GraphCalc.romanWeight f - 1 ≤ Fintype.card V
    · exact minUpTo_le (GraphCalc.romanWeight f - 1) h_le_n h_ball_univ
    · have hradcard := eccentricity_le_card_pred G u hrad hnt
      omega
  have h_rad_le := radius_le_eccentricity G u
  omega
