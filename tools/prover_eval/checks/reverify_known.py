"""Re-verify every proof this project has ever accepted.

The restored mathlib came from a June backup. If it differs from the mathlib the
original runs used, previously accepted proofs could silently stop verifying —
or, worse, something previously rejected could start passing. Re-checking the
known-good proofs is the cheapest evidence that the restored environment is
equivalent to the one the recorded results were produced in.
"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 900
from tools.prover_eval.w16 import build_solution
from pipeline.theorem_prover import LeanSubprocessProver

root = "benchmark/challenges_gold"
idx = {c["id"]: c for c in json.load(open(os.path.join(root, "index.json")))}
lean = LeanSubprocessProver(CONFIG)
total = bad = 0
for f in glob.glob("benchmark/w16_*.json") + glob.glob("benchmark/f16_*.json"):
    for r in json.load(open(f)).get("results", []):
        if not r.get("proof"):
            continue
        total += 1
        d = r["verified_direction"]
        ch = open(os.path.join(root, idx[r["id"]]["file"])).read()
        ok, log = lean._run_lean(build_solution(ch, f"{d}_{r['id']}", r["proof"]),
                                 audit_axioms=True)
        print(f"  {'OK  ' if ok else 'FAIL'} {d:7s} {r['statement'][:56]}")
        if not ok:
            bad += 1
            print("      ", log.strip()[-250:])
print(f"\n{total - bad}/{total} previously accepted proofs still verify")
sys.exit(1 if bad else 0)
