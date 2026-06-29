#!/usr/bin/env python3
"""
tools/run_prove.py — Phase 4 driver: prove the merged survivors via the
DeepSeek-Prover-V2-671B vLLM server + tools/prover_shim.py.

Run after the vLLM server (see tools/slurm/prove_671b.sbatch) and the shim
are both up and healthy. Wires CONFIG to the new "deepseek-671b" backend
(pipeline/theorem_prover.PROVER_REGISTRY) and calls run_cegis's --reprove
path, which loads results/cegis_survivors.dill (written by merge_shards.py)
and attempts proving the top-N simplest survivors.

Usage:
    SHIM_URL=http://127.0.0.1:8800 python tools/run_prove.py --prove-top 100
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove-top", type=int, default=100)
    ap.add_argument("--time-budget-h", type=float, default=15.0,
                    help="self-limit so the prove loop persists results before "
                         "the SLURM --time kill")
    args = ap.parse_args(argv)

    shim_url = os.environ.get("SHIM_URL", "http://127.0.0.1:8800")
    CONFIG.prover_api_url = shim_url
    # deepseek-671b only: the `lean` tactic backend (decide/simp/omega/...) can't
    # close graph-theory inequalities yet still spends ~2-4 min/conjecture on full
    # `import Mathlib` compiles — ~2h of pure waste over 43 survivors. The shim
    # does its own kernel-check on each model candidate anyway.
    CONFIG.prover_backends = ("deepseek-671b",)
    CONFIG.prove_time_budget_s = int(args.time_budget_h * 3600)

    import run_cegis
    return run_cegis.main(["--reprove", "--prove-top", str(args.prove_top)])


if __name__ == "__main__":
    sys.exit(main())
