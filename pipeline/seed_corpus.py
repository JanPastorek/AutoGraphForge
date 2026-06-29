"""
pipeline/seed_corpus.py — the small "expressible" seed S for CEGIS.

S starts from **TxGraffiti's expressive graph collection** (the edge-lists bundled
with the txgraffiti package) and *grows* as the counterexample search finds hard
witnesses (active learning). Every seed graph carries the full graphcalc battery,
computed exactly and cached by graph6 id so it is never recomputed.

The corpus keeps the actual networkx structures alongside the invariant frame, so
witnesses found during refutation can be (a) looked up as graphs, (b) persisted,
(c) handed to the autoformalizer.

Persistence (approved in docs/CEGIS_PLAN.md §3):
  database/hard_seed/graphs.g6        accumulated witness graphs (graph6, deduped)
  database/cache/seed_battery.parquet graph6 → battery row cache (incremental)
"""
from __future__ import annotations

import logging
import os
from typing import Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd

from config import Config, CONFIG
from pipeline import invariants_graphcalc as battery

logger = logging.getLogger(__name__)

# txgraffiti's bundled expressive graphs (edge lists, 0-indexed "u v" per line)
def _txgraffiti_edgelist_dir() -> Optional[str]:
    try:
        import txgraffiti
        d = os.path.join(os.path.dirname(txgraffiti.__file__),
                         "example_data", "graph-edgelists")
        return d if os.path.isdir(d) else None
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# graph6 id helpers (canonical, dedup-friendly)
# --------------------------------------------------------------------------- #
def graph6_id(G: nx.Graph) -> str:
    """Canonical graph6 string id (relabelled to 0..n-1 ints)."""
    H = nx.convert_node_labels_to_integers(G)
    return nx.to_graph6_bytes(H, header=False).strip().decode("ascii")


def from_graph6(s: str) -> nx.Graph:
    return nx.from_graph6_bytes(s.encode("ascii"))


# --------------------------------------------------------------------------- #
# corpus
# --------------------------------------------------------------------------- #
class SeedCorpus:
    """Growing set of seed graphs + their cached graphcalc battery frame."""

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self.graphs: Dict[str, nx.Graph] = {}      # graph6 id → structure
        self.frame: pd.DataFrame = pd.DataFrame()   # index = graph6 id
        self._cache: pd.DataFrame = self._load_cache()

    # ---------------------------------------------------------------- cache --
    def _cache_path(self) -> str:
        return os.path.join(self.cfg.cache_dir, "seed_battery.parquet")

    def _load_cache(self) -> pd.DataFrame:
        p = self._cache_path()
        if os.path.exists(p):
            try:
                df = battery._coerce(pd.read_parquet(p))
                logger.info("[seed] battery cache: %d graphs", len(df))
                return df
            except Exception as e:
                logger.warning("[seed] cache read failed: %s", e)
        return pd.DataFrame()

    def _save_cache(self) -> None:
        os.makedirs(self.cfg.cache_dir, exist_ok=True)
        try:
            self._cache.to_parquet(self._cache_path())
        except Exception as e:
            logger.warning("[seed] cache write failed: %s", e)

    # -------------------------------------------------------------- battery --
    def _battery_for(self, ids: List[str], graphs: List[nx.Graph]) -> pd.DataFrame:
        """Battery rows for ids, using the cache and filling misses."""
        miss = [(i, g) for i, g in zip(ids, graphs)
                if self._cache.empty or i not in self._cache.index]
        if miss:
            logger.info("[seed] computing battery for %d new graph(s)", len(miss))
            new = battery.compute_battery(
                [g for _, g in miss],
                cap_s=self.cfg.battery_cap_s,
                max_n=self.cfg.exact_tier_max_n,
                # parallelise: large witnesses take the (slower) per-invariant
                # salvage path, so fan them across the same worker budget the
                # refute/search phases use instead of computing them serially.
                workers=max(1, int(getattr(self.cfg, "cegis_workers", 1))),
            )
            new.index = [i for i, _ in miss]
            self._cache = (new if self._cache.empty
                           else pd.concat([self._cache, new]))
            self._cache = self._cache[~self._cache.index.duplicated(keep="last")]
            self._save_cache()
        return self._cache.loc[[i for i in ids if i in self._cache.index]]

    # ------------------------------------------------------------- building --
    def add(self, graphs: List[nx.Graph]) -> List[str]:
        """Add graphs (dedup by graph6), extend the frame. Returns new ids."""
        new_ids, new_graphs = [], []
        for G in graphs:
            if G is None or G.number_of_nodes() < 2:
                continue
            gid = graph6_id(G)
            if gid in self.graphs:
                continue
            self.graphs[gid] = G
            new_ids.append(gid)
            new_graphs.append(G)
        if not new_ids:
            return []
        rows = self._battery_for(new_ids, new_graphs)
        self.frame = rows if self.frame.empty else pd.concat([self.frame, rows])
        self.frame = self.frame[~self.frame.index.duplicated(keep="last")]
        return new_ids

    # --------------------------------------------------------------- loaders --
    @classmethod
    def from_txgraffiti(cls, cfg: Config = CONFIG,
                        include_persisted: bool = True) -> "SeedCorpus":
        c = cls(cfg)
        graphs: List[nx.Graph] = []
        d = _txgraffiti_edgelist_dir()
        if d:
            for f in sorted(os.listdir(d)):
                try:
                    G = nx.read_edgelist(os.path.join(d, f), nodetype=int)
                    if G.number_of_nodes() >= 2:
                        graphs.append(G)
                except Exception:
                    pass
            logger.info("[seed] loaded %d TxGraffiti expressive graphs", len(graphs))
        else:
            logger.warning("[seed] txgraffiti edge-lists not found; seed will be small")
        if include_persisted:
            graphs += cls._load_persisted_graphs(cfg)
        c.add(graphs)
        logger.info("[seed] corpus: %d graphs, frame %s",
                    len(c.graphs), tuple(c.frame.shape))
        return c

    # ------------------------------------------------------- persisted seed --
    @staticmethod
    def _hard_seed_path(cfg: Config) -> str:
        return os.path.join(cfg.hard_seed_dir, "graphs.g6")

    @classmethod
    def _load_persisted_graphs(cls, cfg: Config) -> List[nx.Graph]:
        p = cls._hard_seed_path(cfg)
        if not os.path.exists(p):
            return []
        out = []
        with open(p, "r") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(from_graph6(line))
                    except Exception:
                        pass
        if out:
            logger.info("[seed] loaded %d persisted hard witnesses", len(out))
        return out

    def persist_witnesses(self, ids: List[str]) -> None:
        """Append newly-found hard witnesses to the persistent hard seed."""
        if not (self.cfg.persist_seed and ids):
            return
        os.makedirs(self.cfg.hard_seed_dir, exist_ok=True)
        p = self._hard_seed_path(self.cfg)
        existing = set()
        if os.path.exists(p):
            with open(p) as fh:
                existing = {ln.strip() for ln in fh if ln.strip()}
        add = [i for i in ids if i not in existing]
        if add:
            with open(p, "a") as fh:
                for i in add:
                    fh.write(i + "\n")
            logger.info("[seed] persisted %d new hard witness(es)", len(add))

    # ----------------------------------------------------------------- views --
    def numeric_targets(self) -> List[str]:
        return battery.numeric_invariants(self.frame)

    def booleans(self) -> List[str]:
        return battery.boolean_properties(self.frame)

    def graph_for(self, gid: str) -> Optional[nx.Graph]:
        return self.graphs.get(gid)
