#!/bin/bash
#SBATCH --job-name=gpu_probe
#SBATCH --partition=gpu_short
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --time=00:15:00
#SBATCH --output=results/gpu_probe_%j.log
#SBATCH --error=results/gpu_probe_%j.log

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

echo "=== nvidia-smi ==="
nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv

echo "=== torch CUDA sanity ==="
.venv-prover/bin/python - <<'PY'
import torch
print("cuda available:", torch.cuda.is_available())
print("device count:", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    p = torch.cuda.get_device_properties(i)
    print(f"  gpu{i}: {p.name}  {p.total_memory/1e9:.1f} GB")
PY
