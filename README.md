# GraphConjecturing

An automated graph-theory **conjecturing → refutation → formal-proof** pipeline.
It generates candidate invariant inequalities on a small "expressible" seed of
graphs, refutes the false ones against tiered pools and active search until a
fixed point, then exports the survivors to **Lean 4 / mathlib** and tries to
**kernel-verify** them with a locally-run **DeepSeek-Prover-V2** (no API tokens).

The design is Fajtlowicz's *Graffiti* loop framed as **CEGIS**
(counterexample-guided inductive synthesis): conjecture on a small set, refute,
add the refuting graph back to the seed, regenerate, repeat.

---

## Quick start

```bash
pip install -e ".[dev]"            # core + tests; add [rl] [prover] [llm] as needed

graphconj cegis --rounds 3 --prove-top 12     # full run: generate → refute → prove
graphconj cegis --reprove                      # re-run just the wrap+prove stage
graphconj prove --curated                      # prove a few known theorems (chain check)
graphconj precompute-battery --max-n 14        # build the offline big-DB refutation tier
```

Requirements: Python ≥3.10, and (for the prover) a CUDA GPU + Lean 4 via `elan`
with the mathlib cache fetched in `lean_project/` (`lake exe cache get`).

---

## The pipeline

```
  seed (TxGraffiti expressive graphs, full graphcalc battery)
        │
        ▼  generate            graffiti3 FAST: ratio / product / √ / log + Sophie
  raw candidates  ──►  filter  drop constant bounds → Dalmatian → Morgan → novelty
        │
        ▼  refute (cheap→expensive, first hit wins)
   ┌───────────────────────────────────────────────────────────────┐
   │ symbolic → families → random → hog → bigdb → active search     │
   └───────────────────────────────────────────────────────────────┘
        │  witnesses (refuting graphs)
        ▼  add to seed, regenerate  ── repeat to a fixed point ──┐
        │                                                        │
        ▼  survivors  ──►  Lean export  ──►  DeepSeek-Prover-V2  ─┘
                            (supported subset)   kernel-verify
```

### 1. Generation — `pipeline/cegis.py`, `pipeline/seed_corpus.py`
graffiti3 (`txgraffiti`) in FAST mode mines nonlinear bounds (ratios, products,
√, log) plus **Sophie** sufficient-conditions over the seed's full
[graphcalc](https://pypi.org/project/graphcalc/) battery (59 invariants). The
seed starts from the TxGraffiti expressive graphs and grows only by hard
witnesses. Generation (the ~13-min cost) is **cached** (`dill`) keyed by the seed
+ targets, so reruns restore instantly.

### 2. Candidate filters — `pipeline/cegis.py`, `pipeline/candidate_filters.py`, `pipeline/cegis_novelty.py`
- **Constant-bound filter**: drops *unconditioned* `invariant ≤ const` bounds
  (`clique_number ≤ 20`); *class-conditioned* ones are kept (they can be real
  theorems, e.g. `(K_4_free) ⇒ clique_number ≤ 3`).
- **Dalmatian** (significance) + **Morgan** (hypothesis-maximality) filters prune
  the ~10⁵ raw products to the non-dominated envelope (a few thousand).
- **Novelty filter** flags survivors that rediscover a classical theorem
  (ω≤χ, König–Egerváry, …) via the 203-theorem table + convex-LP implication.

### 3. Refutation — `pipeline/refute_matrix.py`, `pipeline/symbolic_refute.py`, `pipeline/search/`
Tiered, NaN-aware, coverage-masked; the first tier to produce a counterexample
wins, and the refuting graph becomes a seed witness:

| Tier | What | Notes |
|---|---|---|
| `symbolic` | constructive | refutes constant/degree bounds (`order ≤ 14`) by building an extremal in-class witness, independent of pool size |
| `families` | atlas + parametric (barbells, lollipops, …) | full battery, n≤12 |
| `random` | class-aware random models | full battery |
| `hog` | HoG export's **precomputed** invariants | ~28 invariants for 69k graphs incl. **big** ones (n≤60), partial/NaN-aware, ingested directly (no recompute) |
| `bigdb` | offline-recomputed full battery | `tools/precompute_battery.py` |
| active search | z3 → cross-entropy → vns → sa → mcts → rl | black-box over `violation = -slack`; per-candidate time budget |

Refutation provenance (which tier killed each candidate) is logged and persisted
per round.

### 4. Formalization — `lean_project/LeanProject/GraphInvariants.lean`, `pipeline/lean_export.py`
A small mathlib `SimpleGraph` preamble defines the invariants used by the
simplest survivors:
- mathlib-backed: `cliqueNum`, `indepNum`, `minDegree`, `maxDegree`, `chromaticNumber`
- defined here: `order`, `size`, domination family, `slaterNumber`,
  `annihilationNumber`, the **zero-forcing family** (`zeroForcingNumber` +
  total/connected), and graph-**class predicates** (regular/cubic/subcubic/
  triangle_free/K_4_free/bipartite/eulerian).

`lean_export` emits self-contained, compilable theorems for the *supported*
subset — unconditioned bounds and class-conditioned ones over the formalized
classes — and skips conjectures over not-yet-formalized invariants/classes
rather than mis-formalizing them.

### 5. Proving — `pipeline/theorem_prover.py`, `pipeline/lemma_retrieval.py`
`DeepSeekProverLocal` runs DeepSeek-Prover-V2-7B locally via 🤗 transformers
(pass@k sampling), grounded per-goal by `lemma_retrieval` (greps the pinned
mathlib for relevant lemma signatures). Every candidate proof is
**kernel-verified** with `lake env lean` against mathlib + the preamble — a
success is a real proof, never the model's say-so. Other backends
(`lean` tactics, `claude`, HTTP `goedel`/`deepseek`) remain in the ensemble.

---

## Configuration

All knobs live in `config.py` (`Config` dataclass, env-overridable). Highlights:

| Knob | Meaning |
|---|---|
| `cegis_rounds` | max generate→refute passes (or fixed point) |
| `cegis_searchers` | active-search ensemble order |
| `refute_symbolic / refute_use_hog / refute_use_bigdb` | toggle refutation tiers |
| `cegis_drop_constant_bounds / cegis_dalmatian / cegis_morgan / cegis_filter_known` | filters |
| `search_orders`, `search_time_budget_s` | active-search order sweep + per-candidate budget |
| `deepseek_*` | local prover (model id, dtype, pass@k attempts) |
| `prover_backends` | ordered prover ensemble |

---

## Outputs

- `results/cegis_results.json` — survivors (with novelty flags, touches, Lean),
  round history, refutation-by-tier provenance.
- `results/cegis_survivors.dill` — persisted survivors for `--reprove`.
- `database/hard_seed/graphs.g6` — accumulated hard witnesses (grows across runs).
- `database/cache/*.parquet|*.dill` — battery + generation caches (regenerable).

---

## Repository layout

```
config.py                 central configuration
conjecture.py             Conjecture / Inequality data model
run_cegis.py              the CEGIS entry point (also: graphconj cegis)
graphconj_cli.py          single CLI dispatcher
pipeline/
  cegis.py                the CEGIS loop
  seed_corpus.py          seed + incremental battery cache
  invariants_graphcalc.py graphcalc battery wrapper
  candidate_filters.py    constant-bound filter
  cegis_novelty.py        known-theorem filter adapter
  refute_matrix.py        tiered refutation (incl. hog/bigdb tiers)
  symbolic_refute.py      constructive refutation of constant/degree bounds
  search/                 z3 + metaheuristics + rlgt active search
  lean_export.py          supported-subset Lean export (uncond. + class-cond.)
  lemma_retrieval.py      per-goal mathlib lemma retrieval for the prover
  theorem_prover.py       prover ensemble incl. local DeepSeek-Prover-V2
  reporting.py            ranking / printing
lean_project/             Lean 4 + mathlib project; GraphInvariants.lean preamble
tools/                    precompute_battery, prove_curated/demo/new
tests/                    pytest unit tests for the CEGIS core
legacy/                   superseded entry points + generation/falsification stack
docs/                     CEGIS_PLAN.md (design), MIGRATION.md (legacy→CEGIS map)
```

See **`docs/MIGRATION.md`** for the legacy→CEGIS feature map and **`docs/CEGIS_PLAN.md`**
for the full design rationale.

---

## Testing & CI

```bash
pytest tests/test_cegis_core.py -q          # fast unit tests (fake-native fixtures)
cd lean_project && lake build LeanProject     # build/kernel-check the preamble
```

CI (`.github/workflows/ci.yml`) runs the Python tests + ruff and builds the Lean
preamble against the mathlib cache.
