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
        """Publish the battery cache atomically.

        Written to a temporary file in the same directory and then renamed:
        ``os.replace`` is atomic on POSIX, so a concurrent shard reading this
        file sees either the whole previous version or the whole new one, never
        a half-written parquet. That is what makes ``_rows_from_peers`` safe —
        every cache file has exactly one writer and is only ever published whole.
        """
        os.makedirs(self.cfg.cache_dir, exist_ok=True)
        path = self._cache_path()
        tmp = f"{path}.tmp.{os.getpid()}"
        try:
            self._cache.to_parquet(tmp)
            os.replace(tmp, path)
        except Exception as e:
            logger.warning("[seed] cache write failed: %s", e)
            try:
                os.remove(tmp)
            except OSError:
                pass

    # ------------------------------------------------- peer battery reuse --
    def _peer_cache_paths(self) -> List[str]:
        """Other shards' seed batteries.

        Safe to read precisely because of the invariant above: one writer per
        file, published by atomic rename. No locking is involved and none is
        needed — this process never writes these files.
        """
        pattern = getattr(self.cfg, "peer_battery_glob", "")
        if not pattern:
            return []
        import glob as _glob
        mine = os.path.abspath(self._cache_path())
        return [p for p in sorted(_glob.glob(pattern))
                if os.path.abspath(p) != mine]

    def _rows_from_peers(self, ids: List[str]) -> pd.DataFrame:
        """Battery rows for ``ids`` another shard has already computed.

        A witness costs seconds to a minute of graphcalc time, and every shard
        needs the same rows for the same shared witnesses, so recomputing them
        per shard is pure duplicated work. Read failures are non-fatal: a peer
        mid-write, absent, or corrupt just means we compute the rows ourselves.
        """
        want, found = set(ids), []
        for path in self._peer_cache_paths():
            if not want:
                break
            try:
                peer = pd.read_parquet(path)
            except Exception as e:
                logger.debug("[seed] peer cache unreadable (%s): %s", path, e)
                continue
            hit = peer.index.intersection(list(want))
            if len(hit):
                found.append(peer.loc[hit])
                want -= set(hit)
        if not found:
            return pd.DataFrame()
        rows = pd.concat(found)
        rows = rows[~rows.index.duplicated(keep="first")]
        logger.info("[seed] reused %d battery row(s) computed by other shards",
                    len(rows))
        return rows

    # -------------------------------------------------------------- battery --
    def _battery_for(self, ids: List[str], graphs: List[nx.Graph]) -> pd.DataFrame:
        """Battery rows for ids, using the cache and filling misses."""
        miss = [(i, g) for i, g in zip(ids, graphs)
                if self._cache.empty or i not in self._cache.index]
        if miss:
            # Before paying graphcalc, take whatever a peer shard already
            # computed for these graphs. Shared witnesses are the common case:
            # every shard absorbs them, so without this each one recomputes the
            # same battery rows independently.
            borrowed = self._rows_from_peers([i for i, _ in miss])
            if not borrowed.empty:
                self._cache = (borrowed if self._cache.empty
                               else pd.concat([self._cache, borrowed]))
                self._cache = self._cache[~self._cache.index.duplicated(keep="last")]
                miss = [(i, g) for i, g in miss if i not in self._cache.index]
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
        self.publish_witnesses(ids)

    # ------------------------------------------------- cross-shard sharing --
    def publish_witnesses(self, ids: List[str]) -> None:
        """Append witnesses to the log shared by every concurrent shard.

        Opened in append mode and written one short line at a time: on POSIX an
        ``O_APPEND`` write below ``PIPE_BUF`` is atomic, so concurrent shards
        interleave whole lines and never corrupt each other's. That keeps the
        shards lock-free and unsynchronised — no barrier, no slowest-shard
        stall — while still sharing evidence within a round.
        """
        if not (self.cfg.share_witnesses and ids and self.cfg.shared_witness_log):
            return
        path = self.cfg.shared_witness_log
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "a") as fh:
                for gid in ids:
                    fh.write(gid + "\n")
        except Exception as e:                             # pragma: no cover
            logger.warning("[seed] could not publish witnesses to %s: %s", path, e)

    def absorb_shared_witnesses(self) -> int:
        """Pull in witnesses other shards have published since the last call.

        Returns the number of genuinely new graphs added. Cheap by design: the
        log holds thousands of graph6 lines against a 292k-graph refutation
        tier, and ``add`` already skips graphs the corpus has.
        """
        if not (self.cfg.share_witnesses and self.cfg.shared_witness_log):
            return 0
        path = self.cfg.shared_witness_log
        if not os.path.exists(path):
            return 0
        fresh = []
        try:
            with open(path) as fh:
                for line in fh:
                    gid = line.strip()
                    # A torn final line from a shard writing concurrently simply
                    # fails to parse and is skipped; it will be read next round.
                    if gid and gid not in self.graphs:
                        try:
                            fresh.append(from_graph6(gid))
                        except Exception:
                            continue
        except Exception as e:                             # pragma: no cover
            logger.warning("[seed] could not read %s: %s", path, e)
            return 0
        if not fresh:
            return 0
        added = self.add(fresh)
        if added:
            logger.info("[seed] absorbed %d witness(es) published by other shards",
                        len(added))
        return len(added)

    # ----------------------------------------------------------------- views --
    def numeric_targets(self) -> List[str]:
        return battery.numeric_invariants(self.frame)

    def booleans(self) -> List[str]:
        return battery.boolean_properties(self.frame)

    def graph_for(self, gid: str) -> Optional[nx.Graph]:
        return self.graphs.get(gid)
