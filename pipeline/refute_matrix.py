"""
pipeline/refute_matrix.py — tiered, cached, NaN-aware refutation for CEGIS.

Each *tier* is a pool of graphs carrying the graphcalc battery (same columns as
the seed, so any generated conjecture is directly evaluable) plus the actual
networkx structures (so a refuting graph becomes a seed witness). Tiers are
ordered cheap → expensive and short-circuit: the first tier that produces a
counterexample wins.

A candidate is a **graffiti3 native** Relation/Conjecture exposing
``slack(df) -> Series`` (negative slack ⇒ violated). Evaluation is vectorised by
graffiti3 over the whole tier frame at once. Missing columns (a tier that lacks
an invariant the conjecture needs) raise inside graffiti3 → caught → treated as
"this tier can't judge it" (coverage miss), never as a false survival.

Tiers built here (all with structures + graphcalc battery, cached by graph6):
  * families  — connected graph atlas (n≤7) + parametric families incl. barbells
  * random    — class-aware random models over several orders

The 348k HoG+census DB is a *separate, offline* tier (tools/precompute_battery.py
writes its battery cache); it is loaded here only if that cache exists, since the
raw CSVs carry different column names than the graphcalc battery.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from config import Config, CONFIG
from pipeline import invariants_graphcalc as battery
from pipeline.seed_corpus import graph6_id
from pipeline.random_models import sample_graphs

logger = logging.getLogger(__name__)

_REFUTE_CLASSES = (None, "regular", "bipartite", "tree", "triangle_free",
                   "cubic", "planar")


# --------------------------------------------------------------------------- #
# family generators (structures only; battery added + cached downstream)
# --------------------------------------------------------------------------- #
def _atlas_connected(max_n: int) -> List[nx.Graph]:
    from networkx.generators.atlas import graph_atlas_g
    return [G for G in graph_atlas_g()
            if 2 <= G.number_of_nodes() <= max_n and nx.is_connected(G)]


def _parametric_families(max_n: int) -> List[nx.Graph]:
    """Named families that are classic counterexample sources, incl. barbells."""
    out: List[nx.Graph] = []
    for n in range(3, max_n + 1):
        out += [nx.path_graph(n), nx.cycle_graph(n), nx.complete_graph(min(n, max_n)),
                nx.star_graph(n - 1), nx.wheel_graph(n)]
        for m in range(1, n):
            if m + 1 <= n:
                out.append(nx.lollipop_graph(m, n - m) if m >= 2 and n - m >= 1 else nx.path_graph(n))
        # barbells: two K_m joined by a path
        for m in range(2, max_n):
            for p in range(0, max_n):
                if 2 * m + p <= max_n:
                    out.append(nx.barbell_graph(m, p))
    # complete bipartite
    for a in range(1, max_n):
        for b in range(1, max_n):
            if a + b <= max_n:
                out.append(nx.complete_bipartite_graph(a, b))
    # dedup by graph6
    seen, uniq = set(), []
    for G in out:
        if G.number_of_nodes() < 2:
            continue
        gid = graph6_id(G)
        if gid not in seen:
            seen.add(gid); uniq.append(G)
    return uniq


# --------------------------------------------------------------------------- #
# tier
# --------------------------------------------------------------------------- #
@dataclass
class Tier:
    name: str
    frame: pd.DataFrame                 # index = graph6 id, graphcalc battery cols
    graphs: Dict[str, nx.Graph]


class Refuter:
    """Holds the refutation tiers and judges candidate conjectures."""

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self.tiers: List[Tier] = []
        self._symbolic_cols: Optional[List[str]] = None   # set lazily on first refute
        self._build_tiers()

    # ----------------------------------------------------------- build tiers --
    def _tier_from_graphs(self, name: str, graphs: List[nx.Graph],
                          cache_file: str, max_n: int) -> Optional[Tier]:
        graphs = [g for g in graphs if g.number_of_nodes() <= max_n]
        if not graphs:
            return None
        ids = [graph6_id(g) for g in graphs]
        gmap = dict(zip(ids, graphs))
        frame = battery.cached_battery(
            list(gmap.values()), list(gmap.keys()),
            cache_path=os.path.join(self.cfg.cache_dir, cache_file),
            cap_s=self.cfg.battery_cap_s, max_n=max_n)
        if frame.empty:
            return None
        logger.info("[refute] tier '%s': %d graphs, %d cols", name, len(frame), frame.shape[1])
        return Tier(name, frame, {i: gmap[i] for i in frame.index if i in gmap})

    def _build_tiers(self) -> None:
        mx = self.cfg.refute_families_max_n
        if self.cfg.refute_use_families:
            fam = _atlas_connected(min(7, mx)) + _parametric_families(mx)
            t = self._tier_from_graphs("families", fam, "battery_families.parquet", mx)
            if t:
                self.tiers.append(t)
        if self.cfg.refute_use_random:
            rnd: List[nx.Graph] = []
            for cls in _REFUTE_CLASSES:
                rnd += sample_graphs(cls, per=self.cfg.refute_random_per)
            t = self._tier_from_graphs("random", rnd, "battery_random.parquet", mx + 6)
            if t:
                self.tiers.append(t)
        if self.cfg.refute_use_bigdb:
            t = self._load_bigdb_tier()
            if t:
                self.tiers.append(t)
        # Column vocabulary for the symbolic tier = the graphcalc battery names
        # carried by a structured (non-bigdb) tier.
        for t in self.tiers:
            if t.name in ("families", "random"):
                self._symbolic_cols = list(t.frame.columns)
                break

    def _load_bigdb_tier(self) -> Optional[Tier]:
        """Load the offline-precomputed HoG/census battery if it exists."""
        p = os.path.join(self.cfg.cache_dir, "battery_bigdb.parquet")
        if not os.path.exists(p):
            logger.info("[refute] big-DB battery cache absent — run "
                        "tools/precompute_battery.py to enable that tier (skipping)")
            return None
        try:
            frame = pd.read_parquet(p)
        except Exception as e:
            logger.warning("[refute] big-DB cache read failed: %s", e)
            return None
        graphs = {}
        if "graph6" in frame.columns:
            for gid in frame["graph6"].dropna():
                try:
                    graphs[gid] = nx.from_graph6_bytes(gid.encode())
                except Exception:
                    pass
            frame = frame.set_index("graph6")
        logger.info("[refute] tier 'bigdb': %d graphs", len(frame))
        return Tier("bigdb", frame, graphs)

    # --------------------------------------------------------------- judging --
    def refute(self, native, tol: float = 1e-9
               ) -> Tuple[bool, List[nx.Graph], Optional[str]]:
        """
        Evaluate ``native`` across tiers (cheap→expensive). Return
        (refuted, witness_graphs, tier_name). Uses graffiti3's ``check`` so the
        hypothesis condition is respected (failures = applicable ∧ violated).
        witness_graphs are recoverable structures of the failing rows.
        """
        # Tier 0 — constructive: refute constant/degree bounds by building an
        # extremal witness, independent of pool size (catches `order ≤ 14` etc.
        # that a bounded-order active search misses). Only engages for cheap
        # invariants; otherwise returns None and we fall through to the pools.
        if self.cfg.refute_symbolic and self._symbolic_cols:
            try:
                from pipeline.symbolic_refute import symbolic_refute
                g = symbolic_refute(native, self._symbolic_cols)
                if g is not None:
                    return True, [g], "symbolic"
            except Exception:
                pass
        for tier in self.tiers:
            try:
                _applicable, _holds, failures = native.check(tier.frame)
            except Exception:
                continue                       # coverage miss: tier lacks a column
            if failures is not None and len(failures):
                idx = list(failures.index)
                wits = [tier.graphs[g] for g in idx if g in tier.graphs]
                return True, wits[:32], tier.name
        return False, [], None

    def touch_count(self, native, seed_frame: pd.DataFrame) -> int:
        # Tight graphs (slack ≈ 0) on the *current* seed frame. graffiti3 exposes
        # slack via the conjecture's relation, not the conjecture itself.
        rel = getattr(native, "relation", None)
        if rel is not None and hasattr(rel, "slack"):
            try:
                s = np.asarray(pd.Series(rel.slack(seed_frame)).values, dtype=float)
                return int((np.abs(s) < 1e-9).sum())
            except Exception:
                pass
        # Fall back to the touch count precomputed at generation. Note ``.touch_count``
        # is an *attribute* (int) on a native graffiti3 Conjecture, not a method.
        tc = getattr(native, "touch_count", None)
        if isinstance(tc, (int, np.integer)):
            return int(tc)
        if callable(tc):
            try:
                return int(tc(seed_frame))
            except Exception:
                pass
        return 0
