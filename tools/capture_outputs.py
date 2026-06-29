#!/usr/bin/env python3
"""
tools/capture_outputs.py — bring-up diagnostic: dump the RAW DeepSeek-Prover-V2
output for the first N exportable survivors so we can see exactly what Lean the
model emits, how _extract_lean parses it, and why the kernel-check passes/fails.

Validity debugging only (not a prove run). Writes a human-readable dump to
results/capture_outputs.txt. Uses the same prompt/extraction as the shim, calls
vLLM directly (greedy), and kernel-checks via the (now bare-lean) LeanSubprocess.
"""
from __future__ import annotations
import os, sys, time, json, requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG
from pipeline.theorem_prover import DeepSeekProverLocal, LeanSubprocessProver

VLLM_URL = os.environ.get("VLLM_URL", "http://127.0.0.1:8000").rstrip("/")
VLLM_MODEL = os.environ["VLLM_MODEL"]
N = int(os.environ.get("CAPTURE_N", "8"))
MAXTOK = int(os.environ.get("CAPTURE_MAXTOK", "3000"))  # enough to see format + short proofs
OUT = os.path.join(CONFIG.output_dir, "capture_outputs.txt")


def main():
    import dill
    survivors = dill.load(open(os.path.join(CONFIG.output_dir, "cegis_survivors.dill"), "rb"))
    cands = [c for c in survivors if getattr(c, "lean_statement", None)][:N]
    dsl = DeepSeekProverLocal(CONFIG)
    lean = LeanSubprocessProver(CONFIG)
    print(f"[capture] LEAN_PATH ok = {bool(lean._compute_lean_path(CONFIG.lean_project_root))}")
    out = open(OUT, "w")
    parsed = realfail = verified = 0
    for i, c in enumerate(cands):
        stmt = c.lean_statement
        prompt = dsl._PROMPT.format(cheatsheet=dsl._retrieved_cheatsheet(stmt), stmt=stmt)
        t0 = time.time()
        try:
            r = requests.post(f"{VLLM_URL}/v1/chat/completions", json={
                "model": VLLM_MODEL, "messages": [{"role": "user", "content": prompt}],
                "max_tokens": MAXTOK, "temperature": 0.0}, timeout=2400)
            raw = r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raw = f"<<vLLM call failed: {e}>>"
        ext = DeepSeekProverLocal._extract_lean(raw)
        code = None; ok = False; klog = ""
        if ext:
            code = ext if ext.lstrip().startswith("import") else \
                "import Mathlib\n" + CONFIG.lean_preamble_import + "\n\n" + ext
            ok, klog = lean._run_lean(code)
        if ext and "theorem" in ext: parsed += 1
        if ok: verified += 1
        elif ext and "error:" in klog and "unexpected" not in klog: realfail += 1
        dt = time.time() - t0
        for blk, label in [(stmt, "STATEMENT"), (raw, "RAW MODEL OUTPUT"),
                           (ext or "<None>", "EXTRACTED"),
                           (klog[:600], "KERNEL LOG")]:
            out.write(f"\n{'='*70}\n[{i}] {label}  (verified={ok}, {dt:.0f}s)\n{'='*70}\n{blk}\n")
        out.flush()
        print(f"[capture] {i}: extracted={bool(ext)} has_theorem={'theorem' in (ext or '')} "
              f"verified={ok} {dt:.0f}s")
    summary = f"[capture] DONE N={len(cands)} extracted_theorem={parsed} real_proof_fail={realfail} VERIFIED={verified}"
    print(summary); out.write("\n" + summary + "\n"); out.close()


if __name__ == "__main__":
    main()
