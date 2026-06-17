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

    @classmethod
    def from_csv(cls, paths, verbose=True):
        """Load one or more invariant CSVs (e.g. the enriched HoG dataset + the
        n≤9 census) into a database of invariant vectors.

        Only the invariant columns are read; a placeholder graph is stored since
        hypothesis generation works on the invariant vectors and the falsifiers
        synthesise their own graphs. Missing values are simply absent (handled by
        the generator's finite-mask). ``paths`` may be a str or an iterable.
        """
        import csv as _csv
        import os as _os
        import sys as _sys
        import networkx as _nx
        from graphs.invariants import INVARIANTS, BOOLEANS

        _csv.field_size_limit(_sys.maxsize)
        if isinstance(paths, str):
            paths = [paths]
        keys = list(INVARIANTS.keys()) + list(BOOLEANS.keys())
        db = cls()
        for path in paths:
            if not _os.path.isfile(path):
                logger.warning("Database CSV not found: %s", path)
                continue
            count = 0
            with open(path, newline="") as fh:
                for row in _csv.DictReader(fh):
                    inv = {}
                    for k in keys:
                        v = row.get(k, "")
                        if v not in ("", None):
                            try:
                                inv[k] = float(v)
                            except ValueError:
                                pass
                    if not inv:
                        continue
                    name = f"{_os.path.basename(path)}:{row.get('name') or count}"
                    entry = GraphEntry(name, _nx.Graph(), inv)
                    db._name_index[name] = len(db._entries)
                    db._entries.append(entry)
                    count += 1
            if verbose:
                logger.info("Loaded %d graphs from %s", count, path)
        logger.info("Database loaded: %d graphs from %d source(s)", len(db), len(paths))
        return db

    def add(self, G, name=None, invariants=None, is_counterexample=False, quiet=False):
        if name is None:
            name = f"G_{len(self._entries)}"
        if name in self._name_index:
            return self._entries[self._name_index[name]]
        inv = invariants if invariants is not None else evaluate_all(G, self._inv_set)
        entry = GraphEntry(name, G, inv, is_counterexample)
        idx = len(self._entries)
        self._entries.append(entry)
        self._name_index[name] = idx
        if not quiet:
            logger.debug("Added %s (n=%d)", name, G.number_of_nodes())
        return entry

    def add_counterexample(self, G, name=None, persist_path=None):
        entry = self.add(G, name or f"CEX_{len(self._entries)}", is_counterexample=True)
        if persist_path:
            self.persist_counterexample(G, persist_path, entry.name)
        return entry

    @staticmethod
    def persist_counterexample(G, path, name):
        """Append a found counterexample (with its computed invariants) to a CSV
        so the dataset learns permanently. Header matches the loader's schema."""
        import csv as _csv
        import os as _os
        import networkx as _nx
        from graphs.invariants import INVARIANTS, BOOLEANS, evaluate_all

        keys = list(INVARIANTS.keys()) + list(BOOLEANS.keys())
        try:
            inv = evaluate_all(G)
            g6 = _nx.to_graph6_bytes(
                _nx.convert_node_labels_to_integers(G), header=False
            ).strip().decode("ascii")
        except Exception as exc:
            logger.warning("Could not persist counterexample: %s", exc)
            return
        _os.makedirs(_os.path.dirname(path) or ".", exist_ok=True)
        new = not _os.path.isfile(path)
        with open(path, "a", newline="") as fh:
            w = _csv.writer(fh)
            if new:
                w.writerow(["name", "n", "m", "g6"] + keys)
            w.writerow([name, G.number_of_nodes(), G.number_of_edges(), g6]
                       + [inv.get(k, "") for k in keys])
        logger.info("Counterexample persisted → %s", path)

    def get(self, name):
        idx = self._name_index.get(name)
        return self._entries[idx] if idx is not None else None

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def invariant_names(self):
        names = set()
        for entry in self._entries:
            names.update(entry.invariants.keys())
        return sorted(names)

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
