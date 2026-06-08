"""
graphs/loaders.py — load graph corpora from the on-disk classes in ``graphs/``.

Handles the heterogeneous formats found in this repository:

* plain ``.g6``                         (graph6, one graph per line)
* gzip-compressed ``.g6.gz``            (e.g. some Ramsey files)
* bzip2-compressed ``.bz2``             (e.g. some strongly-regular files)
* zipped ``.zip`` archives of ``.g6``   (minimally rigid graphs)
* strongly-regular ``.txt``             (Spence adjacency-matrix format)

Robustness features
-------------------
* Files that are actually saved HTML error pages (some ``cages``/``ramsey``
  files were downloaded as ``<!DOCTYPE html>``) are detected and skipped.
* Per-source caps with **reservoir sampling** keep huge classes
  (all 9-vertex graphs, minimally rigid V12, ...) tractable.

Every public loader yields ``(name, networkx.Graph)`` pairs so they can be fed
straight into :class:`graphs.database.GraphDatabase`.
"""

from __future__ import annotations

import bz2
import gzip
import logging
import os
import random
import zipfile
from typing import Iterable, Iterator, List, Optional, Tuple

import networkx as nx

logger = logging.getLogger(__name__)

# Repository ``graphs/`` directory (this file lives inside it).
GRAPHS_DIR = os.path.dirname(os.path.abspath(__file__))

Pair = Tuple[str, nx.Graph]


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _looks_like_html(chunk: bytes) -> bool:
    """True if the bytes begin with an HTML document (corrupted download)."""
    head = chunk.lstrip()[:64].lower()
    return head.startswith(b"<!doctype") or head.startswith(b"<html")


def _open_maybe_compressed(path: str) -> bytes:
    """Read a file, transparently decompressing .gz / .bz2."""
    low = path.lower()
    if low.endswith(".gz"):
        with gzip.open(path, "rb") as fh:
            return fh.read()
    if low.endswith(".bz2"):
        with bz2.open(path, "rb") as fh:
            return fh.read()
    with open(path, "rb") as fh:
        return fh.read()


def _parse_g6_lines(raw: bytes) -> Iterator[nx.Graph]:
    """Yield graphs from graph6 bytes, skipping blank/HTML/garbage lines."""
    if _looks_like_html(raw):
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # graph6 payload bytes are all printable ASCII in [63, 126]; an HTML
        # tag or stray text will start with '<' or other low bytes.
        if line[:1] in (b"<", b"#"):
            continue
        # tolerate an optional '>>graph6<<' header on the line
        try:
            G = nx.from_graph6_bytes(line)
        except Exception:
            continue
        yield G


def _parse_srg_txt(raw: bytes) -> Iterator[nx.Graph]:
    """
    Parse Spence strongly-regular-graph text format: an optional header line
    like ``dim=5, degree=2, lambda=0, mu=1`` followed by blank-separated
    square 0/1 adjacency matrices (one matrix == one graph).
    """
    if _looks_like_html(raw):
        return
    text = raw.decode("ascii", errors="ignore")
    rows: List[str] = []

    def flush() -> Optional[nx.Graph]:
        if not rows:
            return None
        n = len(rows)
        if any(len(r) != n for r in rows):
            return None
        A = [[1 if ch == "1" else 0 for ch in r] for r in rows]
        return _graph_from_matrix(A)

    for line in text.splitlines():
        s = line.strip()
        if s and set(s) <= {"0", "1"}:
            rows.append(s)
        else:
            G = flush()
            if G is not None:
                yield G
            rows = []
    G = flush()
    if G is not None:
        yield G


def _graph_from_matrix(A: List[List[int]]) -> nx.Graph:
    G = nx.Graph()
    n = len(A)
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if A[i][j]:
                G.add_edge(i, j)
    return G


def _reservoir(it: Iterable[nx.Graph], cap: Optional[int], rng: random.Random) -> List[nx.Graph]:
    """Reservoir-sample at most ``cap`` graphs from a (possibly huge) stream."""
    if cap is None:
        return list(it)
    sample: List[nx.Graph] = []
    for i, g in enumerate(it):
        if i < cap:
            sample.append(g)
        else:
            j = rng.randint(0, i)
            if j < cap:
                sample[j] = g
    return sample


# ---------------------------------------------------------------------------
# Per-file loaders
# ---------------------------------------------------------------------------

def load_g6_file(path: str, cap: Optional[int] = None, seed: int = 42) -> List[nx.Graph]:
    """Load (and optionally sample) all graphs from a g6 / .gz / .bz2 file."""
    raw = _open_maybe_compressed(path)
    rng = random.Random(seed)
    return _reservoir(_parse_g6_lines(raw), cap, rng)


def load_srg_file(path: str, cap: Optional[int] = None, seed: int = 42) -> List[nx.Graph]:
    raw = _open_maybe_compressed(path)
    rng = random.Random(seed)
    return _reservoir(_parse_srg_txt(raw), cap, rng)


def _stream_zip_member(fh) -> Iterator[nx.Graph]:
    """Yield graphs from an open zip member, one line at a time (no full read)."""
    for raw_line in fh:
        line = raw_line.strip()
        if not line or line[:1] in (b"<", b"#"):
            continue
        try:
            yield nx.from_graph6_bytes(line)
        except Exception:
            continue


def load_zip_g6(
    path: str,
    cap_per_member: Optional[int] = None,
    max_n: Optional[int] = None,
    seed: int = 42,
) -> Iterator[Pair]:
    """
    Yield (member_name, graph) from a zip of g6 files.  ``cap_per_member``
    reservoir-samples each archive member; ``max_n`` skips members whose graphs
    exceed that vertex count.  Members are streamed line-by-line, so an
    over-large member is skipped after reading only its first line.
    """
    rng = random.Random(seed)
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            if info.is_dir() or not info.filename.lower().endswith(".g6"):
                continue
            member = os.path.splitext(os.path.basename(info.filename))[0]
            with zf.open(info) as fh:
                stream = _stream_zip_member(fh)
                first = next(stream, None)
                if first is None:
                    continue
                if max_n is not None and first.number_of_nodes() > max_n:
                    continue

                def chained() -> Iterator[nx.Graph]:
                    yield first
                    yield from stream

                for i, g in enumerate(_reservoir(chained(), cap_per_member, rng)):
                    yield (f"{member}#{i}", g)


# ---------------------------------------------------------------------------
# Per-directory / class loaders
# ---------------------------------------------------------------------------

def _iter_dir_g6(subdir: str, cap_per_file: Optional[int], seed: int) -> Iterator[Pair]:
    d = os.path.join(GRAPHS_DIR, subdir)
    if not os.path.isdir(d):
        logger.warning("class dir missing: %s", d)
        return
    skipped = 0
    for fname in sorted(os.listdir(d)):
        low = fname.lower()
        if not (low.endswith(".g6") or low.endswith(".g6.gz") or low.endswith(".gz")):
            continue
        path = os.path.join(d, fname)
        graphs = load_g6_file(path, cap=cap_per_file, seed=seed)
        if not graphs:
            skipped += 1
            continue
        stem = fname
        for i, g in enumerate(graphs):
            yield (f"{subdir}:{stem}#{i}", g)
    if skipped:
        logger.info("%s: skipped %d empty/HTML files", subdir, skipped)


def load_cographs(cap_per_file: Optional[int] = None, seed: int = 42) -> Iterator[Pair]:
    yield from _iter_dir_g6("cographs", cap_per_file, seed)


def load_minimal_cayley(cap_per_file: Optional[int] = None, seed: int = 42) -> Iterator[Pair]:
    yield from _iter_dir_g6("minimal_cayley", cap_per_file, seed)


def load_cages(cap_per_file: Optional[int] = None, seed: int = 42) -> Iterator[Pair]:
    yield from _iter_dir_g6("cages", cap_per_file, seed)


def load_minimal_ramsey(cap_per_file: Optional[int] = None, seed: int = 42) -> Iterator[Pair]:
    yield from _iter_dir_g6("minimal_ramsey", cap_per_file, seed)


def load_srg(cap_per_file: Optional[int] = None, seed: int = 42) -> Iterator[Pair]:
    d = os.path.join(GRAPHS_DIR, "srg_spence")
    if not os.path.isdir(d):
        return
    for fname in sorted(os.listdir(d)):
        if not (fname.endswith(".txt") or fname.endswith(".bz2")):
            continue
        path = os.path.join(d, fname)
        for i, g in enumerate(load_srg_file(path, cap=cap_per_file, seed=seed)):
            yield (f"srg_spence:{fname}#{i}", g)


def load_minimally_rigid(
    cap_per_member: Optional[int] = 500,
    max_n: Optional[int] = 11,
    seed: int = 42,
) -> Iterator[Pair]:
    d = os.path.join(GRAPHS_DIR, "minimally_rigid_graphs")
    if not os.path.isdir(d):
        return
    for fname in sorted(os.listdir(d)):
        if not fname.lower().endswith(".zip"):
            continue
        path = os.path.join(d, fname)
        zstem = os.path.splitext(fname)[0]
        for name, g in load_zip_g6(path, cap_per_member, max_n, seed):
            yield (f"rigid:{zstem}/{name}", g)


def load_hog(cap: Optional[int] = None, seed: int = 42) -> Iterator[Pair]:
    path = os.path.join(GRAPHS_DIR, "hog_all_28859_graphs.g6")
    if not os.path.isfile(path):
        return
    for i, g in enumerate(load_g6_file(path, cap=cap, seed=seed)):
        yield (f"hog:#{i}", g)


def load_nauty(
    max_vertices: int = 9,
    connected_only: bool = False,
    cap_per_n: Optional[int] = None,
    seed: int = 42,
) -> Iterator[Pair]:
    """Load the geng-generated corpus from ``generated_nauty/``."""
    d = os.path.join(GRAPHS_DIR, "generated_nauty")
    kind = "connected" if connected_only else "all"
    for n in range(1, max_vertices + 1):
        path = os.path.join(d, f"graphs_{n}v_{kind}.g6")
        if not os.path.isfile(path):
            continue
        for i, g in enumerate(load_g6_file(path, cap=cap_per_n, seed=seed + n)):
            yield (f"nauty:{n}v_{kind}#{i}", g)


__all__ = [
    "load_cographs", "load_minimal_cayley", "load_cages", "load_minimal_ramsey",
    "load_srg", "load_minimally_rigid", "load_hog", "load_nauty",
    "load_g6_file", "load_srg_file", "load_zip_g6",
]
