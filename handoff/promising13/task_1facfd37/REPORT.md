# Report: Challenge 1facfd37

## Direction Settled
**PROVED**: Settled `prove_1facfd37 : Candidate`.

Conjecture under test:
`(nontrivial) ⇒ independence_number ≤ edge_cover_number`

## Key Mathematical Idea
Let $G = (V, E)$ be any finite graph.
1. Let $I \subseteq V$ be any independent set and let $s \subseteq E$ be any edge cover of $G$.
2. For every vertex $v \in I$, because $s$ is an edge cover, there exists an edge $e \in s$ such that $v \in e$.
3. We define an assignment $f : I \to s$ by choosing, for each $v \in I$, an edge $f(v) \in s$ containing $v$.
4. If $f(u) = f(v) = e$ for distinct vertices $u, v \in I$, then both $u$ and $v$ belong to $e \in E(G)$. By definition of edges in simple graphs, $u$ and $v$ must be adjacent in $G$. However, $u, v \in I$ contradicts $I$ being an independent set. Hence $f$ is injective on $I$.
5. By injectivity, $|I| \le |s|$.
6. In `GraphCalc`, `indepNum G` is the maximum cardinality of an independent set (or 0 if none), and `edgeCoverNumber G` is the minimum cardinality $k \le |V|$ of an edge cover $s \subseteq G.\text{edgeFinset}$ (or $|V|$ if none). Since every independent set has cardinality bounded by any edge cover, and bounded by $|V|$, it follows directly that $\text{indepNum}(G) \le \text{edgeCoverNumber}(G)$.

## Final Checker Output
```
LINT: ok
/tmp/tmp.z05v25CXN9.lean:86:8: warning: declaration uses `sorry`
'prove_1facfd37' depends on axioms: [propext, Classical.choice, Quot.sound]
'refute_1facfd37' depends on axioms: [propext, sorryAx, Classical.choice, Quot.sound]
CHECK: elaborated. Allowed axioms: propext, Classical.choice, Quot.sound.
       'sorryAx' in a list above means that theorem is unfinished.
```
