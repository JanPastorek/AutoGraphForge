#!/usr/bin/env python
"""tools/build_class_hierarchy.py — derive the class-subsumption lattice from ISGCI.

``pipeline/novelty.py`` only applies a known theorem to a candidate when the
theorem's class is a superclass of the candidate's class, so every missing edge
in that lattice is a rediscovery the filter fails to flag. Hand-maintaining it
does not scale: the six entries it started with cover a fraction of the true
containments among the classes we already model.

ISGCI (https://graphclasses.org) publishes the containments as data — 1,690
classes, 3,929 inclusion relationships — and the ``graphotaxy`` project ships a
machine-readable snapshot of it. This script reads that snapshot, resolves our
column names to ISGCI classes, and writes the *transitive* superclass closure
restricted to our own vocabulary to ``pipeline/data/class_hierarchy.json``.

Only our vocabulary is kept, deliberately. A theorem is only ever tagged with a
class we model, so the other ~1,200 ISGCI classes can never match; keeping them
would add a megabyte of data that no lookup can reach, and would make the table
impossible to review by hand. The generated file is checked in, so the pipeline
has no runtime dependency on graphotaxy or on network access.

Usage:
    git clone --depth 1 https://github.com/alabarre/graphotaxy
    python tools/build_class_hierarchy.py --graphotaxy ./graphotaxy
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Our class-column name → the ISGCI class name it denotes.
#
# Two mismatches are deliberate and load-bearing:
#
#   * ISGCI classes are hereditary, so its "tree" is what we call *acyclic*
#     (= forest). We point both of our names at it: for `acyclic` that is exact,
#     and for `tree` it is sound in the direction we need, since every tree is a
#     forest and therefore lies in every superclass of forests.
#   * `subcubic` is ISGCI's "maximum degree 3".
#
# Classes with no ISGCI counterpart (regular, connected, eulerian, nontrivial,
# the order thresholds) are handled by MANUAL_SUPERCLASSES in pipeline/novelty.py.
COLUMN_TO_ISGCI = {
    # modelled today — battery columns and known-theorem tags
    "bipartite": "bipartite",
    "chordal": "chordal",
    "claw_free": "claw-free",
    "cograph": "cograph",
    "cubic": "cubic",
    "hamiltonian": "hamiltonian",
    "K_4_free": "K_{4}-free",
    "outerplanar": "outerplanar",
    "planar": "planar",
    "split": "split",
    "subcubic": "maximum degree 3",
    "triangle_free": "triangle-free",
    "well_covered": "well covered",
    "acyclic": "tree",
    "tree": "tree",
    # not generated today, but classical theorems are stated for them, so having
    # the containments in place lets such a theorem subsume candidates in the
    # subclasses we *do* generate (e.g. anything known for perfect graphs
    # immediately covers bipartite, chordal, cograph and split candidates).
    "perfect": "perfect",
    "comparability": "comparability",
    "distance_hereditary": "distance-hereditary",
    "interval": "interval",
    "threshold": "threshold",
    "series_parallel": "series-parallel",
    "block": "block",
    "cactus": "cactus",
    "unicyclic": "unicyclic",
    "caterpillar": "caterpillar",
    "complete": "complete",
    "line_graph": "line",
}

# When two of our columns denote the same ISGCI class, only one may be used to
# label that class in the reverse direction — otherwise every *subclass* of it
# would inherit both names, and the narrower name would be wrong. ISGCI's "tree"
# is the hereditary class of forests, so `acyclic` is the faithful label; the
# `tree ⊆ acyclic` edge is then supplied manually in novelty.py. Losing
# `caterpillar ⊆ tree` this way is a conservative under-approximation, which is
# the safe direction for a filter that must never hide a genuine conjecture.
CANONICAL = {"tree": "acyclic"}


def _load(gx_dir: str):
    import networkx as nx

    isgci = os.path.join(gx_dir, "src", "isgci")
    if not os.path.isdir(isgci):
        raise SystemExit(f"not a graphotaxy checkout (no src/isgci): {gx_dir}")

    def _j(name):
        with open(os.path.join(isgci, name)) as fh:
            return json.load(fh)

    graph = nx.node_link_graph(_j("isgci_inclusion_graph.json"), edges="edges")
    equivalences = _j("isgci_equivalences.json")
    id_to_name = {k: v.strip() for k, v in _j("isgci_ids_to_names.json").items()}
    version = _j("isgci_version_info.json")
    return graph, equivalences, id_to_name, version


def resolve(name, graph, equivalences, name_to_ids):
    """ISGCI class name → a node id present in the inclusion graph.

    ISGCI records equal classes under several ids and the shipped graph keeps one
    representative per equivalence class, so the id a name maps to is often not
    itself a node (``bipartite`` is stored, the graph carries the equivalent
    ``(0,2)-colorable``). Following the equivalence list is exact, not a guess:
    ISGCI equivalence means the two classes contain the same graphs.
    """
    for i in name_to_ids.get(name, []):
        if i in graph:
            return i, i
    for i in name_to_ids.get(name, []):
        for _, j in equivalences.get(i, []):
            if j in graph:
                return j, i
    return None, None


def build(gx_dir: str):
    import networkx as nx

    graph, equivalences, id_to_name, version = _load(gx_dir)
    name_to_ids = {}
    for i, n in id_to_name.items():
        name_to_ids.setdefault(n, []).append(i)

    node_of, unresolved = {}, []
    for col, isgci_name in COLUMN_TO_ISGCI.items():
        node, via = resolve(isgci_name, graph, equivalences, name_to_ids)
        if node is None:
            unresolved.append((col, isgci_name))
        else:
            node_of[col] = node
    if unresolved:
        raise SystemExit("unresolved ISGCI names (fix COLUMN_TO_ISGCI): "
                         + ", ".join(f"{c} → {n!r}" for c, n in unresolved))

    # reverse map, one label per node (see CANONICAL)
    label_of = {}
    for col, node in sorted(node_of.items()):
        isgci_name = COLUMN_TO_ISGCI[col]
        chosen = CANONICAL.get(isgci_name)
        if chosen is not None and chosen != col:
            continue
        if node in label_of and label_of[node] != col:
            raise SystemExit(
                f"columns {label_of[node]!r} and {col!r} both denote ISGCI node "
                f"{node} ({id_to_name.get(node)!r}); add an entry to CANONICAL "
                f"choosing which one may label subclasses of it.")
        label_of[node] = col

    # Ancestors are the superclasses: an arc runs from a class to its subclasses
    # (planar → 'K_{4}-free ∩ planar'), and nx.ancestors is already transitive,
    # which is what novelty.py's flat lookup needs.
    table = {}
    for col, node in sorted(node_of.items()):
        sup = sorted({label_of[a] for a in nx.ancestors(graph, node)
                      if a in label_of} - {col})
        if sup:
            table[col] = sup

    meta = {
        "source": "ISGCI (https://graphclasses.org) via github.com/alabarre/graphotaxy",
        "isgci_download_date": version.get("download date"),
        "isgci_classes": version.get("number of classes"),
        "isgci_inclusions": version.get("number of inclusion relationships"),
        "note": ("Transitive superclass closure restricted to the class vocabulary "
                 "this pipeline models. Generated by tools/build_class_hierarchy.py "
                 "— edit that script, not this file. Classes outside ISGCI (regular, "
                 "connected, eulerian, order thresholds) live in novelty.MANUAL_SUPERCLASSES."),
    }
    return {"_meta": meta, "superclasses": table}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphotaxy", required=True,
                    help="path to a graphotaxy checkout (needs src/isgci/)")
    ap.add_argument("--out", default=os.path.join("pipeline", "data",
                                                  "class_hierarchy.json"))
    args = ap.parse_args()

    payload = build(args.graphotaxy)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")

    table = payload["superclasses"]
    edges = sum(len(v) for v in table.values())
    print(f"{len(table)} classes, {edges} superclass edges → {args.out}")
    print(f"ISGCI snapshot {payload['_meta']['isgci_download_date']} "
          f"({payload['_meta']['isgci_classes']} classes)")
    for col in sorted(table):
        print(f"  {col:22s} ⊆ {', '.join(table[col])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
