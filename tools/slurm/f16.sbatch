#!/bin/bash
#SBATCH --job-name=f16
#SBATCH --partition=gpu_short
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=64
#SBATCH --time=2-00:00:00
#SBATCH --output=results/f16_%x_%j.log
#SBATCH --error=results/f16_%x_%j.log

# Compiler-feedback loop (4 branches x 4 rounds) for one or more models on one benchmark partition.
#
#   sbatch tools/slurm/w16.sbatch gold Pythagoras-Prover-4B DeepSeek-Prover-V2-7B
#
# Models run *sequentially* inside one job because this account is capped at 4
# concurrent nodes. Fanning out one model per node hits the cap at three models
# and the rest are rejected outright rather than queued, so batching them here
# is what actually gets all seven run.
#
# A model that fails to serve is logged and skipped; one bad checkpoint must not
# cost the whole batch.

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

PARTITION="${1:?usage: w16.sbatch <partition> <model> [model...]}"
shift
[ "$#" -ge 1 ] || { echo "ERROR: no models given"; exit 1; }

export PATH="$PWD/.venv-prover/bin:$PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0

# vLLM JIT-compiles fp8 kernels at runtime against the nvidia-cu13 wheel, which
# is not laid out like a real CUDA install: headers are off the default include
# path and only versioned `libX.so.NN` ship (no unversioned target for `-lX`, no
# driver stub). Expose both to the compiler without polluting the runtime
# loader — putting these on PATH/LD_LIBRARY_PATH previously broke NCCL init.
CU13="$PWD/.venv-prover/lib/python3.11/site-packages/nvidia/cu13"
LINKDIR="$PWD/.venv-prover/cuda_link"
mkdir -p "$LINKDIR"
for so in "$CU13"/lib/*.so.*; do
    [ -e "$so" ] || continue
    base="$(basename "$so")"; stem="${base%%.so.*}"
    ln -sf "$so" "$LINKDIR/${stem}.so"
done
drv=$(ldconfig -p 2>/dev/null | awk '/libcuda\.so\.1 /{print $NF; exit}')
[ -z "$drv" ] && drv=$(ls /usr/lib64/libcuda.so.1 2>/dev/null | head -1)
[ -n "$drv" ] && ln -sf "$drv" "$LINKDIR/libcuda.so"
export CPATH="$CU13/include:${CPATH:-}"
export LIBRARY_PATH="$LINKDIR:${LIBRARY_PATH:-}"

VLLM_PID=""
cleanup() { [ -n "$VLLM_PID" ] && kill "$VLLM_PID" 2>/dev/null; wait 2>/dev/null; }
trap cleanup EXIT

PORT=$((8000 + SLURM_JOB_ID % 900))

for MODEL_NAME in "$@"; do
    MODEL_DIR="$PWD/.hf_cache/${MODEL_NAME}"
    if [ ! -d "$MODEL_DIR" ]; then
        echo "SKIP $MODEL_NAME: no such directory $MODEL_DIR"; continue
    fi

    # Tensor parallelism by footprint on 143 GB H200s. Leanstral is an MoE whose
    # card specifies 4; the 32Bs fit on one card but get 2 for KV headroom.
    case "$MODEL_NAME" in
        Leanstral*) TP=4 ;;
        *32B*)      TP=2 ;;
        *)          TP=1 ;;
    esac

    # `--gpu-memory-utilization` is a fraction of TOTAL memory, and vLLM refuses
    # to start when free < util*total. Hard-coding 0.90 therefore fails outright
    # on a card that is not pristine — gpu02 held 82 GiB from a foreign process
    # and killed three models in a row while gpu03/gpu04 ran fine. Size the
    # request to what is actually free, leaving 4 GiB of headroom.
    read -r FREE_MIB TOTAL_MIB < <(
        nvidia-smi --query-gpu=memory.free,memory.total \
                   --format=csv,noheader,nounits -i 0 2>/dev/null | tr ',' ' ')
    UTIL=0.90
    if [ -n "${FREE_MIB:-}" ] && [ -n "${TOTAL_MIB:-}" ] && [ "$TOTAL_MIB" -gt 0 ]; then
        UTIL=$(awk -v f="$FREE_MIB" -v t="$TOTAL_MIB" \
                   'BEGIN{u=(f-4096)/t; if(u>0.90)u=0.90; printf "%.2f", u}')
        echo "GPU0 free ${FREE_MIB}/${TOTAL_MIB} MiB -> --gpu-memory-utilization $UTIL"
    fi
    if awk -v u="$UTIL" 'BEGIN{exit !(u < 0.10)}'; then
        echo "SKIP $MODEL_NAME: only ${FREE_MIB:-?} MiB free on GPU0, not enough to serve"
        continue
    fi

    PORT=$((PORT + 1))
    echo "############ $MODEL_NAME (TP=$TP, port $PORT, util $UTIL) ############"
    .venv-prover/bin/python -m vllm.entrypoints.openai.api_server \
        --model "$MODEL_DIR" \
        --served-model-name "$MODEL_NAME" \
        --tensor-parallel-size "$TP" \
        --dtype bfloat16 \
        --trust-remote-code \
        --max-model-len 32768 \
        --gpu-memory-utilization "$UTIL" \
        --max-num-seqs 32 \
        --port "$PORT" \
        > "results/vllm_${MODEL_NAME}_${SLURM_JOB_ID}.log" 2>&1 &
    VLLM_PID=$!

    ok=0
    for i in $(seq 1 360); do
        if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
            echo "vLLM ready after $((i*10))s"; ok=1; break
        fi
        if ! kill -0 "$VLLM_PID" 2>/dev/null; then
            echo "ERROR: vLLM exited before becoming healthy for $MODEL_NAME"
            tail -25 "results/vllm_${MODEL_NAME}_${SLURM_JOB_ID}.log"
            break
        fi
        sleep 10
    done

    if [ "$ok" -eq 1 ]; then
        .venv/bin/python -u tools/prover_eval/f16.py \
            --model "$MODEL_NAME" \
            --url "http://127.0.0.1:${PORT}" \
            --partition "$PARTITION" \
            --branches 4 --rounds 4
    else
        echo "SKIP $MODEL_NAME: server never became healthy (not scoring against a dead server)"
    fi

    kill "$VLLM_PID" 2>/dev/null; wait "$VLLM_PID" 2>/dev/null
    VLLM_PID=""
    sleep 20        # let GPU memory actually free before the next model loads
done

echo "=== batch complete ==="
