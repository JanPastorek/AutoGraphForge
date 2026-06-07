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

    # ----------------------------------------------- Hypothesis generation --
    txgraffiti_max_conjectures: int = 30
    txgraffiti_max_offset: float = 5.0
    txgraffiti_coefficients: tuple = (0.5, 1.0, 1.5, 2.0, 3.0)
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
