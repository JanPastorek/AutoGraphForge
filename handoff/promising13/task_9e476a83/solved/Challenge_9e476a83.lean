import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ 2 ≤ total_domination_number
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasTotalDominationNumber G → 2 ≤ GraphCalc.totalDominationNumber G

theorem card_ge_two_of_totalDominatingSet {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hnt : GraphCalc.IsNontrivialClass G)
    (s : Finset V) (hs : GraphCalc.IsTotalDominatingSet G s) :
    2 ≤ s.card := by
  by_contra h
  interval_cases hc : s.card
  · rw [Finset.card_eq_zero] at hc
    subst hc
    have hcard : 2 ≤ Fintype.card V := hnt
    have : Nonempty V := Fintype.card_pos_iff.mp (by omega)
    rcases this with ⟨v⟩
    rcases hs v with ⟨u, hu, _⟩
    exact Finset.notMem_empty u hu
  · rcases Finset.card_eq_one.mp hc with ⟨x, rfl⟩
    rcases hs x with ⟨u, hu, hadj⟩
    simp only [Finset.mem_singleton] at hu
    subst hu
    exact G.irrefl hadj

theorem totalDominationNumber_ge_two {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hnt : GraphCalc.IsNontrivialClass G)
    (hhas : GraphCalc.HasTotalDominationNumber G) :
    2 ≤ GraphCalc.totalDominationNumber G := by
  unfold GraphCalc.totalDominationNumber GraphCalc.minCard
  rcases hhas with ⟨s₀, hs₀_pow, hs₀_dom⟩
  have hmem : s₀ ∈ Finset.filter (GraphCalc.IsTotalDominatingSet G) Finset.univ.powerset := by
    rw [Finset.mem_filter]
    exact ⟨hs₀_pow, hs₀_dom⟩
  have himage : s₀.card ∈ Finset.image Finset.card (Finset.filter (GraphCalc.IsTotalDominatingSet G) Finset.univ.powerset) :=
    Finset.mem_image_of_mem Finset.card hmem
  rcases Finset.min_of_mem himage with ⟨b, hb⟩
  have hb_mem : b ∈ Finset.image Finset.card (Finset.filter (GraphCalc.IsTotalDominatingSet G) Finset.univ.powerset) :=
    Finset.mem_of_min hb
  rcases Finset.mem_image.mp hb_mem with ⟨s, hs_filt, hsb⟩
  rw [Finset.mem_filter] at hs_filt
  have hge2 : 2 ≤ s.card := card_ge_two_of_totalDominatingSet G hnt s hs_filt.2
  have hget : ((Finset.image Finset.card (Finset.filter (GraphCalc.IsTotalDominatingSet G) Finset.univ.powerset)).min).getD 0 = b := by
    rw [hb]
    rfl
  rw [hget]
  rw [← hsb]
  exact hge2

theorem prove_9e476a83 : Candidate := by
  intro V _ _ G _ hnt hhas
  exact totalDominationNumber_ge_two G hnt hhas

theorem refute_9e476a83 : ¬ Candidate := by
  sorry
