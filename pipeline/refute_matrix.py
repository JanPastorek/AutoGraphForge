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

from config import CONFIG, Config
from pipeline import invariants_graphcalc as battery
from pipeline.random_models import sample_graphs
from pipeline.seed_corpus import graph6_id

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
            seen.add(gid)
            uniq.append(G)
    return uniq


# --------------------------------------------------------------------------- #
# tier
# --------------------------------------------------------------------------- #
# Precomputed-invariant ingestion: HoG enriched export column → graphcalc battery
# name. Only invariants graphcalc/graffiti3 also speak about are mapped (the rest
# are dropped). These come already computed — including for *big* graphs — so we
# ingest them directly instead of recomputing the battery (which caps at n≤14).
_HOG_TO_GC = {
    "n": "order", "m": "size", "chi": "chromatic_number",
    "alpha": "independence_number", "omega": "clique_number",
    "gamma": "domination_number", "nu": "matching_number",
    "Delta": "maximum_degree", "delta": "minimum_degree",
    "diam": "diameter", "rad": "radius", "alg": "algebraic_connectivity",
    "avg_deg": "average_degree", "ind_dom": "independent_domination_number",
    "spectral_radius": "spectral_radius", "lap_max": "largest_laplacian_eigenvalue",
    "vertex_cover": "vertex_cover_number",
    "eig2": "second_largest_adjacency_eigenvalue",
    "eig_min": "smallest_adjacency_eigenvalue",
    "zero_eigenvalues": "zero_adjacency_eigenvalues_count",
    "bipartite": "bipartite", "planar": "planar", "regular": "regular",
    "eulerian": "eulerian", "chordal": "chordal", "tree": "tree",
    "claw_free": "claw_free", "connected": "connected",
}
_HOG_BOOL_COLS = {"bipartite", "planar", "regular", "eulerian", "chordal",
                  "tree", "claw_free", "connected"}


class _LazyG6Map:
    """graph6-id → networkx graph, reconstructed on demand (no upfront memory for
    the whole tier; only refuting witnesses are ever built)."""

    def __init__(self, ids):
        self._ids = set(ids)

    def __contains__(self, k):
        return k in self._ids

    def __getitem__(self, k):
        return nx.from_graph6_bytes(k.encode() if isinstance(k, str) else k)


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
    def _tier_cache_dir(self) -> str:
        """Where tier batteries live.

        Tier batteries are identical across shards and are never written during
        a run, so pointing every shard at one shared directory saves both disk
        and page cache — the bigdb battery alone was stored six times over. The
        seed battery stays in ``cache_dir``, which is per-shard and written
        constantly.
        """
        return getattr(self.cfg, "tier_cache_dir", "") or self.cfg.cache_dir

    def _tier_from_graphs(self, name: str, graphs: List[nx.Graph],
                          cache_file: str, max_n: int) -> Optional[Tier]:
        graphs = [g for g in graphs if g.number_of_nodes() <= max_n]
        if not graphs:
            return None
        ids = [graph6_id(g) for g in graphs]
        gmap = dict(zip(ids, graphs, strict=True))
        frame = battery.cached_battery(
            list(gmap.values()), list(gmap.keys()),
            cache_path=os.path.join(self._tier_cache_dir(), cache_file),
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
        if getattr(self.cfg, "refute_use_degenerate", True):
            # Disconnected / edgeless / isolate-bearing graphs. The census and
            # family tiers are connected by construction, so without these a
            # conjecture false only on a degenerate graph cannot be refuted.
            from pipeline.degenerate_graphs import degenerate_graphs
            t = self._tier_from_graphs(
                "degenerate", degenerate_graphs(min(10, mx)),
                "battery_degenerate.parquet", min(10, mx))
            if t:
                self.tiers.append(t)
        if self.cfg.refute_use_random:
            rnd: List[nx.Graph] = []
            for cls in _REFUTE_CLASSES:
                rnd += sample_graphs(cls, per=self.cfg.refute_random_per)
            t = self._tier_from_graphs("random", rnd, "battery_random.parquet", mx + 6)
            if t:
                self.tiers.append(t)
        if self.cfg.refute_use_hog:
            t = self._load_hog_tier()
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

    def _load_hog_tier(self) -> Optional[Tier]:
        """Ingest the HoG enriched export's *already-computed* invariants as a
        partial, NaN-aware tier — covering big graphs the n≤14 battery can't.
        Only the mapped columns are kept; missing/partial values stay NaN, and a
        conjecture referencing a column this tier lacks is a coverage miss (the
        refuter falls through), never a false survival."""
        path = self.cfg.refute_hog_csv
        if not os.path.exists(path):
            return None
        try:
            usecols = ["g6"] + [c for c in _HOG_TO_GC]
            df = pd.read_csv(path, usecols=lambda c: c in usecols)
        except Exception as e:
            logger.warning("[refute] HoG tier read failed: %s", e)
            return None
        if "g6" not in df.columns:
            return None
        df = df.dropna(subset=["g6"]).copy()
        if self.cfg.refute_hog_max_n and "n" in df.columns:
            df = df[pd.to_numeric(df["n"], errors="coerce").fillna(1e9) <= self.cfg.refute_hog_max_n]
        # rename to graphcalc names; coerce numerics / booleans; drop dup graphs
        ren = {h: g for h, g in _HOG_TO_GC.items() if h in df.columns}
        ids = df["g6"].astype(str)
        df = df.rename(columns=ren)
        for h in _HOG_BOOL_COLS:
            g = _HOG_TO_GC[h]
            if g in df.columns:
                # 1/0 are omitted deliberately: they hash equal to True/False,
                # so listing them would be redundant, and pandas matches an
                # int/float 1 against the True key already.
                df[g] = df[g].map({True: True, False: False,
                                   "True": True, "False": False,
                                   "1": True, "0": False})
        for g in df.columns:
            if g not in _HOG_BOOL_COLS and g not in _HOG_TO_GC.values():
                continue
            if g not in {_HOG_TO_GC[h] for h in _HOG_BOOL_COLS}:
                df[g] = pd.to_numeric(df[g], errors="coerce")
        frame = df.drop(columns=[c for c in ("g6",) if c in df.columns])
        frame.index = ids.values
        frame = frame[~frame.index.duplicated(keep="first")]
        if frame.empty:
            return None
        logger.info("[refute] tier 'hog': %d graphs, %d precomputed invariants "
                    "(incl. big graphs, partial/NaN-aware)",
                    len(frame), frame.shape[1])
        return Tier("hog", frame, _LazyG6Map(frame.index))

    def _load_bigdb_tier(self) -> Optional[Tier]:
        """Load the offline-precomputed HoG/census battery if it exists."""
        p = os.path.join(self._tier_cache_dir(), "battery_bigdb.parquet")
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
        # Sophie sufficient-conditions (hyp ⇒ property) carry no ``check`` method;
        # route them to the boolean-implication refuter so they face the same
        # corpus as the inequalities (a condition is refuted by any graph where
        # the hypothesis holds but the property fails).
        if hasattr(native, "hyp_relation") and hasattr(native, "property_name"):
            return self._refute_sophie(native)

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

    def _refute_sophie(self, sophie
                       ) -> Tuple[bool, List[nx.Graph], Optional[str]]:
        """Refute a Sophie sufficient-condition ``hyp ⇒ property`` across the
        tiers. A witness is a row where the hypothesis relation holds but the
        boolean property fails. NaN-aware: rows whose hypothesis columns or
        whose property column are missing in a tier are coverage misses, never
        false refutations (mirrors the inequality path)."""
        pn = sophie.property_name
        neg = pn.startswith("¬") or pn.startswith("~")
        col = pn[1:] if neg else pn
        for tier in self.tiers:
            frame = tier.frame
            if col not in frame.columns:
                continue                       # coverage miss: tier lacks the property
            try:
                hyp = np.asarray(pd.Series(sophie.hyp_relation.evaluate(frame)).values,
                                 dtype=float)
            except Exception:
                continue                       # coverage miss: tier lacks a hyp column
            prop_raw = pd.to_numeric(frame[col], errors="coerce").values  # bool→{0,1}, NaN kept
            prop = (prop_raw == 0) if neg else (prop_raw == 1)   # property holds?
            # applicable ∧ violated: hyp holds (≈1), property fully known, property fails
            valid = ~np.isnan(hyp) & ~np.isnan(prop_raw)
            viol = valid & (hyp >= 0.5) & (~prop)
            if viol.any():
                idx = [frame.index[i] for i in np.flatnonzero(viol)]
                wits = [tier.graphs[g] for g in idx if g in tier.graphs]
                return True, wits[:32], tier.name
        return False, [], None

    def touch_count(self, native, seed_frame: pd.DataFrame) -> int:
        """Graphs on the current seed frame where the conjecture is tight.

        Tight means *applicable and at equality*: a class-conditioned conjecture
        may only be credited with graphs that satisfy its hypothesis. Scoring
        the relation alone over the whole frame credits `(claw-free ∧ cubic) ⇒
        χ = ω` with every seed graph where χ = ω, including the ones that are
        neither claw-free nor cubic — which made the touch number identical
        across completely different hypotheses over the same body.

        This is graffiti3's own definition (``Conjecture.touch_count`` computes
        ``applicable & is_tight``), but it is recomputed here rather than
        delegated: that method overwrites itself with an ``int`` via
        ``setattr`` on first call, so calling it again returns a stale count
        from whichever frame happened to see it first.
        """
        rel = getattr(native, "relation", None)
        if rel is not None and hasattr(rel, "is_tight") and hasattr(native, "check"):
            try:
                applicable, _, _ = native.check(seed_frame)
                tight = rel.is_tight(seed_frame).reindex(seed_frame.index)
                both = (pd.Series(applicable).astype(bool)
                        & pd.Series(tight).fillna(False).astype(bool))
                return int(both.sum())
            except Exception:
                pass
        # Fall back to the count graffiti3 cached at generation time. It was
        # computed condition-aware, but against the seed as it stood then, so it
        # is only used when the conjecture cannot be re-scored here.
        tc = getattr(native, "touch_count", None)
        if isinstance(tc, (int, np.integer)):
            return int(tc)
        if callable(tc):
            try:
                return int(tc(seed_frame))
            except Exception:
                pass
        return 0
