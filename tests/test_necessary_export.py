"""Tests for the necessary-condition exporters.

Shape: ``(inequality) ⇒ class-conclusion`` — an inequality among the invariants
forcing the graph into or out of a class. Both directions are covered: the
theorem (pipeline/lean_export.render_necessary) and its disproof at a witness
(pipeline/lean_disproof). The generated Lean is kernel-checked separately by
tools/export_disproofs.py --verify; here we pin scope and shape.
"""
import networkx as nx
import pytest

from pipeline import lean_disproof as ld
from pipeline import lean_export as le

COLS = ["order", "size", "independence_number", "domination_number", "slater",
        "clique_number", "maximum_degree", "minimum_degree",
        "zero_forcing_number", "radius",
        "tree", "cubic", "subcubic", "K_4_free", "connected", "cograph",
        "claw_free", "planar", "chordal", "nontrivial"]

P4 = nx.to_graph6_bytes(nx.path_graph(4), header=False).strip().decode()


class FakeNative:
    def __init__(self, pretty):
        self._pretty = pretty

    def pretty(self):
        return self._pretty


# -- the theorem --------------------------------------------------------------

def test_renders_negated_conclusion():
    src = le.render_necessary(FakeNative("((2 · independence_number) < order) ⇒ ¬tree"),
                              COLS)
    assert src is not None
    assert "(_h0 : 2 * G.indepNum < G.order)" in src
    assert ": ¬ G.IsTreeClass :=" in src
    assert src.rstrip().endswith("sorry")


def test_renders_conjunctive_conclusion():
    src = le.render_necessary(
        FakeNative("(order ≤ ((3 · slater) + -2)) ⇒ subcubic & K_4_free"), COLS)
    assert src is not None
    # denominators cleared, negative constant moved across
    assert "(_h0 : G.order + 2 ≤ 3 * G.slaterNumber)" in src
    assert ": G.IsSubcubicClass ∧ G.IsK4FreeClass :=" in src


def test_renders_rational_coefficients():
    src = le.render_necessary(FakeNative(
        "(domination_number ≤ (((4/7) · independence_number) + (-5/7))) ⇒ ¬cubic"),
        COLS)
    assert "(_h0 : 7 * G.dominationNumber + 5 ≤ 4 * G.indepNum)" in src


@pytest.mark.parametrize("statement,why", [
    ("((2 · independence_number) < order) ⇒ ¬planar", "class not formalized"),
    ("((2 · independence_number) < order) ⇒ ¬chordal", "class not formalized"),
    ("(radius < order) ⇒ ¬tree", "invariant not formalized"),
    ("((2 · independence_number) < order) ⇒ order ≤ size", "conclusion not a class"),
    ("((tree) ∧ (cubic)) ⇒ order ≤ size", "class-conditioned shape"),
    ("order ≤ size", "not an implication"),
])
def test_refuses_out_of_scope(statement, why):
    assert le.render_necessary(FakeNative(statement), COLS) is None, why


def test_is_supported_accepts_the_new_shape():
    assert le.is_supported(
        FakeNative("((2 · independence_number) < order) ⇒ ¬tree"), COLS)


def test_class_conditioned_shape_still_routes_to_its_own_renderer():
    nat = FakeNative("((tree)) ⇒ domination_number ≤ order")
    assert le.render_conditioned(nat, COLS) is not None
    assert le.render_necessary(nat, COLS) is None


# -- the disproof -------------------------------------------------------------

def test_disproof_keeps_hypothesis_inside_the_implication():
    src = ld.render("((2 · independence_number) < order) ⇒ ¬tree", COLS, P4)
    assert src is not None
    assert ("2 * GraphCalc.indepNum G < GraphCalc.order G → "
            "¬ GraphCalc.IsTreeClass G") in src
    # no class hypothesis to discharge, so no trailing `(by decide)` arguments
    assert "have := @h (Fin 4) _ _ Gcex _\n" in src
    assert "(by decide)" not in src
    assert src.rstrip().endswith("decide")


def test_disproof_renders_conjunctive_conclusion():
    src = ld.render("(order ≤ ((3 · slater) + -2)) ⇒ subcubic & K_4_free", COLS, P4)
    assert ("GraphCalc.IsSubcubicClass G ∧ GraphCalc.IsK4FreeClass G") in src


def test_every_statable_invariant_is_also_refutable():
    """The two exporters must cover the same invariants.

    An invariant present in the specification layer but missing from the
    computable one yields conjectures that can be *stated* as theorems and
    never refuted, so a counterexample the pipeline already holds cannot be
    turned into a disproof. `connected_zero_forcing_number` was exactly that
    case until a computable mirror was added, and the gap is silent — the
    exporter simply returns None — so it is worth asserting rather than
    rediscovering.
    """
    assert set(le.SUPPORTED) == set(ld.SUPPORTED)
    # Classes too. `bipartite` was statable via the spec-layer `G.Colorable 2`
    # but had no decidable mirror, so a conjecture conditioned on it could be
    # exported as a theorem and never refuted on a witness — the same silent
    # gap, one level up. Comparing only SUPPORTED missed it.
    assert set(le.CLASS_PREDICATES) == set(ld.CLASS_PREDICATES)


def test_disproof_respects_witness_size_limit():
    big = nx.to_graph6_bytes(nx.path_graph(ld.MAX_WITNESS_ORDER + 1),
                             header=False).strip().decode()
    assert ld.render("((2 · independence_number) < order) ⇒ ¬tree", COLS, big) is None


def test_necessary_condition_export_carries_the_nontrivial_guard():
    """Both directions must scope the statement to non-trivial graphs.

    graffiti3 generates every conjecture under a `nontrivial` (order >= 2) base
    hypothesis. The class-conditioned shape carries it because it appears in the
    printed statement; this shape's hypothesis is an inequality, so the guard has
    to be reinserted explicitly. Without it the exported statement quantifies
    over `Fin 0`, where every `forall v` class predicate is vacuously true and
    every invariant is 0 — making it refutable by the empty graph with no
    mathematical content. That is not a hypothetical: it produced three
    "resolutions" that were formalization gaps, not proofs.
    """
    stmt = "((2 · independence_number) < order) ⇒ ¬tree"
    thm = le.render_necessary(FakeNative(stmt), COLS)
    assert "IsNontrivialClass" in thm, "theorem lost the nontrivial guard"
    dis = ld.render(stmt, COLS, P4)
    assert "GraphCalc.IsNontrivialClass G →" in dis, "disproof lost the guard"


def test_partial_invariants_carry_a_definedness_hypothesis():
    """`minCard` returns 0 when nothing satisfies its predicate.

    `univ` is always a dominating set and always a vertex cover, so the fallback
    is invisible there. It is not for connected zero forcing: on a disconnected
    graph no subset induces a connected subgraph, so the invariant reads 0 while
    graphcalc reports no value at all. `Z_c + 2 <= 2 * Z_t` then degenerates to
    `2 <= 0` and is refutable with no mathematical content — which is exactly
    what a model found. The conjecture never claimed anything about those
    graphs, so both exports must say so.
    """
    cols = COLS + ["connected_zero_forcing_number", "total_zero_forcing_number"]
    stmt = ("((nontrivial) ∧ (subcubic)) ⇒ "
            "connected_zero_forcing_number ≤ total_zero_forcing_number")
    thm = le.render_conditioned(FakeNative(stmt), cols)
    assert "HasConnectedZeroForcingNumber" in thm
    assert "HasTotalZeroForcingNumber" in thm
    dis = ld.render(stmt, cols, P4)
    assert "GraphCalc.HasConnectedZeroForcingNumber G" in dis
    assert "GraphCalc.HasTotalZeroForcingNumber G" in dis
