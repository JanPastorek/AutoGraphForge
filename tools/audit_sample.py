#!/usr/bin/env python
"""Reproduce the survivor audit of the paper (Table `tab:audit`).

Ranks survivors by the touch heuristic — the top of the pipeline's own output
ordering, i.e. exactly what a practitioner reading the results sees first — and
prints each with the evidence needed to judge it.

Touch is recomputed here, hypothesis-aware. The count stored in
``cegis_results.json`` came from a version of ``Refuter.touch_count`` that
scored the *relation* over the whole seed frame without re-applying the
conjecture's class hypothesis, so a conditioned bound was credited with tight
graphs outside its own class: ``(claw-free ∧ cubic) ⇒ χ = ω`` was recorded at
3,295 when its true count is 20. Ranking by the stored value therefore floats
heavily-conditioned statements to the top. Only 20 of the old top 100 survive
into the corrected one.

The known/trivial/artefact/interesting judgement is human; this script pins down
*which* statements were judged and pre-sorts them into buckets so the manual
pass starts from evidence rather than from a bare list.

Usage:
    python tools/audit_sample.py [--top 100] [--json OUT] [--latex OUT]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import conjecture_lattice as cl  # noqa: E402
from pipeline.cegis_novelty import classify_statement  # noqa: E402

CORPUS = [
    os.path.join("database", "cache", "battery_bigdb.parquet"),
    os.path.join("database", "cache", "battery_families.parquet"),
    os.path.join("database", "cache", "battery_random.parquet"),
    os.path.join("database", "cache", "battery_degenerate.parquet"),
    os.path.join("database", "cache", "seed_battery.parquet"),
    os.path.join("database", "shards", "*", "cache", "seed_battery.parquet"),
]
GENERATION = [
    os.path.join("database", "cache", "seed_battery.parquet"),
    os.path.join("database", "shards", "*", "cache", "seed_battery.parquet"),
]


def _load(patterns):
    paths = sorted({p for pat in patterns for p in glob.glob(pat)})
    frame = cl.load_pool(paths)
    return (cl.PoolEvaluator(frame) if frame is not None else None), len(paths)


# graphcalc attaches these to every Graffiti3 conjecture as a base guard; they
# are not class restrictions, so a conjecture carrying only these is
# *unconditioned*, and calling its hypothesis "decorative" would be a category
# error rather than a finding.
BASE_HYPOTHESES = {"nontrivial"}


def _bucket(record) -> str:
    """Qualitative verdict, most-dismissable first.

    Three families, matching how a reader actually triages the output:

    *trivial*  — the statement is already known, is implied by another
                 survivor, or its hypothesis does no work.
    *weak*     — it survives, but on too little evidence to mean much: a
                 handful of graphs in its class, or a class the corpus barely
                 represents.
    *promising*— it survives on real evidence. Split by whether the class
                 hypothesis is load-bearing, because a bound that holds for all
                 graphs is a different kind of result from one that needs its
                 class.

    Only the *promising* rows need human thought; the rest carry a stated
    reason that can be confirmed or overturned quickly.
    """
    if record["known_as"]:
        return "trivial:known"
    if record["subsumed_by"]:
        return "trivial:subsumed"
    base_only = set(record["classes"]) <= BASE_HYPOTHESES
    if record["decorative"] and not base_only:
        return "trivial:decorative"
    if record["support_generation"] is not None and record["support_generation"] < 20:
        return "weak:low-support"
    if record["decorative"]:
        return "promising:universal"
    return "promising:class" if not base_only else "promising:universal"


BUCKET_ORDER = ("trivial:known", "trivial:subsumed", "trivial:decorative",
                "weak:low-support", "promising:universal", "promising:class")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join("results", "cegis_results.json"))
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--json", default=os.path.join("results", "audit_top.json"))
    ap.add_argument("--latex", default="")
    ap.add_argument("--listing", default=os.path.join("results", "survivors_by_touch.txt"),
                    help="human-readable listing of every survivor, ranked by touch")
    args = ap.parse_args()

    with open(args.results) as fh:
        conjectures = json.load(fh)["conjectures"]
    tokens = set()
    for c in conjectures:
        tokens |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", c.get("statement") or ""))
    cols = sorted(tokens | {"order_bigger_than_2", "order_bigger_than_3"})

    survivors = cl.parse_survivors(conjectures)
    corpus, n_corpus = _load(CORPUS)
    generation, n_gen = _load(GENERATION)
    if corpus is None or generation is None:
        print("No cached batteries — cannot recompute touch. Run the pipeline first.")
        return 2
    print(f"{len(conjectures)} survivors ({len(survivors)} rankable), "
          f"corpus {corpus.n_rows} graphs / {n_corpus} caches, "
          f"generation {generation.n_rows} graphs / {n_gen} caches")

    subsumed = cl.find_subsumed(survivors)
    records = []
    for i, s in enumerate(survivors):
        if not generation.can_evaluate(s):
            continue
        try:
            known, why = classify_statement(s.statement, cols)
        except Exception:
            known, why = False, None
        _, sup_gen = generation.survives(s.classes, s.norm)
        _, sup_corpus = corpus.survives(s.classes, s.norm)
        lifted = cl.lift(s, corpus)
        records.append({
            "statement": s.statement,
            "classes": sorted(s.classes),
            "touch_generation": generation.touches(s.classes, s.norm),
            "touch_stored": s.touches,
            "support_generation": sup_gen,
            "support_corpus": sup_corpus,
            "known_as": why if known else None,
            "subsumed_by": survivors[subsumed[i]].statement if i in subsumed else None,
            "decorative": bool(cl.is_decorative(s, corpus)),
            "lifts_to": sorted(lifted[0]) if lifted else None,
        })
    records.sort(key=lambda r: -r["touch_generation"])
    for r in records:
        r["bucket"] = _bucket(r)
    # Two rankings. The full one is what the pipeline actually outputs; the
    # novel-only one is what a reader looking for new mathematics wants, since
    # the touch heuristic ranks *known* theorems highest by construction —
    # they are maximally tight, so they crowd the head of the list.
    novel = [r for r in records if not r["known_as"]]
    for i, r in enumerate(records, 1):
        r["rank_all"] = i
    for i, r in enumerate(novel, 1):
        r["rank_novel"] = i
    top = records[: args.top]

    counts = {}
    for r in top:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
    print(f"\npre-classification of the top {len(top)}:")
    for bucket in BUCKET_ORDER:
        if counts.get(bucket):
            print(f"  {bucket:12s} {counts[bucket]:4d}")

    print(f"\n{'#':>3}  {'touch':>6} {'supp':>6}  bucket        statement")
    for i, r in enumerate(top, 1):
        print(f"{i:3d}  {r['touch_generation']:6d} {r['support_generation']:6d}  "
              f"{r['bucket']:19s}  {r['statement'][:68]}")
        if r["known_as"]:
            print(f"      `-> known: {r['known_as'][:88]}")
        elif r["lifts_to"]:
            print(f"      `-> generalises to ({' ∧ '.join(r['lifts_to'])})")

    print(f"\nranking excluding known theorems — top {min(20, len(novel))}:")
    for r in novel[:20]:
        print(f"{r['rank_novel']:3d}  (all #{r['rank_all']:4d})  touch {r['touch_generation']:6d}  "
              f"{r['bucket']:19s}  {r['statement'][:60]}")

    if args.listing:
        os.makedirs(os.path.dirname(args.listing) or ".", exist_ok=True)
        with open(args.listing, "w") as fh:
            fh.write("# AutoGraphForge survivors, ranked by touch number\n")
            fh.write(f"# {len(conjectures)} survivors; {len(records)} carry a "
                     f"recomputed (hypothesis-aware) touch count.\n")
            fh.write("# Format:  [touch] statement    -- verdict\n\n")
            fh.write(f"## Ranked by touch ({len(records)})\n\n")
            for r in records:
                fh.write(f"[{r['touch_generation']:6d}] {r['statement']}"
                         f"    -- {r['bucket']}\n")
            rest = [c.get("statement") or "" for c in conjectures
                    if c.get("statement") not in {r["statement"] for r in records}]
            fh.write(f"\n\n## Not touch-rankable ({len(rest)})\n")
            fh.write("# Necessary conditions `(inequality) => class`: the touch\n"
                     "# heuristic measures how often a *bound* is sharp, which\n"
                     "# has no meaning for a statement whose conclusion is a\n"
                     "# class membership. Listed alphabetically.\n\n")
            for stmt in sorted(rest):
                fh.write(f"[     -] {stmt}\n")
        print(f"\nwrote {args.listing}  ({len(records)} ranked + "
              f"{len(conjectures) - len(records)} unranked)")

    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump({"total_survivors": len(conjectures),
                       "rankable": len(records),
                       "buckets": counts,
                       "conjectures": top,
                       "all_ranked": records}, fh, indent=2)
        print(f"\nwrote {args.json}")
    if args.latex:
        with open(args.latex, "w") as fh:
            fh.write("% generated by tools/audit_sample.py — do not edit by hand\n")
            fh.write("\\begin{tabular}{rrrl}\n\\hline\n")
            fh.write("Rank & Touch & Support & Statement \\\\\n\\hline\n")
            for i, r in enumerate(top, 1):
                stmt = (r["statement"].replace("_", r"\_").replace("⇒", r"$\Rightarrow$")
                        .replace("∧", r"$\wedge$").replace("≤", r"$\leq$")
                        .replace("¬", r"$\neg$").replace("·", r"$\cdot$"))
                fh.write(f"{i} & {r['touch_generation']} & {r['support_generation']} "
                         f"& {stmt} \\\\\n")
            fh.write("\\hline\n\\end{tabular}\n")
        print(f"wrote {args.latex}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
