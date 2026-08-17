#!/usr/bin/env python3
"""tools/verify_proofs.py — authoritative, independent re-verification of every
proof the prover shim persisted to results/verified_proofs/.

Why this exists (run 53863): the live reprove count is gated by the HTTP client
(LocalEndpointProver), whose timeout (prover_timeout_s + 30) can be SHORTER than a
multi-round agentic proof, so a genuinely kernel-verified proof gets dropped from
the job-level tally even though it passed. The shim now persists each verified
proof the instant it passes; this script re-checks those saved artifacts with the
SAME sound bare-`lean` + LEAN_PATH kernel check (LeanSubprocessProver._run_lean,
canary-tested true/false), decoupling the trustworthy count from the orchestration.

This is the number to cite: a proof counts iff its self-contained `.lean` file
(mathlib + GraphInvariants preamble + the proof) elaborates cleanly here, with no
network, no model, and no client in the loop.

Usage:
    .venv/bin/python tools/verify_proofs.py [--dir results/verified_proofs]
Exit code is the number of proofs that FAILED re-verification (0 = all good).
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from pipeline.theorem_prover import LeanSubprocessProver
from pipeline import proof_audit


def _program(text: str) -> str:
    """Return just the self-contained Lean program, dropping any metadata header.
    A persisted file is a comment header + the wrapped proof; the proof always
    begins with `import Mathlib` (LeanSubprocessProver/_wrap guarantees it). Taking
    from the first standalone `import Mathlib` line skips the header — and also
    salvages files written before the persistence header was line-comment-safe
    (where a multi-line statement leaked in as bare code above the real proof)."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() == "import Mathlib":
            return "\n".join(lines[i:])
    return text


def _requested_statement(text: str) -> str:
    """The statement the prover was asked about, recovered from the header.

    Two header formats exist. The current one comments every statement line
    (``-- stmt: …``). Older artifacts commented only the first line
    (``-- statement: import Mathlib``) and leaked the rest as bare code above the
    proof; there the statement runs to the standalone ``import Mathlib`` that
    starts the proof proper. Returns "" when neither header is present.
    """
    lines = text.splitlines()
    tagged = [ln[len("-- stmt:"):].lstrip() for ln in lines if ln.startswith("-- stmt:")]
    if tagged:
        return "\n".join(tagged)
    for i, ln in enumerate(lines):
        if ln.startswith("-- statement:"):
            head = [ln[len("-- statement:"):].lstrip()]
            for rest in lines[i + 1:]:
                if rest.strip() == "import Mathlib":     # start of the proof file
                    return "\n".join(head)
                head.append(rest)
            return "\n".join(head)
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join("results", "verified_proofs"),
                    help="directory of persisted *.lean proofs to re-verify")
    args = ap.parse_args()

    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean binary available to kernel-check — aborting "
              "(an unverifiable run must not report success).")
        return 2

    files = sorted(glob.glob(os.path.join(args.dir, "*.lean")))
    if not files:
        print(f"No persisted proofs found in {args.dir} (nothing to verify).")
        return 0

    passed, failed = [], []
    for path in files:
        with open(path) as f:
            text = f.read()
        code = _program(text)
        name = os.path.basename(path)
        # Identity first: a proof of the wrong statement must not be counted even
        # if it elaborates perfectly. Skipped only for artifacts with no recorded
        # request (pre-header files), where there is nothing to compare against.
        want = _requested_statement(text)
        if want.strip():
            ok, why = proof_audit.static_audit(want, code)
            if not ok:
                failed.append(name)
                print(f"  ✗ {name}  (identity: {why[:150]})")
                continue
        ok, log = lean._run_lean(code)
        if ok:
            passed.append(name)
            print(f"  ✓ {name}")
        else:
            failed.append(name)
            first = next((ln for ln in log.splitlines() if "error" in ln.lower()), log[:160])
            print(f"  ✗ {name}  ({first.strip()[:160]})")

    print(f"\nINDEPENDENTLY KERNEL-VERIFIED: {len(passed)} / {len(files)} "
          f"persisted proofs (failed: {len(failed)})")
    return len(failed)


if __name__ == "__main__":
    raise SystemExit(main())
