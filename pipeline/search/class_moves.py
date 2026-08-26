"""
pipeline/search/class_moves.py — keep the counterexample searchers inside the
hypothesis class.

Every generated conjecture is class-conditioned: ``(cubic ∧ triangle_free) ⇒ …``
says nothing about a graph outside that class, so a graph outside it is not a
counterexample. ``GraphSearchProblem.violation`` encodes this by returning
``-inf`` there — which is correct, and which makes the objective a plateau: the
searchers get no gradient anywhere except on the class itself.

That would be tolerable if the class were a large part of the space. It is not.
Measured over the 293,756-graph refutation pool, the median class-conditioned
survivor's hypothesis is satisfied by 0.07% of graphs; 56% of survivors have a
hypothesis holding on under 0.1% of the pool, and ``chordal ∧ cubic ∧
nontrivial`` holds on exactly one. A blind edge flip from an in-class graph
almost always lands outside, so SA/VNS/MCTS spend their budget rejecting -inf
and cross-entropy's independent-Bernoulli sampler essentially never produces a
member of the class at all.

This module supplies the missing structure: a start distribution *on* the class,
a neighbourhood move that *preserves* it, and — where the class is an edge-set
restriction — the reduced pair set the sampling searchers should sample over.

Where a class has an exact structure-preserving move it is used, so no budget
goes to rejection:

  bipartite      flips are confined to pairs crossing a fixed bipartition
  tree           remove an edge, reconnect the two resulting components
  regular/cubic  double edge swap (preserves the degree sequence exactly)

Every other class falls back to rejection: propose a blind flip, keep it only if
the class still holds. That is still a large improvement over an unconstrained
move, because the rejection is decided by a cheap networkx predicate rather than
by computing the full graphcalc battery and reading ``-inf`` off the objective.

The predicates here are deliberately independent re-implementations in plain
networkx, not calls into graphcalc: they run inside the inner loop of every
searcher, thousands of times per conjecture. They decide only *where the search
walks*. Whether a graph found this way is really a counterexample is still
decided by ``GraphSearchProblem.violation`` through graphcalc, so a disagreement
between the two can cost search efficiency but cannot manufacture a refutation.
"""
from __future__ import annotations

import itertools
import logging
import re
import time
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import networkx as nx

logger = logging.getLogger(__name__)


# ------------------------------------------------------------- tier lookup --
# Some conjunctions collapse to a class so thin that neither sampling nor a
# descent finds it: a tree that is a cograph is exactly a star, and hill-
# climbing on the induced-P4 count stalls at a local minimum well away from it.
# Those classes are already enumerated, though — the refutation tiers carry the
# boolean class columns for every graph they hold, so the members can simply be
# looked up. A tier graph is a *start*, not a witness: the walk moves off it,
# and for orders above the tier cap the constructive path still applies.
_TIER_FILES = ("battery_families.parquet", "battery_degenerate.parquet",
               "battery_random.parquet", "battery_bigdb.parquet")
_TIER_MEMBERS: Dict[Tuple[str, ...], Dict[int, List[str]]] = {}


def _tier_members(classes: Tuple[str, ...], cache_dir: str = "") -> Dict[int, List[str]]:
    """{order: [graph6, …]} for graphs in the tiers satisfying every class."""
    if classes in _TIER_MEMBERS:
        return _TIER_MEMBERS[classes]
    import os

    import pandas as pd

    from config import CONFIG
    # Shards point `tier_cache_dir` at the shared tier batteries and keep only
    # their own (frequently rewritten) seed battery in `cache_dir`, so the tier
    # lookup has to follow the same override the refuter does.
    root = (cache_dir or getattr(CONFIG, "tier_cache_dir", "")
            or getattr(CONFIG, "cache_dir", "")
            or os.path.join("database", "cache"))
    out: Dict[int, List[str]] = {}
    for fname in _TIER_FILES:
        path = os.path.join(root, fname)
        if not os.path.exists(path):
            continue
        try:
            df = pd.read_parquet(path, columns=[c for c in classes if c != "nontrivial"])
        except Exception:
            continue                       # tier lacks one of the class columns
        if df.empty:
            continue
        keep = df.astype(bool).all(axis=1)
        for gid in df.index[keep].astype(str):
            try:
                n = nx.from_graph6_bytes(gid.encode()).number_of_nodes()
            except Exception:
                continue
            out.setdefault(n, []).append(gid)
    _TIER_MEMBERS[classes] = out
    return out


# --------------------------------------------------------------- predicates --
def _is_regular(G: nx.Graph) -> bool:
    d = [x for _, x in G.degree()]
    return bool(d) and len(set(d)) == 1


def _is_cubic(G: nx.Graph) -> bool:
    return all(x == 3 for _, x in G.degree())


def _is_triangle_free(G: nx.Graph) -> bool:
    return sum(nx.triangles(G).values()) == 0


def _is_k4_free(G: nx.Graph) -> bool:
    return all(len(c) < 4 for c in nx.find_cliques(G))


def _is_claw_free(G: nx.Graph) -> bool:
    """No induced K_{1,3}: no vertex has three pairwise non-adjacent neighbours."""
    for v in G:
        nbrs = list(G[v])
        if len(nbrs) < 3:
            continue
        for a, b, c in itertools.combinations(nbrs, 3):
            if not (G.has_edge(a, b) or G.has_edge(a, c) or G.has_edge(b, c)):
                return False
    return True


def _is_cograph(G: nx.Graph) -> bool:
    """P4-free, via the recursive union/join characterisation.

    Checking all 4-subsets is O(n^4) and this runs in the searchers' inner loop.
    A cograph is exactly a graph that is a single vertex, or disconnected with
    cograph components, or whose complement is disconnected with cograph
    components — which recurses on strictly smaller graphs.
    """
    if G.number_of_nodes() <= 1:
        return True
    comps = list(nx.connected_components(G))
    if len(comps) > 1:
        return all(_is_cograph(G.subgraph(c)) for c in comps)
    H = nx.complement(G)
    ccomps = list(nx.connected_components(H))
    if len(ccomps) == 1:
        return False                      # connected with connected complement
    return all(_is_cograph(G.subgraph(c)) for c in ccomps)


def _is_eulerian(G: nx.Graph) -> bool:
    return (G.number_of_nodes() > 0 and nx.is_connected(G)
            and all(d % 2 == 0 for _, d in G.degree()))


def _count_p4(G: nx.Graph) -> int:
    """Number of induced P4s.

    Counted through the *middle* edge, which every induced P4 has exactly one
    of: for an edge uv, an induced a-u-v-b needs a adjacent to u but not v, b
    adjacent to v but not u, and a, b non-adjacent. That is O(m·d²) rather than
    the O(n^4) of enumerating 4-subsets, and this runs in the inner loop of the
    repair descent on sparse graphs where the difference is decisive.
    """
    total = 0
    for u, v in G.edges():
        left = [a for a in G[u] if a != v and not G.has_edge(a, v)]
        right = [b for b in G[v] if b != u and not G.has_edge(b, u)]
        for a in left:
            for b in right:
                if a != b and not G.has_edge(a, b):
                    total += 1
    return total


def _count_claws(G: nx.Graph) -> int:
    """Number of induced K_{1,3}: independent triples inside a neighbourhood."""
    total = 0
    for v in G:
        nbrs = list(G[v])
        if len(nbrs) < 3:
            continue
        for a, b, c in itertools.combinations(nbrs, 3):
            if not (G.has_edge(a, b) or G.has_edge(a, c) or G.has_edge(b, c)):
                total += 1
    return total


# How far a graph is from a class, as a nonnegative integer that is 0 exactly
# when the class holds. `start` hill-climbs on the sum of these to reach a
# conjunction no single generator can produce — a star for `tree & cograph`, a
# disjoint union of K4s for `cubic & claw_free`. A binary predicate gives a
# hill-climber nothing to descend; a defect count gives it a gradient.
DEFECTS: Dict[str, Callable[[nx.Graph], int]] = {
    "connected":     lambda G: max(0, nx.number_connected_components(G) - 1),
    "tree":          lambda G: (max(0, nx.number_connected_components(G) - 1)
                                + abs(G.number_of_edges()
                                      - (G.number_of_nodes() - 1))),
    "bipartite":     lambda G: 0 if nx.is_bipartite(G) else 1 + _odd_defect(G),
    "regular":       lambda G: (max(d for _, d in G.degree())
                                - min(d for _, d in G.degree())) if G else 0,
    "cubic":         lambda G: sum(abs(d - 3) for _, d in G.degree()),
    "subcubic":      lambda G: sum(max(0, d - 3) for _, d in G.degree()),
    "triangle_free": lambda G: sum(nx.triangles(G).values()) // 3,
    "K_4_free":      lambda G: sum(1 for c in nx.find_cliques(G) if len(c) >= 4),
    "claw_free":     _count_claws,
    "cograph":       _count_p4,
    "eulerian":      lambda G: (sum(1 for _, d in G.degree() if d % 2)
                                + max(0, nx.number_connected_components(G) - 1)),
    "planar":        lambda G: 0 if nx.check_planarity(G)[0] else 1,
    "chordal":       lambda G: 0 if nx.is_chordal(G) else 1,
    "nontrivial":    lambda G: max(0, 2 - G.number_of_nodes()),
}


def _odd_defect(G: nx.Graph) -> int:
    """Edges inside a part of a greedy 2-colouring — a gradient toward bipartite."""
    colour: Dict[int, int] = {}
    for comp in nx.connected_components(G):
        root = next(iter(comp))
        colour[root] = 0
        for u, v in nx.bfs_edges(G, root):
            colour[v] = 1 - colour[u]
    return sum(1 for u, v in G.edges() if colour.get(u) == colour.get(v))


PREDICATES: Dict[str, Callable[[nx.Graph], bool]] = {
    "connected":     lambda G: G.number_of_nodes() > 0 and nx.is_connected(G),
    "tree":          nx.is_tree,
    "bipartite":     nx.is_bipartite,
    "regular":       _is_regular,
    "cubic":         _is_cubic,
    "subcubic":      lambda G: all(d <= 3 for _, d in G.degree()),
    "triangle_free": _is_triangle_free,
    "K_4_free":      _is_k4_free,
    "claw_free":     _is_claw_free,
    "cograph":       _is_cograph,
    "eulerian":      _is_eulerian,
    "planar":        lambda G: nx.check_planarity(G)[0],
    "chordal":       lambda G: nx.is_chordal(G),
    # graffiti3 puts this on every conjecture; it is a bound on the order, not a
    # structural restriction, and the searchers never propose n < 2 anyway.
    "nontrivial":    lambda G: G.number_of_nodes() >= 2,
}

# Ignored when choosing moves: constraining to it restricts nothing.
_TRIVIAL = {"nontrivial"}


def hypothesis_classes(native, all_cols: Sequence[str]) -> Tuple[str, ...]:
    """The graph classes a conjecture is conditioned on, in `PREDICATES`.

    Reads the hypothesis side of ``(condition) ⇒ body``. A necessary-condition
    conjecture — ``(inequality) ⇒ ¬tree`` — has no class in its hypothesis and
    correctly yields (): it *does* speak about graphs outside `tree`, so the
    search must not be restricted for it.
    """
    try:
        pretty = native.pretty()
    except Exception:
        return ()
    if "⇒" not in pretty:
        return ()
    cond = pretty.split("⇒", 1)[0]
    return tuple(c for c in all_cols
                 if c in PREDICATES
                 and re.search(r"\b" + re.escape(c) + r"\b", cond))


# ------------------------------------------------------------- constraint --
class ClassConstraint:
    """Start distribution, neighbourhood and pair set for one class conjunction.

    ``classes`` is the conjunction from the conjecture's hypothesis. An empty
    conjunction (or one containing only trivial classes) gives the unconstrained
    behaviour the searchers had before, so this is safe to install everywhere.
    """

    def __init__(self, classes: Sequence[str] = (), *, max_tries: int = 40,
                 repair_time_s: float = 1.0, start_pool: int = 3):
        self.classes = tuple(c for c in classes if c in PREDICATES)
        self.active = tuple(c for c in self.classes if c not in _TRIVIAL)
        self.max_tries = int(max_tries)
        # The repair descent is the expensive part (the cograph defect counts
        # induced P4s, O(n^4) per evaluation) and the searchers call `start`
        # once per order per searcher — six times over for the same order. So
        # it is bounded in wall-clock and its results are pooled: after a few
        # in-class graphs have been found for an order, later calls draw from
        # them instead of paying for the descent again.
        self.repair_time_s = float(repair_time_s)
        self.start_pool = int(start_pool)
        self._starts: Dict[int, List[nx.Graph]] = {}

    def __bool__(self) -> bool:
        return bool(self.active)

    def __repr__(self) -> str:
        return f"ClassConstraint({', '.join(self.active) or 'unconstrained'})"

    # -------------------------------------------------------------- testing --
    def satisfies(self, G: Optional[nx.Graph]) -> bool:
        if G is None:
            return False
        try:
            return all(PREDICATES[c](G) for c in self.classes)
        except Exception:
            return False

    # --------------------------------------------------------------- starts --
    def start(self, n: int, rng) -> Optional[nx.Graph]:
        """A graph of order n in the class, or None if none was produced.

        Four sources, cheapest first (`_find_start`, then `_tier_start`): a
        direct constructor for classes rejection cannot reach, the class-aware
        generators in ``pipeline.random_models``, Erdős–Rényi rejection, a
        defect descent for conjunctions no single generator lands on, and
        finally a lookup of known members in the refutation tiers. Every
        candidate is checked against the *whole* conjunction, because a
        generator only knows about one class of it.

        Results are pooled per order: the six searchers each ask for a start at
        each order, and the descent is far too expensive to repeat.

        Returning None is a meaningful answer, not a failure to handle: some
        conjunctions really have no member at a given order — a chordal cubic
        graph is K4 and nothing else — and the caller should fall back rather
        than pretend it started in-class.
        """
        if not self.active:
            return None
        pool = self._starts.setdefault(n, [])
        if len(pool) >= self.start_pool:
            return pool[int(rng.integers(len(pool)))].copy()
        G = self._find_start(n, rng) or self._tier_start(n, rng)
        if G is not None:
            pool.append(G.copy())
        return G

    def _tier_start(self, n: int, rng) -> Optional[nx.Graph]:
        """A known member of the class from the refutation tiers, at order n."""
        try:
            members = _tier_members(self.classes)
        except Exception:
            return None
        ids = members.get(n) or []
        if not ids:
            return None
        for _ in range(min(self.max_tries, len(ids))):
            gid = ids[int(rng.integers(len(ids)))]
            try:
                G = nx.from_graph6_bytes(gid.encode())
            except Exception:
                continue
            if self.satisfies(G):
                return nx.convert_node_labels_to_integers(G)
        return None

    def _find_start(self, n: int, rng) -> Optional[nx.Graph]:
        from pipeline.random_models import sample_graphs

        if "bipartite" in self.active:
            # Built on the canonical bipartition so that the cross-pair move set
            # and the RL action mask apply to this graph as generated.
            A, B = self.canonical_parts(n)
            pairs = [(u, v) for u in A for v in B]
            for _ in range(self.max_tries):
                G = nx.Graph()
                G.add_nodes_from(range(n))
                keep = rng.random(len(pairs)) < float(rng.uniform(0.2, 0.7))
                G.add_edges_from(q for q, k in zip(pairs, keep) if k)
                if self.satisfies(G):
                    return G
        for _ in range(self.max_tries):
            for cls in self.active:
                build = _CONSTRUCTORS.get(cls)
                if build is not None:
                    try:
                        G = build(n, rng)
                    except Exception:
                        G = None
                    if self.satisfies(G):
                        return G
                try:
                    for G in sample_graphs(cls, orders=(n,), per=3,
                                           seed=int(rng.integers(1 << 30))):
                        if self.satisfies(G):
                            return nx.convert_node_labels_to_integers(G)
                except Exception:
                    pass
            p = float(rng.uniform(0.1, 0.8))
            G = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
            if self.satisfies(G):
                return G
        return self._repair(n, rng)

    def defect(self, G: nx.Graph) -> int:
        """Total distance from the conjunction; 0 exactly when it holds."""
        return sum(DEFECTS[c](G) for c in self.classes)

    # Classes with a move that provably preserves them. When one of these is in
    # the conjunction it acts as the *carrier*: the descent walks with its move,
    # so that class stays satisfied for free and only the rest has to be
    # repaired. This is what makes the frequent conjunctions reachable —
    # `tree & cograph` is the star, and walking tree-moves down the induced-P4
    # count finds it, where blind flips have to rediscover treeness at every
    # step and stall on the plateau.
    _CARRIERS = ("tree", "cubic", "regular", "bipartite")

    def _repair(self, n: int, rng) -> Optional[nx.Graph]:
        """Hill-climb onto the conjunction when no generator lands on it.

        The frequent hypotheses are conjunctions — `tree & cograph` heads the
        survivor list — and no single generator produces one: a random tree is
        almost never a cograph, a random cograph is almost never a tree. Their
        intersection is not empty, though, so descending on the summed defect
        finds it where sampling from either class alone never would.

        Bounded in wall-clock: the cograph and claw-free defects count induced
        4-subsets, and this runs inside a searcher that has 15 seconds for the
        whole conjecture.
        """
        deadline = time.time() + self.repair_time_s
        carrier = next((c for c in self._CARRIERS if c in self.active), None)
        move = (self._carrier_move(carrier) if carrier else None) or \
            (lambda G, r: _blind_flip(G, r, 1))
        for G in self._repair_seeds(n, rng, carrier):
            score = self.defect(G)
            for step in range(60 * n):
                if score == 0:
                    return G
                if (step & 15) == 0 and time.time() > deadline:
                    return None
                H = move(G, rng)
                if H is None:
                    continue
                sh = self.defect(H)
                if sh <= score:                  # plateau moves allowed: the
                    G, score = H, sh             # defect is coarse and flat
            if time.time() > deadline:
                return None
        return None

    @staticmethod
    def _carrier_move(carrier: str):
        if carrier == "tree":
            return _tree_move
        if carrier in ("cubic", "regular"):
            return _degree_preserving_move
        return None

    def _repair_seeds(self, n: int, rng, carrier: Optional[str] = None):
        """Starting points for the repair descent, best-informed first.

        A graph already satisfying the carrier class is the seed that matters:
        the carrier move keeps it satisfied, so the descent only has to work on
        what is left. Seeds for the other classes and plain Erdős–Rényi follow
        as fallbacks for a conjunction with no carrier.
        """
        from pipeline.random_models import sample_graphs

        order = ([carrier] if carrier else []) + \
            [c for c in self.active if c != carrier]
        for cls in order:
            build = _CONSTRUCTORS.get(cls)
            if build is not None:
                for _ in range(3):
                    try:
                        yield build(n, rng)
                    except Exception:
                        break
            for _ in range(3):
                try:
                    for G in sample_graphs(cls, orders=(n,), per=2,
                                           seed=int(rng.integers(1 << 30))):
                        yield nx.convert_node_labels_to_integers(G)
                except Exception:
                    break
        if carrier is None:
            for _ in range(max(4, self.max_tries // 8)):
                yield nx.gnp_random_graph(n, float(rng.uniform(0.1, 0.6)),
                                          seed=int(rng.integers(1 << 30)))

    # ---------------------------------------------------------------- pairs --
    #
    # A *static* pair restriction is only sound for a class that is literally a
    # restriction on which vertex pairs may be edges — one where toggling any
    # subset of the allowed pairs is guaranteed to stay in the class. Bipartite
    # is the archetype: fix a 2-colouring and every cross pair is free.
    #
    # Most classes are not of this kind. `cubic` and `regular` constrain
    # degrees, `connected` constrains the whole edge set jointly, `claw_free`
    # and `chordal` forbid induced subgraphs. For those a static mask would be
    # either unsound or so restrictive it would cut out the interesting members,
    # so `allowed_pairs` returns None and the searchers use the moves below.
    #
    # `triangle_free` and `K_4_free` are listed as compatible because bipartite
    # implies both, so restricting to cross pairs cannot leave those classes.
    # They are not sufficient on their own: restricting a triangle-free search
    # to the bipartite graphs would throw away C5 and the Petersen graph, which
    # is exactly the kind of witness this search exists to find.
    _EDGE_RESTRICTED_WITH = {"bipartite", "triangle_free", "K_4_free"}

    def canonical_parts(self, n: int) -> Tuple[List[int], List[int]]:
        """The bipartition every bipartite-aware component agrees on.

        Starts, moves, the cross-pair set and the RL action mask must all use
        the *same* 2-colouring: a move is class-preserving only relative to a
        fixed colouring, and letting each component pick its own would silently
        lose the guarantee.
        """
        half = (n + 1) // 2
        return list(range(half)), list(range(half, n))

    def allowed_pairs(self, n: int) -> Optional[List[Tuple[int, int]]]:
        """Pairs the sampling searchers may toggle freely, or None.

        None means "this class is not an edge-set restriction" — the caller must
        fall back to the neighbourhood moves rather than sample a pair subset.
        """
        if not self.active or "bipartite" not in self.active:
            return None
        if any(c not in self._EDGE_RESTRICTED_WITH for c in self.active):
            return None
        A, B = self.canonical_parts(n)
        return [(u, v) for u in A for v in B]

    # ----------------------------------------------------------- projection --
    def project(self, G: nx.Graph, rng, budget: int = 60) -> Optional[nx.Graph]:
        """Move an arbitrary graph onto the class, or None within `budget` steps.

        This is what a *sampling* searcher needs. Cross-entropy draws each edge
        independently, so for a structural hypothesis nearly every sample it
        draws is outside the class and scores -inf — measured, 3,098 of 4,803 —
        and no pair mask can help, because only `bipartite` is an edge-set
        restriction. Projecting the sample instead lets the searcher keep
        learning over its own edge distribution while every graph it *evaluates*
        is a member of the class.

        Deliberately cheap and allowed to fail: it descends on the defect using
        blind flips, and the cost has to stay well under the graphcalc battery
        evaluation it is feeding, or it would buy in-class samples with the
        budget that was going to be spent testing them.
        """
        if not self.active:
            return G
        score = self.defect(G)
        for _ in range(budget):
            if score == 0:
                return G
            H = _blind_flip(G, rng, 1)
            sh = self.defect(H)
            if sh <= score:
                G, score = H, sh
        return G if score == 0 else None

    # ----------------------------------------------------------- neighbours --
    def neighbor(self, G: nx.Graph, rng, k: int = 1) -> nx.Graph:
        """A k-step move that stays in the class where the class allows it.

        Returns G unchanged when no in-class move was found within the try
        budget. That is the honest outcome for a class this move set cannot
        walk — the searcher sees no improvement, rather than being handed an
        out-of-class graph that scores -inf and teaches it nothing.
        """
        if not self.active:
            return _blind_flip(G, rng, k)
        H = G
        for _ in range(k):
            H = self._one_step(H, rng)
        return H

    def _one_step(self, G: nx.Graph, rng) -> nx.Graph:
        act = set(self.active)
        if "tree" in act:
            H = _tree_move(G, rng)
            if H is not None and self.satisfies(H):
                return H
        if act & {"regular", "cubic"}:
            H = _degree_preserving_move(G, rng)
            if H is not None and self.satisfies(H):
                return H
        if "bipartite" in act:
            part = self.canonical_parts(G.number_of_nodes())
            for _ in range(self.max_tries):
                H = _flip_across(G, part, rng)
                if H is not None and self.satisfies(H):
                    return H
        for _ in range(self.max_tries):                       # rejection
            H = _blind_flip(G, rng, 1)
            if self.satisfies(H):
                return H
        return G


# ----------------------------------------------------------- constructors --
def _random_cograph(n: int, rng) -> nx.Graph:
    """Build a cograph directly from a random cotree.

    Rejection sampling cannot reach this class: cographs are a vanishing
    fraction of graphs on 10 vertices, so an Erdős–Rényi sampler effectively
    never produces one. Building unions and joins bottom-up produces one by
    construction, which is the definition of the class.
    """
    parts = [nx.empty_graph(1)]
    while sum(g.number_of_nodes() for g in parts) < n:
        parts.append(nx.empty_graph(1))
    while len(parts) > 1:
        i = int(rng.integers(len(parts)))
        A = parts.pop(i)
        j = int(rng.integers(len(parts)))
        B = parts.pop(j)
        A = nx.convert_node_labels_to_integers(A)
        B = nx.convert_node_labels_to_integers(B, first_label=A.number_of_nodes())
        H = nx.union(A, B)
        if rng.random() < 0.5:                                   # join
            H.add_edges_from((u, v) for u in A for v in B)
        parts.append(H)
    return nx.convert_node_labels_to_integers(parts[0])


def _random_chordal(n: int, rng) -> nx.Graph:
    """Build a chordal graph by repeatedly adding a simplicial vertex.

    A graph is chordal exactly when it has a perfect elimination ordering, so
    attaching each new vertex to a clique of the graph built so far produces one
    by construction and gives the ordering for free. As with cographs,
    rejection sampling does not reach this class at useful orders.
    """
    G = nx.Graph()
    G.add_node(0)
    for v in range(1, n):
        cliques = list(nx.find_cliques(G))
        C = list(cliques[int(rng.integers(len(cliques)))])
        k = 1 + int(rng.integers(len(C)))
        rng.shuffle(C)
        G.add_node(v)
        G.add_edges_from((v, u) for u in C[:k])
    return G


# Classes a rejection sampler cannot reach at useful orders, built directly.
_CONSTRUCTORS: Dict[str, Callable[[int, object], nx.Graph]] = {
    "cograph": _random_cograph,
    "chordal": _random_chordal,
}


# ------------------------------------------------------------------ moves --
def _blind_flip(G: nx.Graph, rng, k: int = 1) -> nx.Graph:
    H = G.copy()
    nodes = list(H.nodes())
    if len(nodes) < 2:
        return H
    for _ in range(k):
        u, v = rng.choice(nodes, size=2, replace=False)
        u, v = int(u), int(v)
        H.remove_edge(u, v) if H.has_edge(u, v) else H.add_edge(u, v)
    return H


def _flip_across(G: nx.Graph, part, rng) -> Optional[nx.Graph]:
    """Toggle one pair crossing the fixed bipartition — never creates an odd cycle."""
    A, B = sorted(part[0]), sorted(part[1])
    if not A or not B:
        return None
    u = int(A[int(rng.integers(len(A)))])
    v = int(B[int(rng.integers(len(B)))])
    H = G.copy()
    H.remove_edge(u, v) if H.has_edge(u, v) else H.add_edge(u, v)
    return H


def _tree_move(G: nx.Graph, rng) -> Optional[nx.Graph]:
    """Remove an edge and reconnect the two components — a tree stays a tree."""
    edges = list(G.edges())
    if not edges:
        return None
    u, v = edges[int(rng.integers(len(edges)))]
    H = G.copy()
    H.remove_edge(u, v)
    comps = list(nx.connected_components(H))
    if len(comps) != 2:
        return None
    a, b = sorted(comps[0]), sorted(comps[1])
    x = int(a[int(rng.integers(len(a)))])
    y = int(b[int(rng.integers(len(b)))])
    H.add_edge(x, y)
    return H


def _degree_preserving_move(G: nx.Graph, rng) -> Optional[nx.Graph]:
    """Double edge swap: (a,b),(c,d) → (a,d),(c,b). Degrees are unchanged, so a
    regular graph stays regular and a cubic graph stays cubic."""
    if G.number_of_edges() < 2:
        return None
    H = G.copy()
    try:
        nx.double_edge_swap(H, nswap=1, max_tries=100,
                            seed=int(rng.integers(1 << 30)))
    except Exception:
        return None
    return H
