"""Tests for the curated known-relations parser (pipeline/known_relations.py)."""
from pipeline import known_relations as kr


def _one(text):
    out = kr.parse_relation(text)
    assert len(out) == 1, f"{text!r} -> {out}"
    return out[0]


def test_every_curated_string_parses():
    # The whole curated list must parse without exception; we keep it clean so
    # that nothing is silently dropped (any future junk fails loudly here).
    raw = kr.KNOWN_CONJECTURES + kr.KNOWN_INEQUALITIES
    parsed = [s for s in raw if kr.parse_relation(s)]
    assert len(parsed) == len(raw), "some curated relations failed to parse"


def test_load_dedups():
    rels = kr.load_relations()
    assert rels and len(rels) <= len(kr.KNOWN_CONJECTURES) + len(kr.KNOWN_INEQUALITIES)


def test_geq_normalized_to_leq():
    # a ≥ b  ⇒  b ≤ a
    lhs, rhs, off, cls, _ = _one("annihilation_number >= matching_number")
    assert lhs == "nu" and rhs == {"annihilation_number": 1.0} and off == 0.0


def test_scaled_lower_bound():
    # γ ≥ ½·roman  ⇒  roman ≤ 2γ
    lhs, rhs, off, cls, _ = _one("domination_number >= 1/2 * roman_domination_number")
    assert lhs == "roman_domination_number" and rhs == {"gamma": 2.0} and off == 0.0


def test_order_minus_invariant_rhs():
    # τ ≤ n − α
    lhs, rhs, off, cls, _ = _one("vertex_cover_number <= order - independence_number")
    assert lhs == "vertex_cover" and rhs == {"n": 1.0, "alpha": -1.0} and off == 0.0


def test_class_hypothesis_captured():
    lhs, rhs, off, cls, _ = _one(
        "If G is a connected and claw-free graph, then independent_domination_number <= domination_number")
    assert lhs == "ind_dom" and rhs == {"gamma": 1.0} and cls == "claw_free"


def test_unsupported_hypothesis_skipped():
    # "not K_n" / degree-bounded hypotheses are not modellable -> dropped (novel)
    assert kr.parse_relation(
        "If G is a connected graph which is not K_n, then zero_forcing_number <= order - 2") == []


def test_negated_paren_group_rejected():
    # paren-stripping would mis-sign this, so it must be skipped, not mis-encoded
    assert kr.parse_relation(
        "independence_number <= order - (order - annihilation_number)") == []


def test_equality_emits_both_directions():
    out = kr.parse_relation(
        "If G is a connected and claw-free graph, then zero_forcing_number = positive_semidefinite_zero_forcing_number")
    assert len(out) == 2
    lhss = {t[0] for t in out}
    assert lhss == {"zero_forcing_number", "positive_semidefinite_zero_forcing_number"}
