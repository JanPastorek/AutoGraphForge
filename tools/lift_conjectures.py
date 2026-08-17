#!/usr/bin/env python
"""tools/lift_conjectures.py — deduplicate survivors and generalise them.

The survivor list contains the same claim at several strengths, and claims whose
class hypothesis does no work. This tool annotates both, using the ISGCI class
lattice imported by ``tools/build_class_hierarchy.py``.

  * dedup (always) — a survivor whose hypothesis is *stronger* than another
    survivor's, over the same body, is logically implied by it.
  * ``--lift`` — relax each hypothesis upward and re-test on the refutation
    pool, keeping the weakest one that still survives.
  * ``--lift`` also flags **decorative** hypotheses: bodies that survive with no
    hypothesis at all, which are usually artifacts of the pool's bounded size
    rather than theorems about the class.

Lifting reads the cached batteries, so it needs no recomputation, but its
verdicts are only as good as that pool — a lift is a stronger conjecture to
re-refute, not a proven generalisation.

Usage:
    python tools/lift_conjectures.py                    # dedup only
    python tools/lift_conjectures.py --lift --self-check
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import conjecture_lattice as cl  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join("results", "cegis_results.json"))
    ap.add_argument("--out", default=os.path.join("results", "lifted.json"))
    # Every graph the conjectures were exposed to, not just the refutation
    # tiers. The seed corpora matter most: they are the accumulated witnesses
    # that killed earlier conjectures, so they are the extremal graphs and are
    # concentrated in exactly the classes the tiers cover worst (cubic, regular,
    # tree). Sharded runs keep their own seed under database/shards/<id>/ —
    # a graph found hard by one shard is still evidence for every shard.
    ap.add_argument("--corpus", nargs="+", default=[
        os.path.join("database", "cache", "battery_bigdb.parquet"),
        os.path.join("database", "cache", "battery_families.parquet"),
        os.path.join("database", "cache", "battery_random.parquet"),
        os.path.join("database", "cache", "seed_battery.parquet"),
        os.path.join("database", "shards", "*", "cache", "seed_battery.parquet"),
    ], help="cached battery parquets forming the corpus (globs allowed)")
    # The generation corpus on its own. A conjecture is *proposed* because it
    # holds — and is tight — on these graphs, so ranking by them says how the
    # generator found it interesting; ranking by the full corpus says how well
    # the claim holds up. The two orders differ, and both are worth having.
    ap.add_argument("--generation", nargs="+", default=[
        os.path.join("database", "cache", "seed_battery.parquet"),
        os.path.join("database", "shards", "*", "cache", "seed_battery.parquet"),
    ], help="cached batteries of the seed corpus the conjectures were generated on")
    ap.add_argument("--lift", action="store_true",
                    help="also relax hypotheses upward and re-test on the pool")
    ap.add_argument("--min-support", type=int, default=100,
                    help="flag conjectures tested against fewer pool graphs than this")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any survivor is refuted by the corpus")
    args = ap.parse_args()

    if not os.path.exists(args.results):
        print(f"No results at {args.results} — run the CEGIS loop first.")
        return 0
    with open(args.results) as fh:
        conjectures = json.load(fh).get("conjectures", [])
    survivors = cl.parse_survivors(conjectures)
    print(f"{len(conjectures)} survivors, {len(survivors)} class-conditioned "
          f"with a parseable body")
    if not survivors:
        return 0

    # ---- dedup (no data needed) --------------------------------------------
    subsumed = cl.find_subsumed(survivors)
    print(f"\ndedup: {len(subsumed)} subsumed by a more general survivor")
    for i, j in list(subsumed.items())[:5]:
        print(f"  redundant : {survivors[i].statement}")
        print(f"    implied by: {survivors[j].statement}")

    records = []
    for i, s in enumerate(survivors):
        records.append({
            "statement": s.statement,
            "classes": sorted(s.classes),
            "touches": s.touches,
            "subsumed_by": survivors[subsumed[i]].statement if i in subsumed else None,
        })

    # ---- lift (needs the pool) ---------------------------------------------
    if args.lift:
        paths = sorted({p for pattern in args.corpus for p in glob.glob(pattern)})
        frame = cl.load_pool(paths)
        if frame is None:
            print(f"\nNo corpus matched {args.corpus} — cannot lift. "
                  f"Run tools/precompute_battery.py first.")
            return 2
        evaluator = cl.PoolEvaluator(frame)
        print(f"\ncorpus: {evaluator.n_rows} distinct graphs from {len(paths)} "
              f"cache(s), {len(evaluator.classes)} class columns")

        gen_paths = sorted({p for pattern in args.generation for p in glob.glob(pattern)})
        gen_frame = cl.load_pool(gen_paths)
        gen = cl.PoolEvaluator(gen_frame) if gen_frame is not None else None
        if gen is not None:
            print(f"generation corpus: {gen.n_rows} distinct seed graphs "
                  f"from {len(gen_paths)} cache(s)")
        else:
            print("generation corpus: none found — seed rankings unavailable")

        lifted = decorative = low_support = untestable = refuted = 0
        for record, s in zip(records, survivors, strict=True):
            if not evaluator.can_evaluate(s):
                record["support"] = None
                untestable += 1
                continue
            ok, support = evaluator.survives(s.classes, s.norm)
            record["support_corpus"] = support
            record["touch_corpus"] = evaluator.touches(s.classes, s.norm)
            if gen is not None and gen.can_evaluate(s):
                _, gen_support = gen.survives(s.classes, s.norm)
                record["support_generation"] = gen_support
                record["touch_generation"] = gen.touches(s.classes, s.norm)
            if ok is False:
                # A survivor the corpus refutes. Sharded runs each saw only
                # their own witnesses, so a graph that one shard found hard can
                # refute a conjecture another shard kept. Flagged rather than
                # fatal: this is new information, not a broken evaluator.
                record["refuted_by_corpus"] = True
                refuted += 1
                continue
            if 0 < support < args.min_support:
                record["low_support"] = True
                low_support += 1
            if cl.is_decorative(s, evaluator):
                record["decorative"] = True
                decorative += 1
                continue            # no hypothesis needed; a lift adds nothing
            best = cl.lift(s, evaluator)
            if best is not None:
                target, target_support = best
                record["lifts_to"] = sorted(target)
                record["lift_support"] = target_support
                lifted += 1

        print(f"\nrefuted by the full corpus: {refuted} "
              f"(kept by a shard that never saw the witness)")
        print(f"lift: {lifted} generalise to a weaker hypothesis that still survives")
        print(f"      {decorative} are DECORATIVE — the body survives with no "
              f"hypothesis at all")
        print(f"      {low_support} tested against < {args.min_support} pool graphs "
              f"(weak evidence)")
        print(f"      {untestable} not testable (invariant absent from the pool)")

        worst = sorted((r for r in records if r.get("low_support")),
                       key=lambda r: r["support_corpus"])[:5]
        if worst:
            print("\n  least-tested survivors:")
            for r in worst:
                print(f"    support {r['support_corpus']:5d}  {r['statement'][:88]}")

        # The two rankings answer different questions, so show both.
        live = [r for r in records
                if not r["subsumed_by"] and not r.get("decorative")
                and not r.get("refuted_by_corpus")]
        for label, field in (("generation (seed) touch", "touch_generation"),
                             ("full-corpus touch", "touch_corpus")):
            ranked = sorted((r for r in live if r.get(field)),
                            key=lambda r: -r[field])[:5]
            if not ranked:
                continue
            print(f"\n  top by {label}:")
            for r in ranked:
                print(f"    touch {r[field]:6d}  (corpus {r.get('touch_corpus', 0):6d} / "
                      f"seed {r.get('touch_generation', 0):5d})  {r['statement'][:70]}")
        overlap = {id(r) for r in sorted((r for r in live if r.get("touch_generation")),
                                         key=lambda r: -r["touch_generation"])[:50]}
        other = {id(r) for r in sorted((r for r in live if r.get("touch_corpus")),
                                       key=lambda r: -r["touch_corpus"])[:50]}
        if overlap and other:
            print(f"\n  top-50 by seed touch vs by corpus touch: "
                  f"{len(overlap & other)} in common")

    keep = sum(1 for r in records
               if not r["subsumed_by"] and not r.get("decorative")
               and not r.get("refuted_by_corpus"))
    payload = {
        "total": len(records),
        "subsumed": len(subsumed),
        "decorative": sum(1 for r in records if r.get("decorative")),
        "refuted_by_corpus": sum(1 for r in records if r.get("refuted_by_corpus")),
        "lifted": sum(1 for r in records if r.get("lifts_to")),
        "low_support": sum(1 for r in records if r.get("low_support")),
        "kept": keep,
        "conjectures": records,
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"\n{keep} survivors kept after dedup"
          f"{', corpus refutation and decorative filtering' if args.lift else ''}"
          f" → {args.out}")
    if args.strict and payload["refuted_by_corpus"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
