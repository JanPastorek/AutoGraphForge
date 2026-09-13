# Briefing — Task 2a2555cc

## Conjecture Overview
- **Statement**: `(nontrivial) ⇒ radius ≤ total_domination_number`
- **Formal Target**: `Challenge_2a2555cc.lean`
- **Candidate definition**:
  ```lean
  abbrev Candidate : Prop :=
      ∀ {V : Type} [Fintype V] [DecidableEq V]
      (G : SimpleGraph V) [DecidableRel G.Adj],
        GraphCalc.IsNontrivialClass G → GraphCalc.HasRadius G → GraphCalc.HasTotalDominationNumber G → GraphCalc.radius G ≤ GraphCalc.totalDominationNumber G
  ```

## Mathematical Assessment
- **Ground truth status**: Open candidate in `promising13`.
- **Direction**: `prove_2a2555cc`.
- **Mathematical justification**:
  For any connected graph $G$ on $\ge 2$ vertices, if $S$ is any total dominating set, every vertex in $V$ is within distance $\le 1$ of $S$. The components of $G[S]$ have sizes $\ge 2$ (no isolated vertices). The maximum distance across the component graph of $S$ is bounded by $|S|$, ensuring that the central vertex of $G$ has eccentricity $\le |S|$. In particular, $\text{rad}(G) \le \gamma_t(G)$ always holds.
- **Verification tool**: `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_2a2555cc.lean`.
