#!/bin/bash
#SBATCH --job-name=rescore
#SBATCH --partition=cpu_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=1-00:00:00
#SBATCH --output=results/rescore_%j.log
#SBATCH --error=results/rescore_%j.log
set -uo pipefail
cd "$SLURM_SUBMIT_DIR"
.venv/bin/python -u tools/prover_eval/rescore.py --partition gold --workers 24
