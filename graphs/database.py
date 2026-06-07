"""graphs/database.py — graph database with pre-computed invariant vectors."""
from __future__ import annotations
import logging
from typing import Dict, List, Optional, Tuple
import networkx as nx
from graphs.invariants import evaluate_all, FAST_INVARIANTS, BOOLEANS
from graphs.generators import named_graphs, generate_random_batch
logger = logging.getLogger(__name__)

class GraphEntry:
    __slots__ = ("name", "graph", "invariants", "is_counterexample")
    def __init__(self, name, graph, invariants=None, is_counterexample=False):
        self.name = name
        self.graph = graph
        self.invariants: Dict[str, float] = invariants or {}
        self.is_counterexample = is_counterexample
    def __repr__(self):
        return f"GraphEntry({self.name!r}, n={self.graph.number_of_nodes()})"

class GraphDatabase:
    def __init__(self, fast_only=False):
        self._entries: List[GraphEntry] = []
        self._name_index: Dict[str, int] = {}
        self._inv_set = {**FAST_INVARIANTS, **BOOLEANS} if fast_only else None

    @classmethod
    def build(cls, random_count=15, min_n=4, max_n=12, named_max_n=15,
              seed=42, fast_only=False, verbose=True):
        db = cls(fast_only=fast_only)
        named = [(n, G) for n, G in named_graphs() if G.number_of_nodes() <= named_max_n]
        random_batch = generate_random_batch(random_count, min_n, max_n, seed)
        for name, G in named + random_batch:
            db.add(G, name, quiet=not verbose)
        logger.info("Database built: %d graphs", len(db))
        return db

    def add(self, G, name=None, is_counterexample=False, quiet=False):
        if name is None:
            name = f"G_{len(self._entries)}"
        if name in self._name_index:
            return self._entries[self._name_index[name]]
        inv = evaluate_all(G, self._inv_set)
        entry = GraphEntry(name, G, inv, is_counterexample)
        idx = len(self._entries)
        self._entries.append(entry)
        self._name_index[name] = idx
        if not quiet:
            logger.debug("Added %s (n=%d)", name, G.number_of_nodes())
        return entry

    def add_counterexample(self, G, name=None):
        return self.add(G, name or f"CEX_{len(self._entries)}", is_counterexample=True)

    def get(self, name):
        idx = self._name_index.get(name)
        return self._entries[idx] if idx is not None else None

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def invariant_matrix(self, invariant_names=None):
        names_out, rows = [], []
        for e in self._entries:
            if invariant_names is None or all(k in e.invariants for k in invariant_names):
                names_out.append(e.name)
                rows.append(e.invariants)
        return names_out, rows

    def graphs_with_invariants(self, *inv_names):
        return [e for e in self._entries if all(k in e.invariants for k in inv_names)]

    def summary(self):
        lines = [f"GraphDatabase ({len(self)} graphs):"]
        for e in self._entries[:10]:
            tag = " [CEX]" if e.is_counterexample else ""
            lines.append(f"  {e.name}{tag}")
        if len(self) > 10:
            lines.append(f"  ... and {len(self) - 10} more")
        return "\n".join(lines)
