# GraphConjecturing

An automated graph-theory **conjecturing → refutation → formal-proof** pipeline.
It generates candidate invariant inequalities on a small "expressible" seed of
graphs, refutes the false ones against tiered pools and active search until a
fixed point, then exports the survivors to **Lean 4 / mathlib** and tries to
**kernel-verify** them with neural provers — a local **DeepSeek-Prover-V2-7B**,
or a larger **vLLM-served** model (**DeepSeek-Prover-V2-671B** / **OProver-32B**)
behind a shim — every proof checked by the Lean kernel itself (no API tokens).

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

For the **served** prover path (large models on a cluster), launch a vLLM model +
shim and reprove the survivors via SLURM — see `tools/slurm/` (`prove_671b.sbatch`,
`prove_oprover.sbatch`) and `tools/run_prove.py`; the multi-node CEGIS run uses
`tools/slurm/cegis_shard.sbatch` + `tools/merge_shards.py`.

Requirements: Python ≥3.10, and (for the prover) a CUDA GPU + Lean 4 via `elan`
with the mathlib cache fetched in `lean_project/` (`lake exe cache get`). The
served path additionally needs the `.venv-prover` stack (vLLM, fastapi, uvicorn).

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
  (ω≤χ, König–Egerváry, …) via the 559-relation table + convex-LP implication.
  A theorem proved for a superclass is applied to its subclasses through a
  class-subsumption lattice derived from ISGCI (`pipeline/data/class_hierarchy.json`,
  regenerate with `tools/build_class_hierarchy.py`).

### 3. Refutation — `pipeline/refute_matrix.py`, `pipeline/symbolic_refute.py`, `pipeline/search/`
Tiered, NaN-aware, coverage-masked; the first tier to produce a counterexample
wins, and the refuting graph becomes a seed witness:

| Tier | What | Notes |
|---|---|---|
| `symbolic` | constructive | refutes constant/degree bounds (`order ≤ 14`) by building an extremal in-class witness, independent of pool size |
| `families` | atlas + parametric (barbells, lollipops, …) | full battery, n≤12 |
| `random` | class-aware random models | full battery |
| `hog` | HoG export's **precomputed** invariants | ~28 invariants for **28,859** graphs incl. **big** ones (n≤60), partial/NaN-aware, ingested directly (no recompute) |
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
  triangle_free/K_4_free/bipartite/eulerian), plus `connected` and `tree`
  (mathlib's `Connected` / `IsTree`, the latter reached through the decidable
  edge-count form proved equivalent in `isTreeClass_iff`) and the two
  forbidden-induced-subgraph classes `claw_free` (K₁,₃) and `cograph` (P₄).
  `chordal` and `planar` remain unformalized.

`lean_export` emits self-contained, compilable theorems for the *supported*
subset — unconditioned bounds and class-conditioned ones over the formalized
classes — and skips conjectures over not-yet-formalized invariants/classes
rather than mis-formalizing them.

### 5. Proving — `pipeline/theorem_prover.py`, `pipeline/lemma_retrieval.py`, `tools/prover_shim.py`, `tools/verify_proofs.py`
One rule governs both prover paths: **every candidate proof is independently
kernel-verified** against the pinned mathlib + the `GraphInvariants` preamble
before it counts — a success is a real proof, never the model's say-so.

- **In-process (small model):** `DeepSeekProverLocal` runs DeepSeek-Prover-V2-7B
  locally via 🤗 transformers (pass@k), grounded per-goal by `lemma_retrieval`
  (greps the pinned mathlib for relevant lemma signatures).
- **Served (large models):** for models too big for the in-process backend,
  `tools/prover_shim.py` (FastAPI) adapts a **vLLM**-served model to the
  `LocalEndpointProver` HTTP schema — registered as the `deepseek-671b` backend
  (`PROVER_REGISTRY`; point `cfg.prover_api_url` at the shim). The same shim
  serves **DeepSeek-Prover-V2-671B** or the Lean-specialised **OProver-32B**,
  supports a multi-round **agentic** mode (`AGENTIC_ROUNDS`: feed each failed
  attempt's Lean error back, with the invariant definitions grounding the
  prompt), and **persists every verified proof** to `results/verified_proofs/*.lean`.
  `tools/verify_proofs.py` re-checks those artifacts with a standalone kernel
  pass, so the reported count is reproducible from the files alone.

Verification uses **bare `lean` + a computed `LEAN_PATH`** (lake-free, so it
never mutates the mathlib cache on no-git compute nodes; `lake env lean` is a
fallback). Other ensemble backends (`lean` tactics, `claude`, HTTP
`goedel`/`deepseek`) remain registered in `PROVER_REGISTRY`.

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
- `results/refutations.json` — refuted conjectures paired with the graph that
  refutes them (input to `tools/export_disproofs.py`).
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
  random_models.py        class-aware random graph models (random tier)
  search/                 z3 + metaheuristics + rlgt active search
  lean_export.py          supported-subset Lean export (uncond. + class-cond.)
  lean_disproof.py        Lean disproofs (¬∀ discharged on a refuting graph)
  proof_audit.py          statement-identity + axiom guards for candidate proofs
  known_relations.py      curated known relations feeding the novelty filter
  novelty.py              known-theorem LP + ISGCI class-subsumption lattice
  data/class_hierarchy.json  generated: superclass closure over our class vocabulary
  lemma_retrieval.py      per-goal mathlib lemma retrieval for the prover
  theorem_prover.py       prover ensemble (local + served endpoint backends)
  reporting.py            ranking / printing
lean_project/             Lean 4 + mathlib project; GraphInvariants.lean preamble
                          + GraphInvariantsComputable.lean (decidable mirror)
tools/
  precompute_battery.py   offline full-battery recompute (bigdb tier)
  prove_curated.py / prove_demo.py / prove_new.py   curated / demo / survivor proving
  run_prove.py            served-prover reprove driver (deepseek-671b backend)
  prover_shim.py          FastAPI: vLLM (671B / OProver-32B) → endpoint schema; agentic mode; persists proofs
  verify_proofs.py        independent re-verification of persisted proofs
  export_disproofs.py     emit + kernel-check disproofs from refutations.json
  validate_known_relations.py  empirical check of the novelty table
  build_class_hierarchy.py     regenerate the class lattice from a graphotaxy/ISGCI snapshot
  run_shard.py / merge_shards.py   CEGIS SLURM-array shard launch + survivor/witness merge
  slurm/                  sbatch scripts (cegis_shard, prove_671b, prove_oprover, gpu_probe, merge, …)
tests/                    pytest unit tests for the CEGIS core
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
