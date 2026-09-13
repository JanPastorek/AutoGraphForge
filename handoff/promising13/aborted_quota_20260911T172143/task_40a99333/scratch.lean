import Mathlib
import LeanProject.GraphInvariantsComputable

theorem card_two_one_le_romanWeight {V : Type} [Fintype V] [DecidableEq V] (f : V → Fin 3) :
    2 * (Finset.univ.filter (fun v => f v = 2)).card +
      (Finset.univ.filter (fun v => f v = 1)).card ≤ GraphCalc.romanWeight f := by
  unfold GraphCalc.romanWeight
  let V2 := Finset.univ.filter (fun v => f v = 2)
  let V1 := Finset.univ.filter (fun v => f v = 1)
  have h_disj : Disjoint V2 V1 := by
    rw [Finset.disjoint_filter]
    intro x _ h2 h1
    have : (2 : Fin 3) = (1 : Fin 3) := h2.symm.trans h1
    revert this
    decide
  have h_sub : V2 ∪ V1 ⊆ Finset.univ := Finset.subset_univ _
  have h1 : ∑ v ∈ V2 ∪ V1, (f v : ℕ) ≤ ∑ v ∈ Finset.univ, (f v : ℕ) :=
    Finset.sum_le_sum_of_subset_of_nonneg h_sub (fun _ _ _ => Nat.zero_le _)
  rw [Finset.sum_union h_disj] at h1
  have h_v2 : ∑ v ∈ V2, (f v : ℕ) = 2 * V2.card := by
    have : (∑ v ∈ V2, (f v : ℕ)) = ∑ v ∈ V2, 2 := by
      apply Finset.sum_congr rfl
      intro x hx
      simp only [V2, Finset.mem_filter] at hx
      rw [hx.2]
      rfl
    rw [this, Finset.sum_const, smul_eq_mul]
    ring
  have h_v1 : ∑ v ∈ V1, (f v : ℕ) = V1.card := by
    have : (∑ v ∈ V1, (f v : ℕ)) = ∑ v ∈ V1, 1 := by
      apply Finset.sum_congr rfl
      intro x hx
      simp only [V1, Finset.mem_filter] at hx
      rw [hx.2]
      rfl
    rw [this, Finset.sum_const, smul_eq_mul, one_mul]
  dsimp [V2, V1] at h_v2 h_v1 h1
  omega
