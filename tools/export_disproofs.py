#!/usr/bin/env python
"""tools/export_disproofs.py — formal Lean 4 disproofs from refuted conjectures.

The generate--refute loop discards far more conjectures than it keeps, and for
each one it knows the graph that killed it (``results/refutations.json``). That
pair is a theorem: ``¬∀ G, hypotheses → bound``, proved by evaluating both sides
on the witness. This script emits one self-contained ``.lean`` file per
formalizable refutation and (optionally) kernel-checks each one.

A disproof counts only if the kernel accepts it here — same discipline as
``tools/verify_proofs.py`` for the positive direction.

Usage:
    python tools/export_disproofs.py [--limit N] [--verify] [--out DIR]
Exit code is the number of emitted disproofs that FAILED verification.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG  # noqa: E402
from pipeline import lean_disproof  # noqa: E402


def _columns(refutations) -> list:
    """Invariant/class identifiers appearing in the refuted statements."""
    toks = set()
    for r in refutations:
        toks |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", r.get("statement") or ""))
    return sorted(toks)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refutations",
                    default=os.path.join("results", "refutations.json"))
    ap.add_argument("--out", default=os.path.join("results", "disproofs"))
    ap.add_argument("--limit", type=int, default=None,
                    help="stop after this many formalizable refutations")
    ap.add_argument("--verify", action="store_true",
                    help="kernel-check each emitted disproof")
    args = ap.parse_args()

    if not os.path.exists(args.refutations):
        print(f"No refutation record at {args.refutations}. Run the CEGIS loop "
              f"first (refutations are written alongside cegis_results.json).")
        return 0

    with open(args.refutations) as fh:
        payload = json.load(fh)
    refutations = payload.get("refutations", payload if isinstance(payload, list) else [])
    if not refutations:
        print("Refutation record is empty — nothing to export.")
        return 0

    cols = _columns(refutations)
    exported = lean_disproof.export_refutations(refutations, cols, limit=args.limit)
    total_with_witness = sum(1 for r in refutations if r.get("witness_graph6"))
    print(f"{len(refutations)} refuted, {total_with_witness} with a witness, "
          f"{len(exported)} formalizable → {args.out}")
    if not exported:
        return 0

    os.makedirs(args.out, exist_ok=True)
    paths = []
    for i, (rec, src) in enumerate(exported):
        path = os.path.join(args.out, f"disproof_{i:04d}.lean")
        with open(path, "w") as fh:
            fh.write(src)
        paths.append((path, rec))

    if not args.verify:
        print(f"Wrote {len(paths)} disproof file(s). Re-run with --verify to "
              f"kernel-check them.")
        return 0

    from pipeline.theorem_prover import LeanSubprocessProver
    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean binary available to kernel-check — aborting "
              "(an unverifiable run must not report success).")
        return 2

    failed = 0
    for path, rec in paths:
        with open(path) as fh:
            ok, log = lean._run_lean(fh.read())
        name = os.path.basename(path)
        if ok:
            print(f"  ✓ {name}  (n={rec.get('witness_order')}) "
                  f"{(rec.get('statement') or '')[:70]}")
        else:
            failed += 1
            first = next((ln for ln in log.splitlines() if "error" in ln.lower()),
                         log[:160])
            print(f"  ✗ {name}  ({first.strip()[:160]})")
    print(f"\nKERNEL-VERIFIED DISPROOFS: {len(paths) - failed} / {len(paths)}")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
