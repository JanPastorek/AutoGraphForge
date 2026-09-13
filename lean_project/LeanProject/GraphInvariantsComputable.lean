/-
GraphInvariantsComputable.lean — a *computable* mirror of the invariants in
`GraphInvariants.lean`, so that a claim about one explicit finite graph can be
settled by `decide` rather than by a hand proof.

Why this file exists
--------------------
`GraphInvariants.lean` defines the invariants the way a mathematician states
them: `dominationNumber G = sInf { n | ∃ s, s.card = n ∧ G.IsDominatingSet s }`.
That is the right *specification*, but `sInf` over a `Set ℕ` (under
`open scoped Classical`) is **noncomputable**, so the kernel cannot evaluate it
on a concrete graph — measured directly, `decide` succeeds on `order`, `size`
and `minDegree`, and fails on every `sInf`/`sSup` invariant (domination,
annihilation, the zero-forcing family, and mathlib's own `indepNum`/`cliqueNum`).

That blocks the cheapest source of formal results we have. The refutation engine
kills thousands of candidates and knows exactly which graph kills each one; each
such pair is a `¬∀ …` theorem whose proof is "evaluate both sides on this graph"
— but only if the invariants actually evaluate.

The definitions here are the same mathematical objects expressed as a minimum
over an explicitly enumerated `Finset`, which the kernel *can* reduce. They are
deliberately kept in their own namespace: nothing in the existing proof pipeline
changes, and `GraphInvariants.lean` remains the specification of record.
-/
import Mathlib

open Finset

namespace GraphCalc

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Least cardinality of a subset satisfying `p`, or `0` when none does.

The `0` fallback is only harmless when *some* subset satisfies `p` — for
`indepNum`, `dominationNumber` and `vertexCoverNumber`, `univ` always does. It
is NOT harmless in general, and treating it as such produced a real defect:
`IsConnectedZeroForcingSet` is unsatisfiable on a disconnected graph (`univ`
does not induce a connected subgraph), so the invariant silently read `0` where
graphcalc reports "undefined". A conjecture `Z_c + 2 ≤ 2 * Z_t` then became
`2 ≤ 0` and was refutable with no mathematical content.

Any new invariant built on `minCard` must either prove `univ` satisfies its
predicate, or expose a `Has…` witness predicate below and be exported under it. -/
def minCard (p : Finset V → Prop) [DecidablePred p] : ℕ :=
  ((univ.powerset.filter p).image Finset.card).min.getD 0

/-- Some subset satisfies `p`: exactly the precondition `minCard` needs for its
value to mean "the least cardinality" rather than "there were none". -/
def HasWitness (p : Finset V → Prop) [DecidablePred p] : Prop :=
  ∃ s ∈ (univ : Finset V).powerset, p s

instance (p : Finset V → Prop) [DecidablePred p] : Decidable (HasWitness p) := by
  unfold HasWitness; infer_instance

/-- Greatest `k ≤ n` satisfying `p`, or `0` when none does. -/
def maxUpTo (n : ℕ) (p : ℕ → Prop) [DecidablePred p] : ℕ :=
  (((range (n + 1)).filter p).max).getD 0

/-- Least `k ≤ n` satisfying `p`, or `n` when none does. -/
def minUpTo (n : ℕ) (p : ℕ → Prop) [DecidablePred p] : ℕ :=
  (((range (n + 1)).filter p).min).getD n

/- ── order / size ─────────────────────────────────────────────────────────── -/

def order (_G : SimpleGraph V) : ℕ := Fintype.card V

def size (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ := G.edgeFinset.card

/- ── independence / clique ────────────────────────────────────────────────── -/

/-- `s` is independent: no two of its vertices are adjacent. -/
def IsIndependentFinset (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) : Prop :=
  ∀ u ∈ s, ∀ w ∈ s, ¬ G.Adj u w

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Decidable (IsIndependentFinset G s) := by
  unfold IsIndependentFinset; infer_instance

/-- Independence number: the largest independent set. -/
def indepNum (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  (((univ.powerset.filter (IsIndependentFinset G)).image Finset.card).max).getD 0

/-- `s` is a clique: distinct vertices of `s` are pairwise adjacent. -/
def IsCliqueFinset (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) : Prop :=
  ∀ u ∈ s, ∀ w ∈ s, u ≠ w → G.Adj u w

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Decidable (IsCliqueFinset G s) := by
  unfold IsCliqueFinset; infer_instance

/-- Clique number: the largest clique. -/
def cliqueNum (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  (((univ.powerset.filter (IsCliqueFinset G)).image Finset.card).max).getD 0

/- ── domination family ────────────────────────────────────────────────────── -/

def IsDominatingSet (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) : Prop :=
  ∀ v : V, v ∈ s ∨ ∃ w ∈ s, G.Adj v w

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Decidable (IsDominatingSet G s) := by
  unfold IsDominatingSet; infer_instance

def dominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsDominatingSet G)

def IsIndependentDominatingSet (G : SimpleGraph V) [DecidableRel G.Adj]
    (s : Finset V) : Prop :=
  IsDominatingSet G s ∧ IsIndependentFinset G s

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Decidable (IsIndependentDominatingSet G s) := by
  unfold IsIndependentDominatingSet; infer_instance

def independentDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsIndependentDominatingSet G)

/- ── degree-sequence invariants ───────────────────────────────────────────── -/

/-- Sum of the `k` smallest degrees.

Stated as a minimum over `k`-element subsets rather than by sorting the degree
sequence: the two agree (a `k`-subset of minimum degree-sum is exactly a choice
of `k` smallest degrees), and this form stays decidable, whereas both
`Multiset.sort` and `Finset.toList` are noncomputable and stall kernel
reduction. -/
def smallestDegreeSum (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) : ℕ :=
  (((univ.powersetCard k).image (fun s => ∑ v ∈ s, G.degree v)).min).getD 0

/-- Sum of the `k` largest degrees (dual of `smallestDegreeSum`). -/
def largestDegreeSum (G : SimpleGraph V) [DecidableRel G.Adj] (k : ℕ) : ℕ :=
  (((univ.powersetCard k).image (fun s => ∑ v ∈ s, G.degree v)).max).getD 0

/-- Annihilation number: largest `k` whose `k` smallest degrees sum to `≤ m`. -/
def annihilationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  maxUpTo (Fintype.card V) (fun k => smallestDegreeSum G k ≤ size G)

/-- Slater number: least `t` with `t +` (sum of the `t` largest degrees) `≥ n`. -/
def slaterNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minUpTo (Fintype.card V)
    (fun t => Fintype.card V ≤ t + largestDegreeSum G t)

/- ── bipartite ────────────────────────────────────────────────────────────── -/

/-- `G` is bipartite: some vertex set has every edge crossing it.

The specification says `G.Colorable 2`, which quantifies over colourings and has
no `Decidable` instance, so `decide` cannot touch it — leaving `bipartite` a
class that could be *stated* in an exported theorem but never refuted on a
witness. Searching the powerset is decidable and finite; `isBipartiteClass_iff`
proves the two agree. -/
def IsBipartiteClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∃ s ∈ (univ : Finset V).powerset,
    ∀ u ∈ (univ : Finset V), ∀ v ∈ (univ : Finset V), G.Adj u v → (u ∈ s ↔ v ∉ s)

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsBipartiteClass G) := by
  unfold IsBipartiteClass; infer_instance

/- ── vertex cover ─────────────────────────────────────────────────────────── -/

/-- `s` covers every edge. This is mathlib's `SimpleGraph.IsVertexCover`
restricted to a `Finset`, which is what makes it decidable: mathlib quantifies
over `Set V` and its `vertexCoverNum` is an `⨅` over that, hence noncomputable.
`isVertexCoverFinset_iff` below proves the two agree, so the mathlib definition
remains the specification and nothing is taken on trust. -/
def IsVertexCoverFinset (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Prop :=
  ∀ u ∈ (univ : Finset V), ∀ v ∈ (univ : Finset V), G.Adj u v → u ∈ s ∨ v ∈ s

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Decidable (IsVertexCoverFinset G s) := by
  unfold IsVertexCoverFinset; infer_instance

theorem isVertexCoverFinset_iff (G : SimpleGraph V) [DecidableRel G.Adj]
    (s : Finset V) : IsVertexCoverFinset G s ↔ G.IsVertexCover (↑s : Set V) := by
  simp [IsVertexCoverFinset, SimpleGraph.IsVertexCover]

def vertexCoverNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsVertexCoverFinset G)

/- ── zero-forcing family ──────────────────────────────────────────────────── -/

def forcingStep (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Finset V :=
  S ∪ univ.filter (fun w => w ∉ S ∧ ∃ v ∈ S, G.neighborFinset v \ S = {w})

def forcingClosure (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Finset V :=
  (forcingStep G)^[Fintype.card V] S

def IsZeroForcingSet (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Prop :=
  forcingClosure G S = univ

instance (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) :
    Decidable (IsZeroForcingSet G S) := by
  unfold IsZeroForcingSet; infer_instance

def zeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsZeroForcingSet G)

def IsTotalZeroForcingSet (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Prop :=
  IsZeroForcingSet G S ∧ ∀ v ∈ S, ∃ w ∈ S, G.Adj v w

instance (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) :
    Decidable (IsTotalZeroForcingSet G S) := by
  unfold IsTotalZeroForcingSet; infer_instance

def totalZeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsTotalZeroForcingSet G)

/-- `totalZeroForcingNumber` is meaningful: a total zero-forcing set exists.
False whenever some vertex has no neighbour in any forcing set — isolated
vertices being the common case. -/
def HasTotalZeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  HasWitness (IsTotalZeroForcingSet G)

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (HasTotalZeroForcingNumber G) := by
  unfold HasTotalZeroForcingNumber; infer_instance

/-- One step of reachability inside `S`: everything already in `T`, plus the
vertices of `S` adjacent to it. -/
def reachWithin (G : SimpleGraph V) [DecidableRel G.Adj] (S T : Finset V) : Finset V :=
  T ∪ S.filter (fun w => ∃ v ∈ T, G.Adj v w)

/-- The vertices of `S` reachable from `v` without leaving `S`. Iterating `n`
times suffices: each step that changes anything adds at least one vertex. -/
def componentWithin (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) (v : V) :
    Finset V :=
  (reachWithin G S)^[Fintype.card V] {v}

/-- `S` induces a connected subgraph.

The specification layer says `(G.induce ↑S).Connected`, which is a statement
about walks in a subtype and carries no `Decidable` instance. This is the
decidable equivalent: `S` is nonempty and every vertex of it reaches all of `S`
from inside. `Connected` is `Preconnected ∧ Nonempty`, so both conjuncts are
accounted for — the nonemptiness is not incidental. -/
def IsConnectedSubset (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) : Prop :=
  S.Nonempty ∧ ∀ v ∈ S, componentWithin G S v = S

instance (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) :
    Decidable (IsConnectedSubset G S) := by
  unfold IsConnectedSubset; infer_instance

/-- A connected zero-forcing set: zero-forcing and inducing a connected
subgraph, matching graphcalc's `is_connected_zero_forcing_set`. -/
def IsConnectedZeroForcingSet (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) :
    Prop :=
  IsZeroForcingSet G S ∧ IsConnectedSubset G S

instance (G : SimpleGraph V) [DecidableRel G.Adj] (S : Finset V) :
    Decidable (IsConnectedZeroForcingSet G S) := by
  unfold IsConnectedZeroForcingSet; infer_instance

def connectedZeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsConnectedZeroForcingSet G)

/-- `connectedZeroForcingNumber` is meaningful: a connected zero-forcing set
exists. False on every disconnected graph, which is precisely where graphcalc
reports no value and where the conjectures never made a claim. -/
def HasConnectedZeroForcingNumber (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  HasWitness (IsConnectedZeroForcingSet G)

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (HasConnectedZeroForcingNumber G) := by
  unfold HasConnectedZeroForcingNumber; infer_instance

/- ── graph-class predicates ───────────────────────────────────────────────── -/

def IsNontrivialClass (G : SimpleGraph V) : Prop := 2 ≤ order G

instance (G : SimpleGraph V) : Decidable (IsNontrivialClass G) := by
  unfold IsNontrivialClass; infer_instance

def IsRegularClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ u v : V, G.degree u = G.degree v

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsRegularClass G) := by unfold IsRegularClass; infer_instance

def IsCubicClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v : V, G.degree v = 3

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsCubicClass G) := by unfold IsCubicClass; infer_instance

def IsSubcubicClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v : V, G.degree v ≤ 3

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsSubcubicClass G) := by unfold IsSubcubicClass; infer_instance

/-- Eulerian: connected, with every degree even (graphcalc's `eulerian` is
`networkx.is_eulerian`, which requires connectivity — see GraphInvariants). -/
def IsEulerianClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  G.Connected ∧ ∀ v : V, G.degree v % 2 = 0

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsEulerianClass G) := by unfold IsEulerianClass; infer_instance

/-- Triangle-free: no 3-element clique. -/
def IsTriangleFreeClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ s ∈ univ.powerset, IsCliqueFinset G s → s.card ≠ 3

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsTriangleFreeClass G) := by
  unfold IsTriangleFreeClass; infer_instance

/-- `K₄`-free: no 4-element clique. -/
def IsK4FreeClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ s ∈ univ.powerset, IsCliqueFinset G s → s.card ≠ 4

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsK4FreeClass G) := by unfold IsK4FreeClass; infer_instance

/-- Connected. Mathlib's `SimpleGraph.Connected` already has a `Decidable`
instance on a finite vertex type (`Connectivity/Finite.lean`) and it *does*
reduce in the kernel — verified directly — so this is a plain alias rather than
a reimplementation. -/
def IsConnectedClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop := G.Connected

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsConnectedClass G) := by unfold IsConnectedClass; infer_instance

/-- A tree: connected with `m + 1 = n`.

Mathlib's `SimpleGraph.IsTree` is built on `IsAcyclic`, a statement about *all*
walks, and has no `Decidable` instance — `decide` fails on it outright. The edge
count is the decidable equivalent, and `isTreeClass_iff` below proves the two
agree, so nothing is taken on trust. -/
def IsTreeClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  G.Connected ∧ size G + 1 = order G

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsTreeClass G) := by unfold IsTreeClass; infer_instance

omit [DecidableEq V] in
/-- The computable tree test is exactly mathlib's `IsTree`. -/
theorem isTreeClass_iff (G : SimpleGraph V) [DecidableRel G.Adj] :
    IsTreeClass G ↔ G.IsTree := by
  rw [SimpleGraph.isTree_iff_connected_and_card]
  simp [IsTreeClass, size, order, Nat.card_eq_fintype_card, Set.toFinset_card,
        SimpleGraph.edgeFinset]

/-- Claw-free: no vertex has three pairwise non-adjacent neighbours.

Phrased through `IsIndependentFinset` over `powersetCard 3` rather than as four
plain `∀ v a b c : V` binders with `a ≠ b` side conditions: the latter is the
more readable statement (and is what `GraphInvariants.lean` records) but its
`Decidable` instance does not reduce, so `decide` gets stuck on it. This form
reduces. -/
def IsClawFreeClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v ∈ (univ : Finset V), ∀ s ∈ univ.powersetCard 3,
    (∀ u ∈ s, G.Adj v u) → ¬ IsIndependentFinset G s

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsClawFreeClass G) := by unfold IsClawFreeClass; infer_instance

/-- Cograph: no four vertices induce a path `P₄`. -/
def IsCographClass (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ a b c d : V, G.Adj a b → G.Adj b c → G.Adj c d →
    ¬ G.Adj a c → ¬ G.Adj b d → G.Adj a d

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (IsCographClass G) := by unfold IsCographClass; infer_instance

/- ── sub-total domination ─────────────────────────────────────────────────── -/

/-- Sub-total domination number: least `t` whose `t` largest degrees sum to
`≥ n`.

graphcalc computes this by sorting the degree sequence and scanning prefixes;
`largestDegreeSum` is that prefix sum expressed as a maximum over `t`-subsets
(see the note there on why sorting is not available to the kernel). -/
def subTotalDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minUpTo (Fintype.card V) (fun t => Fintype.card V ≤ largestDegreeSum G t)

/-- Defined exactly when *some* prefix reaches `n`. graphcalc returns no value
when the scan runs off the end — an edgeless graph has every degree `0`, so no
prefix ever reaches `n` — while `minUpTo` would fall back to `n`. Monotonicity
of `largestDegreeSum` makes the whole-graph check `t = n` sufficient. -/
def HasSubTotalDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  Fintype.card V ≤ largestDegreeSum G (Fintype.card V)

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (HasSubTotalDominationNumber G) := by
  unfold HasSubTotalDominationNumber; infer_instance

/- ── total domination ─────────────────────────────────────────────────────── -/

/-- Every vertex has a neighbour in `s` — note `G.Adj v u` excludes `v = u`, so
a vertex may not dominate itself. -/
def IsTotalDominatingSet (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Prop := ∀ v : V, ∃ u ∈ s, G.Adj v u

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset V) :
    Decidable (IsTotalDominatingSet G s) := by
  unfold IsTotalDominatingSet; infer_instance

def totalDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minCard (IsTotalDominatingSet G)

/-- Undefined on a graph with an isolated vertex: nothing dominates it, so not
even `univ` is a total dominating set and `minCard` would read `0`. graphcalc
raises there rather than returning a number. -/
def HasTotalDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  HasWitness (IsTotalDominatingSet G)

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (HasTotalDominationNumber G) := by
  unfold HasTotalDominationNumber; infer_instance

/- ── edge cover ───────────────────────────────────────────────────────────── -/

/-- A set of edges meeting every vertex. -/
def IsEdgeCoverFinset (G : SimpleGraph V) [DecidableRel G.Adj]
    (s : Finset (Sym2 V)) : Prop := ∀ v : V, ∃ e ∈ s, v ∈ e

instance (G : SimpleGraph V) [DecidableRel G.Adj] (s : Finset (Sym2 V)) :
    Decidable (IsEdgeCoverFinset G s) := by
  unfold IsEdgeCoverFinset; infer_instance

/-- Edge cover number: least `k ≤ n` such that some `k` edges meet every vertex.

Searched by size over `edgeFinset`, not over its whole powerset. A minimum edge
cover never needs more than `n - 1` edges (Gallai: `ρ = n − ν`, and `ν ≥ 1` once
there is an edge), so bounding `k` by `n` loses nothing. It matters: the full
powerset of `K₆`'s 15 edges is 32,768 subsets and exhausted the kernel's
recursion depth, while the subsets of size at most 6 number 9,949. -/
def edgeCoverNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  minUpTo (Fintype.card V)
    (fun k => ∃ s ∈ G.edgeFinset.powersetCard k, IsEdgeCoverFinset G s)

/-- Undefined exactly when some vertex is isolated — networkx raises "no edge
cover exists" there, and `minUpTo`'s fallback would read `n`. An edge cover
exists iff every vertex has a neighbour (take one incident edge per vertex), so
this is stated directly instead of by a second subset search. -/
def HasEdgeCover (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v : V, ∃ u : V, G.Adj v u

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (HasEdgeCover G) := by unfold HasEdgeCover; infer_instance

/- ── Roman domination ─────────────────────────────────────────────────────── -/

/-- `f : V → {0,1,2}` is a Roman dominating function when every vertex labelled
`0` has a neighbour labelled `2`.

graphcalc solves this as a MIP over binaries `x, y` with `f = x + 2y`,
constraint `x v + y v + Σ_{u ∈ N(v)} y u ≥ 1` and exclusion `x v + y v ≤ 1`;
that is exactly the condition below. -/
def IsRomanDominatingFunction (G : SimpleGraph V) [DecidableRel G.Adj]
    (f : V → Fin 3) : Prop := ∀ v : V, f v = 0 → ∃ u : V, G.Adj v u ∧ f u = 2

instance (G : SimpleGraph V) [DecidableRel G.Adj] (f : V → Fin 3) :
    Decidable (IsRomanDominatingFunction G f) := by
  unfold IsRomanDominatingFunction; infer_instance

def romanWeight (f : V → Fin 3) : ℕ := ∑ v : V, (f v : ℕ)

/-- Total, not partial: the constant function `2` is always Roman dominating
(no vertex is labelled `0`), so a witness always exists. -/
def romanDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  (((univ.filter (IsRomanDominatingFunction G)).image romanWeight).min).getD 0

/- ── double Roman domination ──────────────────────────────────────────────── -/

/-- `f : V → {0,1,2,3}` is double Roman dominating when a vertex labelled `0`
has either a neighbour labelled `3` or two neighbours labelled `2`, and a vertex
labelled `1` has a neighbour labelled `≥ 2`.

The first clause is written as graphcalc's linearisation
`0.5·|N₂(v)| + |N₃(v)| ≥ 1`, but as two existentials rather than as
`Finset.card` of a filter: "at least two neighbours labelled 2" is "two distinct
neighbours labelled 2", and the kernel reduces a pair of quantifiers over `V`
far more cheaply than it builds and counts a `Finset`. Written the counting way
first, all seven order-5 checks exhausted their heartbeat budget. -/
def IsDoubleRomanDominatingFunction (G : SimpleGraph V) [DecidableRel G.Adj]
    (f : V → Fin 4) : Prop :=
  (∀ v : V, f v = 0 →
      (∃ u : V, G.Adj v u ∧ f u = 3) ∨
      (∃ u : V, ∃ w : V, u ≠ w ∧ G.Adj v u ∧ G.Adj v w ∧ f u = 2 ∧ f w = 2)) ∧
  (∀ v : V, f v = 1 → ∃ u : V, G.Adj v u ∧ 2 ≤ (f u : ℕ))

instance (G : SimpleGraph V) [DecidableRel G.Adj] (f : V → Fin 4) :
    Decidable (IsDoubleRomanDominatingFunction G f) := by
  unfold IsDoubleRomanDominatingFunction; infer_instance

def doubleRomanWeight (f : V → Fin 4) : ℕ := ∑ v : V, (f v : ℕ)

/-- Total, for the same reason as `romanDominationNumber`: constant `3` works. -/
def doubleRomanDominationNumber (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  (((univ.filter (IsDoubleRomanDominatingFunction G)).image
    doubleRomanWeight).min).getD 0

/- ── radius ───────────────────────────────────────────────────────────────── -/

/-- Vertices within `k` steps of `v`, by iterated neighbourhood expansion.
Distance is not available to the kernel directly (`SimpleGraph.dist` is defined
through `sInf` over walk lengths), so it is reconstructed as reachability. -/
def ballWithin (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ → V → Finset V
  | 0,       v => {v}
  | (k + 1), v =>
      let B := ballWithin G k v
      B ∪ B.biUnion (fun u => univ.filter (fun w => G.Adj u w))

/-- Eccentricity of `v`: least `k` with every vertex within `k` steps. -/
def eccentricity (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) : ℕ :=
  minUpTo (Fintype.card V) (fun k => ballWithin G k v = univ)

def radius (G : SimpleGraph V) [DecidableRel G.Adj] : ℕ :=
  ((univ.image (eccentricity G)).min).getD 0

/-- Undefined on a disconnected graph, where some vertex never reaches all of
`univ` and `minUpTo` would fall back to `n`. networkx raises there. -/
def HasRadius (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v : V, ballWithin G (Fintype.card V) v = univ

instance (G : SimpleGraph V) [DecidableRel G.Adj] :
    Decidable (HasRadius G) := by unfold HasRadius; infer_instance

/- ── graph construction from an explicit edge list ────────────────────────── -/

/-- The graph on `Fin n` with the given edge list, symmetrised and loop-free.
This is the shape the disproof exporter emits for a refuting witness.

`SimpleGraph.fromRel` supplies the symmetry and irreflexivity proofs, so this
stays a definition rather than a bundle of obligations that would have to be
re-discharged (and re-adjusted across mathlib versions) in generated code. It is
an `abbrev` so that `DecidableRel` synthesis can see through it at the use site. -/
abbrev ofEdges (n : ℕ) (es : List (Fin n × Fin n)) : SimpleGraph (Fin n) :=
  SimpleGraph.fromRel (fun u v => (u, v) ∈ es)

end GraphCalc
