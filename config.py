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
        "database/counterexamples.csv",   # graphs found by the falsifiers (grows)
    )
    # Counterexamples discovered during a run are appended here so the dataset
    # learns permanently (this file is also one of the db_csv_paths above).
    counterexample_csv: str = "database/counterexamples.csv"

    # ----------------------------------------------------- Adversarial filter --
    adversarial_enabled: bool = True   # permanent counterexample-search stage
    adversarial_max_n: int = 18        # max order of pool graphs (exact invariants)
    adversarial_seed: int = 2025

    # ----------------------------------------------- Hypothesis generation --
    txgraffiti_max_conjectures: int = 30
    txgraffiti_max_offset: float = 5.0
    txgraffiti_coefficients: tuple = (0.5, 1.0, 1.5, 2.0, 3.0)
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
    lean_binary: str = "lean"       # path to Lean 4 binary (or "lean")
    lean_timeout_s: int = 60
    lean_project_root: str = ""     # directory with a Lean/mathlib project

    # ------------------------------------------------------- Prover stubs --
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
