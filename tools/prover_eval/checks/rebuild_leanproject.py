"""Rebuild LeanProject modules with bare `lean` + LEAN_PATH.

Never use `lake build` in this project. lake's resolver decides the mathlib
remote URL has changed, DELETES .lake/packages/mathlib, and re-clones — and on a
compute node without git the re-clone fails, leaving no mathlib at all. That is
not hypothetical: it happened, wiping 8,000 oleans and silently turning every
subsequent verification into a false negative.

`lean` with an explicit LEAN_PATH never consults lake, never needs git, and
never mutates the package tree.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from config import CONFIG
from pipeline.theorem_prover import LeanSubprocessProver

root = CONFIG.lean_project_root
prover = LeanSubprocessProver(CONFIG)
lean_path = prover._compute_lean_path(root)
env = dict(os.environ)
elan = os.path.expanduser("~/.elan/bin")
if os.path.isdir(elan):
    env["PATH"] = elan + os.pathsep + env.get("PATH", "")
env["LEAN_PATH"] = lean_path

outdir = os.path.join(root, ".lake", "build", "lib", "lean", "LeanProject")
os.makedirs(outdir, exist_ok=True)
for mod in ["Basic", "GraphInvariants", "GraphInvariantsComputable"]:
    src = os.path.join(root, "LeanProject", f"{mod}.lean")
    if not os.path.exists(src):
        print(f"  skip {mod}: no source"); continue
    olean = os.path.join(outdir, f"{mod}.olean")
    print(f"building {mod} ...", flush=True)
    r = subprocess.run([os.path.expanduser("~/.elan/bin/lean"), src,
                        "-o", olean, "-i", olean.replace(".olean", ".ilean")],
                       env=env, capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        print(f"  FAILED {mod}:\n{(r.stdout + r.stderr)[-2500:]}")
        sys.exit(1)
    print(f"  ok {mod}")
print("all modules rebuilt")
