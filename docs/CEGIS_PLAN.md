# CEGIS conjecturing over the full graphcalc battery — design & plan

Status: **implemented** (run via `python run_cegis.py`). Modules:
`pipeline/{invariants_graphcalc,seed_corpus,refute_matrix,cegis}.py`,
`pipeline/search/{problem,simulated_annealing,rlgt_adapter,__init__}.py`,
`tools/precompute_battery.py`, entry point `run_cegis.py`. The §7 list below was
the build plan; the as-built layout matches it (SA + rlgt cover the searchers;
MCTS/VNS/Z3 remain available in `pipeline/falsification.py` for future wiring).
Goal: (1) find novel, publishable graph-theory conjectures/theorems; (2) showcase
the end-to-end pipeline; (3) make it fast; via a counterexample-guided
(CEGIS) loop that generates on a *small expressible seed* and refutes against
everything we have.

---

## 1. Core idea (counterexample-guided / Fajtlowicz–Graffiti)

Generation is expensive *per candidate*; refutation is cheap *per candidate*.
So:

- **Generate** tight bounds on a **small "expressible" seed** S where graphcalc
  computes the *whole* invariant battery exactly.
- **Refute** each candidate against the largest pool where its invariants are
  known — structured families, random models, the 348k HoG+census DB (for the
  columns it carries), and an **active counterexample search** (Z3 + metaheuristics).
- **Add witnesses back to S** and re-generate (active learning). Stop at a
  **fixed point**: a round where nothing refutes anything. Survivors hold on
  everything we tried.

This replaces fitting graffiti3/Sage on the full 348k DB (infeasible anyway —
those rows don't carry zero-forcing, Roman domination, spectral invariants).

---

## 2. Invariant battery = graphcalc (all of it)

- Provider: **`graphcalc.graphs.all_properties([G]) → DataFrame`** (accepts plain
  networkx graphs; returns **59 columns** in graphcalc 2.0.0). For a chosen
  subset use `compute_knowledge_table(function_names, graphs)`.
- Invariants are grouped in `graphcalc.graphs.invariants.{classics, core_invariants,
  critical_invariants, cycle_invariants, degree, domination, graph_indices,
  local_invariants, spectral, transversal_invariants, zero_forcing,
  advanced_colorings, coloring_predicates}`, each carrying
  `@invariant_metadata(display_name, notation, category, …)` readable via
  `graphcalc.metadata.get_graphcalc_metadata(fn)`.
- Use **category** metadata to (a) group/iterate targets, (b) label the report,
  (c) emit notation into Lean statements.
- NP-hard invariants (domination, independence, zero forcing, …) are computed
  **exactly via ILP** (graphcalc's pulp solver). This is why the seed must be
  small — see timing below.
- This supersedes the hand-rolled `graphs/invariants.py` (~16 invariants).

### graphcalc.all_properties timing vs n (measured, dense gnp(0.4) worst case)

| n | 5 | 7 | 9 | 10 | 12 | 14 | 16 | 18 | 20 |
|---|---|---|---|----|----|----|----|----|----|
| s/graph | 0.06 | 0.08 | 0.19 | 0.15 | 0.21 | **0.94** | **2.9** | **11** (≤25) | **70+ / ILP errors** |

**Decision:** `exact_tier_max_n = 14` default (~1 s/graph; sparser graphs faster),
`16` acceptable, `≥18` selectively / offline only. n=20 is the practical ceiling
(ILP blows up / errors). All battery computation is embarrassingly parallel.

---

## 3. Data model: two coverage axes, incomplete tables OK

A conjecture `f ≤ g(…)` can only be **refuted on a graph where every invariant it
mentions is known.** Tables are allowed to be **incomplete** (NaN cells): we
refute *where values exist* and ignore the rest — never block on missing coverage.

| tier | #graphs | invariants | role |
|------|---------|-----------|------|
| **Seed S** (TxGraffiti expressive graphs) | hundreds | **all** (graphcalc, exact) | generation + grows with witnesses |
| **Exact families** (barbells, named families, atlas, n≤14–16) | thousands | all (exact, precomputed once) | cheap refute |
| **Random models** (regular/gnp/tree/bipartite, several orders) | thousands | all (exact) | typical-interior refute |
| **Big DB** (HoG enriched 75k + census 273k) | **348k** | only precomputed columns | mass refute for DB-column conjectures |
| **Active search** (Z3 + MCTS/VNS/SA/RL/CE) | generated on demand | computed per candidate | adversarial witness construction |

### Seed = TxGraffiti's expressive graphs
The starting S is **the expressive graph collection bundled with TxGraffiti**
(not the atlas). Reconstruct the actual graph *structures* (mostly standard named
/ small graphs within the exact tier) and recompute the full graphcalc battery on
them. The atlas is demoted to an "exact families" refuter tier.

### Persisted grown seed (approved)
S accumulates hard witnesses **across runs** → a reusable `database/hard_seed/`
corpus (graph6 + cached battery). This is itself a paper asset ("the hardest
graphs for these inequalities").

### Offline battery precompute (approved)
One-time job computes graphcalc's full battery on the families + as much of HoG as
feasible (n≤16) → cached `.npy`/parquet. Over time this upgrades the big DB from
"few columns" toward "full battery", widening what can be mass-refuted.

---

## 4. The loop

```
S = load_txgraffiti_expressive_seed()          # full battery, exact, persisted
refuters = [exact_families, random_models, big_db_columns]   # cached matrices
searchers = [Z3, MCTS, VNS, SA, RL, CE]        # active counterexample generators

repeat (until fixed point or round budget):
  C = graffiti3(S) + sage_tuned(S)             # generate on S — FAST (|S| small)
  C = filter_known(dedup(C))                   # drop classical/trivial bounds
  refuted = {}
  for tier in refuters:                        # cheap → expensive cascade
      W = vectorized_refute(C, tier)           # NaN-aware closed-form eval
      refuted |= W
      if W: S += witnesses(W); C -= W
  for c in C (survivors so far):               # active adversarial search
      for searcher in searchers:               # black-box: build graph, eval via graphcalc
          g = searcher.attack(c)
          if g: S += [g]; refuted[c]=g; break
  if not refuted: break                         # FIXED POINT
report survivors  ranked by (touch desc, complexity asc)
  → autoformalize (Lean) → prove (real Lean+mathlib / Claude / DeepSeek-Colab)
  → {kernel-verified = THEOREMS ; rest = OPEN CONJECTURES}
```

---

## 5. Counterexample search (your RL/MCTS/VNS/SA requirement)

`pipeline/falsification.py` already has **Z3, MCTS, VNS, CrossEntropy**, but they
are wired to a *hardcoded* invariant-pair Z3 encoding and only handle a few
invariants. For the full battery we generalize to **black-box graph search**:
the objective is the conjecture's **slack** `slack(G) = rhs(G) − lhs(G)`; a
counterexample is any graph with `slack < 0`. Every searcher just needs to
*propose graphs* and *evaluate slack* (compute the needed graphcalc invariants on
the proposal). This works for any invariant.

| searcher | status | notes |
|----------|--------|-------|
| Z3/SMT | exists | exact for the few SMT-encodable invariants; keep for those |
| MCTS | exists → generalize | tree over edge add/remove; reward = violation |
| VNS | exists → generalize | neighborhoods = k-edge flips |
| CrossEntropy (linear) | exists | keep as the no-torch fallback |
| **Deep Cross-Entropy (Wagner)** | **via `rlgt`** | upgrades the linear CE |
| **REINFORCE / PPO** | **via `rlgt`** | rlgt ships both agents |
| **Simulated Annealing** | **NEW (small)** | edge-flip proposals, Metropolis on violation, cooling schedule |

### RL via the `rlgt` package (chosen — do not hand-roll)
Use **[`rlgt`](https://github.com/Ivan-Damnjanovic/rlgt)** (`pip install rlgt[agents]`,
installed: rlgt 1.0.1) for the RL searchers. It is Wagner's *deep cross-entropy*
method + REINFORCE/PPO over a graph-construction environment.

API contract (verified):
- `rlgt.environments.graph_environment.GraphEnvironment(graph_invariant: Callable[[rlgt Graph], np.ndarray], graph_invariant_diff=None, sparse_setting=False)`
  — **you supply the reward callable**; agents construct graphs to maximize it.
- Agents: `rlgt.agents.deep_cross_entropy_agent.DeepCrossEntropyAgent(env, policy_network, optimizer, candidates_count=200, elite_count=30, survivors_count=50, …)`, plus `reinforce_agent`, `ppo_agent`.
- Graph conversion: `rlgt.graphs.graph.Graph` ↔ networkx via `rlgt.graphs.graph_formats`.

**Wiring:** reward `= violation(G) = lhs(G) − rhs(G)` computed with graphcalc on
the agent's proposed graph (NaN/uncomputable ⇒ large negative). `violation > 0`
⇒ counterexample → add to S, stop the episode. A tiny MLP policy + Adam is enough;
runs on CPU (torch installed) and uses GPU automatically if present.

Shared infra to build: a `GraphSearchProblem(conjecture)` exposing
`violation(G)`, `neighbors(G)`, `random_start(n)`, so the non-rlgt searchers
(MCTS/VNS/SA/Z3) share one objective; the rlgt searchers consume the same
`violation` as their `graph_invariant` reward. Per-class search
(regular/gnp/tree) restricts proposals/starts to that hypothesis class.

### Dependency note
`rlgt[agents]` pulled **torch 2.12 + CUDA wheels** and upgraded **numpy
2.1.3 → 2.4.6**. Verified the existing stack (pandas, scipy, networkx, graphcalc,
txgraffiti) still imports and graphcalc still computes (59 cols) under numpy 2.4.6.
Pin these in `requirements.txt`. RL is optional — guard the import so the pipeline
runs without torch (falls back to linear CE + MCTS/VNS/SA).

---

## 6. Performance plan (priority order)

1. **Generate on S, not 348k** — removes the Qhull/LP-over-348k blowup. Biggest win.
2. **Vectorized refute matrices** — each tier as numpy `(graphs × invariants)` +
   column index; candidate `f ≤ a·g+b·h+c` → one NaN-aware `np.all` reduction.
   Replaces per-candidate `native.check(df)`.
3. **Cache matrices** keyed by (tier, graphcalc version) to `.npy`/parquet; the
   exact-tier battery (ILP, expensive) is computed once and reused.
4. **Coverage-masked refuter selection** — skip tiers that lack a conjecture's
   invariants (don't run 348k for a zero-forcing conjecture).
5. **Parallelize across candidates** (and across seed graphs for battery compute).
6. **Search cascade** — pool lookup first (kills most), metaheuristics only on
   survivors, Z3/ILP last.
7. Cap RHS arity; rank by **touch** (Dalmatian) to prune weak candidates early.

---

## 7. New / changed modules (when we build)

- `pipeline/invariants_graphcalc.py` — battery provider over `all_properties`;
  `numeric_invariants()`, `boolean_properties()`, `categories()`, `notation()`.
- `pipeline/seed_corpus.py` — load TxGraffiti expressive seed; persist/grow
  `database/hard_seed/`.
- `pipeline/refute_matrix.py` — tiered cached numpy matrices; NaN-aware
  `refute(candidates, tier)`; coverage masks.
- `pipeline/search/` — `GraphSearchProblem` (shared `violation` objective) +
  generalized MCTS/VNS/linear-CE + **new** `simulated_annealing.py` + **`rlgt_adapter.py`**
  (wraps `rlgt` deep-CE/REINFORCE/PPO: maps `violation` → `GraphEnvironment`
  reward, converts rlgt Graph ↔ networkx, import-guarded so torch stays optional).
- `pipeline/cegis.py` — the loop (§4); owns S and the re-generate trigger.
- `tools/precompute_battery.py` — offline graphcalc battery on families/HoG → cache.
- `config.py` — `mode="cegis"|"fulldb"`, `seed_source="txgraffiti"`,
  `exact_tier_max_n=14`, `refute_tiers`, `searchers`, `persist_seed=True`,
  cache paths.
- `run_cegis.py` — headline experiment entry point (keeps `fulldb` path as baseline).
- Refactor `graffiti3_stage.py` + `tuning.py` to fit on a passed-in seed frame.

---

## 8. Paper protocol (goals 1 & 2)

1. Seed = TxGraffiti expressive graphs; battery = all graphcalc; `filter_known=on`.
2. Run CEGIS to fixed point; log: candidates/round, refutations by tier,
   witnesses added, |S| growth, wall-clock.
3. Rank survivors by touch × simplicity; autoformalize; Lean-verify.
4. Report table: *conjecture · notation · touch · complexity · deepest refuter
   survived · proved?* — Lean-closed ⇒ **theorems**; rest ⇒ **open conjectures**.
5. Baseline comparison vs. `fulldb` mode (speed + #novel) to justify the design.
6. Ablations: with/without each searcher; seed-growth curve; exact_tier_max_n sweep.

---

## 9. Open implementation details to confirm at build time
- Exact way TxGraffiti ships its expressive graphs (edge lists vs. names) →
  reconstruct structures for the seed.
- graphcalc invariant ↔ our Lean-formalization name map (for autoformalization).
- ILP solver robustness near n=18–20 (saw errors at n=20) — cap + try/except per graph.
