"""Tests for cross-shard battery reuse (pipeline/seed_corpus.py).

A shared witness is otherwise measured once per shard, which is the expensive
part of absorbing another shard's counterexamples. Sharing it safely rests on
one invariant: every cache file has exactly one writer and is published whole,
by atomic rename. These tests pin that invariant and the failure behaviour
around it, because a torn read would silently poison a shard's seed frame.
"""
import os

import networkx as nx
import pandas as pd
import pytest

from config import Config
from pipeline.seed_corpus import SeedCorpus, graph6_id


@pytest.fixture
def shards(tmp_path):
    def _make(name):
        cfg = Config()
        cfg.cache_dir = str(tmp_path / name / "cache")
        cfg.hard_seed_dir = str(tmp_path / name / "hard_seed")
        cfg.shared_witness_log = str(tmp_path / "shared.g6")
        cfg.peer_battery_glob = str(tmp_path / "*" / "cache" / "seed_battery.parquet")
        return SeedCorpus(cfg)
    return _make


# -- the atomicity invariant --------------------------------------------------

def test_cache_is_published_by_atomic_rename(shards, tmp_path, monkeypatch):
    corpus = shards("a")
    corpus.add([nx.path_graph(4)])
    renamed = {}
    real_replace = os.replace

    def spy(src, dst):
        renamed["src"], renamed["dst"] = src, dst
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    corpus._save_cache()
    assert renamed["dst"].endswith("seed_battery.parquet")
    assert ".tmp." in renamed["src"]
    # the temp file must not survive publication
    leftovers = [p for p in os.listdir(os.path.dirname(renamed["dst"]))
                 if ".tmp." in p]
    assert leftovers == []


def test_failed_write_leaves_no_temp_file(shards, monkeypatch):
    corpus = shards("a")
    corpus.add([nx.path_graph(4)])

    def boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", boom)
    corpus._save_cache()                       # must not raise
    cache_dir = corpus.cfg.cache_dir
    assert [p for p in os.listdir(cache_dir) if ".tmp." in p] == []


# -- peer reuse ---------------------------------------------------------------

def test_peer_rows_are_reused_instead_of_recomputed(shards, monkeypatch):
    witness = nx.path_graph(5)
    gid = graph6_id(witness)

    first = shards("a")
    first.add([witness])                       # computes + publishes the battery
    assert gid in first._cache.index

    second = shards("b")
    from pipeline import invariants_graphcalc as battery

    def fail(*a, **k):
        raise AssertionError("recomputed a battery a peer already had")

    monkeypatch.setattr(battery, "compute_battery", fail)
    second.add([witness])                      # must come from the peer cache
    assert gid in second.graphs
    assert gid in second._cache.index


def test_a_shard_never_reads_its_own_cache_as_a_peer(shards):
    corpus = shards("a")
    corpus.add([nx.path_graph(4)])
    corpus._save_cache()
    assert corpus._peer_cache_paths() == []


def test_unreadable_peer_is_skipped_not_fatal(shards, tmp_path):
    corpus = shards("b")
    bad = tmp_path / "a" / "cache"
    bad.mkdir(parents=True)
    (bad / "seed_battery.parquet").write_text("not a parquet file")
    # a peer caught mid-write, or corrupt, must simply be ignored
    assert corpus._rows_from_peers(["Ch"]).empty


def test_peer_reuse_is_off_without_a_glob(tmp_path):
    cfg = Config()
    cfg.cache_dir = str(tmp_path / "cache")
    cfg.hard_seed_dir = str(tmp_path / "hard_seed")
    cfg.peer_battery_glob = ""
    corpus = SeedCorpus(cfg)
    assert corpus._peer_cache_paths() == []
    assert corpus._rows_from_peers(["Ch"]).empty
