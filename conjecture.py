"""
conjecture.py — core data model for the graph-theory conjecture pipeline.

Classes
-------
ConjectureStatus  — lifecycle enum
Inequality        — linear inequality between two graph invariants
Counterexample    — a graph that refutes a conjecture
Conjecture        — the central object passed between pipeline stages
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

class ConjectureStatus(Enum):
    PROPOSED    = "proposed"      # freshly generated; not yet tested
    FALSIFIED   = "falsified"     # a counterexample was found
    SURVIVED    = "survived"      # passed all falsification attempts
    FORMALIZED  = "formalized"    # translated to Lean 4
    PROVEN      = "proven"        # machine-checkable proof exists
    PROOF_FAILED = "proof_failed" # prover gave up or timed out


# ---------------------------------------------------------------------------
# Inequality
# ---------------------------------------------------------------------------

@dataclass
class Inequality:
    """
    Represents:  coeff_a · inv_a(G)  ≤  coeff_b · inv_b(G)  +  offset

    Both inv_a and inv_b are keys from graphs.invariants.INVARIANTS.
    """

    inv_a: str
    inv_b: str
    coeff_a: float = 1.0
    coeff_b: float = 1.0
    offset: float = 0.0

    # ---------------------------------------------------------------- API --

    def evaluate(self, vals: Dict[str, float]) -> Optional[bool]:
        """Return True if the inequality holds, False if violated, None if data missing."""
        lhs, rhs = self._lhs_rhs(vals)
        if lhs is None:
            return None
        return lhs <= rhs

    def slack(self, vals: Dict[str, float]) -> Optional[float]:
        """rhs − lhs.  Negative → violated; zero → tight; positive → slack."""
        lhs, rhs = self._lhs_rhs(vals)
        if lhs is None:
            return None
        return rhs - lhs

    def is_tight(self, vals: Dict[str, float], tol: float = 1e-9) -> bool:
        s = self.slack(vals)
        return s is not None and abs(s) < tol

    # ----------------------------------------------------------- internals --

    def _lhs_rhs(self, vals):
        if self.inv_a not in vals or self.inv_b not in vals:
            return None, None
        lhs = self.coeff_a * vals[self.inv_a]
        rhs = self.coeff_b * vals[self.inv_b] + self.offset
        return lhs, rhs

    def __str__(self) -> str:
        def _fmt(coeff, name):
            if coeff == 1.0:
                return f"{name}(G)"
            return f"{coeff:g}·{name}(G)"

        lhs = _fmt(self.coeff_a, self.inv_a)
        rhs = _fmt(self.coeff_b, self.inv_b)
        if self.offset == 0.0:
            return f"{lhs} ≤ {rhs}"
        sign = "+" if self.offset > 0 else "-"
        return f"{lhs} ≤ {rhs} {sign} {abs(self.offset):g}"

    def to_dict(self) -> dict:
        return {
            "inv_a": self.inv_a,
            "inv_b": self.inv_b,
            "coeff_a": self.coeff_a,
            "coeff_b": self.coeff_b,
            "offset": self.offset,
            "latex": str(self),
        }


# ---------------------------------------------------------------------------
# Counterexample
# ---------------------------------------------------------------------------

@dataclass
class Counterexample:
    """A concrete graph that refutes a conjecture."""

    graph_name: str
    n_vertices: int
    n_edges: int
    invariant_values: Dict[str, float]
    violation_magnitude: float          # |slack| when slack < 0
    edge_list: List[tuple] = field(default_factory=list)  # for serialisation

    def to_dict(self) -> dict:
        return {
            "graph_name": self.graph_name,
            "n_vertices": self.n_vertices,
            "n_edges": self.n_edges,
            "invariant_values": {
                k: (v if v != float("inf") else "inf")
                for k, v in self.invariant_values.items()
            },
            "violation_magnitude": self.violation_magnitude,
            "edges": self.edge_list,
        }


# ---------------------------------------------------------------------------
# Conjecture
# ---------------------------------------------------------------------------

@dataclass
class Conjecture:
    """
    Central data object flowing through the pipeline.

    Lifecycle
    ---------
    PROPOSED → [falsifier] → FALSIFIED | SURVIVED
    SURVIVED → [formalizer] → FORMALIZED
    FORMALIZED → [prover] → PROVEN | PROOF_FAILED
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    # Human-readable statement (may be set by generator or derived from inequality)
    statement: str = ""

    # Structured representation (TxGraffiti conjectures only)
    inequality: Optional[Inequality] = None

    # Lean 4 artefacts
    lean_statement: Optional[str] = None
    lean_proof: Optional[str] = None

    # Lifecycle
    status: ConjectureStatus = field(default=ConjectureStatus.PROPOSED)
    counterexample: Optional[Counterexample] = None

    # Graphs where equality holds (witnesses to tightness)
    tightness_witnesses: List[str] = field(default_factory=list)

    # Provenance
    generation_method: str = "txgraffiti"   # "txgraffiti" | "funsearch"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Quality score (higher = more interesting / tight)
    score: float = 0.0

    # ---------------------------------------------------------------- API --

    def is_active(self) -> bool:
        return self.status not in (
            ConjectureStatus.FALSIFIED,
            ConjectureStatus.PROOF_FAILED,
        )

    def mark_falsified(self, cex: Counterexample) -> None:
        self.status = ConjectureStatus.FALSIFIED
        self.counterexample = cex

    def mark_survived(self) -> None:
        if self.status == ConjectureStatus.PROPOSED:
            self.status = ConjectureStatus.SURVIVED

    def mark_formalized(self, lean_stmt: str) -> None:
        self.lean_statement = lean_stmt
        self.status = ConjectureStatus.FORMALIZED

    def mark_proven(self, lean_proof: str) -> None:
        self.lean_proof = lean_proof
        self.status = ConjectureStatus.PROVEN

    def mark_proof_failed(self, reason: str = "") -> None:
        self.status = ConjectureStatus.PROOF_FAILED
        self.metadata["proof_failure_reason"] = reason

    # -------------------------------------------------------------- repr --

    def __str__(self) -> str:
        return (
            f"Conjecture[{self.id}]({self.generation_method}) "
            f"{self.statement!r} [{self.status.value}]"
        )

    def __repr__(self) -> str:
        return self.__str__()

    # -------------------------------------------------------- serialisation --

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "statement": self.statement,
            "status": self.status.value,
            "generation_method": self.generation_method,
            "score": self.score,
            "tightness_witnesses": self.tightness_witnesses,
            "lean_statement": self.lean_statement,
            "lean_proof": self.lean_proof,
            "metadata": self.metadata,
        }
        if self.inequality:
            d["inequality"] = self.inequality.to_dict()
        if self.counterexample:
            d["counterexample"] = self.counterexample.to_dict()
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
