#!/usr/bin/env python
"""tools/prover_eval/build_benchmark.py — freeze a prover benchmark.

The proposed AutoGraphForge-ProverEval design asks for a 300-item benchmark
with a 100-item gold set: 50 true statements carrying a trusted Lean proof and
50 false ones carrying a formal refutation. This builder exists to construct
what the repository can actually support, and to *report the shortfall* rather
than pad the set to the requested size.

Two facts constrain it, both measured rather than assumed:

  * The trusted Lean environment defines 25 of the battery's 59 invariants, so
    only ~8.8% of survivors and ~4.5% of refutations can even be *stated*. An
    item whose statement mentions `burning_number` is not a hard proving
    problem, it is an unformalized one, and scoring a model on it measures our
    coverage rather than its ability.
  * The pipeline has proved nothing (`proved: 0`). There is no pool of
    AutoGraphForge conjectures with trusted Lean proofs to draw a "true" half
    from, and if there were, that would be the paper rather than its benchmark.

So truth labels come from provenance, not from proofs:

  refuted   an explicit counterexample graph — the strongest label available,
            and the only one this pipeline produces mechanically
  known     the novelty filter matched a named theorem from the literature
  open      no label; these are the discovery frontier and are scored for
            progress, never for accuracy

Usage:
    python tools/prover_eval/build_benchmark.py [--out benchmark/] [--seed 20260804]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from config import CONFIG  # noqa: E402

VERSION = "AutoGraphForge-ProverEval-v1"

# Invariants that exist in the trusted Lean development. An item is
# "expressible" exactly when every battery name it mentions is in this set;
# anything else cannot be written down, let alone proved.
def lean_vocabulary():
    from pipeline import lean_export as le
    return set(le.SUPPORTED) | set(le.CLASS_PREDICATES)


# Mathlib-native invariants: those whose Lean definition is mathlib's own
# rather than one of ours. Proving over these is a different task from proving
# over a definition the model has never seen, which is the whole point of the
# stratification.
NATIVE = {"order", "size", "minimum_degree", "maximum_degree", "connected",
          "tree", "bipartite", "regular", "nontrivial"}


def battery_columns():
    import pandas as pd
    path = os.path.join(CONFIG.cache_dir, "seed_battery.parquet")
    return set(pd.read_parquet(path).columns)


_TOKEN = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")


def mentioned(statement: str, columns) -> set:
    return {t for t in _TOKEN.findall(statement) if t in columns}


def stratum(names) -> str:
    """native | supported_custom | cold_custom, by the weakest invariant used.

    A statement is only as well-supported as its least-supported invariant, so
    a single custom invariant pulls the whole item out of `native`.
    """
    if not names:
        return "native"
    if names <= NATIVE:
        return "native"
    # Custom invariants that carry bridge lemmas in the development are
    # "supported"; the rest are cold. zero-forcing is the motivating cold case.
    supported = {"independence_number", "clique_number", "domination_number",
                 "independent_domination_number", "annihilation_number", "slater"}
    return "supported_custom" if names <= (NATIVE | supported) else "cold_custom"


def load_items(columns, vocab):
    """Every candidate item with its provenance and truth label."""
    out = []

    refuted_path = os.path.join(CONFIG.output_dir, "cegis_refuted.json")
    if os.path.exists(refuted_path):
        for r in json.load(open(refuted_path)):
            out.append({"statement": r["statement"], "label": "false",
                        "label_source": "counterexample",
                        "witness_g6": r.get("witness_g6"),
                        "id": r.get("id"),
                        "generation_method": r.get("generation_method")})

    results_path = os.path.join(CONFIG.output_dir, "cegis_results.json")
    for c in json.load(open(results_path))["conjectures"]:
        meta = c.get("metadata") or {}
        known = meta.get("known_as")
        out.append({"statement": c["statement"],
                    "label": "true" if known else "open",
                    "label_source": "literature" if known else "unresolved",
                    "known_as": known,
                    "witness_g6": None,
                    "id": c.get("id"),
                    "generation_method": c.get("generation_method"),
                    "touches": meta.get("touches"),
                    "novel": meta.get("novel")})

    for item in out:
        names = mentioned(item["statement"], columns)
        item["invariants"] = sorted(names)
        item["expressible"] = bool(names) and names <= vocab
        item["stratum"] = stratum(names)
        item["statement_sha256"] = hashlib.sha256(
            item["statement"].encode()).hexdigest()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="benchmark")
    ap.add_argument("--seed", type=int, default=20260804)
    ap.add_argument("--gold-true", type=int, default=50)
    ap.add_argument("--gold-false", type=int, default=50)
    ap.add_argument("--frontier", type=int, default=140)
    ap.add_argument("--dev", type=int, default=60)
    args = ap.parse_args()

    columns, vocab = battery_columns(), lean_vocabulary()
    items = load_items(columns, vocab)
    usable = [i for i in items if i["expressible"]]

    print(f"{VERSION}")
    print(f"  Lean vocabulary: {len(vocab)} of {len(columns)} battery invariants")
    print(f"  items: {len(items)}   expressible: {len(usable)} "
          f"({100 * len(usable) / len(items):.1f}%)")
    for lab in ("true", "false", "open"):
        n = sum(1 for i in usable if i["label"] == lab)
        print(f"    {lab:6s} {n}")

    rng = random.Random(args.seed)
    pools = {lab: [i for i in usable if i["label"] == lab]
             for lab in ("true", "false", "open")}
    for p in pools.values():
        p.sort(key=lambda i: i["statement_sha256"])   # deterministic order
        rng.shuffle(p)

    shortfall = {}
    partitions = {}

    def take(pool, n, name):
        got = pool[:n]
        del pool[:len(got)]
        if len(got) < n:
            shortfall[name] = {"requested": n, "available": len(got)}
        return got

    # Development first: it must not overlap the gold set, and it is the
    # partition we can most afford to shrink.
    partitions["development"] = take(pools["open"], args.dev, "development")
    partitions["gold"] = (take(pools["true"], args.gold_true, "gold_true")
                          + take(pools["false"], args.gold_false, "gold_false"))
    partitions["frontier"] = take(pools["open"], args.frontier, "frontier")

    os.makedirs(args.out, exist_ok=True)
    manifest = {
        "version": VERSION,
        "seed": args.seed,
        "lean_vocabulary": sorted(vocab),
        "battery_invariants": len(columns),
        "counts": {k: len(v) for k, v in partitions.items()},
        "shortfall": shortfall,
        "expressible_rate": len(usable) / len(items),
    }
    for name, part in partitions.items():
        path = os.path.join(args.out, f"{name}.json")
        with open(path, "w") as fh:
            json.dump(part, fh, indent=1)
        strata = {}
        for i in part:
            strata[i["stratum"]] = strata.get(i["stratum"], 0) + 1
        print(f"  wrote {path}: {len(part)} items  {strata}")
    with open(os.path.join(args.out, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)

    if shortfall:
        print("\nSHORTFALL — the requested benchmark cannot be built from "
              "current artifacts:")
        for name, s in shortfall.items():
            print(f"  {name}: requested {s['requested']}, available "
                  f"{s['available']}")
        print("\nThe binding constraint is Lean coverage, not conjecture "
              f"supply: {100 * len(usable) / len(items):.1f}% of items are "
              "expressible. Formalizing the top blocking invariants raises "
              "every partition at once.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
