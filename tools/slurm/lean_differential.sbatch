#!/bin/bash
#SBATCH --job-name=lean_diff
#SBATCH --partition=cpu_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=results/leandiff_%j.log
#SBATCH --error=results/leandiff_%j.log

# Differential-test graphcalc against the Lean kernel on a compute node.
# This is hours of `decide` evaluation across thousands of examples and must
# not run on the login node.
#
#   sbatch tools/slurm/lean_differential.sbatch [MAX_N]

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

MAX_N="${1:-6}"
.venv/bin/python -u tools/lean_differential.py \
    --max-n "$MAX_N" --timeout 43200
