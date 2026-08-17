"""
pipeline/lean_disproof.py — formal Lean 4 *disproofs* for refuted conjectures.

The refutation engine already produces the hard part of a disproof: a conjecture
together with a graph on which it fails. Turning that pair into a machine-checked
theorem costs nothing extra — the proof is "evaluate both sides on this graph" —
provided the invariants can actually be evaluated by the kernel. They can, via
the computable mirror in ``LeanProject.GraphInvariantsComputable`` (the
specification-style definitions in ``GraphInvariants.lean`` use ``sInf`` over a
``Set`` and are noncomputable, so ``decide`` stalls on them).

The emitted shape is a negated universal discharged at the witness::

    theorem CEGIS_disproof_ab12 :
        ¬ (∀ {V : Type} [Fintype V] [DecidableEq V]
             (G : SimpleGraph V) [DecidableRel G.Adj],
             GraphCalc.IsNontrivialClass G →
             GraphCalc.totalZeroForcingNumber G ≤ GraphCalc.zeroForcingNumber G) := by
      intro h
      have := @h (Fin 5) _ _ Gcex _ (by decide)
      revert this
      decide

Scope mirrors ``lean_export``: a conjecture whose invariants or classes are not
in the computable layer is skipped rather than mis-formalized, and so is a
witness too large to evaluate (the subset enumerations are exponential in the
vertex count).
"""
from __future__ import annotations

import hashlib
import re
from typing import Dict, List, Optional, Tuple

from pipeline import linear_form

# invariant column → expression over `(G : SimpleGraph V)` in the computable layer.
SUPPORTED: Dict[str, str] = {
    "order":                         "GraphCalc.order G",
    "size":                          "GraphCalc.size G",
    "minimum_degree":                "G.minDegree",
    "maximum_degree":                "G.maxDegree",
    "clique_number":                 "GraphCalc.cliqueNum G",
    "independence_number":           "GraphCalc.indepNum G",
    "domination_number":             "GraphCalc.dominationNumber G",
    "independent_domination_number": "GraphCalc.independentDominationNumber G",
    "slater":                        "GraphCalc.slaterNumber G",
    "annihilation_number":           "GraphCalc.annihilationNumber G",
    "zero_forcing_number":           "GraphCalc.zeroForcingNumber G",
    "total_zero_forcing_number":     "GraphCalc.totalZeroForcingNumber G",
    # Computable mirror added alongside the spec-layer `sInf` version, which is
    # noncomputable and so was unusable here; checked against graphcalc by
    # tools/lean_differential.py before being listed.
    "connected_zero_forcing_number": "GraphCalc.connectedZeroForcingNumber G",
    "vertex_cover_number":            "GraphCalc.vertexCoverNumber G",
}

# class column → decidable predicate in the computable layer.
CLASS_PREDICATES: Dict[str, str] = {
    "nontrivial":     "GraphCalc.IsNontrivialClass",
    "regular":        "GraphCalc.IsRegularClass",
    "cubic":          "GraphCalc.IsCubicClass",
    "subcubic":       "GraphCalc.IsSubcubicClass",
    "eulerian":       "GraphCalc.IsEulerianClass",
    "triangle_free":  "GraphCalc.IsTriangleFreeClass",
    "K_4_free":       "GraphCalc.IsK4FreeClass",
    "connected":      "GraphCalc.IsConnectedClass",
    "tree":           "GraphCalc.IsTreeClass",
    "claw_free":      "GraphCalc.IsClawFreeClass",
    "cograph":        "GraphCalc.IsCographClass",
    # Computable mirror of the spec-layer `G.Colorable 2`, which has no
    # Decidable instance; validated against graphcalc before being listed.
    "bipartite":      "GraphCalc.IsBipartiteClass",
}

# Every invariant is a minimum/maximum over subsets of V, so evaluation is
# exponential in the vertex count, and past some size the kernel check stops
# being worth attempting. The refutation itself is still recorded either way.
#
# The previous value of 8 turned out to measure the *heartbeat limit* rather
# than feasibility: order-9 witnesses all failed at ~26 s with `maxHeartbeats`
# exceeded, but one verified in 387 s once heartbeats were unbounded (see the
# preamble). 10 is deliberately conservative — beyond it the cost has not been
# measured, and an unbounded heartbeat count means a bad case hangs until the
# subprocess timeout rather than failing fast.
MAX_WITNESS_ORDER = 10

_REL_LEAN = {"≤": "≤", "≥": "≥", "<=": "≤", ">=": "≥", "=": "="}

# `maxRecDepth` raises the *elaborator's* recursion limit only; it does not
# weaken the kernel check that follows. The whole proof is evaluation, and the
# class tests enumerate vertex tuples: the cograph test is four nested
# quantifiers, so an 8-vertex witness needs 8⁴ steps. Measured at n = 8 — the
# default depth fails on cograph (connected/tree/claw-free still pass), this
# value succeeds.
# `maxHeartbeats 0` removes the elaborator's *time* limit, not any soundness
# check — the kernel still rechecks the finished term. Without it the default
# budget expires after roughly 26 s, which silently capped the usable witness
# size: an order-9 disproof that needs 387 s of honest evaluation was being
# reported as a failure indistinguishable from a false statement.
_PREAMBLE = ("import Mathlib\n"
             "import LeanProject.GraphInvariantsComputable\n\n"
             "set_option maxRecDepth 100000\n"
             "set_option maxHeartbeats 0\n\n"
             "open SimpleGraph\n")


# Invariants whose `minCard` has no witness on some graphs — `connectedZeroForcingNumber`
# on any disconnected graph, `totalZeroForcingNumber` whenever a vertex has no
# neighbour in any forcing set. There `minCard` falls back to 0 while graphcalc
# reports nothing, so a conjecture like `Z_c + 2 <= 2 * Z_t` degenerates to
# `2 <= 0` and is refutable with no mathematics. The generator never claimed
# anything about those graphs, so the export carries the definedness hypothesis.
PARTIAL_INVARIANTS = {
    "connected_zero_forcing_number": "HasConnectedZeroForcingNumber",
    "total_zero_forcing_number":     "HasTotalZeroForcingNumber",
}


def definedness_hyps(names, qualify):
    """Definedness predicates required by the invariants in `names`."""
    return [qualify(PARTIAL_INVARIANTS[n]) for n in sorted(names)
            if n in PARTIAL_INVARIANTS]


def _edge_list(graph6: str) -> Optional[Tuple[int, List[Tuple[int, int]]]]:
    """(order, edges) for a graph6 string, else None."""
    try:
        import networkx as nx
        G = nx.from_graph6_bytes(graph6.encode("ascii"))
        G = nx.convert_node_labels_to_integers(G)
        return G.number_of_nodes(), sorted(tuple(sorted(e)) for e in G.edges())
    except Exception:
        return None




def _parse(statement: str, columns) -> Optional[Tuple[List[str], str]]:
    """(classes, lean_body) for a class-conditioned inequality.

    The body is any rational linear comparison, not just ``invariant REL
    invariant``. Restricting it to bare invariants rejected most of what the
    generator actually produces — constant bounds like ``zero_forcing_number ≤
    8`` and scaled forms like ``maximum_degree ≤ 2 · independence_number`` — so
    conjectures went unrefuted for want of a parser rather than for want of a
    counterexample.

    ``linear_form`` does the rewriting, the same module the necessary-condition
    branch uses. It scales by the lcm of the denominators and moves negative
    terms across, so every coefficient ends up non-negative and the ℕ statement
    is equivalent rather than merely truncated.
    """
    if "⇒" not in statement:
        return None
    cond, body = statement.split("⇒", 1)
    classes = [c for c in columns if re.search(r"\b" + re.escape(c) + r"\b", cond)]
    if not classes or any(c not in CLASS_PREDICATES for c in classes):
        return None
    # A body that is itself all classes is the necessary-condition shape.
    names = set(linear_form.invariants(body))
    if not names or names <= set(CLASS_PREDICATES):
        return None
    if any(n not in SUPPORTED for n in names):
        return None
    rendered = linear_form.render_comparison(body, SUPPORTED)
    if rendered is None:
        return None
    return classes, rendered, definedness_hyps(names, lambda h: f"GraphCalc.{h} G")


def _parse_necessary(statement: str) -> Optional[Tuple[str, str]]:
    """(lean_hypothesis, lean_conclusion) for an ``(inequality) ⇒ classes``
    survivor, else None.

    The hypothesis is normalised to ℕ by ``linear_form`` — the same rewriting the
    positive exporter applies, so the theorem and its disproof are statements
    about the same proposition.
    """
    if "⇒" not in statement:
        return None
    cond, concl = statement.split("⇒", 1)
    clauses = linear_form.parse_class_conclusion(concl)
    if not clauses or any(c not in CLASS_PREDICATES for _, c in clauses):
        return None
    names = set(linear_form.invariants(cond))
    if not names or names <= set(CLASS_PREDICATES):
        return None                        # class-conditioned shape, not this one
    if any(n not in SUPPORTED for n in names):
        return None
    hyp = linear_form.render_comparison(cond, SUPPORTED)
    if hyp is None:
        return None
    goal = " ∧ ".join(
        f"¬ {CLASS_PREDICATES[c]} G" if neg else f"{CLASS_PREDICATES[c]} G"
        for neg, c in clauses)
    # Mirror the theorem: the conjecture is about non-trivial graphs, so a
    # disproof must exhibit one. Omitting this made every statement of this
    # shape refutable by Fin 0, where the class predicates hold vacuously.
    guards = [f"{CLASS_PREDICATES['nontrivial']} G"] + \
        definedness_hyps(names, lambda h: f"GraphCalc.{h} G")
    return " → ".join(guards + [hyp]), goal


def is_supported(statement: str, columns, witness_graph6: Optional[str]) -> bool:
    """True iff ``render`` would produce a disproof for this refutation."""
    return render(statement, columns, witness_graph6) is not None


def render(statement: str, columns, witness_graph6: Optional[str],
           name: Optional[str] = None) -> Optional[str]:
    """A self-contained Lean 4 disproof file, or None if out of scope."""
    if not witness_graph6:
        return None
    parsed = _parse(statement, columns)
    necessary = _parse_necessary(statement) if parsed is None else None
    if parsed is None and necessary is None:
        return None
    built = _edge_list(witness_graph6)
    if built is None:
        return None
    n, edges = built
    if n < 1 or n > MAX_WITNESS_ORDER:
        return None

    if name is None:
        name = "CEGIS_disproof_" + hashlib.sha1(statement.encode()).hexdigest()[:8]

    es = ", ".join(f"({a}, {b})" for a, b in edges)
    if parsed is not None:
        classes, body, defined = parsed
        parts = [f"{CLASS_PREDICATES[c]} G" for c in classes] + defined
        hyp_types = " → ".join(parts)
        # One `(by decide)` per hypothesis, discharged on the witness.
        hyp_args = " ".join("(by decide)" for _ in parts)
    else:
        # (inequality) ⇒ classes. The hypothesis is about the graph rather than
        # a typeclass argument, so it stays inside the implication and is
        # discharged by the same `decide` that settles the conclusion.
        hyp_types, body = necessary
        hyp_args = ""

    return (
        f"{_PREAMBLE}\n"
        f"-- Refuted conjecture: {statement}\n"
        f"-- Counterexample (graph6): {witness_graph6}  "
        f"[order {n}, size {len(edges)}]\n"
        f"abbrev Gcex : SimpleGraph (Fin {n}) := GraphCalc.ofEdges {n} [{es}]\n\n"
        f"theorem {name} :\n"
        f"    ¬ (∀ {{V : Type}} [Fintype V] [DecidableEq V]\n"
        f"         (G : SimpleGraph V) [DecidableRel G.Adj],\n"
        f"         {hyp_types} → {body}) := by\n"
        f"  intro h\n"
        f"  have := @h (Fin {n}) _ _ Gcex _{' ' + hyp_args if hyp_args else ''}\n"
        f"  revert this\n"
        f"  decide\n"
    )


def export_refutations(refutations, columns, limit: Optional[int] = None
                       ) -> List[Tuple[dict, str]]:
    """(record, lean_source) for every refutation we can formalize.

    Smallest witnesses first: they are both the cheapest to check and the most
    informative counterexamples.
    """
    ranked = sorted(
        (r for r in refutations if r.get("witness_graph6")),
        key=lambda r: (r.get("witness_order") or 99, r.get("witness_size") or 99))
    out: List[Tuple[dict, str]] = []
    for rec in ranked:
        src = render(rec.get("statement", ""), columns, rec.get("witness_graph6"))
        if src is not None:
            out.append((rec, src))
            if limit and len(out) >= limit:
                break
    return out
