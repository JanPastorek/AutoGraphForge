#!/bin/bash
#SBATCH --job-name=t0_baseline
#SBATCH --partition=cpu_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=results/t0_%j.log
#SBATCH --error=results/t0_%j.log

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

# `maxHeartbeats 0` means a pathological witness runs until the subprocess
# timeout rather than failing fast, so give each item real headroom.
for P in gold frontier; do
    echo "=== T0 on $P ==="
    .venv/bin/python -u tools/prover_eval/t0_baseline.py \
        --partition "$P" --timeout 1800
done
