#!/usr/bin/env python
"""tools/prover_eval/challenge.py — emit the immutable challenge pair per item.

The evaluation design hands every model two declarations for one conjecture C::

    theorem prove_candidate  :   C := by sorry
    theorem refute_candidate : ¬ C := by sorry

and counts the item resolved when either is accepted. That only measures what
it claims if both mention the *same* C. In this repository they did not.

The pipeline carries two Lean layers. ``GraphInvariants`` is the specification:
``sInf`` over a ``Set``, noncomputable, in the ``SimpleGraph`` namespace, so it
reads ``G.zeroForcingNumber``. ``GraphInvariantsComputable`` is the executable
mirror in the ``GraphCalc`` namespace, which ``decide`` can actually evaluate.
The positive exporter targeted the first and the disproof exporter the second,
so a "proof" and a "refutation" of one conjecture were statements about two
different functions, and a model could in principle satisfy both.

This module states both directions over the **computable** layer, for a reason
beyond convenience: that is the layer whose agreement with graphcalc has been
checked. ``tools/lean_differential.py`` verified 4,709 (graph, invariant) pairs
against ``GraphCalc`` for n ≤ 6 — and caught a real defect doing it. The
specification layer carries only two bridge theorems, so its agreement with the
values that produced the truth labels is largely unestablished. Labelling an
item with a graphcalc counterexample and then asking about the specification
layer would inherit that gap silently.

Usage:
    python tools/prover_eval/challenge.py --partition gold [--out challenges/]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from config import CONFIG  # noqa: E402

PREAMBLE = ("import Mathlib\n"
            "import LeanProject.GraphInvariantsComputable\n\n"
            "set_option maxRecDepth 10000\n\n"
            "open SimpleGraph\n")

BINDERS = ("{V : Type} [Fintype V] [DecidableEq V]\n"
           "    (G : SimpleGraph V) [DecidableRel G.Adj]")


def body_for(statement: str, columns):
    """The Lean proposition for a conjecture, over the computable layer.

    Returns (hypotheses, conclusion) with hypotheses as a list of Lean
    propositions, or None when the statement is outside the formalized
    vocabulary.
    """
    from pipeline import lean_disproof as ld, linear_form

    parsed = ld._parse(statement, columns)
    if parsed is not None:
        # `_parse` also returns the definedness hypotheses required by any
        # partial invariant in the body (`minCard` has no witness on some
        # graphs). They belong in the challenge for the same reason the class
        # hypotheses do: without them the statement is broader than the
        # conjecture and refutable on graphs it never spoke about.
        classes, concl, defined = parsed
        return ([f"{ld.CLASS_PREDICATES[c]} G" for c in classes] + defined,
                concl)

    necessary = ld._parse_necessary(statement)
    if necessary is not None:
        hyp, concl = necessary
        return [hyp], concl
    return None


def render_pair(statement: str, columns, ident: str):
    """(challenge_source, C_as_text) or None."""
    parts = body_for(statement, columns)
    if parts is None:
        return None
    hyps, concl = parts
    # One universally quantified proposition, written once and referenced by
    # both declarations so they cannot drift apart.
    arrow = "".join(f"{h} → " for h in hyps)
    prop = (f"∀ {BINDERS},\n      {arrow}{concl}")
    src = (f"{PREAMBLE}\n"
           f"-- Conjecture under test: {statement}\n"
           f"-- Both declarations refer to the same `Candidate`.\n"
           f"abbrev Candidate : Prop :=\n    {prop}\n\n"
           f"theorem prove_{ident} : Candidate := by\n  sorry\n\n"
           f"theorem refute_{ident} : ¬ Candidate := by\n  sorry\n")
    return src, prop


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", default="benchmark")
    ap.add_argument("--partition", default="gold")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    import pandas as pd
    columns = list(pd.read_parquet(
        os.path.join(CONFIG.cache_dir, "seed_battery.parquet")).columns)

    items = json.load(open(os.path.join(args.benchmark,
                                        f"{args.partition}.json")))
    out = args.out or os.path.join(args.benchmark, f"challenges_{args.partition}")
    os.makedirs(out, exist_ok=True)

    written, skipped = 0, 0
    index = []
    for item in items:
        ident = item["statement_sha256"][:8]
        pair = render_pair(item["statement"], columns, ident)
        if pair is None:
            skipped += 1
            continue
        src, prop = pair
        path = os.path.join(out, f"Challenge_{ident}.lean")
        with open(path, "w") as fh:
            fh.write(src)
        index.append({"id": ident, "file": os.path.basename(path),
                      "statement": item["statement"], "label": item["label"],
                      "label_source": item["label_source"],
                      "stratum": item["stratum"],
                      "witness_g6": item.get("witness_g6"),
                      "challenge_sha256": hashlib.sha256(src.encode()).hexdigest()})
        written += 1

    with open(os.path.join(out, "index.json"), "w") as fh:
        json.dump(index, fh, indent=1)

    print(f"partition '{args.partition}': {len(items)} items")
    print(f"  challenges written: {written}")
    print(f"  outside formalized vocabulary: {skipped}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
