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

open scoped Classical

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

/- ── Degree-sequence invariants ─────────────────────────────────────────── -/

/-- Degrees in non-decreasing order. -/
noncomputable def degreesAsc (G : SimpleGraph V) [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map (fun v => G.degree v)).sort (· ≤ ·)

/-- Degrees in non-increasing order. -/
noncomputable def degreesDesc (G : SimpleGraph V) [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map (fun v => G.degree v)).sort (· ≥ ·)

/-- Annihilation number `a(G)`: the largest `k ≤ n` such that the `k` smallest
degrees sum to at most the number of edges. -/
noncomputable def annihilationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  sSup { k | k ≤ Fintype.card V ∧ ((G.degreesAsc).take k).sum ≤ G.size }

/-- Slater number `sl(G)`: the least `t` with `t + (sum of the t largest degrees) ≥ n`.
A classical lower bound on the domination number. -/
noncomputable def slaterNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  sInf { t | (Fintype.card V) ≤ t + ((G.degreesDesc).take t).sum }

/- ── Zero forcing family ───────────────────────────────────────────────── -/

/-- One zero-forcing colour-change step: a blue vertex with a unique white
neighbour forces it blue. -/
noncomputable def forcingStep (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) : Finset V :=
  S ∪ Finset.univ.filter (fun w => w ∉ S ∧ ∃ v ∈ S, G.neighborFinset v \ S = {w})

/-- Zero-forcing closure: iterate the step `|V|` times (a fixpoint is reached, as
each non-final step adds at least one vertex). -/
noncomputable def forcingClosure (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) : Finset V :=
  (G.forcingStep)^[Fintype.card V] S

/-- `S` is a zero-forcing set if its closure is everything. -/
def IsZeroForcingSet (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Prop :=
  G.forcingClosure S = Finset.univ

/-- Zero forcing number `Z(G)`: minimum size of a zero-forcing set. -/
noncomputable def zeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  sInf { k | ∃ S : Finset V, S.card = k ∧ G.IsZeroForcingSet S }

/-- A total zero-forcing set: zero-forcing and inducing no isolated vertex. -/
def IsTotalZeroForcingSet (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Prop :=
  G.IsZeroForcingSet S ∧ ∀ v ∈ S, ∃ w ∈ S, G.Adj v w

/-- Total zero forcing number `Z_t(G)`. -/
noncomputable def totalZeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  sInf { k | ∃ S : Finset V, S.card = k ∧ G.IsTotalZeroForcingSet S }

/-- A connected zero-forcing set: zero-forcing and inducing a connected subgraph. -/
def IsConnectedZeroForcingSet (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Prop :=
  G.IsZeroForcingSet S ∧ (G.induce (↑S)).Connected

/-- Connected zero forcing number `Z_c(G)`. -/
noncomputable def connectedZeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  sInf { k | ∃ S : Finset V, S.card = k ∧ G.IsConnectedZeroForcingSet S }

/- ── Graph-class predicates (hypotheses for conditioned conjectures) ──────── -/

/-- `G` is regular (every vertex the same degree). -/
def IsRegularClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∃ d, G.IsRegularOfDegree d
/-- `G` is cubic (3-regular). -/
def IsCubicClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  G.IsRegularOfDegree 3
/-- `G` is subcubic (maximum degree ≤ 3). -/
def IsSubcubicClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  G.maxDegree ≤ 3
/-- `G` is triangle-free. -/
def IsTriangleFreeClass (G : SimpleGraph V) : Prop := G.CliqueFree 3
/-- `G` is `K₄`-free. -/
def IsK4FreeClass (G : SimpleGraph V) : Prop := G.CliqueFree 4
/-- `G` is bipartite (2-colourable). -/
def IsBipartiteClass (G : SimpleGraph V) : Prop := G.Colorable 2
/-- `G` is Eulerian-degree (every vertex has even degree). -/
def IsEulerianClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v, Even (G.degree v)
/-- `G` is nontrivial (at least two vertices): the graphcalc `nontrivial`
flag, `|V(G)| ≥ 2`, i.e. `2 ≤ G.order`. -/
def IsNontrivialClass (G : SimpleGraph V) : Prop := 2 ≤ G.order

end SimpleGraph
