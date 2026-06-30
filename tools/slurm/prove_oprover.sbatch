#!/bin/bash
#SBATCH --job-name=prove_oprover
#SBATCH --partition=gpu_short
#SBATCH --nodes=1
#SBATCH --gres=gpu:8
#SBATCH --time=2-00:00:00
#SBATCH --output=results/prove_671b_%j.log
#SBATCH --error=results/prove_671b_%j.log

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"

MODEL_DIR="$PWD/.hf_cache/OProver-32B"
VLLM_PORT=8000
SHIM_PORT=8800
export VLLM_URL="http://127.0.0.1:${VLLM_PORT}"
export VLLM_MODEL="$MODEL_DIR"
export SHIM_URL="http://127.0.0.1:${SHIM_PORT}"
# vLLM JIT-compiles fp8 MoE / GEMM kernels at runtime, which needs BOTH `ninja`
# (build driver) and `nvcc` (CUDA compiler). Put the venv bin (ninja) and the
# bundled CUDA toolkit bin (nvcc/ptxas, from the nvidia-cu13 wheel) on PATH, and
# set CUDA_HOME so nvcc finds its headers/libs. Also disable the flashinfer
# top-k/top-p sampler (its own JIT kernel) to use the native PyTorch sampler.
# Fast inference (DeepGEMM fp8 kernels) needs the CUDA toolchain (nvcc + cicc +
# ptxas) for its runtime JIT. We expose it via an `nvcc` *wrapper* in the venv
# bin (tools/.../nvcc) that prepends the CUDA-wheel bin to PATH for the compile
# subprocess only — so the JIT works WITHOUT cu13/bin on the global PATH, which
# previously broke vLLM's NCCL worker init. DeepGEMM stays enabled (the big MoE
# speedup; Triton fp8 alone was ~4 tok/s). Only the flashinfer sampler is left
# off (native sampler; avoids one more JIT path we don't need).
export PATH="$PWD/.venv-prover/bin:$PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0
# OProver is a Qwen3 thinking model: it spends tokens in <think> before the
# proof, so give generation more headroom than the 671B's 4096. The 33B is fast
# (TP=2) so this still completes well inside the shim's 2400s timeout.
export DEEPSEEK_MAX_TOKENS=8192
# Use OProver as designed: the agentic multi-round compiler-feedback loop (its
# core strength, +5-7 Pass@32 per the paper) instead of independent pass@k. The
# shim grounds the Reference slot with the custom GraphInvariants definitions.
export AGENTIC_ROUNDS=6
export PROVER_NAME=oprover-32b

# vLLM/flashinfer/DeepGEMM JIT-compile fp8 kernels at *runtime* (host c++ AND
# device nvcc steps), but the nvidia-cu13 wheel isn't laid out like a real CUDA
# install, so each compiler search path is broken in a different way:
#   - HEADERS: the host c++ steps need <cuda_fp16.h>/<cublasLt.h> etc., which a
#     real CUDA_HOME would put on the default include path; the wheel does not.
#     Run 53607 died on the first inference with "fatal error: cuda_fp16.h: No
#     such file or directory". Fix via CPATH (gcc consults it at *compile* time
#     only — safe, unlike PATH/LD_LIBRARY_PATH which broke NCCL init before).
#   - LINK LIBS: the wheel ships only versioned `libX.so.NN` (no unversioned
#     `libX.so` that `-lX` needs) and no `libcuda.so` driver stub, and
#     flashinfer hardcodes `-L<venv>/lib64`. Run 53605 died at "ld: cannot find
#     -lcudart". Stage unversioned symlinks for EVERY cu13 lib (+ the node's
#     real driver libcuda.so) in one dir on LIBRARY_PATH (gcc *link* time only).
# Together these expose the wheel's toolchain to JIT without polluting runtime.
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
if [ -n "$drv" ]; then ln -sf "$drv" "$LINKDIR/libcuda.so"; echo "libcuda.so -> $drv"; \
  else echo "WARNING: no driver libcuda.so.1 found for link stub"; fi
export CPATH="$CU13/include:${CPATH:-}"
export LIBRARY_PATH="$LINKDIR:${LIBRARY_PATH:-}"
echo "CPATH=$CPATH"; echo "LIBRARY_PATH=$LIBRARY_PATH"; echo "linkdir libs: $(ls "$LINKDIR" | wc -l)"

VLLM_PID=""
SHIM_PID=""
cleanup() {
    echo "=== tearing down vLLM server + shim ==="
    [ -n "$SHIM_PID" ] && kill "$SHIM_PID" 2>/dev/null
    [ -n "$VLLM_PID" ] && kill "$VLLM_PID" 2>/dev/null
}
trap cleanup EXIT

echo "=== starting vLLM server (tensor-parallel-size 8) ==="
# --enforce-eager is KEPT deliberately: it's the exact config run 53616 used to
# load + generate end-to-end (~3.5 tok/s solo, ~8-10 tok/s batched). Reliability
# is the priority now that the verifier (mathlib) is finally fixed — we want a
# dependable verified signal, not a faster startup that risks a new cudagraph-
# capture failure. SPEED OPTIMIZATION (future): removing --enforce-eager enables
# CUDA-graph capture, which eliminates the per-token kernel-launch overhead that
# caps single-stream decode on this 671B MoE — the real decode-speed lever
# (DeepGEMM only speeds the GEMM math). Switch once verified counts are in hand.
.venv-prover/bin/vllm serve "$MODEL_DIR" \
    --served-model-name "$MODEL_DIR" \
    --tensor-parallel-size 2 \
    --trust-remote-code \
    --enforce-eager \
    --max-num-seqs 16 \
    --port "$VLLM_PORT" \
    > results/vllm_server_${SLURM_JOB_ID}.log 2>&1 &
VLLM_PID=$!

echo "=== waiting for vLLM /health (up to 60 min) ==="
vllm_ok=0
for i in $(seq 1 360); do
    if curl -sf "http://127.0.0.1:${VLLM_PORT}/health" > /dev/null 2>&1; then
        echo "vLLM ready after $((i*10))s"; vllm_ok=1; break
    fi
    # abort early if the server process died
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
        echo "ERROR: vLLM process exited before becoming healthy"; exit 1
    fi
    sleep 10
done
if [ "$vllm_ok" -ne 1 ]; then
    echo "ERROR: vLLM never became healthy within 60 min — aborting (not proving against a dead server)"
    exit 1
fi

echo "=== starting prover_shim ==="
.venv-prover/bin/uvicorn tools.prover_shim:app --host 127.0.0.1 --port "$SHIM_PORT" \
    > results/prover_shim_${SLURM_JOB_ID}.log 2>&1 &
SHIM_PID=$!

for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:${SHIM_PORT}/health" > /dev/null 2>&1; then
        echo "shim ready after ${i}0s"
        break
    fi
    sleep 10
done

echo "=== proving curated classical inequalities (671B baseline) ==="
.venv/bin/python tools/run_prove_curated.py

echo "=== proving the exportable machine-generated survivors (top-100) ==="
.venv/bin/python tools/run_prove.py --prove-top 100 --time-budget-h 12

# Authoritative count: re-verify every proof the shim PERSISTED, independently of
# the HTTP client (whose short timeout can drop a slow agentic proof from the live
# tally — see run 53863). This number, over the saved self-contained .lean files,
# is the one to trust and to cite.
echo "=== independent re-verification of persisted proofs ==="
.venv/bin/python tools/verify_proofs.py
