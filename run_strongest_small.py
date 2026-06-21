#!/usr/bin/env python3
"""Run the full pipeline with the strongest *feasible* hyperparameters on a small
dataset (the 340-graph TxGraffiti corpus). graffiti3 is held at FAST mode because
STANDARD/DEEP do not finish even on tiny data."""
import run_parallel
from config import CONFIG

# --- small dataset ---
CONFIG.db_csv_paths = ("database/txgraffiti_data.csv",)

# --- strongest linear generation: both engines, multivariable, high budget ---
CONFIG.txgraffiti_engine = "both"            # numpy grid fit + txgraffiti optimal coeffs (+LP)
CONFIG.txgraffiti_multivariable = True
CONFIG.txgraffiti_max_rhs_terms = 2
CONFIG.txgraffiti_condition_on_classes = True
CONFIG.txgraffiti_filter_known = True

# --- graffiti3 nonlinear stage (FAST) + Sophie ---
CONFIG.graffiti3_enabled = True
CONFIG.graffiti3_mode = "fast"
CONFIG.graffiti3_sophie = True
CONFIG.graffiti3_max_n = 7
CONFIG.graffiti3_max_per_target = 60
CONFIG.graffiti3_refute_random = True

# --- Sage stage with optimal-coefficient tuning ---
CONFIG.sage_enabled = True
CONFIG.sage_tune_coefficients = True

# --- strongest refutation: structured pool + class-aware random models ---
CONFIG.adversarial_random_models = True
CONFIG.adversarial_random_per = 8

CONFIG.report_sort_by = "complexity"

if __name__ == "__main__":
    run_parallel.main(["--rounds", "3", "--max-conjectures", "500",
                       "--gen-workers", "4", "--attack-workers", "8",
                       "--search-n", "14"])
