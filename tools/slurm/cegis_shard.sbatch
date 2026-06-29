#!/bin/bash
#SBATCH --job-name=cegis_shard
#SBATCH --partition=cpu_long
#SBATCH --array=0-4
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --cpus-per-task=256
#SBATCH --time=30:00:00
#SBATCH --output=results/cegis_shard_%a_%j.log
#SBATCH --error=results/cegis_shard_%a_%j.log

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

# Self-limit a bit under the SLURM --time above so the process persists
# survivors before SLURM's hard kill (see config.cegis_time_budget_s).
export CEGIS_TIME_BUDGET_S=104400   # 29h
export CEGIS_WORKERS=240

.venv/bin/python tools/run_shard.py
