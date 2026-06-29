"""
pipeline/invariants_graphcalc.py — the invariant battery for CEGIS.

Single source of truth for "all invariants in graphcalc": wraps
``graphcalc.graphs.all_properties`` (59 numeric + boolean columns in graphcalc
2.0) into a robust, NaN-tolerant table builder, plus a best-effort metadata
registry (category / notation / display-name) read from each invariant's
``@invariant_metadata`` decorator.

Design choices (see docs/CEGIS_PLAN.md):
  * Per-graph computation with a wall-clock cap, so one slow/huge graph (the NP-
    hard ILP invariants blow up past n≈18) never stalls a build — it just
    contributes a partial / empty row. **Incomplete tables are expected and OK**;
    refutation is NaN-aware.
  * The union of all rows' keys defines the columns; missing cells are NaN.
"""
from __future__ import annotations

import logging
import os
import signal
from functools import lru_cache
from typing import Dict, List, Optional, Sequence

import networkx as nx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# graphcalc's full-battery entry point (accepts plain networkx graphs); the
# per-invariant entry point + the property name list are used for the salvage
# path (compute each invariant under its own timeout so one slow NP-hard
# invariant blanks only its own cell, not the whole row).
from graphcalc.graphs import all_properties as _all_properties
from graphcalc.graphs import compute_knowledge_table as _ckt
from graphcalc.graphs import GRAPHCALC_PROPERTY_LIST as _PROPS


# --------------------------------------------------------------------------- #
# per-graph timeout
# --------------------------------------------------------------------------- #
class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):           # pragma: no cover - signal handler
    raise _Timeout()


# per-invariant cap (seconds) for the salvage path; a single slow invariant
# blanks only its own cell instead of discarding the whole row. Kept small so a
# big witness with a few intractable invariants does not dominate round time.
_PER_INVARIANT_CAP_S = 3


def _battery_salvage(G: nx.Graph, per_s: int) -> Dict[str, float]:
    """Compute each invariant independently under its own timeout, returning a
    *partial* row: every invariant that finishes in time is kept, the rest are
    simply absent (→ NaN). This is what keeps big/hard graphs from becoming
    all-NaN rows, which would poison graffiti3 generation; partial rows are
    coverage-masked per target by both refutation and generation."""
    row: Dict[str, float] = {}
    have_alarm = hasattr(signal, "SIGALRM")
    if have_alarm:
        old = signal.signal(signal.SIGALRM, _on_alarm)
    try:
        for name in _PROPS:
            if have_alarm:
                signal.alarm(int(per_s))
            try:
                row.update(_ckt([name], [G]).iloc[0].to_dict())
            except Exception:                       # timeout / ILP blow-up / numeric
                pass                                # leave this cell blank (NaN)
            finally:
                if have_alarm:
                    signal.alarm(0)
    finally:
        if have_alarm:
            signal.signal(signal.SIGALRM, old)
    return row


def _battery_one(G: nx.Graph, cap_s: int, max_n: Optional[int] = None) -> Dict[str, float]:
    """Full graphcalc battery for one graph.

    Fast path (graphs within the exact tier ``max_n``): the whole battery in one
    call under a single ``cap_s`` alarm. On timeout/error, or for graphs beyond
    the exact tier, fall back to the per-invariant *salvage* path so the row is
    partial (cheap invariants kept) rather than empty — i.e. NaN means "unknown
    for this graph", never "this graph is unusable"."""
    n = G.number_of_nodes()
    have_alarm = hasattr(signal, "SIGALRM")
    # Graphs above the exact tier: skip the (doomed) whole-battery call and go
    # straight to per-invariant salvage, which still recovers order/size/degree/
    # spectral/… (polynomial) invariants even at large n.
    if max_n is not None and n > max_n:
        return _battery_salvage(G, _PER_INVARIANT_CAP_S)
    if have_alarm:
        old = signal.signal(signal.SIGALRM, _on_alarm)
        signal.alarm(int(cap_s))
    try:
        df = _all_properties([G])
        return df.iloc[0].to_dict()
    except _Timeout:
        logger.debug("[battery] whole-battery timeout (%ds) on n=%d — salvaging "
                     "per-invariant", cap_s, n)
    except Exception as e:                                       # ILP / numeric
        logger.debug("[battery] whole-battery error on n=%d (%s) — salvaging", n, e)
    finally:
        if have_alarm:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old)
    return _battery_salvage(G, _PER_INVARIANT_CAP_S)


# --------------------------------------------------------------------------- #
# public table builder
# --------------------------------------------------------------------------- #
def _battery_one_args(args):
    G, cap_s, max_n = args
    return _battery_one(G, cap_s, max_n)


def compute_battery(graphs: Sequence[nx.Graph], *, cap_s: int = 90,
                    max_n: Optional[int] = None,
                    names: Optional[Sequence[str]] = None,
                    workers: int = 1) -> pd.DataFrame:
    """
    Full graphcalc battery over ``graphs`` as a DataFrame (one row per graph).

    cap_s   per-graph wall-clock cap for the whole-battery fast path.
    max_n   exact-tier threshold: graphs at or below it take the fast path;
            larger graphs go straight to per-invariant salvage (a *partial*
            row of the polynomial invariants), so they are never blank.
            None ⇒ every graph takes the fast path.
    names   optional row labels (stored in the ``graph_name`` column).
    workers fork-pool size for the (embarrassingly parallel) per-graph
            computation; 1 = serial. Each graph's invariants are independent,
            same pattern as the refute/search worker pool in pipeline/cegis.py.
    """
    if workers > 1:
        import multiprocessing as mp
        ctx = mp.get_context("fork")
        args = [(G, cap_s, max_n) for G in graphs]
        with ctx.Pool(workers) as pool:
            rows: List[Dict[str, float]] = pool.map(
                _battery_one_args, args,
                chunksize=max(1, len(args) // (workers * 4) or 1))
    else:
        rows = [_battery_one(G, cap_s, max_n) for G in graphs]
    df = pd.DataFrame(rows)
    df = _coerce(df)
    # ensure a stable order column even if graphcalc names it differently
    if "order" not in df.columns:
        df["order"] = [g.number_of_nodes() for g in graphs]
    if names is not None:
        df.insert(0, "graph_name", list(names))
    n_full = int((df.notna().sum(axis=1) > 1).sum())
    logger.info("[battery] %d graphs → %d cols (%d rows with data)",
                len(graphs), df.shape[1], n_full)
    return df


def _coerce(df: pd.DataFrame) -> pd.DataFrame:
    """Make numeric columns true float (None → NaN) and keep booleans as bool.

    graphcalc returns ``None`` for undefined invariants (e.g. the diameter of a
    disconnected graph), which leaves an *object*-dtype column that breaks
    downstream ``np.isclose``/arithmetic. We coerce: a column whose non-null
    values are all bool becomes ``bool`` (NaN→False); everything else becomes
    numeric with None→NaN.
    """
    for c in df.columns:
        if c == "graph_name":
            continue
        s = df[c]
        if s.dtype == bool:
            continue
        non_null = s.dropna()
        if len(non_null) and non_null.map(lambda v: isinstance(v, (bool,))).all():
            df[c] = s.fillna(False).astype(bool)
        else:
            df[c] = pd.to_numeric(s, errors="coerce")
    return df


def cached_battery(graphs: Sequence[nx.Graph], ids: Sequence[str], *,
                   cache_path: str, cap_s: int = 90,
                   max_n: Optional[int] = None, workers: int = 1) -> pd.DataFrame:
    """Battery for ``graphs`` (index = ``ids``), persisted graph6-keyed to
    ``cache_path``. Only graphs absent from the cache are recomputed."""
    cache = pd.DataFrame()
    if os.path.exists(cache_path):
        try:
            cache = pd.read_parquet(cache_path)
        except Exception as e:
            logger.warning("[battery] cache read failed (%s): %s", cache_path, e)
    miss = [(i, g) for i, g in zip(ids, graphs)
            if cache.empty or i not in cache.index]
    if miss:
        logger.info("[battery] %d new graph(s) → %s", len(miss),
                    os.path.basename(cache_path))
        new = compute_battery([g for _, g in miss], cap_s=cap_s, max_n=max_n, workers=workers)
        new.index = [i for i, _ in miss]
        cache = new if cache.empty else pd.concat([cache, new])
        cache = cache[~cache.index.duplicated(keep="last")]
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        try:
            cache.to_parquet(cache_path)
        except Exception as e:
            logger.warning("[battery] cache write failed: %s", e)
    want = [i for i in ids if i in cache.index]
    return _coerce(cache.loc[want].copy())


def numeric_invariants(df: pd.DataFrame) -> List[str]:
    """Numeric invariant columns (exclude booleans / labels)."""
    out = []
    for c in df.columns:
        if c == "graph_name":
            continue
        s = df[c]
        if s.dtype == bool:
            continue
        if pd.api.types.is_numeric_dtype(s):
            out.append(c)
    return out


def boolean_properties(df: pd.DataFrame) -> List[str]:
    """Boolean (graph-class) columns usable as hypotheses."""
    return [c for c in df.columns if df[c].dtype == bool]


# --------------------------------------------------------------------------- #
# metadata registry (category / notation / display name)  — best effort
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _metadata_registry() -> Dict[str, dict]:
    """Map invariant function-name → {display_name, notation, category}."""
    import inspect
    import pkgutil
    import graphcalc
    from graphcalc.metadata import get_graphcalc_metadata

    reg: Dict[str, dict] = {}
    for m in pkgutil.walk_packages(graphcalc.__path__, "graphcalc."):
        if ".graphs.invariants" not in m.name and ".graphs." not in m.name:
            continue
        try:
            mod = __import__(m.name, fromlist=["x"])
        except Exception:
            continue
        for fn_name, fn in inspect.getmembers(mod, inspect.isfunction):
            md = None
            try:
                md = get_graphcalc_metadata(fn)
            except Exception:
                md = None
            if not md:
                continue
            d = md if isinstance(md, dict) else getattr(md, "__dict__", {}) or {}
            reg[fn_name] = {
                "display_name": d.get("display_name", fn_name),
                "notation": d.get("notation"),
                "category": d.get("category"),
            }
    logger.debug("[battery] metadata registry: %d invariants", len(reg))
    return reg


def metadata(name: str) -> dict:
    """Metadata for an invariant column (display_name/notation/category)."""
    return _metadata_registry().get(
        name, {"display_name": name, "notation": None, "category": None}
    )


def categories(names: Sequence[str]) -> Dict[str, List[str]]:
    """Group invariant names by graphcalc category (None → 'other')."""
    out: Dict[str, List[str]] = {}
    for n in names:
        cat = metadata(n).get("category") or "other"
        out.setdefault(cat, []).append(n)
    return out


def notation(name: str) -> str:
    """Short math notation for an invariant (falls back to its name)."""
    return metadata(name).get("notation") or name
