import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph
open GraphCalc

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
