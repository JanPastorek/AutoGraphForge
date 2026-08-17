"""Tests for the Lean disproof export (pipeline/lean_disproof.py).

The emitted shape is validated against the real kernel separately; these tests
pin the scoping rules and the structure of the generated file.
"""
import networkx as nx

from pipeline import lean_disproof as ld

COLS = ["nontrivial", "eulerian", "cubic", "cograph", "planar", "chordal",
        "claw_free", "tree", "connected",
        "zero_forcing_number", "total_zero_forcing_number",
        "connected_zero_forcing_number", "annihilation_number",
        "domination_number", "order", "harmonic_index"]

P3 = nx.to_graph6_bytes(nx.path_graph(3), header=False).strip().decode()
STMT = "(nontrivial) ⇒ total_zero_forcing_number ≤ zero_forcing_number"


def test_renders_a_disproof():
    src = ld.render(STMT, COLS, P3)
    assert src is not None
    # negated universal, instantiated at the witness, closed by decide
    assert "¬ (∀" in src
    assert "GraphCalc.ofEdges 3 [(0, 1), (1, 2)]" in src
    assert "@h (Fin 3) _ _ Gcex _ (by decide)" in src
    assert src.rstrip().endswith("decide")
    assert "import LeanProject.GraphInvariantsComputable" in src
    # provenance is recorded in the artifact itself
    assert P3 in src and STMT in src


def test_multiple_class_hypotheses_each_discharged():
    src = ld.render("((nontrivial) ∧ (eulerian)) ⇒ "
                    "total_zero_forcing_number ≤ zero_forcing_number", COLS, P3)
    assert src is not None
    # Two classes plus the definedness of `total_zero_forcing_number`: that
    # invariant's `minCard` has no witness when a vertex has no neighbour in any
    # forcing set, so the statement is only about graphs where it is defined.
    assert src.count("(by decide)") == 3
    assert "GraphCalc.IsNontrivialClass G → GraphCalc.IsEulerianClass G" in src
    assert "GraphCalc.HasTotalZeroForcingNumber G" in src


def test_skips_unsupported_invariant():
    # two-forcing has no Lean definition in either layer
    assert ld.render("(nontrivial) ⇒ two_forcing_number ≤ order",
                     COLS + ["two_forcing_number"], P3) is None


def test_skips_unsupported_class():
    # chordal has no decidable mirror; cograph and claw_free do
    assert ld.render("((nontrivial) ∧ (chordal)) ⇒ order ≤ order", COLS, P3) is None


def test_renders_newly_formalized_classes():
    for cls, pred in [("cograph", "GraphCalc.IsCographClass"),
                      ("claw_free", "GraphCalc.IsClawFreeClass"),
                      ("tree", "GraphCalc.IsTreeClass"),
                      ("connected", "GraphCalc.IsConnectedClass")]:
        src = ld.render(f"(({cls})) ⇒ total_zero_forcing_number ≤ "
                        f"zero_forcing_number", COLS, P3)
        assert src is not None, cls
        assert f"{pred} G" in src


def test_skips_without_witness():
    assert ld.render(STMT, COLS, None) is None


def test_skips_oversized_witness():
    big = nx.to_graph6_bytes(nx.path_graph(ld.MAX_WITNESS_ORDER + 1),
                             header=False).strip().decode()
    assert ld.render(STMT, COLS, big) is None


def test_skips_unconditioned_statement():
    assert ld.render("order ≤ order", COLS, P3) is None


def test_export_prefers_smallest_witnesses():
    big = nx.to_graph6_bytes(nx.path_graph(6), header=False).strip().decode()
    recs = [
        {"statement": STMT, "witness_graph6": big, "witness_order": 6, "witness_size": 5},
        {"statement": STMT, "witness_graph6": P3, "witness_order": 3, "witness_size": 2},
    ]
    out = ld.export_refutations(recs, COLS)
    assert len(out) == 2
    assert out[0][0]["witness_order"] == 3      # smallest first


def test_export_respects_limit():
    recs = [{"statement": STMT, "witness_graph6": P3,
             "witness_order": 3, "witness_size": 2} for _ in range(5)]
    assert len(ld.export_refutations(recs, COLS, limit=2)) == 2


def test_preamble_raises_recursion_depth():
    # the class tests are kernel *evaluation*: claw-freeness walks every
    # 3-subset of every neighbourhood, which overruns the default depth at the
    # witness-size limit, so the emitted file must raise it.
    src = ld.render(STMT, COLS, P3)
    assert "set_option maxRecDepth" in src


def test_planar_still_has_no_formalization():
    assert ld.render("((nontrivial) ∧ (planar)) ⇒ order ≤ order", COLS, P3) is None
