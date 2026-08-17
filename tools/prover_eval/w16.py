#!/usr/bin/env python
"""tools/prover_eval/w16.py — whole-proof Pass@16, one model, no feedback.

W16 is the condition that compares against the conventional whole-proof
literature: 16 independent attempts, no compiler feedback, no retrieval, no
cross-attempt communication, and a challenge the model may not edit.

Each benchmark item supplies *two* declarations over one shared `Candidate`,
so a model may attempt either direction and the item counts as resolved when
either is kernel-verified. Which direction verified is recorded, not collapsed:
against a labelled gold item, a verified proof of the wrong direction is not a
success but evidence that the formalization is unsound, and that is the single
most valuable signal this run can produce.

Two guards matter more than the score:

  * every accepted proof is re-checked with the axiom probe, so a `sorryAx`
    reached through a helper lemma cannot pass as a proof;
  * identical candidate proofs are verified once, because 16 samples of a
    deterministic-ish model repeat heavily and Lean is the expensive part.

Usage:
    python tools/prover_eval/w16.py --model oprover-32b --partition gold
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from config import CONFIG  # noqa: E402

PROMPT = """You are completing a Lean 4 theorem in a fixed trusted project.

Return exactly one <answer> block containing only a proof term beginning
with "by".

Do not:
- alter the theorem statement,
- redefine any invariant,
- use sorry or admit,
- declare axioms,
- modify imports,
- use unsafe declarations.

Trusted Lean source:

```lean
{source}
```

Complete the declaration `{target}`.

<answer>
by
  ...
</answer>
"""

_ANSWER = re.compile(r"<answer>(.*?)</answer>", re.S)
# `lean4` must be tried before `lean`, and the tag must be consumed exactly.
# The original `(?:lean)?\s*` matched "lean" inside "```lean4" and then stopped,
# because "4" is not whitespace — so the captured body began "4\n..." and failed
# every downstream check. OProver-8B writes ```lean4 in 60% of replies and
# DeepSeek-7B in 57%, while Goedel-32B writes plain ```lean in 96%, so the bug
# penalised models by which tag they happened to use. Re-scoring every saved
# reply through the fix moved candidate counts a lot (DeepSeek 72 -> 102,
# OProver-8B 11 -> 25) but changed no model's resolution count: Goedel-32B still
# 3, everyone else still 0. The ranking was not an artefact of this regex.
_FENCE = re.compile(r"```(?:lean4|lean)?[^\S\n]*\n?(.*?)```", re.S)
# Reasoning models (OProver and Goedel are Qwen3-style) spend tokens inside
# <think> before answering. Left in place it swamps the parse — and if the token
# budget expires mid-thought there is no answer at all, which is why the budget
# has to be generous for these models rather than the 4096 a one-shot prover
# would need.
_THINK = re.compile(r"<think>.*?</think>", re.S)
_OPEN_THINK = re.compile(r"<think>.*", re.S)
_BY_TAIL = re.compile(r"^\s*(by\b.*)$", re.S)
# Anything that would make a "proof" vacuous. The axiom probe catches these
# even when they are reached indirectly, but rejecting them at the source is
# cheaper and gives a clearer status than a failed audit.
_BANNED = re.compile(r"\b(sorry|admit|axiom|unsafe|native_decide)\b")


def extract_proof(text: str):
    """The proof term from a model reply, or None.

    Tried in order of how much the reply respected the contract: an explicit
    <answer> block, then a fenced Lean block, then a bare `by ...` tail. The
    fallbacks matter — scoring a model as zero because it wrote a correct proof
    in a code fence rather than the requested tag would measure this parser
    rather than the prover.
    """
    text = _THINK.sub("", text or "")
    text = _OPEN_THINK.sub("", text)      # truncated mid-thought: nothing usable after
    m = _ANSWER.search(text)
    body = m.group(1) if m else None
    if body is None:
        fences = _FENCE.findall(text)
        body = fences[-1] if fences else None      # the last block is the answer
    if body is None:
        m = _BY_TAIL.search(text.strip())
        body = m.group(1) if m else None
    if body is None:
        return None
    body = body.strip()
    if body.startswith("```"):
        body = _FENCE.sub(r"\1", body).strip()
    # Prover-style models routinely return the whole declaration rather than the
    # bare term we asked for (`theorem foo : C := by ...`). Rejecting that would
    # score a correct proof as a failure to follow instructions, so take what
    # follows the last top-level `:=`.
    if body.startswith("theorem") or body.startswith("lemma") \
            or body.startswith("example"):
        idx = body.find(":=")
        if idx == -1:
            return None
        body = body[idx + 2:].strip()
    if not body.startswith("by"):
        if not body.startswith(":="):
            return None
        body = body[2:].strip()
        if not body.startswith("by"):
            return None
    return body


def is_timeout(log: str) -> bool:
    """True when Lean ran out of wall-clock rather than rejecting the proof.

    `_run_lean` returns (False, str(exc)) for a TimeoutExpired, so a timeout is
    indistinguishable from a refutation at the call site unless the message is
    inspected. That conflation is not cosmetic: verification here is timing
    sensitive enough that one proof timed out at 900s and verified in 25s once
    the page cache was warm, so a valid proof can be recorded as a failure and
    counted against the model.
    """
    return "timed out after" in (log or "")


def build_solution(challenge: str, target: str, proof: str) -> str:
    """The challenge with `target`'s `sorry` replaced by the model's proof.

    The other declaration is dropped: leaving it in would make the file fail on
    its own untouched `sorry` and mask the result for the one under test.
    """
    out, keep = [], True
    for block in challenge.split("\n\ntheorem "):
        if not out:
            out.append(block)
            continue
        keep = block.startswith(target)
        if keep:
            out.append("theorem " + block.replace("by\n  sorry", proof, 1))
    return "\n\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="served-model-name")
    ap.add_argument("--url", default=os.environ.get(
        "VLLM_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--benchmark", default="benchmark")
    ap.add_argument("--partition", default="gold")
    ap.add_argument("--attempts", type=int, default=16)
    # Frozen at 12288: the six recorded W16 runs used it, and W16-vs-F16 is a
    # paired comparison, so changing it here would confound the feedback effect
    # with a budget effect. It is *not* generous — finish_reason shows ~50% of
    # OProver and Goedel samples truncated, so the advertised Pass@16 is nearer
    # Pass@8 for them, and both Goedel-32B successes came at attempts 11 and 13.
    # Raising it is a separate ablation that must re-run every model, not a
    # silent edit between conditions.
    ap.add_argument("--max-tokens", type=int, default=12288)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--lean-workers", type=int, default=8)
    ap.add_argument("--lean-timeout", type=int, default=600)
    ap.add_argument("--limit", type=int, default=None)
    # Output suffix. The 12288-token results are the frozen comparison set; a
    # budget ablation writing to the same paths would destroy the baseline it
    # is meant to be compared against.
    ap.add_argument("--tag", default="", help="suffix for output filenames")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    CONFIG.lean_timeout_s = args.lean_timeout

    import requests
    from pipeline.theorem_prover import LeanSubprocessProver

    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean available — refusing to score unverifiable proofs.")
        return 2

    root = os.path.join(args.benchmark, f"challenges_{args.partition}")
    index = json.load(open(os.path.join(root, "index.json")))
    if args.limit:
        index = index[:args.limit]
    print(f"W16 | model={args.model} | partition={args.partition} | "
          f"{len(index)} items x 2 directions x {args.attempts} attempts")

    lock = threading.Lock()
    results = []
    t_start = time.time()

    # Every raw completion is written out. Re-scoring a 2-hour run must never
    # require re-running it: the first pass here was discarded precisely because
    # only truncated samples of the *failures* had been kept, which made the
    # parser and the models impossible to tell apart after the fact.
    suffix = f"_{args.tag}" if args.tag else ""
    raw_path = os.path.join(
        args.benchmark, f"raw_{args.partition}_{args.model}{suffix}.jsonl")
    raw_fh = open(raw_path, "w")

    def generate(source: str, target: str, n: int):
        """n independent samples; returns (texts, prompt_tok, completion_tok)."""
        payload = {"model": args.model,
                   "messages": [{"role": "user",
                                 "content": PROMPT.format(source=source,
                                                          target=target)}],
                   "n": n, "temperature": args.temperature,
                   "max_tokens": args.max_tokens}
        r = requests.post(f"{args.url}/v1/chat/completions", json=payload,
                          timeout=3600)
        r.raise_for_status()
        d = r.json()
        usage = d.get("usage", {})
        # `finish_reason` is the only thing separating "ran out of tokens
        # mid-reasoning" from "finished and chose not to emit a proof". Without
        # it a zero score is uninterpretable, and these provers emit thousands
        # of tokens of prose before any Lean appears.
        return ([c["message"]["content"] for c in d["choices"]],
                usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0),
                [c.get("finish_reason") for c in d["choices"]])

    for n, item in enumerate(index, 1):
        challenge = open(os.path.join(root, item["file"])).read()
        rec = {"id": item["id"], "statement": item["statement"],
               "label": item["label"], "stratum": item["stratum"],
               "model": args.model, "condition": "W16",
               "status": "unresolved", "verified_direction": None,
               "attempts_used": 0, "prompt_tokens": 0, "completion_tokens": 0,
               "lean_calls": 0, "lean_timeouts": 0, "first_success_attempt": None}

        for direction in ("prove", "refute"):
            target = f"{direction}_{item['id']}"
            try:
                texts, ptok, ctok, finishes = generate(challenge, target,
                                                       args.attempts)
            except Exception as exc:
                rec["status"] = "generation_error"
                rec["error"] = str(exc)[:200]
                break
            for i_s, (txt, fr) in enumerate(zip(texts, finishes)):
                raw_fh.write(json.dumps({"id": item["id"], "direction": direction,
                                         "sample": i_s, "finish_reason": fr,
                                         "text": txt}) + "\n")
            raw_fh.flush()
            rec["prompt_tokens"] += ptok
            rec["completion_tokens"] += ctok
            rec["attempts_used"] += len(texts)

            # Dedup: verify each distinct proof once, keeping the earliest
            # attempt index so Pass@k stays meaningful.
            candidates = {}
            for i, text in enumerate(texts):
                proof = extract_proof(text or "")
                if not proof or _BANNED.search(proof):
                    continue
                candidates.setdefault(proof, i)

            if not candidates:
                # No parseable proof from any attempt. That is either a real
                # model failure or a parser/budget bug, and the two are
                # indistinguishable from the counters alone — so keep one raw
                # reply to tell them apart afterwards.
                # Keep the TAIL: any <answer> block lives at the end of the
                # reply, so storing the head hides exactly the evidence needed.
                rec.setdefault("unparsed_tail", (texts[0] or "")[-2000:])
                rec.setdefault("unparsed_head", (texts[0] or "")[:600])
                rec.setdefault("unparsed_directions", []).append(direction)
                for fr in finishes:
                    rec.setdefault("finish_reasons", {})
                    rec["finish_reasons"][fr] = rec["finish_reasons"].get(fr, 0) + 1
                continue

            def check(proof_and_idx):
                proof, idx = proof_and_idx
                src = build_solution(challenge, target, proof)
                ok, log = lean._run_lean(src, audit_axioms=True)
                return ok, idx, proof, log

            with cf.ThreadPoolExecutor(max_workers=args.lean_workers) as pool:
                for ok, idx, proof, log in pool.map(check, candidates.items()):
                    with lock:
                        rec["lean_calls"] += 1
                        if not ok and is_timeout(log):
                            rec["lean_timeouts"] = rec.get("lean_timeouts", 0) + 1
                    if ok:
                        best = rec["first_success_attempt"]
                        if best is None or idx < best:
                            rec["first_success_attempt"] = idx
                            rec["verified_direction"] = direction
                            rec["proof"] = proof
                        rec["status"] = ("formally_proved" if direction == "prove"
                                         else "formally_refuted")
            if rec["verified_direction"]:
                break        # resolved; the other direction is moot

        # A verified proof pointing the other way than the label is the finding,
        # not a scoring detail — surface it in the status itself.
        if rec["verified_direction"] and rec["label"] in ("true", "false"):
            expected = "prove" if rec["label"] == "true" else "refute"
            if rec["verified_direction"] != expected:
                rec["status"] = "WRONG_DIRECTION_VERIFIED"

        results.append(rec)
        print(f"[{n}/{len(index)}] {rec['status']:26s} "
              f"attempt={rec['first_success_attempt']} "
              f"lean={rec['lean_calls']:3d} {item['statement'][:52]}",
              flush=True)

    raw_fh.close()
    elapsed = time.time() - t_start
    out = args.out or os.path.join(
        args.benchmark, f"w16_{args.partition}_{args.model}{suffix}.json")
    with open(out, "w") as fh:
        json.dump({"model": args.model, "condition": "W16",
                   "partition": args.partition, "attempts": args.attempts,
                   "max_tokens": args.max_tokens, "tag": args.tag,
                   "wall_s": round(elapsed, 1), "results": results}, fh, indent=1)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"\nW16 {args.model} on {args.partition}: {len(results)} items in "
          f"{elapsed / 60:.0f} min")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:28s} {v}")
    print(f"  completion tokens: {sum(r['completion_tokens'] for r in results)}")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
