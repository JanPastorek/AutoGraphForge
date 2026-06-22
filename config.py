"""
config.py — centralised configuration for the conjecture pipeline.
All knobs are readable from environment variables or set programmatically.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # ------------------------------------------------------------------ LLM --
    anthropic_api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )
    model: str = "claude-opus-4-6"
    llm_max_tokens: int = 4096

    # -------------------------------------------------------- Graph database --
    db_min_vertices: int = 3
    db_max_vertices: int = 14
    db_random_graphs: int = 15      # extra ER graphs to add beyond named ones
    db_random_seed: int = 42
    # Persistent invariant databases loaded by default (HoG rich invariants +
    # the SRG / minimal-Ramsey / Cayley / cages / cographs / nauty / rigid
    # families in graph_database_enriched.csv, plus the exhaustive n≤9 census).
    # Empty ⇒ auto-resolve to whichever of these exist; falls back to a small
    # synthetic build only if none are found.
    db_csv_paths: tuple = (
        "database/graph_database_enriched.csv",
        "database/census_le9.csv",
        "database/txgraffiti_data.csv",    # graph datasets bundled with TxGraffiti
                                            # (sync_txgraffiti_data.py)
        "database/counterexamples.csv",   # graphs found by the falsifiers (grows)
    )
    # Counterexamples discovered during a run are appended here so the dataset
    # learns permanently (this file is also one of the db_csv_paths above).
    counterexample_csv: str = "database/counterexamples.csv"

    # ----------------------------------------------------- Adversarial filter --
    adversarial_enabled: bool = True   # permanent counterexample-search stage
    adversarial_max_n: int = 18        # max order of pool graphs (exact invariants)
    adversarial_seed: int = 2025
    # Also fold class-aware random models (random regular / G(n,p) / trees /
    # bipartite …, several orders) into the adversarial pool, so refutation
    # probes the typical interior of each class, not just structured witnesses.
    adversarial_random_models: bool = True
    adversarial_random_per: int = 4    # random graphs per (class, order)

    # ----------------------------------------------- Hypothesis generation --
    txgraffiti_max_conjectures: int = 30
    txgraffiti_max_offset: float = 5.0
    txgraffiti_coefficients: tuple = (0.5, 1.0, 1.5, 2.0, 3.0)
    # Generation engine:
    #   "txgraffiti" — the txgraffiti package (convex_hull/ratios/LP); finds the
    #                  optimal real coefficients per facet (slower per call).
    #   "numpy"      — the in-house vectorised fit over a fixed coefficient grid
    #                  (txgraffiti_coefficients); much faster, coarser.
    #   "both"       — union of the two (deduplicated by statement).
    txgraffiti_engine: str = "txgraffiti"
    # Generate bounds conditioned on graph classes (bipartite, regular, …),
    # i.e. "for all G with property P: f(G) ≤ …".
    txgraffiti_condition_on_classes: bool = True
    # Allow multivariable right-hand sides:  f(G) ≤ a·g(G) + b·h(G) + c.
    txgraffiti_multivariable: bool = True
    txgraffiti_max_rhs_terms: int = 2   # 2 ⇒ permit one extra RHS invariant
    txgraffiti_min_support: int = 5     # min graphs in a context before fitting
    # Drop bounds that are an equality across the whole class (identities /
    # within-class tautologies such as Δ = δ on regular graphs).
    txgraffiti_drop_identities: bool = True
    # Hide conjectures that merely rediscover a classical/trivial theorem
    # (Whitney, Brooks, ω ≤ χ, ν ≤ n/2, …) so only novel bounds are kept.
    txgraffiti_filter_known: bool = True
    funsearch_conjectures: int = 5   # LLM-generated conjectures per call
    use_funsearch: bool = True

    # --------------------------------------------- Graffiti3 (native expr) --
    # txgraffiti's Graffiti3 system: native-Python nonlinear conjecturing
    # (ratio/LP/poly/products/sqrt/log + Sophie sufficient-conditions + Lean
    # export). Runs on a SMALL exact corpus (the graph atlas, n ≤ max_n), since
    # its STANDARD/DEEP runners are far too slow on large data.
    graffiti3_enabled: bool = True
    graffiti3_mode: str = "fast"     # "fast" (cheap) | "standard" | "deep"
    graffiti3_max_n: int = 7         # corpus = connected atlas graphs up to this
    graffiti3_sophie: bool = True    # also mine Sophie sufficient-conditions
    graffiti3_refute_random: bool = True   # refute against random models too
    graffiti3_max_per_target: int = 40     # keep top-N (by touches) per target
                                           # before the (per-candidate) refutation

    # Sage Conjecturing stage: kept as an option; tune its grid coefficients to
    # the optimal real values by LP (pipeline.tuning) when enabled.
    sage_enabled: bool = True
    sage_tune_coefficients: bool = True
    # Ranking used when printing the final survivors: "score" | "complexity"
    # (simplest first) | "touches".
    report_sort_by: str = "score"

    # ============================================ CEGIS mode (run_cegis.py) ==
    # Counterexample-guided loop: generate on a small "expressible" seed (the
    # TxGraffiti expressive graphs, full graphcalc battery), refute against
    # tiered pools + active search, add witnesses back to the seed, repeat to a
    # fixed point. See docs/CEGIS_PLAN.md.
    cegis_rounds: int = 8               # max generate→refute passes (or fixed point)
    cegis_workers: int = 16             # parallel workers for the per-candidate
                                        # refute + active-search phases (fork; 0/1
                                        # = serial). The pool/SA evals are
                                        # embarrassingly parallel across candidates.
    cegis_targets: tuple = ()           # restrict target invariants ((), = all numeric)
    cegis_max_targets: int = 0          # cap #targets per round (0 = no cap)
    cegis_filter_known: bool = True     # drop classical/trivial bounds
    cegis_dalmatian: bool = True        # Dalmatian significance filter on the seed
                                        # (prunes graffiti3's ~10^5 raw product
                                        #  candidates to the non-dominated envelope)
    cegis_morgan: bool = True           # Morgan hypothesis-maximality filter
                                        # (drops over-conditioned redundant bounds)
    cegis_report_top: int = 40          # survivors to print/formalize/prove
    # Seed corpus
    exact_tier_max_n: int = 14          # graphs ≤ this get the full battery (≈1s/graph)
    battery_cap_s: int = 90             # per-graph wall-clock cap for graphcalc
    persist_seed: bool = True           # accumulate hard witnesses across runs
    hard_seed_dir: str = "database/hard_seed"
    cache_dir: str = "database/cache"
    # Refutation tiers (cheap → expensive); each is NaN-aware + coverage-masked
    refute_use_families: bool = True    # atlas + named families (exact battery)
    refute_use_random: bool = True      # class-aware random models (exact battery)
    refute_random_per: int = 6
    refute_families_max_n: int = 12     # cap n for the (expensive) family battery
    refute_use_bigdb: bool = True       # 348k HoG+census, columns it carries only
    cegis_max_sophie: int = 400         # keep the top-N most significant Sophie
                                        # sufficient-conditions (graffiti3 emits
                                        # ~10^4; ranked by support, not arbitrary).
                                        # Dalmatian/Morgan are inequality-only, so
                                        # Sophie gets its own significance filter.
    # Active counterexample search (run on survivors of pool refutation), tried
    # cheapest-first per candidate: z3 (exact, encodable invariants) → vns → sa →
    # cross_entropy → mcts → rl. All but z3 are black-box over the graphcalc
    # battery. The trial budget is *order-adaptive*: the orders sweep from small
    # to large and the per-order trial count is scaled down ∝ ref/n, so big
    # graphs (expensive evals) get proportionally fewer trials.
    cegis_searchers: tuple = ("z3", "cross_entropy", "vns", "sa", "rl")  # +"mcts"
    cegis_max_search: int = 60          # max pool-survivors/round given active
                                        # search (rest kept as pool-survivors)
    search_orders: tuple = (              # increasing orders, incl. big graphs
        6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 24, 28, 34, 40)
    search_order_ref: int = 6           # reference order for trial scaling
    search_min_trials: int = 30         # floor on per-order trials at large n
    search_eval_cap_s: int = 3          # per-graph invariant-eval timeout
    sa_iterations: int = 300            # base SA steps (scaled down per order)
    sa_restarts: int = 1
    rl_episodes: int = 40               # rlgt deep-CE / REINFORCE iterations
    rl_candidates: int = 200            # rlgt candidates_count per iteration
    rl_agent: str = "deep_cross_entropy"    # "deep_cross_entropy" | "reinforce"
    rl_enabled: bool = True             # set False to skip torch/rlgt entirely

    # --------------------------------------------------- Falsification loop --
    falsification_rounds: int = 2    # retry passes after db augmentation
    z3_enabled: bool = True
    z3_timeout_ms: int = 10_000     # per Z3 solver call
    z3_max_n: int = 9               # max graph size for Z3 search
    mcts_iterations: int = 800
    mcts_c: float = 1.41            # UCT exploration constant
    mcts_n_vertices: int = 9
    vns_iterations: int = 600
    vns_k_max: int = 4              # max neighbourhood size
    ce_iterations: int = 200
    ce_population: int = 60
    ce_elite_frac: float = 0.2
    ce_n_vertices: int = 10

    # ---------------------------------------------- Autoformalization stub --
    # Lean 4 + mathlib kernel-checking. `lean_binary` is resolved via PATH or an
    # absolute elan path; when `lean_project_root` points at a mathlib-backed
    # lake project, proofs are compiled with `lake env lean` (so the mathlib
    # search path + `import Mathlib` are available and kernel-verified).
    lean_binary: str = field(
        default_factory=lambda: (
            os.path.expanduser("~/.elan/bin/lean")
            if os.path.exists(os.path.expanduser("~/.elan/bin/lean")) else "lean"
        )
    )
    lake_binary: str = field(
        default_factory=lambda: (
            os.path.expanduser("~/.elan/bin/lake")
            if os.path.exists(os.path.expanduser("~/.elan/bin/lake")) else "lake"
        )
    )
    lean_timeout_s: int = 180        # mathlib import + elaboration can be slow
    lean_project_root: str = field(
        default_factory=lambda: (
            p if os.path.isdir(p := os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "lean_project")) else ""
        )
    )

    # ------------------------------------------------------- Provers --------
    # Ordered ensemble of prover backends tried per conjecture (first success
    # wins). Registered names: "lean" (local Lean tactics), "claude" (Anthropic
    # API, kernel-verified when a Lean binary is present), "goedel"/"deepseek"
    # (HTTP stubs — point prover_api_url at a self-hosted GPU endpoint to enable).
    prover_backends: tuple = ("lean", "claude", "goedel", "deepseek")
    prover_api_url: str = ""        # e.g. "https://goedel-prover.example.com/v1"
    prover_api_key: str = field(
        default_factory=lambda: os.environ.get("PROVER_API_KEY", "")
    )
    prover_timeout_s: int = 120

    # --------------------------------------------------------------- Output --
    output_dir: str = "results"
    verbose: bool = True
    save_graphs: bool = False       # save networkx graphs to JSON (large)


# Module-level singleton — replace or monkey-patch as needed.
CONFIG = Config()
