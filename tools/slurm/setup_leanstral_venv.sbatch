#!/bin/bash
#SBATCH --job-name=leanstral_venv
#SBATCH --partition=cpu_long
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=results/leanstral_venv_%j.log
#SBATCH --error=results/leanstral_venv_%j.log

# Leanstral needs a newer vLLM and mistral_common than the shared prover venv
# (which pins vllm 0.23.0 / mistral_common 1.11.4 and dies with
# "MistralCommonImageProcessor has no attribute 'fetch_images'"). It gets its
# own environment rather than an upgrade in place: the other six models are
# already validated against .venv-prover and must not move underneath them.

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

VENV="$PWD/.venv-leanstral"
export HF_HOME="$PWD/.hf_home"

python3.11 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip wheel
"$VENV/bin/pip" install --upgrade "vllm>=0.24.0" "mistral_common>=1.11.5" openai requests

"$VENV/bin/python" - <<'PY'
import vllm, mistral_common
print("vllm", vllm.__version__)
print("mistral_common", mistral_common.__version__)
PY
echo "leanstral venv ready at $VENV"
