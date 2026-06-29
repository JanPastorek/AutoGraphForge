#!/bin/bash
#SBATCH --job-name=precompute_n9
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --cpus-per-task=256
#SBATCH --time=06:00:00
#SBATCH --output=results/precompute_n9_%j.log
#SBATCH --error=results/precompute_n9_%j.log

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
.venv/bin/python tools/precompute_battery.py \
    --max-n 9 \
    --g6 graphs/generated_nauty/graphs_9v_all.g6 \
    --workers 240
