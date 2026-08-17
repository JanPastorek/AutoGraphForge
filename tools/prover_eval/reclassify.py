#!/usr/bin/env python
"""tools/prover_eval/reclassify.py — separate real resolutions from formalization gaps.

The evaluation design is explicit that `definition_gap` must never be collapsed
into `formally_refuted`, and the harness had no such status — so four
"resolutions" were reported as model successes when they were defects in the
export:

  * three exploited the missing `nontrivial` guard, refutable by `Fin 0` where
    every `forall v` class predicate holds vacuously;
  * one exploited `minCard` returning 0 for an invariant with no witness, which
    turned `Z_c + 2 <= 2 * Z_t` into `2 <= 0`.

A resolution counts as genuine only if the statement it refuted carried every
guard its content requires. This reads the recorded results, checks each
resolved item against the corrected challenge, and writes the split.
"""
from __future__ import annotations

import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
from pipeline.lean_disproof import PARTIAL_INVARIANTS  # noqa: E402


def main() -> int:
    # A single run is recorded twice — once by the live scorer (w16_*/f16_*) and
    # once by the offline re-scorer (rescored_*). Keyed by (model, condition,
    # item) so the same refutation is not counted as two.
    out, index, seen = [], {}, set()
    for p in ("gold", "frontier", "development"):
        f = f"benchmark/challenges_{p}/index.json"
        if os.path.exists(f):
            for c in json.load(open(f)):
                index[c["id"]] = (p, c)

    for f in sorted(glob.glob("benchmark/rescored_*_*.json")
                    + glob.glob("benchmark/w16_*.json")
                    + glob.glob("benchmark/f16_*.json")):
        d = json.load(open(f))
        resolved = d.get("resolved") or {
            r["id"]: r["verified_direction"] for r in d.get("results", [])
            if r.get("verified_direction")}
        for rid, direction in resolved.items():
            if rid not in index:
                continue
            part, c = index[rid]
            stmt = c["statement"]
            needs_guard = "nontrivial" not in stmt
            needs_defined = [n for n in PARTIAL_INVARIANTS if n in stmt]
            # The recorded run used the pre-fix challenge; the corrected one is
            # what decides whether the refutation had any content.
            gap = needs_guard or bool(needs_defined)
            key = (d.get("model"), d.get("condition", "W16"), rid)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "file": os.path.basename(f), "model": d.get("model"),
                "condition": d.get("condition", "W16"), "partition": part,
                "id": rid, "direction": direction, "statement": stmt,
                "status": "definition_gap" if gap else "verified_resolution",
                "missing_guard": needs_guard,
                "undefined_invariants": needs_defined})

    with open("benchmark/reclassified.json", "w") as fh:
        json.dump(out, fh, indent=1)

    gaps = [r for r in out if r["status"] == "definition_gap"]
    real = [r for r in out if r["status"] == "verified_resolution"]
    print(f"recorded resolutions: {len(out)}")
    print(f"  definition_gap      {len(gaps)}")
    print(f"  verified_resolution {len(real)}")
    for r in gaps:
        why = []
        if r["missing_guard"]:
            why.append("no nontrivial guard")
        if r["undefined_invariants"]:
            why.append("partial: " + ",".join(r["undefined_invariants"]))
        print(f"    GAP  {r['model']:24s} {r['statement'][:48]}  <- {'; '.join(why)}")
    for r in real:
        print(f"    OK   {r['model']:24s} {r['statement'][:48]}")
    print("wrote benchmark/reclassified.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
