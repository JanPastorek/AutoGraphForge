import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ total_domination_number ≤ roman_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalDominationNumber G → GraphCalc.totalDominationNumber G ≤ GraphCalc.romanDominationNumber G

lemma minCard_le {V : Type*} [Fintype V] [DecidableEq V] {p : Finset V → Prop} [DecidablePred p] {s : Finset V} (hs : p s) :
    GraphCalc.minCard p ≤ s.card := by
  unfold GraphCalc.minCard
  have hm : s.card ∈ (Finset.univ.powerset.filter p).image Finset.card := by
    rw [Finset.mem_image]
    refine ⟨s, ?_, rfl⟩
    rw [Finset.mem_filter]
    exact ⟨Finset.mem_powerset.mpr (Finset.subset_univ s), hs⟩
  obtain ⟨a, ha⟩ := Finset.min_of_mem hm
  have hle : a ≤ s.card := Finset.min_le_of_eq hm ha
  have hget : ((Finset.univ.powerset.filter p).image Finset.card).min.getD 0 = a := by
    rw [ha]
    rfl
  rw [hget]
  exact hle

lemma exists_min_roman_dominating_function {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∃ f : V → Fin 3, GraphCalc.IsRomanDominatingFunction G f ∧
      GraphCalc.romanWeight f = GraphCalc.romanDominationNumber G := by
  let f_two : V → Fin 3 := fun _ => ⟨2, by decide⟩
  have hf_two : GraphCalc.IsRomanDominatingFunction G f_two := by
    intro v hv
    change (⟨2, by decide⟩ : Fin 3) = 0 at hv
    have hne : (⟨2, by decide⟩ : Fin 3) ≠ 0 := by decide
    exact False.elim (hne hv)
  have h_nonempty : ((Finset.univ.filter (GraphCalc.IsRomanDominatingFunction G)).image
      GraphCalc.romanWeight).Nonempty := by
    refine ⟨GraphCalc.romanWeight f_two, ?_⟩
    rw [Finset.mem_image]
    refine ⟨f_two, ?_, rfl⟩
    rw [Finset.mem_filter]
    exact ⟨Finset.mem_univ _, hf_two⟩
  obtain ⟨m, hm⟩ := Finset.min_of_nonempty h_nonempty
  have hmem : m ∈ (Finset.univ.filter (GraphCalc.IsRomanDominatingFunction G)).image
      GraphCalc.romanWeight := Finset.mem_of_min hm
  rw [Finset.mem_image] at hmem
  obtain ⟨f, hf_filt, hfw⟩ := hmem
  rw [Finset.mem_filter] at hf_filt
  refine ⟨f, hf_filt.2, ?_⟩
  unfold GraphCalc.romanDominationNumber
  have hget : (((Finset.univ.filter (GraphCalc.IsRomanDominatingFunction G)).image
      GraphCalc.romanWeight).min).getD 0 = m := by
    rw [hm]
    rfl
  rw [hget, hfw]

lemma exists_adj_of_hasTotalDominationNumber {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (h : GraphCalc.HasTotalDominationNumber G) (v : V) :
    ∃ u : V, G.Adj v u := by
  unfold GraphCalc.HasTotalDominationNumber GraphCalc.HasWitness at h
  obtain ⟨s, _, hs⟩ := h
  unfold GraphCalc.IsTotalDominatingSet at hs
  obtain ⟨u, _, hu⟩ := hs v
  exact ⟨u, hu⟩

lemma sum_le_romanWeight {V : Type*} [Fintype V] [DecidableEq V] (f : V → Fin 3) :
    (Finset.univ.filter (fun v => f v = 1)).card +
    2 * (Finset.univ.filter (fun v => f v = 2)).card ≤ GraphCalc.romanWeight f := by
  unfold GraphCalc.romanWeight
  let V1 := Finset.univ.filter (fun v => f v = 1)
  let V2 := Finset.univ.filter (fun v => f v = 2)
  have hdisj : Disjoint V1 V2 := by
    rw [Finset.disjoint_filter]
    intro x _ h1 h2
    have h12 : (1 : Fin 3) = (2 : Fin 3) := h1.symm.trans h2
    revert h12
    decide
  have h1 : ∑ v ∈ V1, (f v : ℕ) = V1.card := by
    have : ∀ v ∈ V1, (f v : ℕ) = 1 := by
      intro v hv
      rw [Finset.mem_filter] at hv
      rw [hv.2]
      rfl
    calc
      ∑ v ∈ V1, (f v : ℕ) = ∑ v ∈ V1, 1 := Finset.sum_congr rfl this
      _ = V1.card := by simp
  have h2 : ∑ v ∈ V2, (f v : ℕ) = 2 * V2.card := by
    have : ∀ v ∈ V2, (f v : ℕ) = 2 := by
      intro v hv
      rw [Finset.mem_filter] at hv
      rw [hv.2]
      rfl
    calc
      ∑ v ∈ V2, (f v : ℕ) = ∑ v ∈ V2, 2 := Finset.sum_congr rfl this
      _ = 2 * V2.card := by simp [mul_comm]
  have hsub : V1 ∪ V2 ⊆ Finset.univ := Finset.subset_univ _
  have h_le : ∑ v ∈ V1 ∪ V2, (f v : ℕ) ≤ ∑ v ∈ (Finset.univ : Finset V), (f v : ℕ) :=
    Finset.sum_le_sum_of_subset_of_nonneg hsub (fun _ _ _ => Nat.zero_le _)
  rw [Finset.sum_union hdisj, h1, h2] at h_le
  exact h_le

theorem totalDom_le_romanDom {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (h_td : GraphCalc.HasTotalDominationNumber G) :
    GraphCalc.totalDominationNumber G ≤ GraphCalc.romanDominationNumber G := by
  obtain ⟨f, hf, hf_weight⟩ := exists_min_roman_dominating_function G
  let V1 : Finset V := Finset.univ.filter (fun v => f v = 1)
  let V2 : Finset V := Finset.univ.filter (fun v => f v = 2)
  let X : Finset V := Finset.univ.filter (fun u => ∀ w ∈ V2, ¬ G.Adj u w)
  have hX_sub : X ⊆ V1 ∪ V2 := by
    intro u hu
    rw [Finset.mem_filter] at hu
    rw [Finset.mem_union, Finset.mem_filter, Finset.mem_filter]
    match hfu : f u with
    | 0 =>
      exfalso
      obtain ⟨w, hw_adj, hw2⟩ := hf u hfu
      have hw_in_V2 : w ∈ V2 := by
        rw [Finset.mem_filter]
        exact ⟨Finset.mem_univ _, hw2⟩
      exact hu.2 w hw_in_V2 hw_adj
    | 1 =>
      left; exact ⟨Finset.mem_univ _, rfl⟩
    | 2 =>
      right; exact ⟨Finset.mem_univ _, rfl⟩
  have hX_card : X.card ≤ V1.card + V2.card := by
    calc
      X.card ≤ (V1 ∪ V2).card := Finset.card_le_card hX_sub
      _ ≤ V1.card + V2.card := Finset.card_union_le V1 V2
  have hnbr : ∀ v : V, ∃ u : V, G.Adj v u :=
    exists_adj_of_hasTotalDominationNumber G h_td
  let nbr : V → V := fun v => Classical.choose (hnbr v)
  have hnbr_adj : ∀ v : V, G.Adj v (nbr v) := fun v => Classical.choose_spec (hnbr v)
  let S : Finset V := V2 ∪ (X.image nbr)
  have hS_card : S.card ≤ V1.card + 2 * V2.card := by
    change (V2 ∪ (X.image nbr)).card ≤ V1.card + 2 * V2.card
    have h1 := Finset.card_union_le V2 (X.image nbr)
    have h2 := Finset.card_image_le (f := nbr) (s := X)
    omega
  have hS_dom : GraphCalc.IsTotalDominatingSet G S := by
    unfold GraphCalc.IsTotalDominatingSet
    intro v
    by_cases hvX : v ∈ X
    · refine ⟨nbr v, ?_, hnbr_adj v⟩
      rw [Finset.mem_union]
      right
      rw [Finset.mem_image]
      exact ⟨v, hvX, rfl⟩
    · have h_exists : ∃ w ∈ V2, G.Adj v w := by
        by_contra h
        apply hvX
        rw [Finset.mem_filter]
        refine ⟨Finset.mem_univ v, ?_⟩
        intro w hw hadj
        exact h ⟨w, hw, hadj⟩
      obtain ⟨w, hw_in_V2, hw_adj⟩ := h_exists
      refine ⟨w, ?_, hw_adj⟩
      rw [Finset.mem_union]
      left
      exact hw_in_V2
  have h_td_le_card : GraphCalc.totalDominationNumber G ≤ S.card :=
    minCard_le hS_dom
  calc
    GraphCalc.totalDominationNumber G ≤ S.card := h_td_le_card
    _ ≤ V1.card + 2 * V2.card := hS_card
    _ ≤ GraphCalc.romanWeight f := sum_le_romanWeight f
    _ = GraphCalc.romanDominationNumber G := hf_weight

theorem prove_40a99333 : Candidate := by
  intro V _ _ G _ _ h_td
  exact totalDom_le_romanDom G h_td

theorem refute_40a99333 : ¬ Candidate := by
  sorry
