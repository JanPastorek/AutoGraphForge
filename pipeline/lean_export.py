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
}

# Injected binders: a finite vertex type with decidable adjacency, enough for
# every invariant above to elaborate.
_HEADER_BINDERS = ("{V : Type*} [Fintype V] [DecidableEq V]\n"
                   "    (G : SimpleGraph V) [DecidableRel G.Adj]")

_PREAMBLE = "import Mathlib\nimport LeanProject.GraphInvariants\n\nopen SimpleGraph\n"

_SIG_RE = re.compile(r"theorem\s+(\w+)\s*\(G\s*:\s*SimpleGraph\s+V\)")


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
    """True iff every invariant the conjecture references is in ``SUPPORTED`` and
    the conjecture is unconditioned (no graph-class hypothesis we can't yet
    formalize). Non-inequality survivors (e.g. SophieCondition, no ``pretty``)
    are unsupported."""
    try:
        pretty = native.pretty()
    except Exception:
        return False                              # SophieCondition / non-inequality
    if "⇒" in pretty or "=>" in pretty:          # conditioned on a graph class
        return False
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
        if not is_supported(nc, columns):
            out.append(None)
            continue
        try:
            raw = g3.conjectures_as_lean([nc], prefix="CEGIS")[0]
            out.append(_finish(raw))
        except Exception:
            out.append(None)
    return out
