import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

open SimpleGraph

-- Conjecture under test: (nontrivial) ⇒ order ≤ (2 · edge_cover_number)
-- Both declarations refer to the same `Candidate`.
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasEdgeCover G → GraphCalc.order G ≤ 2 * GraphCalc.edgeCoverNumber G

lemma card_le_two_mul_card_of_isEdgeCoverFinset {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset (Sym2 V))
    (h : GraphCalc.IsEdgeCoverFinset G s) :
    Fintype.card V ≤ 2 * s.card := by
  have hcov : (Finset.univ : Finset V) ⊆ s.biUnion Sym2.toFinset := by
    intro v _
    rcases h v with ⟨e, he, hv⟩
    exact Finset.mem_biUnion.mpr ⟨e, he, Sym2.mem_toFinset.mpr hv⟩
  have hcard : Fintype.card V ≤ (s.biUnion Sym2.toFinset).card := by
    rw [← Finset.card_univ]
    exact Finset.card_le_card hcov
  have hbound : (s.biUnion Sym2.toFinset).card ≤ s.card * 2 := by
    apply Finset.card_biUnion_le_card_mul
    intro e _
    rw [Sym2.card_toFinset]
    split_ifs <;> omega
  omega

lemma withTop_eq_top_or_exists_coe (x : WithTop ℕ) : x = ⊤ ∨ ∃ k : ℕ, x = ↑k := by
  induction x using WithTop.recTopCoe with
  | top => left; rfl
  | coe k => right; exact ⟨k, rfl⟩

lemma minUpTo_eq_or_prop (n : ℕ) (p : ℕ → Prop) [DecidablePred p] :
    GraphCalc.minUpTo n p = n ∨ (∃ k, p k ∧ GraphCalc.minUpTo n p = k) := by
  unfold GraphCalc.minUpTo
  rcases withTop_eq_top_or_exists_coe (((Finset.range (n + 1)).filter p).min) with h | ⟨k, hk⟩
  · rw [h]
    left
    rfl
  · rw [hk]
    right
    have hmem : k ∈ (Finset.range (n + 1)).filter p := Finset.mem_of_min hk
    rw [Finset.mem_filter] at hmem
    exact ⟨k, hmem.2, rfl⟩

theorem prove_a23c41a0 : Candidate := by
  intro V _ _ G _ _ _
  change Fintype.card V ≤ 2 * GraphCalc.edgeCoverNumber G
  unfold GraphCalc.edgeCoverNumber
  rcases minUpTo_eq_or_prop (Fintype.card V)
    (fun k => ∃ s ∈ G.edgeFinset.powersetCard k, GraphCalc.IsEdgeCoverFinset G s) with h1 | ⟨k, ⟨s, hs, hcov⟩, h2⟩
  · rw [h1]
    omega
  · rw [h2]
    rw [Finset.mem_powersetCard] at hs
    have hle := card_le_two_mul_card_of_isEdgeCoverFinset G s hcov
    omega

theorem refute_a23c41a0 : ¬ Candidate := by
  sorry
