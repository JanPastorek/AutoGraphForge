"""Verify the W16 scoring path before spending GPU hours on it.

Three cases, each of which would invalidate a whole run if it behaved the other
way: a wrong proof must be rejected, a `sorry` must be caught by the axiom probe
even though it compiles, and a true statement must actually verify (otherwise a
broken Lean path would silently score every model as zero).
"""
import sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 300
from tools.prover_eval.w16 import build_solution
from pipeline.theorem_prover import LeanSubprocessProver

lean = LeanSubprocessProver(CONFIG)
f = sorted(glob.glob("benchmark/challenges_gold/*.lean"))[0]
ch = open(f).read(); ident = f.split('_')[-1].replace('.lean', '')

ok, _ = lean._run_lean(build_solution(ch, 'prove_' + ident, 'by decide'), audit_axioms=True)
print("bogus 'by decide' ->", "VERIFIED (BAD!)" if ok else "correctly rejected")
ok2, _ = lean._run_lean(build_solution(ch, 'prove_' + ident, 'by sorry'), audit_axioms=True)
print("'by sorry'        ->", "VERIFIED (BAD!)" if ok2 else "correctly rejected")
ok3, log3 = lean._run_lean(
    "import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"
    "theorem t : 1 + 1 = 2 := by decide\n", audit_axioms=True)
print("true statement    ->", "verified" if ok3 else "FAILED (path broken!)")
if not ok3:
    print(log3.strip()[-400:])
