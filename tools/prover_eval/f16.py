#!/usr/bin/env python
"""tools/prover_eval/f16.py — fixed compiler-feedback loop, 4 branches x 4 rounds.

W16 asks a prover for sixteen independent guesses. F16 spends the same sixteen
model calls differently: four independent branches, each given four rounds in
which it sees the exact Lean diagnostic its previous attempt produced. The call
budget is identical on purpose, so a difference between the two conditions is
attributable to the feedback rather than to extra compute.

This is the condition these models are actually built for. OProver is trained on
retrieval-failure-feedback-repair trajectories and Goedel-V2's central claim is
verifier-guided self-correction; scoring either single-shot measures them
against a design they do not have. A W16 zero is therefore a floor, not a
verdict, and the comparison worth reporting is W16 versus F16 on the same items.

Rounds stop early on success, and a branch that stops changing its proof is
abandoned — repeating a rejected proof costs a Lean call and learns nothing.

Usage:
    python tools/prover_eval/f16.py --model Goedel-Prover-V2-32B --partition gold
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from config import CONFIG  # noqa: E402
from tools.prover_eval.w16 import (PROMPT, _BANNED, build_solution,  # noqa: E402
                                   extract_proof, is_timeout)

REPAIR = """The previous Lean proof failed.

Immutable theorem:

```lean
{header}
```

Previous proof:

```lean
{previous}
```

Lean compiler diagnostics:

```text
{diagnostics}
```

Return exactly one corrected proof term in one <answer> block.
Do not modify the theorem or use sorry, admit, axioms or unsafe declarations.
"""


def diagnostics_of(log: str, limit: int = 2000) -> str:
    """The parts of a Lean log worth showing a model.

    Whole logs are mostly noise — file paths, repeated context — and burn the
    token budget the model needs for the repair itself. Error lines and the
    goal state they carry are the signal.
    """
    keep, take = [], False
    for line in log.splitlines():
        low = line.lower()
        if "error:" in low:
            take = True
        elif line and not line.startswith(" ") and "warning" in low:
            take = False
        if take:
            keep.append(line)
    text = "\n".join(keep) or log
    return text[-limit:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--url", default=os.environ.get(
        "VLLM_URL", "http://127.0.0.1:8000"))
    ap.add_argument("--benchmark", default="benchmark")
    ap.add_argument("--partition", default="gold")
    ap.add_argument("--branches", type=int, default=4)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=12288)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--lean-timeout", type=int, default=600)
    ap.add_argument("--limit", type=int, default=None)
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
    print(f"F16 | model={args.model} | partition={args.partition} | "
          f"{len(index)} items x {args.branches} branches x {args.rounds} rounds")

    raw_path = os.path.join(
        args.benchmark, f"rawf16_{args.partition}_{args.model}.jsonl")
    raw_fh = open(raw_path, "w")
    results = []
    t0 = time.time()

    def ask(content: str):
        payload = {"model": args.model,
                   "messages": [{"role": "user", "content": content}],
                   "n": 1, "temperature": args.temperature,
                   "max_tokens": args.max_tokens}
        r = requests.post(f"{args.url}/v1/chat/completions", json=payload,
                          timeout=3600)
        r.raise_for_status()
        d = r.json()
        c = d["choices"][0]
        return (c["message"]["content"], c.get("finish_reason"),
                d.get("usage", {}).get("completion_tokens", 0))

    for n, item in enumerate(index, 1):
        challenge = open(os.path.join(root, item["file"])).read()
        rec = {"id": item["id"], "statement": item["statement"],
               "label": item["label"], "stratum": item["stratum"],
               "model": args.model, "condition": "F16",
               "status": "unresolved", "verified_direction": None,
               "calls": 0, "lean_calls": 0, "lean_timeouts": 0,
               "completion_tokens": 0,
               "solved_at_round": None, "finish_reasons": {}}

        for direction in ("refute", "prove"):
            target = f"{direction}_{item['id']}"
            if rec["verified_direction"]:
                break
            for branch in range(args.branches):
                if rec["verified_direction"]:
                    break
                prompt = PROMPT.format(source=challenge, target=target)
                previous, last_proof = None, None
                for rnd in range(args.rounds):
                    try:
                        text, finish, ctok = ask(prompt)
                    except Exception as exc:
                        rec["status"] = "generation_error"
                        rec["error"] = str(exc)[:200]
                        break
                    rec["calls"] += 1
                    rec["completion_tokens"] += ctok
                    rec["finish_reasons"][finish] = \
                        rec["finish_reasons"].get(finish, 0) + 1
                    raw_fh.write(json.dumps(
                        {"id": item["id"], "direction": direction,
                         "branch": branch, "round": rnd,
                         "finish_reason": finish, "text": text}) + "\n")
                    raw_fh.flush()

                    proof = extract_proof(text or "")
                    if not proof or _BANNED.search(proof):
                        break            # nothing to repair from
                    if proof == last_proof:
                        break            # branch has stopped moving
                    last_proof = proof

                    src = build_solution(challenge, target, proof)
                    ok, log = lean._run_lean(src, audit_axioms=True)
                    rec["lean_calls"] += 1
                    if not ok and is_timeout(log):
                        rec["lean_timeouts"] = rec.get("lean_timeouts", 0) + 1
                    if ok:
                        rec["verified_direction"] = direction
                        rec["solved_at_round"] = rnd
                        rec["proof"] = proof
                        rec["status"] = ("formally_proved" if direction == "prove"
                                         else "formally_refuted")
                        break
                    previous = proof
                    header = challenge.split("theorem ")[0].strip()
                    prompt = REPAIR.format(header=header, previous=previous,
                                           diagnostics=diagnostics_of(log))

        if rec["verified_direction"] and rec["label"] in ("true", "false"):
            expected = "prove" if rec["label"] == "true" else "refute"
            if rec["verified_direction"] != expected:
                rec["status"] = "WRONG_DIRECTION_VERIFIED"

        results.append(rec)
        print(f"[{n}/{len(index)}] {rec['status']:26s} "
              f"round={rec['solved_at_round']} calls={rec['calls']:2d} "
              f"lean={rec['lean_calls']:2d} {item['statement'][:46]}", flush=True)

    raw_fh.close()
    elapsed = time.time() - t0
    out = args.out or os.path.join(
        args.benchmark, f"f16_{args.partition}_{args.model}.json")
    with open(out, "w") as fh:
        json.dump({"model": args.model, "condition": "F16",
                   "partition": args.partition, "branches": args.branches,
                   "rounds": args.rounds, "wall_s": round(elapsed, 1),
                   "results": results}, fh, indent=1)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"\nF16 {args.model} on {args.partition}: {len(results)} items in "
          f"{elapsed / 60:.0f} min")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:28s} {v}")
    solved = [r["solved_at_round"] for r in results
              if r["solved_at_round"] is not None]
    if solved:
        print(f"  solved at round: {sorted(solved)}   "
              f"(round 0 = no feedback used)")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
