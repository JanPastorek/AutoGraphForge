import Mathlib
import LeanProject.GraphInvariantsComputable

set_option maxRecDepth 10000

lemma ballWithin_zero {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    GraphCalc.ballWithin G 0 v = {v} := rfl

lemma ballWithin_subset_succ {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) (v : V) :
    GraphCalc.ballWithin G k v ⊆ GraphCalc.ballWithin G (k + 1) v := by
  dsimp [GraphCalc.ballWithin]
  exact Finset.subset_union_left

lemma ballWithin_mono {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) {k m : ℕ} (h : k ≤ m) : GraphCalc.ballWithin G k v ⊆ GraphCalc.ballWithin G m v := by
  obtain ⟨d, rfl⟩ := Nat.exists_eq_add_of_le h
  clear h
  induction d with
  | zero => exact Finset.Subset.refl _
  | succ d' ih =>
    exact Finset.Subset.trans ih (ballWithin_subset_succ G (k + d') v)

lemma mem_ballWithin_succ_of_adj {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (k : ℕ) (v u w : V) (hu : u ∈ GraphCalc.ballWithin G k v) (hadj : G.Adj u w) :
    w ∈ GraphCalc.ballWithin G (k + 1) v := by
  dsimp [GraphCalc.ballWithin]
  apply Finset.mem_union_right
  apply Finset.mem_biUnion.mpr
  refine ⟨u, hu, ?_⟩
  rw [Finset.mem_filter]
  exact ⟨Finset.mem_univ w, hadj⟩

lemma mem_ballWithin_of_walk_start {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj] :
    ∀ {u v : V} (p : G.Walk u v), u ∈ GraphCalc.ballWithin G p.length v
  | u, _, .nil => by
    rw [SimpleGraph.Walk.length_nil, ballWithin_zero]
    exact Finset.mem_singleton_self u
  | u, v, .cons hadj p' => by
    rw [SimpleGraph.Walk.length_cons]
    exact mem_ballWithin_succ_of_adj G p'.length v _ u (mem_ballWithin_of_walk_start G p') hadj.symm

lemma mem_ballWithin_of_walk {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    {u v : V} (p : G.Walk u v) : v ∈ GraphCalc.ballWithin G p.length u := by
  have h := mem_ballWithin_of_walk_start G p.reverse
  rw [SimpleGraph.Walk.length_reverse] at h
  exact h

lemma mem_ballWithin_of_walk_le {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    {u v : V} (p : G.Walk u v) {k : ℕ} (h : p.length ≤ k) :
    v ∈ GraphCalc.ballWithin G k u :=
  ballWithin_mono G u h (mem_ballWithin_of_walk G p)

lemma mem_ballWithin_of_dist_le {V : Type} [Fintype V] [DecidableEq V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (u v : V) {k : ℕ} (hle : G.dist u v ≤ k) :
    v ∈ GraphCalc.ballWithin G k u := by
  obtain ⟨p, hp⟩ := hconn.exists_walk_length_eq_dist u v
  rw [← hp] at hle
  exact mem_ballWithin_of_walk_le G p hle

lemma finset_min_getD_le_of_mem (n : ℕ) {s : Finset ℕ} {b : ℕ} (hb : b ∈ s) :
    s.min.getD n ≤ b := by
  have h : s.min ≤ WithTop.some b := Finset.inf_le hb
  cases hm : s.min with
  | top =>
    rw [hm] at h
    simp at h
  | coe m =>
    rw [hm] at h
    exact WithTop.coe_le_coe.mp h

lemma radius_le_eccentricity {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    GraphCalc.radius G ≤ GraphCalc.eccentricity G v := by
  apply finset_min_getD_le_of_mem 0
  apply Finset.mem_image.mpr
  exact ⟨v, Finset.mem_univ v, rfl⟩

lemma eccentricity_le_of_ballWithin_eq_univ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (k : ℕ)
    (hkle : k ≤ Fintype.card V) (heq : GraphCalc.ballWithin G k v = Finset.univ) :
    GraphCalc.eccentricity G v ≤ k := by
  dsimp [GraphCalc.eccentricity, GraphCalc.minUpTo]
  apply finset_min_getD_le_of_mem (Fintype.card V)
  rw [Finset.mem_filter, Finset.mem_range]
  exact ⟨Nat.lt_succ_of_le hkle, heq⟩

lemma min_getD_eq_min' {s : Finset ℕ} (hs : s.Nonempty) (d : ℕ) :
    s.min.getD d = s.min' hs := by
  have h := Finset.coe_min' hs
  rw [← h]
  rfl

lemma exists_totalDominatingSet_card_eq {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (ht : GraphCalc.HasTotalDominationNumber G) :
    ∃ s : Finset V, GraphCalc.IsTotalDominatingSet G s ∧ s.card = GraphCalc.totalDominationNumber G := by
  dsimp [GraphCalc.HasTotalDominationNumber, GraphCalc.HasWitness] at ht
  rcases ht with ⟨s0, hs0mem, hs0dom⟩
  dsimp [GraphCalc.totalDominationNumber, GraphCalc.minCard]
  have hne : s0.card ∈ Finset.image Finset.card (Finset.filter (GraphCalc.IsTotalDominatingSet G) Finset.univ.powerset) := by
    apply Finset.mem_image.mpr
    refine ⟨s0, ?_, rfl⟩
    rw [Finset.mem_filter]
    exact ⟨hs0mem, hs0dom⟩
  have hnonempty : (Finset.image Finset.card (Finset.filter (GraphCalc.IsTotalDominatingSet G) Finset.univ.powerset)).Nonempty := ⟨s0.card, hne⟩
  have hmin := Finset.min'_mem _ hnonempty
  rw [Finset.mem_image] at hmin
  rcases hmin with ⟨s, hs, hscard⟩
  rw [Finset.mem_filter] at hs
  refine ⟨s, hs.2, ?_⟩
  rw [hscard]
  exact (min_getD_eq_min' hnonempty 0).symm
