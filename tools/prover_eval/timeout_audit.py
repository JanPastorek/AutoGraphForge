#!/usr/bin/env python
"""tools/prover_eval/timeout_audit.py — how many rejections were really timeouts?

Every scored run so far used a 600s Lean budget with 16 concurrent checkers on a
network filer. A check that overran was recorded as `ok=False`, which is
indistinguishable in the output from a proof the kernel actually rejected. One
proof in this project timed out at 900s and then verified in 25s, so the
distinction is not academic — some fraction of ~3,500 rejections may be false
negatives charged to the models.

This replays saved candidates serially with a large budget and counts how many
flip from rejected to verified. Serial on purpose: sixteen parallel `lean`
processes contending for the same filer is the condition under test, not the one
to reproduce.

Usage:
    python tools/prover_eval/timeout_audit.py --model Goedel-Prover-V2-32B [--sample 60]
"""
from __future__ import annotations

import argparse, glob, json, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
from config import CONFIG  # noqa: E402
from tools.prover_eval.w16 import (_BANNED, build_solution,  # noqa: E402
                                   extract_proof, is_timeout)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", default="benchmark")
    ap.add_argument("--partition", default="gold")
    ap.add_argument("--model", default="")
    ap.add_argument("--sample", type=int, default=60,
                    help="candidates to re-check per model (0 = all)")
    ap.add_argument("--timeout", type=int, default=2400)
    ap.add_argument("--seed", type=int, default=20260806)
    args = ap.parse_args()
    CONFIG.lean_timeout_s = args.timeout

    from pipeline.theorem_prover import LeanSubprocessProver
    lean = LeanSubprocessProver(CONFIG)
    root = os.path.join(args.benchmark, f"challenges_{args.partition}")
    index = {c["id"]: c for c in json.load(open(os.path.join(root, "index.json")))}
    rng = random.Random(args.seed)
    summary = {}

    for raw in sorted(glob.glob(os.path.join(
            args.benchmark, f"raw*_{args.partition}_*.jsonl"))):
        base = os.path.basename(raw)
        model = base.split(f"_{args.partition}_")[1][:-6]
        if args.model and args.model.lower() not in model.lower():
            continue
        seen, cands = set(), []
        for line in open(raw):
            d = json.loads(line)
            p = extract_proof(d["text"] or "")
            if not p or _BANNED.search(p):
                continue
            key = (d["id"], d["direction"], p)
            if key in seen:
                continue
            seen.add(key)
            cands.append(key)
        if not cands:
            continue
        rng.shuffle(cands)
        pick = cands if args.sample == 0 else cands[:args.sample]

        flipped, timeouts, t0 = [], 0, time.time()
        for item_id, direction, proof in pick:
            ch = open(os.path.join(root, index[item_id]["file"])).read()
            ok, log = lean._run_lean(build_solution(ch, f"{direction}_{item_id}", proof),
                                     audit_axioms=True)
            if ok:
                flipped.append((item_id, direction, proof))
                print(f"  FLIPPED to VERIFIED: {index[item_id]['statement'][:60]}")
            elif is_timeout(log):
                timeouts += 1
        summary[model] = {"rechecked": len(pick), "of_total": len(cands),
                          "flipped": len(flipped), "still_timeout": timeouts,
                          "elapsed_s": round(time.time() - t0, 1)}
        print(f"{model}: re-checked {len(pick)}/{len(cands)} @ {args.timeout}s "
              f"-> {len(flipped)} flipped, {timeouts} still timed out", flush=True)

    out = os.path.join(args.benchmark, f"timeout_audit_{args.partition}.json")
    with open(out, "w") as fh:
        json.dump({"timeout_s": args.timeout, "sample": args.sample,
                   "serial": True, "models": summary}, fh, indent=1)
    total_flip = sum(v["flipped"] for v in summary.values())
    print(f"\n{total_flip} candidate(s) flipped from rejected to verified.")
    if total_flip:
        print("Reported zeros are affected: those were false negatives, not "
              "model failures.")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
