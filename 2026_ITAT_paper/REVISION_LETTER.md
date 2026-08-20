# Letter to the editors

## Response to Reviewers — Submission 40

**AutoGraphForge: Towards Automated Graph Theory Discovery**

Dear Editors,

We thank both reviewers for their careful reading. Below is a complete account of
the changes.

---

## A. Changes responding to Reviewer 1

### A1 — Grammar (comment 3)

> "counterexample search algorithms **is** built upon"
> → "counterexample search algorithms **are** built upon"

### A2 — Grammar (comment 4)

> "the proving stage is **implemented in and** sanity-checked but not yet properly evaluated"
> → "the proving stage is **implemented and** sanity-checked but not yet properly evaluated"

### A3 — Sophie necessary conditions, readability (comment 5)

The long clause chain was replaced by short sentences leading with the mechanism:

> "Sophie *necessary conditions* are handled by contraposition. Such a condition
> has the form $A \Rightarrow \neg C$, where $A$ is a numeric predicate and $C$ a
> graph class. It is flagged known whenever the contrapositive
> $C \Rightarrow \neg A$ appears in the table. For instance
> $(\chi > 2) \Rightarrow \neg\textsf{bipartite}$ is recognised as the
> contrapositive of the known bound $\textsf{bipartite} \Rightarrow \chi \le 2$."

### A4 — Qualitative summary of the inspected conjectures (comment 2) — **ADDED**

A 35-line commented-out draft (a hand-classification of the top 50: 22/12/6/5/5)
was **removed** and replaced with a live paragraph and a new table:

| Category | Count |
| --- | ---: |
| Rediscovery recognised by the novelty filter | 49 |
| Subsumed by a stronger survivor | 2 |
| Decorative hypothesis (class does no work) | 1 |
| Promising, universal | 28 |
| Promising, class-conditioned | 20 |
| **Total** | **100** |

The categories are now computed by `tools/audit_sample.py` from the pipeline's own
novelty table, subsumption lattice and support statistics rather than assigned by
hand, so the classification is reproducible from the released artefacts.

We report no "probably false" category and say so explicitly: every item survived
refutation against the full dataset, so we have no evidence of falsity for any of
them, and asserting one would be an unsupported guess.

---

## B. Changes responding to Reviewer 2

### B1 — SAT/CP-SAT for the NP-hard invariants — **ADDED**

Absent from the submitted version; added after the CPU-budget accounting:

> "Since the precomputation dominates, and within it the NP-hard invariants
> dominate, replacing the ILP formulations with a SAT or CP-SAT encoding is the
> single most promising engineering change available to us. Independence,
> domination and zero-forcing all admit natural propositional encodings, and
> modern conflict-driven and local-search solvers are frequently far faster than
> ILP on instances of this size. A cheaper battery is not merely a saving: it
> would let us extend the refutation tiers to larger orders, and so reach
> invariants that are uninformative on the small graphs the present pool is
> concentrated on. We are grateful to a reviewer for this suggestion."

---

## C. Corrections

### C1 — Survivor count (4 sites: abstract, Table 5 caption, §4.1, §5)

The merge step previously removed cross-partition duplicates and nothing else, so
the reported figure still counted conjectures that a witness found in another
partition had already refuted. The merge now applies those witnesses across
partitions before counting (see C3). The arithmetic makes the difference explicit:
$8{,}281 - 346 = 7{,}935$ was correct for the old merge, and
$8{,}281 - 1{,}413 - 346 = 6{,}522$ for the corrected one.

> "$7{,}935$ surviving conjectures" → "$6{,}522$ surviving conjectures"

C2, C3 and C4 follow from this change.

### C2 — Survivor split (§4.1)

The stated split summed to the old total:

> "split into **$3{,}386$** class-conditioned inequalities and **$4{,}549$**
> Sophie **sufficient-**conditions"
> → "split into **$2{,}677$** class-conditioned inequalities and **$3{,}845$**
> Sophie conditions"

$2{,}677 + 3{,}845 = 6{,}522$.

### C3 — Merge description (Table 5 caption)

The whole reduction was attributed to deduplication, which accounts for only 346
of it:

> "the five sum to the $8{,}281$ raw survivors that the merge step
> **deduplicates to $7{,}935$**."
> → "the five sum to the $8{,}281$ raw survivors. The merge step reduces these to
> $6{,}522$ **in two stages: $1{,}413$ are refuted by witnesses found in another
> partition** — each partition grows its own hard seed and never sees the
> others', so a graph that kills a candidate may sit in the wrong shard — **and a
> further $346$ are cross-partition duplicates**."

### C4 — Ranks in §4.2

The touch heuristic previously ignored the class hypothesis, so different
hypotheses over the same body received identical touch counts:

> "the bipartite class (rank $99$ of $7{,}935$ by touch, touch $2{,}053$) and the
> cubic/regular classes (cubic: rank $72$, touch $2{,}181$; regular: rank $100$,
> touch $2{,}053$)"
> → "the bipartite class (rank $91$ by touch, touch $922$) and the regular class
> (rank $177$, touch $589$). Ranks are among the $2{,}677$ survivors that carry a
> recomputed, hypothesis-aware touch count; **the cubic specialisation (rank
> $453$, touch $233$) is now flagged as subsumed by the regular form**, since
> cubic $\subset$ regular"

### C5 — Boolean count (§3.4)

The paragraph said 14 booleans and then 16, without explanation:

> "while the **$16$** booleans act as Sophie hypotheses and as class conditions"
> → "while the **$14$** booleans — **together with two derived order thresholds
> ($n \ge 3$ and $n \ge 4$) that the battery adds precisely so that bounds
> failing only on the smallest graphs become true class-restricted statements** —
> give the $16$ predicates available to Sophie as hypotheses and class
> conditions"

### C6 — Round-one expansion (§4.1)

> "a $\sim\!20$–$28\%$ expansion of $T$" → "a $\sim\!17$–$28\%$ expansion of $T$"

Per partition against $T = 2{,}860$: 27.7, 17.4, 17.3, 19.7, 20.3 %. The smallest
partition adds 494 witnesses, i.e. 17.3 %, so the lower end was overstated.

### C7 — Rediscovery counts (§3.3 and §4.1, two sites)

The manuscript reported 33 rediscoveries alongside a top-100 audit classifying 49
as recognised by the novelty filter (Table 2). 49 cannot sit inside 33. The two
were measured against different versions of the novelty table, and both sites now
say so.

At §4.1, added:

> "This count is the one recorded *during the run*, against the novelty table as
> it then stood. The table has since been extended to its present $559$ entries,
> and re-classifying the survivors against the extended table flags $146$ of the
> $2{,}677$ ranked survivors as known — among them the $49$ of Table 2. The two
> figures are therefore not comparable: $33$ measures what the run itself caught,
> $146$ what the current filter catches."

At §3.3, the forward reference was corrected:

> "(the $33$ flagged rediscoveries of §4.1)"
> → "(the $33$ rediscoveries flagged *during the run*, §4.1; the filter has since
> been extended and now flags $146$ of the ranked survivors)"

---

## D. Other changes

### D1 — Acknowledgments

> Added: "I also thank anonymous reviewers for helpful suggestions and comments."

> Added: "I gratefully acknowledge financial support for this research from the
> Comenius University (Grant No. UK/1020/2026)."

### D2 — Code availability (addresses Reviewer 1, comment 1)

> Added: "The complete list of surviving conjectures is published there as
> `results/survivors_by_touch.txt`."

### D3 — Declaration on Generative AI

Rewritten to the activity-taxonomy form of the CEUR template, naming the tool and
the activities, and disclosing that the same tool was additionally used as a
coding and experimentation assistant.

---

## E. Disclosure: revisions independent of the review

The manuscript also incorporates work completed after submission and unrelated to
the reviewers' comments. Most substantively, the novelty filter was expanded:

> "The table holds **$203$** entries" → "the list holds **$559$** entries"

with an accompanying change in how redundant candidates are treated:

> "the candidate is provably a structural consequence of the tabled theorems and
> is **discarded**"
> → "… and is **flagged as a known rediscovery** — excluded from the set of novel
> survivors, but stored, so it can serve as a soundness check"

and a strengthened soundness condition on the admissible safe lower bounds. We
note these so that the change record is complete.

---

The required edits increased the number of pages slightly. I apologize for this
and hope it does not cause any problems.

Yours sincerely,

Ján Pastorek
