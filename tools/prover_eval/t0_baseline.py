#!/usr/bin/env python
"""tools/prover_eval/t0_baseline.py — deterministic Lean automation, no model.

T0 answers a question that has to be settled *before* any GPU is spent: how
much of the benchmark does existing Lean automation already solve? Every item
T0 resolves is an item on which all seven provers will score alike, so it
carries no information about them. If T0 clears the false half outright, then
`RefutationSuccess` is a ceiling rather than a measurement and the benchmark's
discriminating power lives entirely in the true half and in direction choice.

For a refuted conjecture this is not a proof search at all. The counterexample
graph is explicit and finite, so the refutation is a kernel computation::

    intro h; have := @h (Fin 8) _ _ Gcex _; revert this; decide

which either reduces or does not. That is exactly what makes the false half
cheap — and exactly why it may fail to separate models.

Usage:
    python tools/prover_eval/t0_baseline.py [--partition gold] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from config import CONFIG  # noqa: E402


def battery_columns():
    import pandas as pd
    return list(pd.read_parquet(
        os.path.join(CONFIG.cache_dir, "seed_battery.parquet")).columns)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", default="benchmark")
    ap.add_argument("--partition", default="gold")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    CONFIG.lean_timeout_s = args.timeout

    from pipeline import lean_disproof
    from pipeline.theorem_prover import LeanSubprocessProver

    items = json.load(open(os.path.join(args.benchmark,
                                        f"{args.partition}.json")))
    if args.limit:
        items = items[:args.limit]
    columns = battery_columns()

    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean available — T0 cannot run.")
        return 2

    results, rendered, resolved = [], 0, 0
    for n, item in enumerate(items, 1):
        rec = {"statement": item["statement"], "label": item["label"],
               "stratum": item["stratum"],
               "sha256": item["statement_sha256"], "status": "unresolved"}

        # Only the false items have a mechanical route: an explicit witness.
        # A true item has no deterministic tactic to try here, so T0 leaves it
        # unresolved rather than pretending `simp` was attempted meaningfully.
        if item["label"] == "false" and item.get("witness_g6"):
            source = lean_disproof.render(item["statement"], columns,
                                          item["witness_g6"])
            if source is None:
                # "not renderable" hides two unrelated problems. A statement
                # outside the formalized vocabulary needs Lean definitions
                # written; a witness larger than MAX_WITNESS_ORDER needs only a
                # raised cap and more patience. Reporting them together would
                # make a tunable look like a research programme.
                built = lean_disproof._edge_list(item["witness_g6"] or "")
                if built and built[0] > lean_disproof.MAX_WITNESS_ORDER:
                    rec["status"] = "witness_too_large"
                    rec["witness_order"] = built[0]
                elif lean_disproof._parse(item["statement"], columns) is None \
                        and lean_disproof._parse_necessary(item["statement"]) is None:
                    rec["status"] = "outside_vocabulary"
                else:
                    rec["status"] = "not_renderable"
            else:
                rendered += 1
                t = time.time()
                ok, log = lean._run_lean(source, audit_axioms=False)
                rec["elapsed_s"] = round(time.time() - t, 1)
                if ok:
                    rec["status"] = "formally_refuted"
                    resolved += 1
                else:
                    rec["status"] = "lean_error"
                    rec["log_tail"] = log.strip()[-300:]
        else:
            rec["status"] = "no_deterministic_route"

        results.append(rec)
        print(f"[{n}/{len(items)}] {rec['status']:22s} {item['statement'][:70]}")

    false_items = [r for r in results if r["label"] == "false"]
    print(f"\nT0 on '{args.partition}': {len(items)} items")
    print(f"  false items:        {len(false_items)}")
    print(f"  renderable:         {rendered}")
    print(f"  formally refuted:   {resolved}")
    breakdown = {}
    for r in false_items:
        breakdown[r["status"]] = breakdown.get(r["status"], 0) + 1
    for status, n in sorted(breakdown.items(), key=lambda kv: -kv[1]):
        print(f"    {status:22s} {n}")
    if false_items:
        print(f"  T0 refutation rate: "
              f"{100 * resolved / len(false_items):.1f}% of the false half")
    print(f"  true/open items:    {len(items) - len(false_items)} "
          f"(no deterministic route attempted)")

    out = args.out or os.path.join(args.benchmark, f"t0_{args.partition}.json")
    with open(out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
