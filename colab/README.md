# Remote DeepSeek-Prover-V2 over Google Colab

This wires a GPU-hosted **DeepSeek-Prover-V2** into the pipeline's prover
ensemble. The pipeline runs on this machine (CPU + local Lean/mathlib);
the heavy neural prover runs on a Colab GPU and is reached over HTTP.

## Why this design

DeepSeek-Prover-V2 needs a GPU we don't have locally. But proof *checking* is
cheap and must be trustworthy, so we split the work:

| step | where | trust |
|------|-------|-------|
| generate a Lean 4 proof candidate | Colab GPU (this folder) | untrusted |
| **kernel-verify** the candidate against pinned mathlib | this machine (`lean_project/`) | **trusted** |

`pipeline/theorem_prover.py` (`DeepSeekProverV2` → `LocalEndpointProver`) POSTs
the goal to the Colab URL, takes back a candidate proof, and recompiles it with
`lake env lean` against our local mathlib. A conjecture only counts as *proved*
if our kernel accepts it — the remote model's own success flag is ignored. So a
flaky/hallucinating remote prover can never produce a false "proved".

## Steps

1. Open `deepseek_prover_colab.ipynb` in Google Colab, set runtime to **GPU**.
2. Upload `deepseek_prover_server.py` into the Colab session (or `wget` it from
   your fork — see the notebook's cell 3).
3. Run the cells. The tunnel cell prints a public URL like
   `https://something.trycloudflare.com`.
4. On **this** machine, before running the pipeline:
   ```python
   from config import CONFIG
   CONFIG.prover_api_url  = "https://something.trycloudflare.com"  # no trailing path
   CONFIG.prover_backends = ("lean", "deepseek")   # cheap local tactics first, then DSP-V2
   ```
   or via env: `export PROVER_API_KEY=...` if you put auth on the tunnel.
5. Run the pipeline as usual (`python run_strongest_small.py`, etc.). The
   autoprove stage will now call Colab and kernel-check the results here.

## Model size

- **DeepSeek-Prover-V2-7B** — fits a free Colab T4 (fp16/bf16). Default.
- **DeepSeek-Prover-V2-671B** — does *not* fit Colab; needs multi-GPU
  (A100/H100). Point `prover_api_url` at such a host with the same server.

## Notes / gotchas

- Colab free tunnels die when the runtime sleeps (~90 min idle, 12 h hard cap).
  For long sweeps use Colab Pro or a persistent GPU box.
- First request triggers the model download + load (a few minutes); later calls
  are fast. The pipeline timeout is `CONFIG.prover_timeout_s` (default 120s) +
  a 30s network grace — bump `prover_timeout_s` if you see timeouts on cold load.
- The server contract (`POST /v1/lean4/prove`) is generic; any prover server
  returning `{"proof": "<lean4>"}` works with `LocalEndpointProver`.
