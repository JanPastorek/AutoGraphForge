"""Tests for keeping the counterexample searchers inside the hypothesis class.

A class-conditioned conjecture says nothing about graphs outside its class, so
``GraphSearchProblem.violation`` scores those -inf. Measured over the refutation
pool the median survivor's hypothesis holds on 0.07% of graphs, which made that
-inf the entire landscape: the searchers had no gradient and cross-entropy's
independent-Bernoulli sampler essentially never drew a member of the class.

These tests pin the two properties that fix costs nothing to keep: a walk that
starts in the class stays in it, and the constraint is derived from the
conjecture rather than passed in (it never was passed in — both call sites left
it None, which is what made the class-aware machinery unreachable).
"""
import networkx as nx
import numpy as np
import pytest

from pipeline.search.class_moves import (PREDICATES, ClassConstraint,
                                         hypothesis_classes)
from pipeline.search.problem import GraphSearchProblem

COLS = ["order", "size", "independence_number", "domination_number",
        "zero_forcing_number", "bipartite", "cubic", "tree", "connected",
        "triangle_free", "chordal", "cograph", "claw_free", "regular",
        "subcubic", "K_4_free", "eulerian", "planar", "nontrivial"]


class FakeNative:
    def __init__(self, pretty):
        self._pretty = pretty

    def pretty(self):
        return self._pretty


# -- reading the class off the conjecture -------------------------------------

def test_classes_read_from_the_hypothesis():
    nat = FakeNative("((nontrivial) ∧ (bipartite)) ⇒ domination_number ≤ order")
    assert set(hypothesis_classes(nat, COLS)) == {"nontrivial", "bipartite"}


def test_necessary_condition_shape_is_not_constrained():
    """``(inequality) ⇒ ¬tree`` *does* speak about graphs outside `tree`.

    Constraining the search to the conclusion's class would make the searcher
    unable to find the counterexamples this shape is refuted by, so the
    hypothesis side is the only thing that may restrict the walk.
    """
    nat = FakeNative("((2 · independence_number) < order) ⇒ ¬tree")
    assert hypothesis_classes(nat, COLS) == ()


def test_unconditioned_statement_is_not_constrained():
    assert hypothesis_classes(FakeNative("order ≤ size"), COLS) == ()


def test_problem_derives_the_constraint_without_being_told():
    nat = FakeNative("((nontrivial) ∧ (cubic)) ⇒ order ≤ size")
    prob = GraphSearchProblem(nat, COLS)
    assert "cubic" in prob.constraint.active


def test_constraint_can_be_switched_off_for_reproducibility():
    nat = FakeNative("((nontrivial) ∧ (cubic)) ⇒ order ≤ size")
    prob = GraphSearchProblem(nat, COLS, constrain_to_class=False)
    assert not prob.constraint


# -- the walk stays in the class ----------------------------------------------

@pytest.mark.parametrize("classes", [
    ("bipartite",), ("tree",), ("cubic",), ("regular",), ("triangle_free",),
    ("chordal",), ("cograph",), ("claw_free",), ("eulerian",), ("subcubic",),
    ("K_4_free",), ("planar",), ("connected",),
    ("bipartite", "connected"), ("cubic", "triangle_free"), ("tree", "subcubic"),
])
def test_walk_stays_in_class(classes):
    c = ClassConstraint(list(classes) + ["nontrivial"])
    rng = np.random.default_rng(0)
    G = c.start(10, rng)
    assert G is not None, f"no start found for {classes}"
    assert c.satisfies(G)
    for _ in range(150):
        G = c.neighbor(G, rng, k=1)
        assert c.satisfies(G), f"{classes} left the class"


def test_empty_class_reports_no_start_rather_than_a_wrong_one():
    """``chordal ∧ cubic`` holds on exactly one graph in the 293,756-graph pool.

    Returning None lets the caller fall back; returning an out-of-class graph
    would hand the searcher something that scores -inf while looking like a
    valid start.
    """
    c = ClassConstraint(["chordal", "cubic", "nontrivial"])
    assert c.start(10, np.random.default_rng(0)) is None


def test_unconstrained_move_is_the_plain_flip():
    c = ClassConstraint(["nontrivial"])          # trivial → no restriction
    assert not c
    G = nx.path_graph(6)
    H = c.neighbor(G, np.random.default_rng(0), k=1)
    assert abs(H.number_of_edges() - G.number_of_edges()) == 1


# -- the edge-set restriction --------------------------------------------------

def test_bipartite_pairs_are_exactly_the_cross_pairs():
    pairs = ClassConstraint(["bipartite"]).allowed_pairs(6)
    A, B = [0, 1, 2], [3, 4, 5]
    assert set(pairs) == {(u, v) for u in A for v in B}


def test_any_subset_of_the_allowed_pairs_is_in_class():
    """What makes a static mask sound: *every* subset must stay in the class."""
    c = ClassConstraint(["bipartite"])
    pairs = c.allowed_pairs(8)
    rng = np.random.default_rng(0)
    for _ in range(50):
        G = nx.Graph()
        G.add_nodes_from(range(8))
        G.add_edges_from(p for p in pairs if rng.random() < 0.5)
        assert c.satisfies(G)


@pytest.mark.parametrize("classes", [
    ("cubic",),                 # degree-defined
    ("chordal",),               # forbidden induced subgraph
    ("bipartite", "connected"),  # connectivity is a joint condition
    ("bipartite", "subcubic"),   # degree bound is not a pair restriction
])
def test_no_static_pair_set_where_one_would_be_unsound(classes):
    assert ClassConstraint(list(classes)).allowed_pairs(8) is None


def test_predicates_cover_every_class_the_exporters_formalize():
    """The move set and the Lean exporters must agree on the class vocabulary.

    A class the exporters can state but the searcher cannot recognise is a
    conjecture whose search silently runs unconstrained — the failure this whole
    module exists to remove, reintroduced one class at a time.
    """
    from pipeline import lean_export as le
    assert set(le.CLASS_PREDICATES) <= set(PREDICATES)


# -- the defect functions ------------------------------------------------------

@pytest.mark.parametrize("seed", range(12))
def test_defect_is_zero_exactly_when_the_class_holds(seed):
    """The descent in `start` steers by the defect; the walk is gated by the
    predicate. If they disagreed the search would climb toward graphs the
    constraint then rejects."""
    from pipeline.search.class_moves import DEFECTS
    rng = np.random.default_rng(seed)
    G = nx.gnp_random_graph(7, float(rng.uniform(0.1, 0.9)),
                            seed=int(rng.integers(1 << 30)))
    for c, pred in PREDICATES.items():
        assert (DEFECTS[c](G) == 0) is pred(G), c


def test_p4_and_claw_counts_match_brute_force():
    """Both are counted through a local structure rather than over 4-subsets;
    the speedup is what makes the descent affordable, so the count has to be
    the same one."""
    import itertools

    from pipeline.search.class_moves import _count_claws, _count_p4
    rng = np.random.default_rng(3)
    for _ in range(20):
        G = nx.gnp_random_graph(7, float(rng.uniform(0.15, 0.8)),
                                seed=int(rng.integers(1 << 30)))
        p4 = claws = 0
        for quad in itertools.combinations(G, 4):
            H = G.subgraph(quad)
            if H.number_of_edges() != 3:
                continue
            deg = sorted(d for _, d in H.degree())
            if deg == [1, 1, 2, 2] and nx.is_connected(H):
                p4 += 1
            elif deg == [1, 1, 1, 3]:
                claws += 1
        assert _count_p4(G) == p4
        assert _count_claws(G) == claws


# -- thin conjunctions ---------------------------------------------------------

def test_thin_conjunction_still_gets_a_start():
    """`tree & cograph` is the most common hypothesis among the survivors and it
    collapses to the star. Neither generator produces it and the descent stalls
    at a local minimum of the induced-P4 count, so the start comes from the tier
    caches, which already record which graphs are in the class."""
    c = ClassConstraint(["tree", "cograph", "nontrivial"])
    G = c.start(8, np.random.default_rng(0))
    assert G is not None and c.satisfies(G)


# -- the RL environment --------------------------------------------------------

def test_rl_action_mask_is_exactly_the_cross_pairs():
    """rlgt's agents set masked logits to -inf, so a mask over the cross pairs
    means the agent cannot construct a non-bipartite graph at all — the class
    boundary is one the RL search never has to cross."""
    pytest.importorskip("rlgt")
    pytest.importorskip("torch")
    from rlgt.environments.global_environments import GlobalFlipEnvironment

    from pipeline.search.rlgt_adapter import (_initial_graph_generator,
                                              _masked_environment,
                                              _rlgt_graph_to_nx)

    nat = FakeNative("((nontrivial) ∧ (bipartite)) ⇒ order ≤ size")
    prob = GraphSearchProblem(nat, COLS)
    n = 8
    gen = _initial_graph_generator(prob, n, np.random.default_rng(0))
    env = _masked_environment(GlobalFlipEnvironment, prob, n)(
        graph_invariant=lambda g: np.zeros(1), graph_order=n,
        initial_graph_generator=gen)

    half = n * (n - 1) // 2
    index, k = {}, 0
    for i in range(n):
        for j in range(i + 1, n):
            index[(i, j)] = k
            k += 1
    A, B = prob.constraint.canonical_parts(n)
    cross = {index[(u, v)] for u in A for v in B}
    mask = env.action_mask
    assert mask is not None and len(mask) == env.action_number
    assert {p for p in range(half) if mask[p]} == cross
    # `flip_only` is False, so actions run over 2 * half and the mask must be
    # tiled: the second half decides whether to apply the flip at that position.
    assert list(mask[:half]) == list(mask[half:])
    for G in _rlgt_graph_to_nx(gen(4)):
        assert nx.is_bipartite(G)


def test_rl_environment_is_unmasked_when_no_static_restriction_exists():
    pytest.importorskip("rlgt")
    from rlgt.environments.global_environments import GlobalFlipEnvironment

    from pipeline.search.rlgt_adapter import _masked_environment

    nat = FakeNative("((nontrivial) ∧ (cubic)) ⇒ order ≤ size")
    prob = GraphSearchProblem(nat, COLS + ["cubic"])
    env = _masked_environment(GlobalFlipEnvironment, prob, 8)(
        graph_invariant=lambda g: np.zeros(1), graph_order=8)
    assert env.action_mask is None


# -- the generation cache guard ------------------------------------------------

def test_gen_cache_without_a_stamp_is_refused(tmp_path):
    """A dilled closure carries its ``__code__``, which is not portable across
    Python minor versions: the load succeeds and the interpreter segfaults when
    the restored function is first called. A segfault is not an exception, so
    the try/except around the load cannot save the run — the mismatch has to be
    caught before the load."""
    from pipeline.cegis import _gen_cache_is_loadable, _stamp_gen_cache

    p = tmp_path / "gen_abc.dill"
    p.write_bytes(b"x")
    assert not _gen_cache_is_loadable(str(p))
    _stamp_gen_cache(str(p))
    assert _gen_cache_is_loadable(str(p))


def test_gen_cache_from_another_interpreter_is_refused(tmp_path):
    from pipeline.cegis import _gen_cache_is_loadable

    p = tmp_path / "gen_abc.dill"
    p.write_bytes(b"x")
    (tmp_path / "gen_abc.dill.python").write_text("2.7\n")
    assert not _gen_cache_is_loadable(str(p))


# -- projection (what a sampling searcher needs) -------------------------------

def test_projection_lands_in_class():
    """Cross-entropy draws edges independently, so almost every sample is out of
    class and only `bipartite` can be expressed as a pair mask. Projection is
    the alternative: the searcher keeps its edge distribution, but what it
    evaluates is a member of the class."""
    rng = np.random.default_rng(0)
    for classes in [("triangle_free",), ("subcubic",), ("connected",),
                    ("K_4_free",), ("claw_free",)]:
        c = ClassConstraint(list(classes) + ["nontrivial"])
        landed = 0
        for _ in range(20):
            G = nx.gnp_random_graph(10, float(rng.uniform(0.2, 0.7)),
                                    seed=int(rng.integers(1 << 30)))
            H = c.project(G, rng)
            if H is not None:
                assert c.satisfies(H), classes
                landed += 1
        assert landed >= 15, f"{classes}: projected only {landed}/20"


def test_projection_is_identity_without_a_constraint():
    c = ClassConstraint(["nontrivial"])
    G = nx.path_graph(6)
    assert c.project(G, np.random.default_rng(0)) is G


def test_projection_reports_failure_rather_than_an_out_of_class_graph():
    """Returning a graph that is not in the class would be worse than failing:
    the caller would evaluate it, score -inf, and learn nothing — which is the
    behaviour this replaces."""
    c = ClassConstraint(["chordal", "cubic", "nontrivial"])
    rng = np.random.default_rng(0)
    G = nx.gnp_random_graph(12, 0.5, seed=1)
    H = c.project(G, rng, budget=20)
    assert H is None or c.satisfies(H)


def test_failed_move_returns_the_same_object_so_callers_can_stop():
    """MCTS rollouts and VNS ascent detect a dead end by identity.

    When rejection exhausts its try budget the move hands the graph back
    unchanged. Continuing would re-evaluate the same graph — free, since
    `violation` memoises by graph6, but it inflates the evaluation count while
    covering no new ground, which is exactly how MCTS came to report 4x the
    evaluations for the same work.
    """
    c = ClassConstraint(["chordal", "cubic", "nontrivial"], max_tries=2)
    G = nx.complete_graph(4)                 # chordal and cubic; nothing adjacent is
    H = c.neighbor(G, np.random.default_rng(0), k=1)
    assert H is G

    u = ClassConstraint(())                  # unconstrained always makes a move
    assert u.neighbor(G, np.random.default_rng(0), k=1) is not G
