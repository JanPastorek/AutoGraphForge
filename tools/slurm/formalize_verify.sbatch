#!/bin/bash
#SBATCH --job-name=formalize
#SBATCH --partition=cpu_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=results/formalize_%j.log
#SBATCH --error=results/formalize_%j.log

# Rebuild the two Lean layers after adding invariants, then differential-test
# every new definition against graphcalc.
#
# Both halves are heavy: elaborating a Mathlib-importing module takes minutes,
# and the differential test is thousands of `decide` evaluations. Neither may
# run on the login node.
#
# NEVER `lake build` here — its resolver deletes and re-clones mathlib, which on
# a node without git leaves no mathlib at all. rebuild_leanproject.py uses bare
# `lean` + LEAN_PATH for exactly that reason.
#
#   sbatch tools/slurm/formalize_verify.sbatch [MAX_N]

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

MAX_N="${1:-6}"

echo "=== [1/2] rebuilding LeanProject modules ==="
.venv/bin/python -u tools/prover_eval/checks/rebuild_leanproject.py || {
    echo "REBUILD FAILED — the new definitions do not elaborate; stopping."
    exit 1
}

echo
echo "=== [2/2] differential test against graphcalc (n <= ${MAX_N}) ==="
.venv/bin/python -u tools/lean_differential.py \
    --max-n "$MAX_N" --timeout 72000 \
    --keep "results/lean_differential_${SLURM_JOB_ID}.lean"
