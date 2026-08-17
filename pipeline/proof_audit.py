"""
pipeline/proof_audit.py — soundness guards for candidate Lean proofs.

A kernel check answers "does this file compile?", never "does it prove the
statement we asked about?". A model can satisfy the first while dodging the
second, and the two failure modes are cheap to reach by accident:

  * **statement substitution** — the candidate re-declares the invariants it is
    supposed to reason about (``def zeroForcingNumber ... := 0``) or restates a
    weaker goal, then proves *that*. The file compiles; the theorem is worthless.
    This is not hypothetical: a concurrent benchmark (GRAFFITI3LOOP, 2026)
    reports exactly this behaviour from an agentic prover, which "does not import
    the benchmark Lean library; rather, it redeclares certain benchmark
    invariants".
  * **axiom smuggling** — a proof that goes through ``sorryAx`` or a bespoke
    ``axiom`` declaration. Grepping the source for the token ``sorry`` does not
    catch a ``sorryAx`` reached through a lemma, nor a user-declared axiom.

Both are closed here, cheaply and independently of the model:

  ``static_audit``  rejects a candidate that redefines a protected invariant or
                    class predicate, drops the preamble import, or proves a
                    signature other than the one we asked about.
  ``with_axiom_probe`` / ``audit_axiom_output``
                    append ``#print axioms`` for every theorem in the file and
                    require the reported axioms to lie inside the standard
                    ``{propext, Classical.choice, Quot.sound}``.

Both are conservative: anything unparseable is reported as a failure with a
reason, never silently accepted.
"""
from __future__ import annotations

import re
from typing import List, Optional, Set, Tuple

# The three axioms every ordinary mathlib proof is allowed to depend on. Anything
# else (notably `sorryAx`, or a candidate-declared `axiom`) invalidates the proof.
ALLOWED_AXIOMS: Set[str] = {"propext", "Classical.choice", "Quot.sound"}

_DECL_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|partial\s+|unsafe\s+)*"
    r"(def|abbrev|instance|axiom|opaque|structure|inductive)\s+([A-Za-z_][\w'.]*)",
    re.M)

_THEOREM_RE = re.compile(
    r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+)?"
    r"(?:theorem|lemma)\s+([A-Za-z_][\w'.]*)", re.M)

# Hypothesis binder names are cosmetic: `(_h0 : P)` and `(h0 : P)` denote the same
# statement, and models rename them freely. Normalise them away before comparing.
_BINDER_NAME_RE = re.compile(r"\(\s*_?h\d*\s*:")


def protected_names() -> Set[str]:
    """Invariant / class-predicate names a candidate must not re-declare.

    Sourced from the export tables so the guard cannot drift away from what we
    actually put in the goals.
    """
    names: Set[str] = set()
    try:
        from pipeline import lean_export as le
        for expr in le.SUPPORTED.values():          # "G.zeroForcingNumber"
            names.add(expr.split(".")[-1])
        names.update(le.CLASS_PREDICATES.values())  # "IsRegularClass"
    except Exception:                               # pragma: no cover - defensive
        pass
    return names


def declared_names(code: str) -> List[str]:
    """Every value-level name the candidate declares (`def`, `instance`, …)."""
    return [m.group(2) for m in _DECL_RE.finditer(code)]


def theorem_names(code: str) -> List[str]:
    return _THEOREM_RE.findall(code)


def redefined_protected(code: str) -> List[str]:
    """Protected invariant names the candidate re-declares (should be empty)."""
    protected = protected_names()
    hits = []
    for name in declared_names(code):
        if name.split(".")[-1] in protected:
            hits.append(name)
    return hits


def _top_level_assign(text: str) -> int:
    """Index of the first ``:=`` outside any bracket, else -1."""
    depth = 0
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == ":" and depth == 0 and text.startswith(":=", i):
            return i
        i += 1
    return -1


def _normalise(sig: str) -> str:
    sig = _BINDER_NAME_RE.sub("(_h :", sig)
    return re.sub(r"\s+", " ", sig).strip()


def signatures(code: str) -> List[str]:
    """Normalised ``binders : goal`` signature of every theorem in ``code``."""
    out: List[str] = []
    for m in _THEOREM_RE.finditer(code):
        rest = code[m.end():]
        cut = _top_level_assign(rest)
        if cut < 0:
            continue
        out.append(_normalise(rest[:cut]))
    return out


def statement_signature(statement: str) -> Optional[str]:
    """The single signature of an exported ``… := sorry`` skeleton."""
    sigs = signatures(statement)
    return sigs[0] if sigs else None


def static_audit(statement: str, candidate: str,
                 require_preamble: bool = True) -> Tuple[bool, str]:
    """(ok, reason) — does ``candidate`` prove *our* ``statement``, honestly?

    Checks, in order: no re-declaration of a protected invariant; the preamble is
    imported (so the invariants mean what we defined them to mean); and some
    theorem in the candidate carries exactly the goal we asked about.
    """
    if not candidate or not candidate.strip():
        return False, "empty candidate"

    redefined = redefined_protected(candidate)
    if redefined:
        return False, ("candidate re-declares protected invariant(s): "
                       + ", ".join(sorted(set(redefined))))

    if require_preamble and "LeanProject.GraphInvariants" not in candidate:
        return False, "candidate does not import the GraphInvariants preamble"

    want = statement_signature(statement)
    if want is None:
        return False, "could not parse a signature from the requested statement"
    got = signatures(candidate)
    if not got:
        return False, "no theorem signature found in candidate"
    if want not in got:
        return False, ("candidate proves a different statement than requested "
                       f"(wanted: {want[:160]})")
    return True, "ok"


# ── axiom auditing ─────────────────────────────────────────────────────────────

_AXIOM_LINE_RE = re.compile(r"'([\w'.]+)' depends on axioms: \[([^\]]*)\]")
_NO_AXIOM_RE = re.compile(r"'([\w'.]+)' does not depend on any axioms")


def with_axiom_probe(code: str) -> Tuple[str, List[str]]:
    """``code`` + a ``#print axioms`` line per theorem, and the probed names."""
    names = theorem_names(code)
    if not names:
        return code, []
    probes = "\n".join(f"#print axioms {n}" for n in names)
    return code.rstrip() + "\n\n" + probes + "\n", names


def audit_axiom_output(output: str, names: List[str]) -> Tuple[bool, str]:
    """(ok, reason) — every probed theorem depends only on ``ALLOWED_AXIOMS``.

    A probed theorem with no axiom report at all is a failure: it means the probe
    did not run, so we have no evidence and must not assume the good case.
    """
    if not names:
        return True, "ok (no theorem to probe)"
    reported = {m.group(1) for m in _NO_AXIOM_RE.finditer(output)}
    for m in _AXIOM_LINE_RE.finditer(output):
        name = m.group(1)
        reported.add(name)
        used = {a.strip() for a in m.group(2).split(",") if a.strip()}
        bad = used - ALLOWED_AXIOMS
        if bad:
            return False, f"{name} depends on disallowed axiom(s): {', '.join(sorted(bad))}"
    missing = [n for n in names if n not in reported]
    if missing:
        return False, "no axiom report for: " + ", ".join(missing)
    return True, "ok"
