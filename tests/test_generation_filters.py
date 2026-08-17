"""Tests for the generation-time evidence gates and cross-shard witness sharing.

Both address defects the first sharded run exposed: survivors resting on a
handful of graphs, conditioned bounds whose hypothesis restricted nothing, and
shards converging to fixed points that were only local because each kept its
witnesses to itself.
"""
import pandas as pd

from pipeline import candidate_filters as cf

FRAME = pd.DataFrame({
    "cubic":  [True,  False, False, False],
    "tree":   [False, True,  True,  True],
    "order":  [4.0,   3.0,   4.0,   5.0],
    "size":   [6.0,   2.0,   3.0,   4.0],
})


class _Relation:
    def __init__(self, holds):
        self._holds = holds

    def evaluate(self, frame):
        return pd.Series(self._holds, index=frame.index)


class _Native:
    """Stand-in exposing the parts of a graffiti3 Conjecture the filters use."""

    def __init__(self, applicable, holds, condition="cls"):
        self.condition = condition
        self.relation = _Relation(holds)
        self._applicable = applicable

    def check(self, frame, auto_base=True):
        return pd.Series(self._applicable, index=frame.index), None, None


# -- support gate -------------------------------------------------------------

def test_support_counts_applicable_rows():
    native = _Native([True, True, False, False], [True] * 4)
    assert cf.hypothesis_support(native, FRAME) == 2


def test_low_support_candidates_are_dropped():
    weak = _Native([True, False, False, False], [True] * 4)
    strong = _Native([True, True, True, False], [True] * 4)
    kept = cf.drop_low_support([weak, strong], FRAME, min_support=2)
    assert kept == [strong]


def test_support_gate_can_be_disabled():
    weak = _Native([True, False, False, False], [True] * 4)
    assert cf.drop_low_support([weak], FRAME, min_support=0) == [weak]


def test_unmeasurable_support_is_none_not_zero():
    class Broken:
        def check(self, frame, auto_base=True):
            raise RuntimeError("no check")
    assert cf.hypothesis_support(Broken(), FRAME) is None


def test_unreadable_candidate_is_never_dropped_for_low_support():
    class Broken:
        def check(self, frame, auto_base=True):
            raise RuntimeError("no check")
    # even a threshold larger than the frame must not drop it: not measurable
    # is not the same as not supported
    assert len(cf.drop_low_support([Broken()], FRAME, min_support=99)) == 1


# -- decorative gate ----------------------------------------------------------

def test_decorative_when_the_relation_holds_everywhere():
    native = _Native([True, False, False, False], [True, True, True, True])
    assert cf.is_decorative(native, FRAME) is True


def test_not_decorative_when_the_relation_fails_somewhere():
    native = _Native([True, False, False, False], [True, True, False, True])
    assert cf.is_decorative(native, FRAME) is False


def test_unconditioned_candidates_are_never_decorative():
    native = _Native([True] * 4, [True] * 4, condition=None)
    assert cf.is_decorative(native, FRAME) is False


def test_all_nan_relation_is_not_treated_as_decorative():
    class NaNRelation:
        def evaluate(self, frame):
            return pd.Series([None] * len(frame), index=frame.index, dtype="object")

    native = _Native([True] * 4, [True] * 4)
    native.relation = NaNRelation()
    assert cf.is_decorative(native, FRAME) is False


def test_drop_decorative_keeps_the_informative_one():
    decorative = _Native([True, False, False, False], [True] * 4)
    real = _Native([True, True, False, False], [True, True, False, False])
    assert cf.drop_decorative([decorative, real], FRAME) == [real]


# -- cross-shard witness sharing ----------------------------------------------

def test_witnesses_published_by_one_shard_reach_another(tmp_path, monkeypatch):
    """The defect this fixes: each shard converged against its own witnesses,
    so a graph one shard found hard could not refute another shard's claims."""
    import networkx as nx

    from config import Config
    from pipeline.seed_corpus import SeedCorpus, graph6_id

    log = tmp_path / "shared_witnesses.g6"

    def _shard(name):
        cfg = Config()
        cfg.cache_dir = str(tmp_path / name / "cache")
        cfg.hard_seed_dir = str(tmp_path / name / "hard_seed")
        cfg.shared_witness_log = str(log)
        cfg.share_witnesses = True
        return SeedCorpus(cfg)

    a, b = _shard("a"), _shard("b")
    witness = nx.path_graph(4)
    a.add([witness])
    a.persist_witnesses([graph6_id(witness)])

    assert graph6_id(witness) not in b.graphs      # b has never seen it
    assert b.absorb_shared_witnesses() == 1
    assert graph6_id(witness) in b.graphs
    # idempotent: a second pull adds nothing
    assert b.absorb_shared_witnesses() == 0


def test_sharing_can_be_switched_off(tmp_path):
    import networkx as nx

    from config import Config
    from pipeline.seed_corpus import SeedCorpus, graph6_id

    cfg = Config()
    cfg.cache_dir = str(tmp_path / "cache")
    cfg.hard_seed_dir = str(tmp_path / "hard_seed")
    cfg.shared_witness_log = str(tmp_path / "shared.g6")
    cfg.share_witnesses = False
    corpus = SeedCorpus(cfg)
    corpus.publish_witnesses([graph6_id(nx.path_graph(4))])
    assert not (tmp_path / "shared.g6").exists()
    assert corpus.absorb_shared_witnesses() == 0


def test_a_torn_line_does_not_break_absorption(tmp_path):
    """Concurrent appends can leave a partial final line; it must be skipped,
    not crash the round."""
    import networkx as nx

    from config import Config
    from pipeline.seed_corpus import SeedCorpus, graph6_id

    good = graph6_id(nx.path_graph(4))
    log = tmp_path / "shared.g6"
    log.write_text(good + "\n" + "!!not-a-graph6!!\n")

    cfg = Config()
    cfg.cache_dir = str(tmp_path / "cache")
    cfg.hard_seed_dir = str(tmp_path / "hard_seed")
    cfg.shared_witness_log = str(log)
    corpus = SeedCorpus(cfg)
    assert corpus.absorb_shared_witnesses() == 1
    assert good in corpus.graphs
