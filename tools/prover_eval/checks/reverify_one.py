"""Re-check the single proof that timed out, with a generous budget.

A timeout is not a rejection. The original run accepted this proof inside 600s;
after the restore it exceeded 900s on a contended node. Either the restored
environment is genuinely slower, or the machine was busy — and the difference
matters, because "previously accepted proof no longer verifies" would mean the
recorded results cannot be trusted, while "took longer on a loaded node" means
nothing is wrong.
"""
import sys, os, json, glob, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 5400
from tools.prover_eval.w16 import build_solution
from pipeline.theorem_prover import LeanSubprocessProver

root = "benchmark/challenges_gold"
idx = {c["id"]: c for c in json.load(open(os.path.join(root, "index.json")))}
target = "slater"
lean = LeanSubprocessProver(CONFIG)
for f in glob.glob("benchmark/w16_gold_*.json"):
    for r in json.load(open(f)).get("results", []):
        if not r.get("proof") or target not in r["statement"]:
            continue
        print("statement:", r["statement"][:80])
        print("proof len:", len(r["proof"]), "chars")
        ch = open(os.path.join(root, idx[r["id"]]["file"])).read()
        t = time.time()
        ok, log = lean._run_lean(build_solution(ch, f"{r['verified_direction']}_{r['id']}",
                                                r["proof"]), audit_axioms=True)
        print(f"  {'VERIFIED' if ok else 'FAILED'} in {time.time()-t:.0f}s")
        if not ok:
            print(log.strip()[-400:])
        sys.exit(0 if ok else 1)
print("not found")
