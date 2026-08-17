"""
pipeline/lean_export.py — well-formed Lean 4 export for the *supported* subset of
CEGIS survivors.

graffiti3 will happily render any conjecture to a Lean stub, but a stub over
undefined symbols (``domination_number G``) can never be kernel-verified. This
module restricts export to conjectures whose invariants are backed by the
``LeanProject.GraphInvariants`` preamble (mathlib defs + a small domination
layer), maps each invariant to its real Lean name, and emits a self-contained,
compilable ``theorem … := sorry`` (imports + binders + ``open SimpleGraph``) that
a prover can actually close.

Out of scope (silently skipped, not mis-formalized): invariants with no faithful
mathlib definition yet (zero forcing, residue, Roman domination, …) and
conjectures conditioned on a graph class with no formalization (chordal, planar).
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from pipeline import linear_form
from pipeline.lean_disproof import definedness_hyps

# pipeline invariant column  →  Lean expression over `(G : SimpleGraph V)`.
# Only invariants with a faithful definition in LeanProject.GraphInvariants (or
# mathlib, re-exported there) appear here.
SUPPORTED: Dict[str, str] = {
    "order":                         "G.order",
    "size":                          "G.size",
    "minimum_degree":                "G.minDegree",
    "maximum_degree":                "G.maxDegree",
    "clique_number":                 "G.cliqueNum",
    "independence_number":           "G.indepNum",
    "domination_number":             "G.dominationNumber",
    "independent_domination_number": "G.independentDominationNumber",
    "slater":                        "G.slaterNumber",
    "annihilation_number":           "G.annihilationNumber",
    "zero_forcing_number":           "G.zeroForcingNumber",
    "total_zero_forcing_number":     "G.totalZeroForcingNumber",
    "connected_zero_forcing_number": "G.connectedZeroForcingNumber",
    "vertex_cover_number":            "(G.vertexCoverNum).toNat",
}

# Injected binders: a finite vertex type with decidable adjacency, enough for
# every invariant above to elaborate.
_HEADER_BINDERS = ("{V : Type*} [Fintype V] [DecidableEq V]\n"
                   "    (G : SimpleGraph V) [DecidableRel G.Adj]")

_PREAMBLE = "import Mathlib\nimport LeanProject.GraphInvariants\n\nopen SimpleGraph\n"

_SIG_RE = re.compile(r"theorem\s+(\w+)\s*\(G\s*:\s*SimpleGraph\s+V\)")

# graph-class column → preamble predicate. The remaining unformalized classes
# are chordal and planar: neither has a mathlib definition or a cheap decidable
# characterization, so conjectures conditioned on them stay unexportable.
CLASS_PREDICATES = {
    "regular": "IsRegularClass", "cubic": "IsCubicClass",
    "subcubic": "IsSubcubicClass", "triangle_free": "IsTriangleFreeClass",
    "K_4_free": "IsK4FreeClass", "bipartite": "IsBipartiteClass",
    "eulerian": "IsEulerianClass",
    # mathlib has these directly (`Connected`, `IsTree`)
    "connected": "IsConnectedClass", "tree": "IsTreeClass",
    # forbidden induced subgraph on four vertices: K₁,₃ and P₄ respectively
    "claw_free": "IsClawFreeClass", "cograph": "IsCographClass",
    # graphcalc's auto-base hypothesis on every Graffiti3 conjecture: |V| ≥ 2.
    "nontrivial": "IsNontrivialClass",
}
_REL_LEAN = {"≤": "≤", "≥": "≥", "<=": "≤", ">=": "≥", "=": "="}


def _condition_classes(cond: str, columns) -> List[str]:
    return [c for c in columns if re.search(r"\b" + re.escape(c) + r"\b", cond)]


def _bare_invariant(side: str, columns) -> Optional[str]:
    """A side that is exactly one supported invariant (no coefficient/offset/
    product), else None."""
    invs = [c for c in columns if re.search(r"\b" + re.escape(c) + r"\b", side)]
    if len(invs) != 1 or invs[0] not in SUPPORTED:
        return None
    leftover = re.sub(r"\b" + re.escape(invs[0]) + r"\b", " ", side)
    leftover = re.sub(r"[()\s]", "", leftover)        # parens/space ok
    return invs[0] if not leftover else None           # any coeff/const → reject


def render_conditioned(native, columns) -> Optional[str]:
    """Self-rendered theorem for a class-conditioned conjecture with a simple
    ``invariant REL invariant`` body, else None. The hypothesis is the conjunction
    of supported class predicates."""
    try:
        pretty = native.pretty()
    except Exception:
        return None
    if "⇒" not in pretty:
        return None
    cond, body = pretty.split("⇒", 1)
    classes = _condition_classes(cond, columns)
    if not classes or any(c not in CLASS_PREDICATES for c in classes):
        return None                                    # unsupported class (chordal, planar)
    # Any rational linear comparison, normalised to ℕ by `linear_form` — the
    # same rewriting `render_necessary` and the disproof exporter apply.
    #
    # Both the ℕ and the widening matter. Restricting the body to bare
    # invariants rejected constant bounds and scaled forms, so most
    # class-conditioned survivors could not be stated at all; and rendering in
    # ℝ here while the disproof rendered in ℕ meant the exported theorem and
    # its refutation were not literally negations of one another. Going through
    # one normaliser keeps `prove` and `refute` about the same proposition.
    names = set(linear_form.invariants(body))
    if not names or names <= set(CLASS_PREDICATES):
        return None
    if any(n not in SUPPORTED for n in names):
        return None
    body_lean = linear_form.render_comparison(body, SUPPORTED)
    if body_lean is None:
        return None
    binders = [f"G.{CLASS_PREDICATES[c]}" for c in classes] + \
        definedness_hyps(names, lambda h: f"G.{h}")
    hyps = " ".join(f"(_h{i} : {b})" for i, b in enumerate(binders))
    thm = (f"theorem CEGIS_1 {_HEADER_BINDERS}\n    {hyps}\n  : {body_lean} :=\nsorry")
    return _PREAMBLE + "\n" + thm


def render_necessary(native, columns) -> Optional[str]:
    """Theorem for a *necessary-condition* survivor, else None.

    These read ``(inequality) ⇒ class-conclusion``: an inequality among the
    invariants forces the graph into (or out of) a class, e.g.
    ``(2 · independence_number < order) ⇒ ¬tree``. The hypothesis is a general
    rational linear comparison, so it goes through ``linear_form``, which
    rewrites it as an equivalent inequality over ℕ (see that module for why not
    ℝ or ℚ). The conclusion is a conjunction of possibly-negated classes.
    """
    try:
        pretty = native.pretty()
    except Exception:
        return None
    if "⇒" not in pretty:
        return None
    cond, concl = pretty.split("⇒", 1)

    clauses = linear_form.parse_class_conclusion(concl)
    if not clauses or any(c not in CLASS_PREDICATES for _, c in clauses):
        return None
    # An all-class hypothesis is the class-conditioned shape, handled elsewhere.
    hypothesis_names = set(linear_form.invariants(cond))
    if not hypothesis_names or hypothesis_names <= set(CLASS_PREDICATES):
        return None
    if any(n not in SUPPORTED for n in hypothesis_names):
        return None

    hyp = linear_form.render_comparison(cond, SUPPORTED)
    if hyp is None:
        return None
    goal = " ∧ ".join(
        f"¬ G.{CLASS_PREDICATES[c]}" if neg else f"G.{CLASS_PREDICATES[c]}"
        for neg, c in clauses)
    # `nontrivial` is restored explicitly: it is part of the conjecture's scope,
    # not decoration. Without it the statement is about all finite graphs
    # including the empty one, which no generated conjecture ever claimed.
    extra = definedness_hyps(hypothesis_names, lambda h: f"G.{h}")
    guards = " ".join(f"(_hd{i} : {e})" for i, e in enumerate(extra))
    thm = (f"theorem CEGIS_1 {_HEADER_BINDERS}\n"
           f"    (_hnt : G.IsNontrivialClass) {guards}(_h0 : {hyp})\n"
           f"  : {goal} :=\nsorry")
    return _PREAMBLE + "\n" + thm


def make_lean_label(columns) -> Dict[str, str]:
    """lean_label for Graffiti3: supported columns → preamble Lean names.

    Unsupported columns still get a placeholder so graffiti3's renderer doesn't
    crash; conjectures that actually *use* them are rejected by ``is_supported``.
    """
    return {c: SUPPORTED.get(c, f"{c} G") for c in columns}


def _columns_used(native, columns) -> List[str]:
    pretty = native.pretty()
    return [c for c in columns if re.search(r"\b" + re.escape(c) + r"\b", pretty)]


def is_supported(native, columns) -> bool:
    """True iff the conjecture is kernel-checkable: either unconditioned with all
    invariants in ``SUPPORTED``, or class-conditioned with a simple body and all
    classes in ``CLASS_PREDICATES`` (see ``render_conditioned``). Non-inequality
    survivors (e.g. SophieCondition, no ``pretty``) are unsupported."""
    try:
        pretty = native.pretty()
    except Exception:
        return False                              # SophieCondition / non-inequality
    if "⇒" in pretty or "=>" in pretty:          # conditioned → needs a class theorem
        return (render_conditioned(native, columns) is not None
                or render_necessary(native, columns) is not None)
    used = _columns_used(native, columns)
    return bool(used) and all(c in SUPPORTED for c in used)


def _finish(raw_lean: str) -> Optional[str]:
    """Turn graffiti3's bare ``theorem NAME (G : SimpleGraph V) : … := sorry``
    into a self-contained, compilable file by injecting binders + preamble."""
    m = _SIG_RE.search(raw_lean)
    if not m:
        return None
    name = m.group(1)
    body = _SIG_RE.sub(f"theorem {name} {_HEADER_BINDERS}", raw_lean, count=1)
    return _PREAMBLE + "\n" + body


def export_supported(g3, natives, columns) -> List[Optional[str]]:
    """Lean theorem (self-contained) for each supported survivor, else None.

    Aligned 1:1 with ``natives``. Uses the g3 instance only as graffiti3's
    renderer; the lean_label must already map supported columns (see
    ``make_lean_label``)."""
    out: List[Optional[str]] = []
    for nc in natives:
        try:
            pretty = nc.pretty()
        except Exception:
            out.append(None)
            continue
        if "⇒" in pretty or "=>" in pretty:           # conditioned → class theorem
            # two shapes: (classes) ⇒ inequality, and (inequality) ⇒ classes
            out.append(render_conditioned(nc, columns)
                       or render_necessary(nc, columns))
            continue
        if not is_supported(nc, columns):
            out.append(None)
            continue
        try:
            raw = g3.conjectures_as_lean([nc], prefix="CEGIS")[0]
            out.append(_finish(raw))
        except Exception:
            out.append(None)
    return out
