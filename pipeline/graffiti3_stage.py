"""
pipeline/graffiti3_stage.py — native-Python expression-tree conjecturing via
txgraffiti's **Graffiti3** system (replacement for the heavy Sage Conjecturing
stage; no Sage / Apptainer needed).

Graffiti3 mines nonlinear conjectures (ratio / LP / polynomial / products /
sqrt / log) and Sophie sufficient-conditions, and exports Lean 4. Because its
STANDARD/DEEP runners are far too slow on large data, this stage runs it on a
small *exact* corpus — the connected graphs of the graph atlas (n ≤ max_n),
each carrying an exact invariant battery (the same `inv_exact` the adversarial
pool uses, so refutation is sound).

Pipeline fit:
  generate (Graffiti3, FAST by default, sharded by target)
    → refute every candidate against the adversarial pool + class-aware random
      models across several orders (the requested refutation stage)
    → wrap survivors as this pipeline's Conjecture objects (statement-only, with
      a Lean 4 skeleton, complexity, touch/support), ready for the report.
"""
from __future__ import annotations

import logging
from typing import List, Optional

import networkx as nx
import pandas as pd

from config import Config, CONFIG
from conjecture import Conjecture
from graphs.invariants import INVARIANTS, BOOLEANS
from pipeline.adversarial import AdversarialPool, CHECKABLE, inv_exact
from pipeline.random_models import sample_graphs
from pipeline.reporting import complexity as _complexity

from txgraffiti.graffiti3.graffiti3 import Graffiti3, Mode

logger = logging.getLogger(__name__)

_MODES = {"fast": Mode.FAST, "standard": Mode.STANDARD, "deep": Mode.DEEP}

# numeric invariants + classes Graffiti3 may use here = those refutable exactly
_NUMERIC = [k for k in INVARIANTS if k in CHECKABLE]
_BOOLS = [k for k in BOOLEANS if k in CHECKABLE]

# refute against these hypothesis classes' random models (plus a general mix)
_REFUTE_CLASSES = (None, "regular", "bipartite", "tree", "triangle_free",
                   "cubic", "planar")

_ATLAS_CACHE: dict = {}


def _atlas_corpus(max_n: int) -> pd.DataFrame:
    """Exact invariant table for all connected atlas graphs with n ≤ max_n."""
    if max_n in _ATLAS_CACHE:
        return _ATLAS_CACHE[max_n]
    from networkx.generators.atlas import graph_atlas_g
    rows = []
    for G in graph_atlas_g():
        if 2 <= G.number_of_nodes() <= max_n and nx.is_connected(G):
            rows.append(inv_exact(G))
    df = _rows_to_frame(rows)
    _ATLAS_CACHE[max_n] = df
    logger.info("[Graffiti3] corpus: %d connected atlas graphs (n ≤ %d), %d cols",
                len(df), max_n, df.shape[1])
    return df


def _rows_to_frame(rows: List[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    keep_num = [c for c in _NUMERIC if c in df.columns and df[c].notna().all()]
    keep_bool = [c for c in _BOOLS if c in df.columns and df[c].notna().all()]
    df = df[keep_num + keep_bool].copy()
    for b in keep_bool:
        df[b] = df[b] >= 0.5          # bool dtype for hypothesis predicates
    return df


class Graffiti3Generator:
    """Generate + refute nonlinear conjectures with Graffiti3 over a small corpus."""

    def __init__(self, db=None, cfg: Config = CONFIG):
        self.db = db
        self.cfg = cfg
        self.lhs_subset: Optional[set] = None     # restrict targets (sharding)
        self._refute_df: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------- refute --
    def _build_refute_frame(self) -> pd.DataFrame:
        """Adversarial pool + class-aware random models, as an exact table."""
        rows = [vals for _G, vals in AdversarialPool.shared(self.cfg).entries]
        if getattr(self.cfg, "graffiti3_refute_random", True):
            seen = set()
            for cls in _REFUTE_CLASSES:
                for G in sample_graphs(cls, per=4):
                    h = nx.weisfeiler_lehman_graph_hash(G)
                    if h in seen:
                        continue
                    seen.add(h)
                    try:
                        rows.append(inv_exact(G))
                    except Exception:
                        pass
        df = pd.DataFrame(rows)
        for b in _BOOLS:
            if b in df.columns:
                df[b] = df[b] >= 0.5
        logger.info("[Graffiti3] refute frame: %d graphs (pool + random models)", len(df))
        return df

    def _is_refuted(self, native) -> bool:
        if self._refute_df is None:
            self._refute_df = self._build_refute_frame()
        try:
            _applicable, _holds, failures = native.check(self._refute_df)
            return len(failures) > 0
        except Exception:
            return False                      # cannot evaluate ⇒ keep (don't drop)

    # ----------------------------------------------------------- generate --
    def generate_candidates(self) -> List[Conjecture]:
        df = _atlas_corpus(self.cfg.graffiti3_max_n)
        numeric_cols = [c for c in df.columns if c in INVARIANTS]
        targets = [t for t in numeric_cols
                   if self.lhs_subset is None or t in self.lhs_subset]
        if not targets:
            return []
        mode = _MODES.get(self.cfg.graffiti3_mode.lower(), Mode.FAST)
        lean_label = {c: f"{c} G" for c in df.columns}
        g3 = Graffiti3(df, lean_label=lean_label)
        res = g3.conjecture(targets, mode=mode,
                            enable_sophie=self.cfg.graffiti3_sophie)

        # cap to the top-N per target (results are pre-sorted by touches) before
        # the per-candidate refutation, which is the stage's cost driver
        cap = max(1, int(self.cfg.graffiti3_max_per_target)) * len(targets)
        conjs = list(res.conjectures)[:cap]
        sophie = list(res.sophie_conditions)[:cap]

        out: List[Conjecture] = []
        out += self._wrap(g3, conjs, "graffiti3", kind="conjecture")
        if self.cfg.graffiti3_sophie and sophie:
            out += self._wrap(g3, sophie, "graffiti3-sophie", kind="sophie")
        logger.info("[Graffiti3] %d survivors after refutation (mode=%s)",
                    len(out), self.cfg.graffiti3_mode)
        return out

    def _wrap(self, g3, natives, method, *, kind) -> List[Conjecture]:
        survivors, lean = [], []
        for nc in natives:
            if kind == "conjecture" and self._is_refuted(nc):
                continue
            survivors.append(nc)
        # batch Lean export (aligned to survivors)
        try:
            if kind == "conjecture":
                lean = g3.conjectures_as_lean(survivors, prefix="Graffiti3")
            else:
                lean = g3.sophie_conditions_as_lean(survivors, prefix="Sufficient")
        except Exception as e:
            logger.debug("[Graffiti3] Lean export failed: %s", e)
            lean = [None] * len(survivors)

        wrapped = []
        for i, nc in enumerate(survivors):
            if kind == "sophie":
                stmt = f"{getattr(nc, 'hyp_name', '?')} ⇔ {getattr(nc, 'property_name', '?')}"
            elif hasattr(nc, "pretty"):
                stmt = nc.pretty()
            else:
                stmt = str(nc)
            touches = getattr(nc, "touch_count", getattr(nc, "touch",
                       getattr(nc, "coverage", 0)))
            support = getattr(nc, "support_n", getattr(nc, "support",
                       getattr(nc, "support_h", 0)))
            c = Conjecture(
                statement=stmt, inequality=None, generation_method=method,
                lean_statement=(lean[i] if i < len(lean) else None),
                score=float(touches or 0),
                metadata={"novel": True, "kind": kind,
                          "touches": int(touches or 0), "support": int(support or 0)},
            )
            c.metadata["complexity"] = _complexity(c)
            wrapped.append(c)
        return wrapped
