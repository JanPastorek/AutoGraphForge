# Verification Report: Task 8ca1b27c

## Outcome
- **Settled Direction**: Proven (`prove_8ca1b27c : Candidate`)
- **Refutation Theorem**: Untouched with `sorry` (`refute_8ca1b27c : ¬ Candidate`)
- **Status**: Formally verified in Lean 4 with kernel-checked proof.

---

## Conjecture Statement
Conjecture under test: `Candidate: (nontrivial) ⇒ 2 ≤ sub_total_domination_number`

```lean
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.HasSubTotalDominationNumber G → 2 ≤ GraphCalc.subTotalDominationNumber G
```

---

## Core Mathematical Reasoning

1. **Order of Nontrivial Graphs**:
   `GraphCalc.IsNontrivialClass G` states that $n = \text{order } G = |V| \ge 2$.

2. **Definition of Sub-Total Domination Number**:
   `GraphCalc.subTotalDominationNumber G` is defined as:
   $$\min_{t \le n} \{ t \mid n \le \text{largestDegreeSum}(G, t) \}$$
   with fallback to $n$ if no such $t \le n$ exists (via `GraphCalc.minUpTo`).

3. **Degree Bound for Simple Graphs**:
   In any simple loopless graph $G = (V, E)$, the neighborhood of every vertex $v \in V$ satisfies $N(v) \subseteq V \setminus \{v\}$. Thus:
   $$\deg(v) \le n - 1 < n \quad \forall v \in V$$
   (proven in Mathlib via `SimpleGraph.degree_lt_card_verts v`).

4. **Analysis of Small Prefixes ($t < 2$)**:
   - For $t = 0$: The only 0-subset of vertices is $\emptyset$, whose degree sum is $0$. Since $n \ge 2 > 0$, $n \le \text{largestDegreeSum}(G, 0) = 0$ is impossible.
   - For $t = 1$: Every 1-subset of vertices is a singleton $\{v\}$, whose degree sum is $\deg(v) < n$. Therefore, the maximum degree sum over 1-subsets satisfies $\text{largestDegreeSum}(G, 1) < n$. Hence $n \le \text{largestDegreeSum}(G, 1)$ is impossible.

5. **Conclusion**:
   No index $k < 2$ can satisfy $n \le \text{largestDegreeSum}(G, k)$.
   Therefore:
   - If no $t \le n$ satisfies the condition, `GraphCalc.minUpTo` evaluates to the fallback value $n \ge 2$.
   - If some $t \le n$ satisfies the condition, the minimal such index must be $\ge 2$.
   In both cases, $\text{subTotalDominationNumber}(G) \ge 2$.

---

## Formal Proof Structure

The formalization adds three modular top-level helper lemmas:
- `minUpTo_ge`: Shows that for any predicate $p$ on $\mathbb{N}$, if $2 \le n$ and every $k \in \{0, \dots, n\}$ satisfying $p(k)$ has $2 \le k$, then $2 \le \text{minUpTo } n\ p$.
- `largestDegreeSum_zero`: Shows `largestDegreeSum G 0 = 0`.
- `largestDegreeSum_one_lt`: Shows that when $2 \le |V|$, $\text{largestDegreeSum } G\ 1 < |V|$.

These lemmas combine cleanly with `interval_cases` and `omega` to prove `prove_8ca1b27c`.

---

## Complete Checker Output

```
LINT: ok
/tmp/tmp.KBwzJ5HmCn.lean:65:8: warning: declaration uses `sorry`
'prove_8ca1b27c' depends on axioms: [propext, Classical.choice, Quot.sound]
'refute_8ca1b27c' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]
CHECK: elaborated. Allowed axioms: propext, Classical.choice, Quot.sound.
       'sorryAx' in a list above means that theorem is unfinished.
```
Exit code: `0`
Axioms used in `prove_8ca1b27c`: only standard Lean axioms (`propext`, `Classical.choice`, `Quot.sound`). No `sorryAx`.
