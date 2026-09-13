import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ independence_number ≤ edge_cover_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasEdgeCover G → GraphCalc.indepNum G ≤ GraphCalc.edgeCoverNumber G

lemma sym2_eq_of_ne_mem {V : Type*} [DecidableEq V] (u v : V) (e : Sym2 V)
    (hu : u ∈ e) (hv : v ∈ e) (hne : u ≠ v) : e = s(u, v) := by
  induction e using Sym2.inductionOn with
  | hf a b =>
    rw [Sym2.mem_iff] at hu hv
    rcases hu with rfl | rfl <;> rcases hv with rfl | rfl
    · contradiction
    · rfl
    · exact Sym2.eq_swap
    · contradiction

lemma indep_card_le_edge_cover_card {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (I : Finset V) (hI : GraphCalc.IsIndependentFinset G I)
    (s : Finset (Sym2 V)) (hs_sub : s ⊆ G.edgeFinset) (hs_cov : GraphCalc.IsEdgeCoverFinset G s) :
    I.card ≤ s.card := by
  let f : V → Sym2 V := fun v => Classical.choose (hs_cov v)
  have hf_spec : ∀ v, f v ∈ s ∧ v ∈ f v := fun v => Classical.choose_spec (hs_cov v)
  have hmaps : Set.MapsTo f (↑I) (↑s) := by
    intro v _
    exact (hf_spec v).1
  have hinj : Set.InjOn f (↑I) := by
    intro u hu v hv heq
    by_contra hne
    have hu_e : u ∈ f u := (hf_spec u).2
    have hv_e : v ∈ f u := by rw [heq]; exact (hf_spec v).2
    have he_eq : f u = s(u, v) := sym2_eq_of_ne_mem u v (f u) hu_e hv_e hne
    have he_in_s : f u ∈ s := (hf_spec u).1
    have he_in_edges : f u ∈ G.edgeFinset := hs_sub he_in_s
    rw [SimpleGraph.mem_edgeFinset] at he_in_edges
    rw [he_eq] at he_in_edges
    rw [SimpleGraph.mem_edgeSet] at he_in_edges
    have h_not_adj : ¬ G.Adj u v := hI u hu v hv
    exact h_not_adj he_in_edges
  exact Finset.card_le_card_of_injOn f hmaps hinj

theorem prove_1facfd37 : Candidate := by
  intro V _ _ G _ _ _
  dsimp [GraphCalc.indepNum, GraphCalc.edgeCoverNumber, GraphCalc.minUpTo]
  cases hmax : ((Finset.univ.powerset.filter (GraphCalc.IsIndependentFinset G)).image Finset.card).max with
  | bot =>
    exact Nat.zero_le _
  | coe alpha =>
    change alpha ≤ Option.getD (((Finset.range (Fintype.card V + 1)).filter
      (fun k => ∃ s ∈ G.edgeFinset.powersetCard k, GraphCalc.IsEdgeCoverFinset G s)).min) (Fintype.card V)
    have h_alpha_mem : alpha ∈ ((Finset.univ.powerset.filter (GraphCalc.IsIndependentFinset G)).image Finset.card) :=
      Finset.mem_of_max hmax
    rw [Finset.mem_image] at h_alpha_mem
    rcases h_alpha_mem with ⟨I, hI, hI_card⟩
    rw [Finset.mem_filter] at hI
    have hI_indep : GraphCalc.IsIndependentFinset G I := hI.2
    cases hmin : (((Finset.range (Fintype.card V + 1)).filter
      (fun k => ∃ s ∈ G.edgeFinset.powersetCard k, GraphCalc.IsEdgeCoverFinset G s)).min) with
    | top =>
      change alpha ≤ Fintype.card V
      subst hI_card
      exact Finset.card_le_univ I
    | coe rho =>
      change alpha ≤ rho
      have h_rho_mem : rho ∈ (((Finset.range (Fintype.card V + 1)).filter
        (fun k => ∃ s ∈ G.edgeFinset.powersetCard k, GraphCalc.IsEdgeCoverFinset G s))) :=
        Finset.mem_of_min hmin
      rw [Finset.mem_filter] at h_rho_mem
      rcases h_rho_mem.2 with ⟨s, hs_pow, hs_cov⟩
      rw [Finset.mem_powersetCard] at hs_pow
      have hs_sub : s ⊆ G.edgeFinset := hs_pow.1
      have hs_card : s.card = rho := hs_pow.2
      have h_le := indep_card_le_edge_cover_card G I hI_indep s hs_sub hs_cov
      rw [hI_card, hs_card] at h_le
      exact h_le

theorem refute_1facfd37 : ¬ Candidate := by
  sorry

