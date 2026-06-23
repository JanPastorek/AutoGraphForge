# Migration: legacy pipeline → CEGIS (canonical)

As of v0.2.0 the package has **one** canonical pipeline (CEGIS) and **one**
entry point. The historical scatter of entry points and the duplicated
generation/falsification stack moved to `legacy/`.

## Entry point

```
graphconj cegis [--rounds N] [--prove-top N] [--reprove] [--no-rl]
graphconj prove [--curated | --demo] [--k N]
graphconj precompute-battery [--max-n N] [--limit N]
graphconj build-db
```

(equivalently `python run_cegis.py …`). The legacy entry points
(`legacy/main.py`, `legacy/discover.py`, `legacy/run_parallel.py`,
`legacy/run_strongest_small.py`) are kept for reference only.

## Why CEGIS is the superset

Both pipelines are the same generate→refute→feed-back loop. CEGIS keeps the
*dataset* small (an expressible seed + full graphcalc battery) and grows it only
by hard counterexamples, which is the better strategy now that the generator
(graffiti3, nonlinear) is the bottleneck and refutation is cheap.

| Capability | Legacy module | CEGIS equivalent | Status |
|---|---|---|---|
| Nonlinear generation | `hypothesis_gen.TxGraffitiGenerator` (linear/ratio/product) | `cegis._generate` → graffiti3 FAST (ratios/products/√/log + Sophie) | **superset** |
| Counterexample search | `falsification` (Z3 + MCTS + VNS + CE) | `pipeline.search` (z3 + cross_entropy + vns + sa + mcts + **rl**) | **superset** |
| Constant/degree bounds | — (escaped a bounded-order search) | `symbolic_refute` tier 0 (constructive) | **new in CEGIS** |
| Adversarial pool | `adversarial` (barbells, lollipops, …) | `refute_matrix` families tier (incl. barbells) | parity (shares `adversarial`) |
| Big-DB refutation | — | `refute_matrix` bigdb tier (`tools/precompute_battery.py`) | **new in CEGIS** |
| Known-theorem filter | `novelty.annotate` | `cegis_novelty.classify_native` → `novelty` | parity (wired in) |
| Autoformalization | `autoformalization` (LLM GoT skeleton, unverified) | `lean_export` + `theorem_prover` (**kernel-verified**) | **superset** |
| Local neural prover | — | `theorem_prover.DeepSeekProverLocal` + `lemma_retrieval` | **new in CEGIS** |

### Not yet ported (intentionally)

- **FunSearch** LLM generation (`hypothesis_gen.FunSearchGenerator`) — needs an
  Anthropic key and was inert; revive it as an optional CEGIS seed generator if
  wanted.
- **Sage Conjecturing** expression-tree generation (`legacy/unified.py` +
  `legacy/expr_bridge.py`) — graffiti3 covers the main expressible forms;
  arbitrary Sage expression trees are a possible future generator plug-in.

## What moved to `legacy/`

Entry points / scripts: `main.py`, `discover.py`, `run_parallel.py`,
`run_strongest_small.py`, `counterexample_search.py`, `verify_candidates.py`,
`verify_class_candidates.py`.

Legacy-internal pipeline modules: `orchestrator.py`, `unified.py`,
`autoformalization.py`, `hypothesis_gen.py`, `graffiti3_stage.py`, `tuning.py`,
`expr_bridge.py`.

## Shared components that **stayed** in `pipeline/`

`falsification.py` (its `Z3Falsifier` backs the CEGIS z3 searcher) and
`adversarial.py` (its families back the refutation tier) are shared, not legacy.
Also shared: `novelty`, `reporting`, `random_models`, `invariants_graphcalc`.
