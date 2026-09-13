"""Tests for the Antigravity handoff (tools/antigravity_handoff.py).

The point of this path is that a result is only counted when the kernel accepts
it *and* the proposition is still the one we asked about. Every formalization
bug this repository has found produced an apparent success, so the cheap guards
— statement identity and direction-versus-label — are the ones worth pinning.
"""
import json

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.antigravity_handoff import _candidate_of

CHALLENGE = """import Mathlib
import LeanProject.GraphInvariantsComputable

open SimpleGraph

-- Conjecture under test: (nontrivial) => order <= size
abbrev Candidate : Prop :=
    ∀ {V : Type} [Fintype V] [DecidableEq V]
      (G : SimpleGraph V) [DecidableRel G.Adj],
      GraphCalc.IsNontrivialClass G → GraphCalc.order G ≤ GraphCalc.size G

theorem prove_ab12 : Candidate := by
  sorry

theorem refute_ab12 : ¬ Candidate := by
  sorry
"""


def test_candidate_is_extracted():
    c = _candidate_of(CHALLENGE)
    assert c is not None
    assert "IsNontrivialClass" in c and "order G ≤" in c


def test_whitespace_only_edits_are_not_treated_as_tampering():
    """A returned file will differ in formatting; that must not be rejected."""
    reflowed = CHALLENGE.replace("∀ {V : Type} [Fintype V] [DecidableEq V]\n      ",
                                 "∀ {V : Type} [Fintype V] [DecidableEq V] ")
    assert _candidate_of(reflowed) == _candidate_of(CHALLENGE)


def test_a_changed_statement_is_detected():
    """The failure this guard exists for: a file that compiles, but about a
    different proposition than the one the benchmark asked about."""
    weakened = CHALLENGE.replace("GraphCalc.order G ≤ GraphCalc.size G",
                                 "GraphCalc.order G ≤ GraphCalc.order G")
    assert _candidate_of(weakened) != _candidate_of(CHALLENGE)


def test_dropping_the_hypothesis_is_detected():
    """Removing `nontrivial` is exactly the gap that produced three bogus
    resolutions in the model campaign — every class predicate is vacuously true
    on `Fin 0` and every invariant is 0 there."""
    unguarded = CHALLENGE.replace(
        "GraphCalc.IsNontrivialClass G → ", "")
    assert _candidate_of(unguarded) != _candidate_of(CHALLENGE)


def test_export_writes_challenges_and_withholds_labels(tmp_path):
    import argparse

    from tools.antigravity_handoff import do_export
    bench = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "benchmark")
    if not os.path.exists(os.path.join(bench, "challenges_gold", "index.json")):
        import pytest
        pytest.skip("benchmark challenges not built in this checkout")
    args = argparse.Namespace(benchmark=bench, partition="gold",
                              out=str(tmp_path / "h"))
    assert do_export(args) == 0
    files = os.listdir(str(tmp_path / "h"))
    assert "README.md" in files and "solved" in files
    # ground truth is written for the verifier, not into the handed-over files
    gt = json.load(open(str(tmp_path / "h" / ".ground_truth.json")))
    assert gt and all("label" in v for v in gt.values())
    for f in files:
        if f.endswith(".lean"):
            assert "label" not in open(str(tmp_path / "h" / f)).read()


# -- compiling the returned file soundly ---------------------------------------
#
# The verifier compiles what the agents return, helper lemmas included, so the
# structural check is what stands between "compiles" and "proves the conjecture
# we asked about". Each case below is a concrete way to get the first without
# the second.

from tools.antigravity_handoff import solution_file, structural_check

PRISTINE_PROVE = "theorem prove_ab12 : Candidate := by\n  sorry"
SOLVED = CHALLENGE.replace(
    PRISTINE_PROVE,
    "lemma helper : True := trivial\n\n"
    "theorem prove_ab12 : Candidate := by\n  intro V _ _ G _ h\n  exact le_refl _")


def test_helper_lemmas_after_candidate_are_admissible():
    ok, why = structural_check(CHALLENGE, SOLVED)
    assert ok, why


def test_extending_candidates_last_line_is_rejected():
    bad = CHALLENGE.replace("GraphCalc.order G ≤ GraphCalc.size G",
                            "GraphCalc.order G ≤ GraphCalc.size G ∨ True")
    ok, why = structural_check(CHALLENGE, bad)
    assert not ok and "extended" in why


def test_continuing_candidate_on_the_next_line_is_rejected():
    """A Lean term does not end at a newline, so an indented `∨ True` below the
    original last line silently becomes part of `Candidate`."""
    bad = CHALLENGE.replace("GraphCalc.order G ≤ GraphCalc.size G\n",
                            "GraphCalc.order G ≤ GraphCalc.size G\n      ∨ True\n")
    ok, why = structural_check(CHALLENGE, bad)
    assert not ok and "continues" in why


def test_redeclaring_candidate_in_a_namespace_is_rejected():
    bad = CHALLENGE.replace(
        PRISTINE_PROVE,
        "lemma helper : True := trivial\n\nnamespace Evil\n"
        "abbrev Candidate : Prop := True\n"
        "theorem prove_ab12 : Candidate := trivial\nend Evil")
    ok, why = structural_check(CHALLENGE, bad)
    assert not ok and "namespace" in why


def test_variable_hypotheses_are_rejected():
    """A `variable (h : False)` is absorbed into the target's type while its
    header text still reads `: Candidate`."""
    bad = CHALLENGE.replace(PRISTINE_PROVE,
                            "lemma helper : True := trivial\n\nvariable (h : False)\n\n"
                            "theorem prove_ab12 : Candidate := h.elim")
    ok, why = structural_check(CHALLENGE, bad)
    assert not ok and "variable" in why


def test_kernel_bypasses_are_rejected():
    for construct in ("by native_decide",
                      "by\n  set_option debug.skipKernelTC true in exact sorry"):
        bad = CHALLENGE.replace(PRISTINE_PROVE,
                                f"theorem prove_ab12 : Candidate := {construct}")
        ok, _ = structural_check(CHALLENGE, bad)
        assert not ok, construct


def test_forbidden_words_inside_comments_are_ignored():
    commented = SOLVED.replace("lemma helper",
                               "-- no native_decide, no axiom, no namespace\nlemma helper")
    ok, why = structural_check(CHALLENGE, commented)
    assert ok, why


def test_solution_file_drops_the_other_direction_and_checks_the_type():
    sol = solution_file(SOLVED, "ab12", "prove")
    assert sol is not None
    assert "theorem refute_ab12" not in sol
    assert "agf_verify_prove : _root_.Candidate := _root_.prove_ab12" in sol
    assert "lemma helper" in sol


def test_an_unattempted_direction_is_not_checked():
    assert solution_file(CHALLENGE, "ab12", "prove") is None
    assert solution_file(SOLVED, "ab12", "refute") is None


# -- the code-execution screen -------------------------------------------------
#
# Agents may run only check.sh, but Lean elaboration can itself run shell
# commands. The screen is what makes that allow-list a real boundary, and the
# verifier depends on it too, since it compiles agent files outside the sandbox.

from tools.antigravity_handoff import lint_text

SCRATCH_HEAD = "import Mathlib\nimport LeanProject.GraphInvariantsComputable\n\n"


@pytest.mark.parametrize("payload", [
    '#eval IO.Process.run { cmd := "touch", args := #["/tmp/x"] }',
    'run_cmd Lean.logInfo "x"',
    "open Lean in\ndef f : Nat := 0",
    'def g : IO Unit := pure ()',
    'def h : BaseIO Unit := pure ()',
    "elab \"boom\" : command => pure ()",
    "@[init] def i : Unit := ()",
    "unsafe def u : Nat := 0",
    'macro "m" : term => `(0)',
])
def test_code_execution_routes_are_refused_in_scratch_files(payload):
    ok, why = lint_text(SCRATCH_HEAD + payload + "\n")
    assert not ok, payload


def test_only_whitelisted_imports_are_allowed():
    ok, why = lint_text("import Lean\n\ntheorem t : True := trivial\n")
    assert not ok and "import" in why


def test_an_ordinary_scratch_lemma_passes():
    ok, why = lint_text(SCRATCH_HEAD + "theorem t (n : ℕ) : n ≤ n + 1 := by omega\n")
    assert ok, why


def test_leanproject_import_is_not_mistaken_for_lean():
    """`\\bLean\\b` must not match `LeanProject`, or every file would be refused."""
    ok, why = lint_text(SCRATCH_HEAD + "theorem t : True := trivial\n")
    assert ok, why


def test_challenge_files_get_the_full_structural_check_through_lint():
    bad = CHALLENGE.replace(PRISTINE_PROVE,
                            'lemma helper : True := trivial\n\n#eval IO.println "x"')
    ok, why = lint_text(bad, original=CHALLENGE)
    assert not ok
