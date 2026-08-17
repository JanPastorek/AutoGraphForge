"""
pipeline/conjecture_lattice.py — reason about survivors using the class lattice.

The generator emits each conjecture against whatever class hypothesis it was
built under, so the survivor set contains the same mathematical claim several
times at different strengths, and contains claims whose hypothesis is doing no
work at all. The subsumption lattice (``novelty.SUPERCLASSES``, imported from
ISGCI) turns both into decidable questions.

Three operations, in increasing order of cost and of what they assume:

``subsumed``
    Pure logic, no data. ``(C_A) ⇒ body`` is redundant when some other survivor
    ``(C_B) ⇒ body`` has a *weaker* hypothesis — every graph satisfying `C_A`
    already satisfies `C_B`. Dropping it loses nothing and keeps the strongest
    form of each claim.

``lift``
    Relax the hypothesis upward through the lattice and re-test the body on the
    refutation pool. This is the safe direction: a weaker hypothesis admits
    *more* graphs, so lifting can never manufacture a vacuous survivor the way
    retreating into a subclass can.

``decorative``
    The body survives with *no* class hypothesis at all. Then the hypothesis was
    never load-bearing, and the conjecture is usually an artifact of the pool's
    bounded size (``(cubic) ⇒ harmonic_index ≤ 29``) rather than a theorem about
    the class.

A lift is evidence, not proof: it inherits every limitation of the pool it was
tested on, so its output is a stronger conjecture to re-refute, never a result.
"""
from __future__ import annotations

import logging
import re
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from pipeline import linear_form
from pipeline.novelty import SUPERCLASSES

logger = logging.getLogger(__name__)

# Matches pipeline/refute_matrix.py, so "still survives" here means the same
# thing it means to the refuter.
TOL = 1e-9

# graphcalc's boolean class columns.
CLASS_COLUMNS = (
    "connected", "bipartite", "chordal", "cubic", "eulerian", "planar",
    "regular", "subcubic", "tree", "K_4_free", "triangle_free", "claw_free",
    "cograph", "nontrivial",
)

NormalisedBody = Tuple[Tuple[Dict[str, int], int], str, Tuple[Dict[str, int], int]]


class Survivor:
    """A class-conditioned survivor, parsed into hypothesis + normalised body."""

    __slots__ = ("statement", "classes", "body", "norm", "touches")

    def __init__(self, statement: str, classes: FrozenSet[str], body: str,
                 norm: NormalisedBody, touches: int = 0):
        self.statement = statement
        self.classes = classes
        self.body = body
        self.norm = norm
        self.touches = touches

    @property
    def body_key(self):
        (lt, lk), rel, (rt, rk) = self.norm
        return (tuple(sorted(lt.items())), lk, rel, tuple(sorted(rt.items())), rk)

    def invariants(self) -> List[str]:
        (lt, _), _, (rt, _) = self.norm
        return list(lt) + list(rt)


def parse_survivors(conjectures: Sequence[dict],
                    class_columns: Sequence[str] = CLASS_COLUMNS) -> List[Survivor]:
    """Class-conditioned survivors with a parseable linear body.

    Statements whose hypothesis mentions an invariant are *necessary
    conditions*, a different shape (see pipeline/lean_export.render_necessary);
    they are skipped here, as are bodies outside the linear grammar.
    """
    known = set(class_columns)
    out: List[Survivor] = []
    for conjecture in conjectures:
        statement = conjecture.get("statement") or ""
        if "⇒" not in statement:
            continue
        condition, body = statement.split("⇒", 1)
        names = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", condition))
        classes = names & known
        if not classes or names - known:
            continue                       # no class, or a necessary condition
        norm = linear_form.normalise(body)
        if norm is None:
            continue
        out.append(Survivor(statement, frozenset(classes), body.strip(), norm,
                            int((conjecture.get("metadata") or {}).get("touches", 0))))
    return out


def implied_classes(classes: FrozenSet[str]) -> FrozenSet[str]:
    """Every class a graph in ``classes`` is guaranteed to belong to."""
    out = set(classes)
    for cls in classes:
        out |= SUPERCLASSES.get(cls, set())
    return frozenset(out)


def weaker(a: FrozenSet[str], b: FrozenSet[str]) -> bool:
    """True when hypothesis ``b`` is weaker than ``a`` — every graph satisfying
    all of ``a`` satisfies all of ``b`` — and the two differ."""
    return a != b and b <= implied_classes(a)


def _simplicity(classes: FrozenSet[str]) -> tuple:
    """Ordering used to pick a representative among *equivalent* hypotheses."""
    return (len(classes), sorted(classes))


def find_subsumed(survivors: Sequence[Survivor]) -> Dict[int, int]:
    """{index of redundant survivor: index of the survivor implying it}.

    Only survivors with the *same* body are compared; a weaker hypothesis over
    the same inequality subsumes the stronger one.

    Hypotheses can be *equivalent* rather than strictly ordered — a tree is
    always planar, so ``tree ∧ planar`` and ``tree`` describe the same graphs and
    each subsumes the other. Dropping both would lose the claim entirely, so one
    representative is kept: the simplest (fewest conjuncts, then alphabetical).
    """
    by_body: Dict[tuple, List[int]] = {}
    for i, s in enumerate(survivors):
        by_body.setdefault(s.body_key, []).append(i)
    subsumed: Dict[int, int] = {}
    for group in by_body.values():
        if len(group) < 2:
            continue
        for i in group:
            for j in group:
                if i == j or not weaker(survivors[i].classes, survivors[j].classes):
                    continue
                if weaker(survivors[j].classes, survivors[i].classes):
                    # equivalent: keep whichever states it more simply
                    if _simplicity(survivors[j].classes) > _simplicity(survivors[i].classes):
                        continue
                subsumed[i] = j
                break
    return subsumed


def generalisations(classes: FrozenSet[str],
                    available: Optional[Sequence[str]] = None) -> List[FrozenSet[str]]:
    """Strictly weaker hypotheses: drop a conjunct, or relax one upward.

    ``available`` restricts targets to classes the pool can actually evaluate;
    a superclass with no column is not testable, so proposing it would be a
    claim we cannot check.
    """
    pool = set(available) if available is not None else None
    out = set()
    for cls in classes:
        if len(classes) > 1:
            out.add(frozenset(classes - {cls}))
        for superclass in SUPERCLASSES.get(cls, set()):
            if pool is None or superclass in pool:
                out.add(frozenset((classes - {cls}) | {superclass}))
    out.discard(classes)
    return sorted((g for g in out if g), key=lambda g: (len(g), sorted(g)))


class PoolEvaluator:
    """Evaluates a normalised body over the cached refutation pool."""

    def __init__(self, frame, class_columns: Sequence[str] = CLASS_COLUMNS):
        import numpy as np
        import pandas as pd

        self._np = np
        self.n_rows = len(frame)
        self.index = frame.index.to_numpy()
        self.classes = {c: frame[c].fillna(False).to_numpy(bool)
                        for c in class_columns if c in frame.columns}
        self.values = {c: pd.to_numeric(frame[c], errors="coerce").to_numpy(float)
                       for c in frame.columns if c not in self.classes}
        self._masks: Dict[FrozenSet[str], object] = {}

    def can_evaluate(self, survivor: Survivor) -> bool:
        return all(name in self.values for name in survivor.invariants())

    def mask(self, classes: FrozenSet[str]):
        if classes not in self._masks:
            m = self._np.ones(self.n_rows, bool)
            for cls in classes:
                column = self.classes.get(cls)
                # An unmodelled class cannot be assumed: treat it as matching
                # nothing, so the hypothesis is never silently widened.
                m &= column if column is not None else self._np.zeros(self.n_rows, bool)
            self._masks[classes] = m
        return self._masks[classes]

    def _rows(self, classes: FrozenSet[str], norm: NormalisedBody):
        """Boolean row mask: satisfies the hypothesis and has every invariant."""
        np = self._np
        (lt, _), _, (rt, _) = norm
        rows = self.mask(classes).copy()
        for name in list(lt) + list(rt):
            column = self.values.get(name)
            if column is None:
                return None
            rows &= ~np.isnan(column)
        return rows

    def _sides(self, norm: NormalisedBody, rows):
        np = self._np
        (lt, lk), _, (rt, rk) = norm
        n = int(rows.sum())
        left = np.full(n, float(lk))
        for name, coefficient in lt.items():
            left = left + coefficient * self.values[name][rows]
        right = np.full(n, float(rk))
        for name, coefficient in rt.items():
            right = right + coefficient * self.values[name][rows]
        return left, right

    def touches(self, classes: FrozenSet[str], norm: NormalisedBody) -> int:
        """Graphs where the bound is *tight* — the two sides are equal.

        The generator's own touch number counts the same thing on the seed, and
        it is the usual measure of how interesting a bound is: a bound met with
        equality by many graphs is sharp rather than slack.

        For an ``=`` conjecture every satisfying graph is trivially tight, so
        the touch count degenerates to the support; rank equalities by support
        instead.
        """
        rows = self._rows(classes, norm)
        if rows is None or not rows.any():
            return 0
        left, right = self._sides(norm, rows)
        return int((self._np.abs(left - right) <= TOL).sum())

    def _violations(self, rows, norm: NormalisedBody):
        """Boolean array over ``rows`` marking where the relation fails."""
        np = self._np
        rel = norm[1]
        left, right = self._sides(norm, rows)
        if rel == "≤":
            return left > right + TOL
        if rel == "<":
            return left >= right - TOL
        return np.abs(left - right) > TOL

    def first_violation(self, classes: FrozenSet[str],
                        norm: NormalisedBody) -> Optional[str]:
        """Identifier of a graph in the class that violates the body, else None."""
        rows = self._rows(classes, norm)
        if rows is None or not rows.any():
            return None
        bad = self._violations(rows, norm)
        if not bad.any():
            return None
        return str(self.index[rows][bad][0])

    def first_class_violation(self, norm: NormalisedBody,
                              clauses: Sequence[Tuple[bool, str]]) -> Optional[str]:
        """For ``(inequality) ⇒ classes``: a graph meeting the inequality that
        is not in the class, else None."""
        np = self._np
        rows = self._rows(frozenset(), norm)
        if rows is None or not rows.any():
            return None
        holds = ~self._violations(rows, norm)
        conclusion = np.ones(int(rows.sum()), bool)
        for negated, cls in clauses:
            column = self.classes.get(cls)
            if column is None:
                return None
            member = column[rows]
            conclusion &= ~member if negated else member
        bad = holds & ~conclusion
        if not bad.any():
            return None
        return str(self.index[rows][bad][0])

    def survives(self, classes: FrozenSet[str],
                 norm: NormalisedBody) -> Tuple[Optional[bool], int]:
        """(survives, support). ``survives`` is None when nothing is testable —
        no graph satisfies the hypothesis, or every such row is missing a column.
        """
        rows = self._rows(classes, norm)
        if rows is None:
            return None, 0
        support = int(rows.sum())
        if not support:
            return None, 0
        return (not self._violations(rows, norm).any()), support


def lift(survivor: Survivor, evaluator: PoolEvaluator
         ) -> Optional[Tuple[FrozenSet[str], int]]:
    """The weakest hypothesis the body still survives under, or None.

    "Weakest" is measured by support — how many pool graphs the relaxed
    hypothesis admits — because that is what the claim is actually tested
    against.
    """
    best: Optional[Tuple[FrozenSet[str], int]] = None
    for candidate in generalisations(survivor.classes, evaluator.classes):
        ok, support = evaluator.survives(candidate, survivor.norm)
        if ok and (best is None or support > best[1]):
            best = (candidate, support)
    return best


def is_decorative(survivor: Survivor, evaluator: PoolEvaluator) -> Optional[bool]:
    """True when the body survives on the whole pool, hypothesis and all.

    This is the honest form of the check: not "the hypothesis is nearly always
    true on this pool" (a threshold), but "removing the hypothesis entirely
    costs nothing" (a fact about the data).
    """
    ok, _ = evaluator.survives(frozenset(), survivor.norm)
    return ok


def find_refuted(conjectures: Sequence[dict], evaluator: "PoolEvaluator",
                 class_columns: Sequence[str] = CLASS_COLUMNS
                 ) -> Tuple[Dict[int, str], int]:
    """({index: refuting graph}, number that could not be checked).

    Covers both survivor shapes:

      ``(classes) ⇒ inequality``  — refuted by a graph in the class that
      violates the inequality.
      ``(inequality) ⇒ classes``  — refuted by a graph satisfying the
      inequality that is not in the class.

    Written for the cross-shard merge: each shard grows its own witness set, so
    a graph one shard found hard is evidence against every shard's survivors,
    but nothing re-checks that when the shards are combined.
    """
    known = set(class_columns)
    refuted: Dict[int, str] = {}
    unchecked = 0
    for index, conjecture in enumerate(conjectures):
        statement = conjecture.get("statement") or ""
        if "⇒" not in statement:
            norm = linear_form.normalise(statement)
            if norm is None:
                unchecked += 1
                continue
            witness = evaluator.first_violation(frozenset(), norm)
            if witness is not None:
                refuted[index] = witness
            continue
        condition, consequent = statement.split("⇒", 1)
        names = set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", condition))
        if names and names <= known:                     # (classes) ⇒ inequality
            norm = linear_form.normalise(consequent)
            if norm is None or not names <= set(evaluator.classes):
                unchecked += 1
                continue
            witness = evaluator.first_violation(frozenset(names), norm)
        else:                                            # (inequality) ⇒ classes
            clauses = linear_form.parse_class_conclusion(consequent)
            norm = linear_form.normalise(condition)
            if (norm is None or not clauses
                    or any(c not in evaluator.classes for _, c in clauses)):
                unchecked += 1
                continue
            witness = evaluator.first_class_violation(norm, clauses)
        if witness is None and norm is None:
            unchecked += 1
        elif witness is not None:
            refuted[index] = witness
    return refuted, unchecked


def load_pool(paths: Sequence[str]):
    """Concatenate cached battery parquets into one corpus, deduped by graph.

    The battery caches are indexed by graph6, and they overlap heavily — the
    refutation tiers are copied per shard, and every seed contains the graphs it
    started from. Concatenating without deduplication would count the same graph
    many times and inflate every support figure, so the index is preserved and
    duplicates dropped.
    """
    import pandas as pd

    frames = []
    for path in paths:
        try:
            frames.append(pd.read_parquet(path))
        except Exception as e:                             # pragma: no cover
            logger.warning("[lattice] could not read %s: %s", path, e)
    if not frames:
        return None
    corpus = pd.concat(frames)
    if corpus.index.is_unique:
        return corpus
    # Duplicated graphs are *merged*, not arbitrarily picked: the same graph
    # often has a more complete row in one cache than another, because an
    # invariant that timed out in one run computed in the next.
    #
    # "First non-null per column" is not enough, because a *boolean* column
    # cannot hold NaN — pandas stores an uncomputed class flag as `False`,
    # which is indistinguishable from a genuine negative. Taking the first
    # non-null then lets a placeholder `False` from a row that computed nothing
    # override a real `True` elsewhere: the graph `A?` (2 vertices, no edges)
    # was recorded `nontrivial=False` with `order=NaN`, and so was excluded
    # from every hypothesis it should have satisfied.
    #
    # Rows are therefore ranked by completeness first, so the row that actually
    # computed something wins the whole group, and only genuinely missing cells
    # are filled in from the rest.
    duplicated = corpus.index.duplicated(keep=False)
    dupes = corpus[duplicated]
    completeness = dupes.notna().sum(axis=1)
    ordered = dupes.iloc[(-completeness.to_numpy()).argsort(kind="stable")]
    merged = ordered.groupby(level=0).first()
    return pd.concat([corpus[~duplicated], merged])
