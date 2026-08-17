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
