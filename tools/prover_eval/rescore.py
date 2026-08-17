#!/usr/bin/env python
"""tools/prover_eval/rescore.py — re-score a finished run from saved replies.

Scoring a prover has two halves: generate candidate proofs, then check them.
Only the first needs a GPU, and only the first is expensive. Because every raw
reply was persisted, a defect in the *checking* half can be repaired without
re-running a single model.

That is not hypothetical here. The fence regex accepted ```lean but not
```lean4, and models differ sharply in which they emit — OProver-8B uses lean4
in about 60% of replies, Goedel-32B in 4%. This script replays the saved replies
through the corrected parser and re-verifies with the same kernel and axiom
probe, so the corrected numbers are comparable to the originals in every respect
except the bug.

Worth recording what the replay actually showed: the bug moved parse rates
substantially (DeepSeek-7B 72 -> 102 checkable candidates, OProver-8B 11 -> 25)
but changed *no* model's resolution count. Goedel-32B still resolves 3 and every
other model still resolves 0. The suspicion that the ranking was an artefact of
the tag was wrong, and the replay is what settled it — which is the argument for
keeping raw replies even when a run looks finished.

Usage:
    python tools/prover_eval/rescore.py [--model NAME] [--partition gold]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from config import CONFIG  # noqa: E402
from tools.prover_eval.w16 import (_BANNED, build_solution,  # noqa: E402
                                   extract_proof)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", default="benchmark")
    ap.add_argument("--partition", default="gold")
    ap.add_argument("--model", default="", help="substring filter")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--lean-timeout", type=int, default=600)
    args = ap.parse_args()
    CONFIG.lean_timeout_s = args.lean_timeout

    from pipeline.theorem_prover import LeanSubprocessProver
    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean available.")
        return 2

    root = os.path.join(args.benchmark, f"challenges_{args.partition}")
    index = {c["id"]: c for c in json.load(open(os.path.join(root, "index.json")))}

    for raw in sorted(glob.glob(os.path.join(
            args.benchmark, f"raw*_{args.partition}_*.jsonl"))):
        base = os.path.basename(raw)
        model = base.split(f"_{args.partition}_")[1][:-6]
        # `raw_` and `rawf16_` files both yield the same model name, so keying
        # the output on the model alone let the F16 re-score silently overwrite
        # the W16 one. The condition has to be part of the identity.
        condition = "F16" if base.startswith("rawf16_") else "W16"
        if args.model and args.model.lower() not in model.lower():
            continue

        # Distinct (item, direction, proof). Dedup is what makes this affordable:
        # 16 samples of one model repeat heavily, and Lean is the slow part.
        cands, seen, parsed_n, total = {}, set(), 0, 0
        for line in open(raw):
            d = json.loads(line)
            total += 1
            p = extract_proof(d["text"] or "")
            if not p or _BANNED.search(p):
                continue
            parsed_n += 1
            key = (d["id"], d["direction"], p)
            if key in seen:
                continue
            seen.add(key)
            cands.setdefault(d["id"], []).append((d["direction"], p))

        print(f"\n=== {condition} {model} ({base})")
        print(f"  replies {total}, parseable {parsed_n} "
              f"({100 * parsed_n / max(total, 1):.1f}%), "
              f"distinct candidates {len(seen)}")

        def check(job):
            item_id, direction, proof = job
            ch = open(os.path.join(root, index[item_id]["file"])).read()
            src = build_solution(ch, f"{direction}_{item_id}", proof)
            ok, _ = lean._run_lean(src, audit_axioms=True)
            return item_id, direction, proof, ok

        jobs = [(i, d, p) for i, lst in cands.items() for d, p in lst]
        resolved, wrong = {}, {}
        t0 = time.time()
        with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for item_id, direction, proof, ok in pool.map(check, jobs):
                if not ok or item_id in resolved:
                    continue
                label = index[item_id]["label"]
                expected = {"true": "prove", "false": "refute"}.get(label)
                if expected and direction != expected:
                    wrong[item_id] = (direction, proof)
                resolved[item_id] = (direction, proof)

        out = os.path.join(
            args.benchmark, f"rescored_{condition}_{args.partition}_{model}.json")
        with open(out, "w") as fh:
            json.dump({"model": model, "condition": condition,
                       "partition": args.partition,
                       "replies": total, "parseable": parsed_n,
                       "distinct_candidates": len(seen),
                       "lean_calls": len(jobs),
                       "resolved": {k: v[0] for k, v in resolved.items()},
                       "wrong_direction": {k: v[0] for k, v in wrong.items()},
                       "elapsed_s": round(time.time() - t0, 1)}, fh, indent=1)
        print(f"  lean calls {len(jobs)}  ->  RESOLVED {len(resolved)}/"
              f"{len(index)}   wrong-direction {len(wrong)}")
        if wrong:
            print("  !! WRONG DIRECTION VERIFIED — formalization may be unsound:")
            for k, (d, _) in wrong.items():
                print(f"     {k} verified '{d}' against label "
                      f"'{index[k]['label']}': {index[k]['statement'][:60]}")
        print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
