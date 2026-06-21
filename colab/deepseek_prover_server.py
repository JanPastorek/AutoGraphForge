#!/usr/bin/env python3
"""
colab/deepseek_prover_server.py
================================
Serve **DeepSeek-Prover-V2-7B** over HTTP so the GraphConjecturing pipeline's
``LocalEndpointProver`` / ``DeepSeekProverV2`` backend can call it from this
machine. Designed to run on a **Google Colab GPU** (free T4 is enough for the
7B model in 4-bit / fp16; the 671B model does *not* fit on Colab).

Contract (matches pipeline/theorem_prover.py):
  POST  <url>/v1/lean4/prove
  body  {"statement": "<lean4 theorem ... := by sorry>",
         "informal_statement": "...", "context": "import Mathlib",
         "strategy": "subgoal_decomposition", "timeout_s": 180}
  resp  {"proof": "<full lean4 file the model produced>",
         "model": "deepseek-ai/DeepSeek-Prover-V2-7B",
         "num_tokens": <int>, "error": null}

The pipeline NEVER trusts this server's output blindly — whatever ``proof`` we
return is re-compiled against the caller's pinned mathlib and only counts if it
passes the Lean kernel there. So this server just has to *produce candidates*.

Run on Colab (see deepseek_prover_colab.ipynb) or anywhere with a GPU:
    pip install fastapi uvicorn vllm transformers
    python deepseek_prover_server.py            # serves on :8000
then expose it, e.g.:
    cloudflared tunnel --url http://localhost:8000
and set, on the pipeline side:
    CONFIG.prover_api_url = "https://<tunnel-host>"   # no trailing path
    CONFIG.prover_backends = ("lean", "deepseek")     # try local tactics, then DSP-V2
"""
from __future__ import annotations

import os
import time

from fastapi import FastAPI
from pydantic import BaseModel

MODEL_ID = os.environ.get("DSP_MODEL", "deepseek-ai/DeepSeek-Prover-V2-7B")
MAX_NEW_TOKENS = int(os.environ.get("DSP_MAX_NEW_TOKENS", "8192"))

# DeepSeek-Prover-V2 expects a Lean 4 header it can elaborate against.
LEAN_HEADER = "import Mathlib\nimport Aesop\nset_option maxHeartbeats 400000\n"

# Non-CoT completion prompt from the DeepSeek-Prover-V2 model card.
PROMPT_TMPL = """Complete the following Lean 4 code:

```lean4
{header}
{informal}
{formal}
```
""".strip()

app = FastAPI(title="DeepSeek-Prover-V2 server")
_llm = None          # vllm.LLM, lazily initialised
_sampling = None
_tokenizer = None


def _load():
    """Load the model once. Prefers vLLM; falls back to transformers."""
    global _llm, _sampling, _tokenizer
    if _llm is not None:
        return
    from transformers import AutoTokenizer
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    try:
        from vllm import LLM, SamplingParams
        _llm = LLM(model=MODEL_ID, trust_remote_code=True,
                   max_model_len=int(os.environ.get("DSP_MAX_LEN", "16384")),
                   gpu_memory_utilization=0.92, dtype="bfloat16")
        _sampling = SamplingParams(temperature=0.0, max_tokens=MAX_NEW_TOKENS,
                                   top_p=0.95)
        _llm._backend = "vllm"
    except Exception as e:                       # pragma: no cover - env dependent
        print(f"[server] vLLM unavailable ({e}); using transformers")
        import torch
        from transformers import AutoModelForCausalLM
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID, torch_dtype=torch.bfloat16, device_map="auto",
            trust_remote_code=True)
        _llm = ("hf", model)
        _sampling = None


def _generate(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    text = _tokenizer.apply_chat_template(messages, tokenize=False,
                                          add_generation_prompt=True)
    if getattr(_llm, "_backend", None) == "vllm":
        out = _llm.generate([text], _sampling)
        return out[0].outputs[0].text
    # transformers fallback
    import torch
    _, model = _llm
    inputs = _tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        gen = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS,
                             do_sample=False, temperature=None, top_p=None)
    return _tokenizer.decode(gen[0][inputs["input_ids"].shape[1]:],
                             skip_special_tokens=True)


def _extract_lean(text: str) -> str:
    """Pull the ```lean4 ...``` block out of the model's reply (else raw text)."""
    import re
    m = re.search(r"```lean4?\s*(.*?)```", text, re.DOTALL)
    body = (m.group(1) if m else text).strip()
    # ensure the snippet is self-contained (caller compiles it as a whole file)
    if not body.lstrip().startswith("import"):
        body = LEAN_HEADER + "\n" + body
    return body


class ProveRequest(BaseModel):
    statement: str
    informal_statement: str = ""
    context: str = "import Mathlib"
    strategy: str = "subgoal_decomposition"
    timeout_s: int = 180


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL_ID, "loaded": _llm is not None}


@app.post("/v1/lean4/prove")
def prove(req: ProveRequest):
    t0 = time.time()
    try:
        _load()
        informal = f"-- {req.informal_statement}" if req.informal_statement else ""
        # strip a trivial `:= by sorry` tail so the model writes the proof body
        formal = req.statement.replace(":= by sorry", "").replace(":= sorry", "").rstrip()
        prompt = PROMPT_TMPL.format(header=LEAN_HEADER, informal=informal, formal=formal)
        raw = _generate(prompt)
        proof = _extract_lean(raw)
        return {"proof": proof, "model": MODEL_ID,
                "num_tokens": len(proof.split()), "error": None,
                "elapsed_s": round(time.time() - t0, 1)}
    except Exception as e:                                    # pragma: no cover
        return {"proof": None, "model": MODEL_ID, "num_tokens": 0,
                "error": f"{type(e).__name__}: {e}",
                "elapsed_s": round(time.time() - t0, 1)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
