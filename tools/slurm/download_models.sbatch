#!/bin/bash
#SBATCH --job-name=dl_provers
#SBATCH --partition=cpu_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=1-00:00:00
#SBATCH --output=results/download_%j.log
#SBATCH --error=results/download_%j.log

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

export HF_HOME="$PWD/.hf_home"
export HF_HUB_ENABLE_HF_TRANSFER=0
mkdir -p "$HF_HOME"

# 671B is excluded on purpose: see tools/prover_eval/download_models.py.
.venv-prover/bin/python tools/prover_eval/download_models.py \
    --root "$PWD/.hf_cache"

echo "downloads finished"
df -h "$PWD" | tail -1
