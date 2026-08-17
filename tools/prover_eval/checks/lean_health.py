"""Is Lean itself healthy, or is the machine the problem?

A `decide` on `2 <= 0` cannot take ten minutes. When trivial checks time out the
fault is the toolchain or the filesystem, not the mathematics — and every score
produced meanwhile is a false negative.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
CONFIG.lean_timeout_s = 900
from pipeline.theorem_prover import LeanSubprocessProver
lean = LeanSubprocessProver(CONFIG)

for name, src in [
    ("no imports at all",        "theorem t : 1 + 1 = 2 := by decide\n"),
    ("import Mathlib only",      "import Mathlib\ntheorem t : 1 + 1 = 2 := by decide\n"),
    ("+ GraphInvariantsComputable",
     "import Mathlib\nimport LeanProject.GraphInvariantsComputable\n"
     "theorem t : 1 + 1 = 2 := by decide\n"),
    ("ofEdges on 2 vertices",
     "import Mathlib\nimport LeanProject.GraphInvariantsComputable\n"
     "open SimpleGraph\nexample : GraphCalc.order (GraphCalc.ofEdges 2 [(0,1)]) = 2 := by decide\n"),
]:
    t = time.time()
    ok, log = lean._run_lean(src, audit_axioms=False)
    print(f"  {'OK  ' if ok else 'FAIL'} {time.time()-t:7.1f}s  {name}")
    if not ok:
        print("        ", log.strip()[-180:])
