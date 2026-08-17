"""Assemble real model proofs and report the Lean error class.

Zero resolutions is only a result if the proofs were genuinely wrong. If instead
the assembled file is malformed, or every error is `unknown identifier`, the run
measured the harness rather than the provers.
"""
import sys, os, json, glob, collections, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 300
from tools.prover_eval.w16 import extract_proof, build_solution, _BANNED
from pipeline.theorem_prover import LeanSubprocessProver

model = sys.argv[1] if len(sys.argv) > 1 else "Pythagoras-Prover-4B"
raw = f"benchmark/raw_gold_{model}.jsonl"
root = "benchmark/challenges_gold"
idx = {c["id"]: c for c in json.load(open(os.path.join(root, "index.json")))}

lean = LeanSubprocessProver(CONFIG)
seen, checked, classes = set(), 0, collections.Counter()
for line in open(raw):
    d = json.loads(line)
    p = extract_proof(d["text"] or "")
    if not p or _BANNED.search(p):
        continue
    key = (d["id"], d["direction"], p)
    if key in seen:
        continue
    seen.add(key)
    ch = open(os.path.join(root, idx[d["id"]]["file"])).read()
    src = build_solution(ch, f"{d['direction']}_{d['id']}", p)
    ok, log = lean._run_lean(src, audit_axioms=True)
    checked += 1
    if ok:
        classes["VERIFIED"] += 1
        print("VERIFIED:", d["id"], d["direction"], p[:80])
    else:
        errs = re.findall(r"error: ([^\n]{0,90})", log)
        classes[errs[0][:60] if errs else "no-error-line/timeout"] += 1
        if checked <= 3:
            print(f"--- {d['id']} {d['direction']}\n  proof: {p[:150]}\n  err: {(errs[0] if errs else log.strip()[-160:])[:160]}")
    if checked >= 25:
        break
print(f"\nchecked {checked} distinct candidates for {model}")
for k, v in classes.most_common(12):
    print(f"  {v:3d}  {k}")
