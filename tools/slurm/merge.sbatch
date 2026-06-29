#!/bin/bash
#SBATCH --job-name=merge_shards
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:30:00
#SBATCH --output=results/merge_%j.log
#SBATCH --error=results/merge_%j.log

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

.venv/bin/python tools/merge_shards.py --shards 5
