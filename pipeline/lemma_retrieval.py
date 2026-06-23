"""
pipeline/lemma_retrieval.py — per-goal lemma grounding for the prover.

Instead of a hand-maintained cheatsheet, build the prover prompt's "available
lemmas" section dynamically: extract the invariant symbols in the goal, grep the
pinned mathlib `SimpleGraph` source for `theorem`/`lemma` declarations that
mention them, and return the top-k signatures ranked by how many of the goal's
symbols they touch. This scales to any invariant in the preamble without editing
Python.

Pure stdlib + ripgrep/grep; degrades to an empty list if mathlib isn't found.
"""
from __future__ import annotations

import os
import re
import subprocess
from functools import lru_cache
from typing import Dict, List, Tuple

# Preamble-defined invariants → a one-line reminder (these are NOT in mathlib).
_PREAMBLE_DEFS: Dict[str, str] = {
    "order": "G.order = Fintype.card V",
    "size": "G.size = G.edgeFinset.card",
    "dominationNumber": "G.dominationNumber = sInf {n | ∃ s, #s = n ∧ G.IsDominatingSet s}",
    "independentDominationNumber":
        "G.independentDominationNumber = sInf {n | ∃ s, #s = n ∧ G.IsDominatingSet s ∧ G.IsIndependentFinset s}",
}

# Lean invariant symbols we care about (preamble + mathlib), used to tokenise goals.
_KNOWN_SYMBOLS = [
    "cliqueNum", "indepNum", "minDegree", "maxDegree", "chromaticNumber",
    "order", "size", "dominationNumber", "independentDominationNumber",
    "edgeFinset", "degree",
]

_DECL_RE = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:protected\s+|private\s+|noncomputable\s+)?"
                      r"(theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*(.*)$")


def _mathlib_graph_dir(lean_root: str) -> str:
    return os.path.join(lean_root, ".lake", "packages", "mathlib",
                        "Mathlib", "Combinatorics", "SimpleGraph")


def goal_symbols(lean_statement: str) -> List[str]:
    toks = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", lean_statement or ""))
    return [s for s in _KNOWN_SYMBOLS if s in toks]


@lru_cache(maxsize=256)
def _grep_decls(symbol: str, graph_dir: str, cap: int = 60) -> Tuple[Tuple[str, str], ...]:
    """(name, signature-line) for theorem/lemma declarations mentioning `symbol`."""
    if not os.path.isdir(graph_dir):
        return ()
    tool = "rg" if _has(("rg", "--version")) else "grep"
    if tool == "rg":
        cmd = ["rg", "-No", "--no-heading", r"^\s*(theorem|lemma)\b.*" + re.escape(symbol),
               graph_dir]
    else:
        cmd = ["grep", "-rEoh", r"^[[:space:]]*(theorem|lemma)[[:space:]].*" + re.escape(symbol),
               graph_dir]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return ()
    decls: List[Tuple[str, str]] = []
    seen = set()
    for line in out.splitlines():
        m = _DECL_RE.match(line)
        if not m:
            continue
        name = m.group(2)
        if name in seen:
            continue
        seen.add(name)
        sig = (name + " " + m.group(3)).strip()
        decls.append((name, sig[:160]))
        if len(decls) >= cap:
            break
    return tuple(decls)


def _has(cmd) -> bool:
    try:
        subprocess.run(list(cmd), capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def retrieve_lemmas(lean_statement: str, lean_root: str, k: int = 12) -> List[str]:
    """Top-k mathlib lemma signatures relevant to the goal's invariant symbols."""
    syms = goal_symbols(lean_statement)
    if not syms:
        return []
    graph_dir = _mathlib_graph_dir(lean_root)
    # score each declaration by how many goal symbols it mentions
    scored: Dict[str, Tuple[int, str]] = {}
    for s in syms:
        for name, sig in _grep_decls(s, graph_dir):
            hits = sum(1 for t in syms if t in sig)
            prev = scored.get(name)
            if prev is None or hits > prev[0]:
                scored[name] = (hits, sig)
    ranked = sorted(scored.values(), key=lambda x: (-x[0], len(x[1])))
    return [sig for _, sig in ranked[:k]]


def cheatsheet_for(lean_statement: str, lean_root: str, k: int = 12) -> str:
    """A grounding block for the prover prompt: preamble reminders + retrieved
    mathlib lemma signatures relevant to this specific goal."""
    syms = goal_symbols(lean_statement)
    lines: List[str] = []
    for s in syms:
        if s in _PREAMBLE_DEFS:
            lines.append(f"  • (preamble) {_PREAMBLE_DEFS[s]}")
    for sig in retrieve_lemmas(lean_statement, lean_root, k=k):
        lines.append(f"  • SimpleGraph.{sig}")
    if not lines:
        return ""
    return ("Relevant verified declarations (use these EXACT names; do not invent "
            "names or use `exact?`/`sorry`):\n" + "\n".join(lines) + "\n\n")
