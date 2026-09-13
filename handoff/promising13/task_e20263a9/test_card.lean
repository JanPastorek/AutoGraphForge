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

lemma eccentricity_le_card {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (hrad : GraphCalc.HasRadius G) :
    GraphCalc.eccentricity G v ≤ Fintype.card V := by
  unfold GraphCalc.eccentricity
  apply minUpTo_le (Fintype.card V) (le_refl _) (hrad v)
