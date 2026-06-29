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
conjectures conditioned on graph-class predicates (chordal, claw_free, …).
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

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
}

# Injected binders: a finite vertex type with decidable adjacency, enough for
# every invariant above to elaborate.
_HEADER_BINDERS = ("{V : Type*} [Fintype V] [DecidableEq V]\n"
                   "    (G : SimpleGraph V) [DecidableRel G.Adj]")

_PREAMBLE = "import Mathlib\nimport LeanProject.GraphInvariants\n\nopen SimpleGraph\n"

_SIG_RE = re.compile(r"theorem\s+(\w+)\s*\(G\s*:\s*SimpleGraph\s+V\)")

# graph-class column → preamble predicate (the tractable classes; cograph /
# chordal / claw_free / planar are not formalized, so conjectures conditioned on
# them stay unexportable).
CLASS_PREDICATES = {
    "regular": "IsRegularClass", "cubic": "IsCubicClass",
    "subcubic": "IsSubcubicClass", "triangle_free": "IsTriangleFreeClass",
    "K_4_free": "IsK4FreeClass", "bipartite": "IsBipartiteClass",
    "eulerian": "IsEulerianClass",
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
        return None                                    # unsupported class (cograph, …)
    rel = next((r for r in _REL_LEAN if r in body), None)
    if rel is None:
        return None
    lhs, rhs = body.split(rel, 1)
    li, ri = _bare_invariant(lhs, columns), _bare_invariant(rhs, columns)
    if not li or not ri:
        return None
    hyps = " ".join(f"(_h{i} : G.{CLASS_PREDICATES[c]})" for i, c in enumerate(classes))
    body_lean = f"({SUPPORTED[li]} : ℝ) {_REL_LEAN[rel]} ({SUPPORTED[ri]} : ℝ)"
    thm = (f"theorem CEGIS_1 {_HEADER_BINDERS}\n    {hyps}\n  : {body_lean} :=\nsorry")
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
        return render_conditioned(native, columns) is not None
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
            out.append(render_conditioned(nc, columns))
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
