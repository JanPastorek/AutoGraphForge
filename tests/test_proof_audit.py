"""Tests for the proof soundness guards (pipeline/proof_audit.py).

A kernel check says a file compiles; these guards say it proves what we asked.
The attack cases below are the ones actually observed in the wild: redefining the
invariants, dropping the preamble, and proving a nearby-but-weaker statement.
"""
from pipeline import proof_audit as pa

STATEMENT = """import Mathlib
import LeanProject.GraphInvariants

open SimpleGraph

theorem delta_le_Delta {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
  : (G.minDegree : ℝ) ≤ (G.maxDegree : ℝ) :=
sorry
"""

GOOD = STATEMENT.replace("sorry", "by exact_mod_cast G.minDegree_le_maxDegree")


def test_accepts_a_faithful_proof():
    assert pa.static_audit(STATEMENT, GOOD) == (True, "ok")


def test_accepts_renamed_theorem_and_reflow():
    # theorem name and whitespace are cosmetic; the goal is what matters
    renamed = GOOD.replace("delta_le_Delta", "my_thm").replace("\n    (G :", " (G :")
    ok, why = pa.static_audit(STATEMENT, renamed)
    assert ok, why


def test_rejects_redefined_invariant():
    attack = GOOD.replace(
        "open SimpleGraph",
        "open SimpleGraph\nnamespace SimpleGraph\n"
        "def minDegree {V : Type*} [Fintype V] (_G : SimpleGraph V) : ℕ := 0\n"
        "end SimpleGraph")
    ok, why = pa.static_audit(STATEMENT, attack)
    assert not ok and "re-declares" in why


def test_rejects_missing_preamble_import():
    ok, why = pa.static_audit(
        STATEMENT, GOOD.replace("import LeanProject.GraphInvariants", ""))
    assert not ok and "preamble" in why


def test_rejects_different_statement():
    weaker = GOOD.replace("(G.minDegree : ℝ) ≤ (G.maxDegree : ℝ)",
                          "(G.minDegree : ℝ) ≤ (G.minDegree : ℝ)")
    ok, why = pa.static_audit(STATEMENT, weaker)
    assert not ok and "different statement" in why


def test_rejects_empty_candidate():
    assert pa.static_audit(STATEMENT, "")[0] is False


# ── axiom auditing ────────────────────────────────────────────────────────────

def test_axiom_probe_appends_one_line_per_theorem():
    code, names = pa.with_axiom_probe(GOOD)
    assert names == ["delta_le_Delta"]
    assert "#print axioms delta_le_Delta" in code


def test_standard_axioms_accepted():
    out = "'t' depends on axioms: [propext, Classical.choice, Quot.sound]"
    assert pa.audit_axiom_output(out, ["t"]) == (True, "ok")


def test_no_axioms_accepted():
    assert pa.audit_axiom_output("'t' does not depend on any axioms", ["t"])[0]


def test_sorry_axiom_rejected():
    out = "'t' depends on axioms: [propext, sorryAx, Classical.choice]"
    ok, why = pa.audit_axiom_output(out, ["t"])
    assert not ok and "sorryAx" in why


def test_missing_axiom_report_rejected():
    # no evidence is not the same as good evidence
    ok, why = pa.audit_axiom_output("", ["t"])
    assert not ok and "no axiom report" in why
