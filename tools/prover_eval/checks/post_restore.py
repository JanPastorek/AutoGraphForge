"""Prove the verification path works before trusting any score again.

After the mathlib wipe every Lean check failed, so runs kept scoring items and
reporting zeros that meant nothing. These assertions are the cheapest thing that
distinguishes "models failed" from "the toolchain is broken".
"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 600
from tools.prover_eval.w16 import build_solution
from pipeline.theorem_prover import LeanSubprocessProver

lean = LeanSubprocessProver(CONFIG)
fail = 0

ok, log = lean._run_lean(
    "import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"
    "theorem t : 1 + 1 = 2 := by decide\n", audit_axioms=True)
print("true statement verifies      ->", "PASS" if ok else "FAIL")
if not ok:
    fail += 1; print(log.strip()[-400:])

# The definitions added this session must exist in the rebuilt olean, or every
# challenge mentioning them silently fails.
for name, expr in [("connectedZeroForcingNumber",
                    "GraphCalc.connectedZeroForcingNumber (GraphCalc.ofEdges 3 [(0,1),(1,2)])"),
                   ("vertexCoverNumber",
                    "GraphCalc.vertexCoverNumber (GraphCalc.ofEdges 3 [(0,1),(1,2)])"),
                   ("IsEulerianClass(connectivity fix)",
                    "decide (¬ GraphCalc.IsEulerianClass (GraphCalc.ofEdges 4 [(0,1),(1,2),(2,0)]))")]:
    ok, log = lean._run_lean(
        "import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"
        f"set_option maxRecDepth 10000\n#eval {expr}\n", audit_axioms=False)
    print(f"{name:34s} ->", "PASS" if ok else "FAIL")
    if not ok:
        fail += 1; print("   ", log.strip()[-300:])

f = sorted(glob.glob("benchmark/challenges_gold/*.lean"))[0]
ch = open(f).read(); ident = f.split('_')[-1].replace('.lean', '')
ok, _ = lean._run_lean(build_solution(ch, 'prove_' + ident, 'by decide'), audit_axioms=True)
print("bogus proof rejected         ->", "PASS" if not ok else "FAIL")
fail += ok
ok2, _ = lean._run_lean(build_solution(ch, 'prove_' + ident, 'by sorry'), audit_axioms=True)
print("'by sorry' caught            ->", "PASS" if not ok2 else "FAIL")
fail += ok2

print("\nALL CHECKS PASS" if fail == 0 else f"\n{fail} CHECK(S) FAILED — do not resubmit")
sys.exit(1 if fail else 0)
