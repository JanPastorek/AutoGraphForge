/-
GraphInvariants.lean — a small, faithful Lean 4 / mathlib formalization layer for
the graph invariants that appear in the *simplest* CEGIS survivors, so that the
machine-generated conjectures are well-formed `theorem … := sorry` goals the
DeepSeek-Prover-V2 backend (and the kernel) can actually act on.

Scope is deliberately small. Invariants already in mathlib are reused directly:

  order n            → `Fintype.card V`        (aliased `SimpleGraph.order`)
  size m             → `G.edgeFinset.card`     (aliased `SimpleGraph.size`)
  minimum_degree δ   → `G.minDegree`           (mathlib)
  maximum_degree Δ   → `G.maxDegree`           (mathlib)
  clique_number ω    → `G.cliqueNum`           (mathlib)
  independence_num α → `G.indepNum`            (mathlib)
  chromatic_number χ → `G.chromaticNumber`     (mathlib, ℕ∞)

Invariants *not* in mathlib but faithfully definable in a few lines are defined
here (domination family). Harder invariants (zero forcing, residue, Roman
domination, …) are intentionally out of scope: conjectures referencing them are
filtered out of the prove set rather than formalized incorrectly.
-/
import Mathlib

namespace SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Order of `G`: the number of vertices. -/
def order (_G : SimpleGraph V) : ℕ := Fintype.card V

/-- Size of `G`: the number of edges. -/
noncomputable def size (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  G.edgeFinset.card

/-- `s` dominates `G`: every vertex is in `s` or adjacent to a vertex of `s`. -/
def IsDominatingSet (G : SimpleGraph V) (s : Finset V) : Prop :=
  ∀ v : V, v ∈ s ∨ ∃ w ∈ s, G.Adj v w

/-- Domination number `γ(G)`: minimum cardinality of a dominating set. -/
noncomputable def dominationNumber (G : SimpleGraph V) : ℕ :=
  sInf { n | ∃ s : Finset V, s.card = n ∧ G.IsDominatingSet s }

/-- `s` is independent in `G`: no two of its vertices are adjacent. -/
def IsIndependentFinset (G : SimpleGraph V) (s : Finset V) : Prop :=
  ∀ ⦃u⦄, u ∈ s → ∀ ⦃w⦄, w ∈ s → ¬ G.Adj u w

/-- Independent domination number `i(G)`: minimum cardinality of an independent
dominating set. -/
noncomputable def independentDominationNumber (G : SimpleGraph V) : ℕ :=
  sInf { n | ∃ s : Finset V, s.card = n ∧ G.IsDominatingSet s ∧ G.IsIndependentFinset s }

end SimpleGraph
