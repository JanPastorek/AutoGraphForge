#!/bin/bash
#SBATCH --job-name=g32
#SBATCH --partition=gpu_short
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=64
#SBATCH --time=2-00:00:00
#SBATCH --output=results/g32_%x_%j.log
#SBATCH --error=results/g32_%x_%j.log

# Goedel-32B at a raised token budget, on one partition.
#
#   sbatch tools/slurm/goedel32_budget.sbatch gold 24576 b24576
#
# Only Goedel-32B is run: it is the sole model with any signal (3/57 vs 0/57 for
# the other six), so spending GPU on the rest before the confounds are fixed
# buys nothing. Half its samples truncated at 12288 and both its early successes
# landed at attempts 11 and 13, so the late samples are exactly the ones the old
# budget was destroying.
#
# Outputs are tagged so the frozen 12288 baseline survives for comparison.

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

PARTITION="${1:-gold}"
MAXTOK="${2:-24576}"
TAG="${3:-b${MAXTOK}}"
MODEL_NAME="Goedel-Prover-V2-32B"
MODEL_DIR="$PWD/.hf_cache/${MODEL_NAME}"
[ -d "$MODEL_DIR" ] || { echo "ERROR: missing $MODEL_DIR"; exit 1; }

export PATH="$PWD/.venv-prover/bin:$PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0
CU13="$PWD/.venv-prover/lib/python3.11/site-packages/nvidia/cu13"
LINKDIR="$PWD/.venv-prover/cuda_link"; mkdir -p "$LINKDIR"
for so in "$CU13"/lib/*.so.*; do
    [ -e "$so" ] || continue
    b="$(basename "$so")"; ln -sf "$so" "$LINKDIR/${b%%.so.*}.so"
done
drv=$(ldconfig -p 2>/dev/null | awk '/libcuda\.so\.1 /{print $NF; exit}')
[ -n "$drv" ] && ln -sf "$drv" "$LINKDIR/libcuda.so"
export CPATH="$CU13/include:${CPATH:-}"
export LIBRARY_PATH="$LINKDIR:${LIBRARY_PATH:-}"

VLLM_PID=""
cleanup() { [ -n "$VLLM_PID" ] && kill "$VLLM_PID" 2>/dev/null; wait 2>/dev/null; }
trap cleanup EXIT

read -r FREE_MIB TOTAL_MIB < <(
    nvidia-smi --query-gpu=memory.free,memory.total \
               --format=csv,noheader,nounits -i 0 2>/dev/null | tr ',' ' ')
UTIL=0.90
if [ -n "${FREE_MIB:-}" ] && [ "${TOTAL_MIB:-0}" -gt 0 ]; then
    UTIL=$(awk -v f="$FREE_MIB" -v t="$TOTAL_MIB" \
               'BEGIN{u=(f-4096)/t; if(u>0.90)u=0.90; printf "%.2f", u}')
fi
echo "### $MODEL_NAME partition=$PARTITION max_tokens=$MAXTOK tag=$TAG util=$UTIL"

PORT=$((8000 + SLURM_JOB_ID % 900))
# Context must exceed max_tokens with room for the prompt, or generation is
# refused outright.
.venv-prover/bin/python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_DIR" --served-model-name "$MODEL_NAME" \
    --tensor-parallel-size 2 --dtype bfloat16 --trust-remote-code \
    --max-model-len 32768 --gpu-memory-utilization "$UTIL" \
    --max-num-seqs 32 --port "$PORT" \
    > "results/vllm_${MODEL_NAME}_${SLURM_JOB_ID}.log" 2>&1 &
VLLM_PID=$!

ok=0
for i in $(seq 1 360); do
    curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && { ok=1; echo "vLLM ready after $((i*10))s"; break; }
    kill -0 "$VLLM_PID" 2>/dev/null || { echo "ERROR: vLLM died"; tail -25 "results/vllm_${MODEL_NAME}_${SLURM_JOB_ID}.log"; break; }
    sleep 10
done
[ "$ok" -eq 1 ] || { echo "ERROR: server never healthy — not scoring against a dead server"; exit 1; }

.venv/bin/python -u tools/prover_eval/w16.py \
    --model "$MODEL_NAME" --url "http://127.0.0.1:${PORT}" \
    --partition "$PARTITION" --max-tokens "$MAXTOK" --tag "$TAG" \
    --lean-workers 16
echo "=== done ==="
