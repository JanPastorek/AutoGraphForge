# Peer Review & Improvement Roadmap

**Paper:** *Automated Conjecturing-Refuting-Formalizing-Proving Loop Pipeline for Graph Theory*
**Venue:** ITAT 2026 (CEUR-WS proceedings) · **Type:** systems / experience report, work-in-progress
**Reviewed:** 2026-06-19 · **Mode:** multi-perspective (EIC + methodology + domain + perspective + devil's advocate)

## Editorial recommendation: **Major revision**

The paper is a genuinely interesting, well-positioned systems report. Its core intellectual move — treating "rejecting one's own discoveries" as the load-bearing contribution rather than an embarrassment — is honest and well argued, and the related-work survey is unusually thorough. But it is not yet camera-ready: the Conclusion is empty, the abstract overclaims relative to the body, several internal numbers disagree, five citations are undefined, and the prose has recurring grammar breaks. None of these are deep; all are fixable in a focused revision.

---

## A. Blocking issues (must fix before acceptance)

1. **Empty Conclusion.** §Conclusion (l.710) has no content. A systems/WIP paper needs a conclusion stating what was achieved, the honest negative result, and concrete next steps (closing the loop to certified Lean proofs). ~1 paragraph.

2. **Five undefined citations** — these compile as `[?]`. The keys `blanchette2020hammer`, `gonthier2013formal`, `li2021graph`, `li2022graph`, `li2023graph` (all in the autoformalization sentence, l.114) are **absent from `sample-ceur.bib`**. Either add the entries or remove the citations. (Confirmed by diffing cite keys against the bib.)

3. **Abstract overclaims vs. body.** The abstract states *"the first successful formalization of a nontrivial graph-theoretic inequality in Lean."* The body (§4.3, l.554–558) only claims autoformalization into **Lean statement skeletons** that "require subsequent elaboration by the Lean kernel, **not a certified proof**." A formalized *statement* is not a formalized (proved) *inequality*. Reconcile these: either downgrade the abstract to "autoformalized statement skeletons," or, if a proof actually closes, document it. As written this is the single most exposed claim in the paper and a reviewer will target it.

4. **Numerical inconsistencies.** Fix so every figure traces to one source:
   - Census: **273,192** (l.289, correct — matches OEIS A001349 summed over n=2..9) vs **273,191** (l.680). Off by one.
   - Corpus: **348,207** (l.122, l.294) vs **347,855** (l.497, "holds on all 347,855 graphs"). If the gap is because κ/λ are blank on some graphs, say so explicitly; otherwise reconcile.

5. **"Four failures" but five are listed.** l.100 says "four possible failures," then enumerates First…Fifth (l.101–108). Change to "five," or merge two.

6. **Dangling contribution.** Contribution 5 (l.140–145) ends mid-thought: *"...the classical record. / pipeline produced and how verification rejected it."* A line was dropped. Rewrite as a complete sentence.

---

## B. Major issues (strongly recommended)

7. **Inconsistent system name.** The system is called *autograph* (l.116), but the released artefact is *graphconj* / `\textsf{graphconj}` (l.297, 317, 733). Pick one name and use it throughout; if `autograph` is the project and `graphconj` the package, say that once explicitly.

8. **"Closed loop" is claimed but not demonstrated.** Title and intro promise a *closed* conjecture→refute→formalize→prove loop, but formalization stops at unverified Lean skeletons and no proof is closed back into the knowledge base. Either soften to "pipeline toward a closed loop" or show one end-to-end traversal. This is the gap a devil's-advocate reviewer will press hardest.

9. **Figure 1's "Devil's Advocate filter" is undefined in the text.** The figure (l.607) and caption introduce a dashed "Devil's Advocate Filter (Assume True)" path that constrains future generation — but no section defines this mechanism. Either define it in §4.4 or remove it from the figure to avoid an orphan component. (Also: the caption is the only place "assume surviving conjectures true to constrain generation" appears — a non-trivial design choice worth a sentence in the body.)

10. **"Two independent expert reviews" (l.694) are asserted, not described.** Who, what protocol, what did they assess? Either give one sentence of provenance or reframe as "manual inspection."

11. **Reproducibility claim lacks an artefact link.** The footnote (l.25) and appendix promise reproducible artefacts, but no repository URL / DOI / archive is given. For a paper whose central virtue is trust and reproducibility, an (anonymized, if needed) link is expected.

12. **Reed's conjecture is stated in a relaxed form.** Table 2 (l.663) gives Reed as `2χ ≤ ω+Δ+2`. Reed's actual conjecture is `χ ≤ ⌈(ω+Δ+1)/2⌉`; the linear form drops the ceiling and is strictly weaker, so "holds (tight)" is testing a relaxation. State that you test the linearized form, or test the ceiling form.

---

## C. Minor issues / polish

13. **Placeholder front matter.** Author "Author One," `author.one@example.org`, ORCID all-zeros, "Affiliation, City, Country" (l.28–33). Fill before camera-ready.

14. **Section title collision.** §3 "Formalizing the problem of conjecturing" uses "formalizing" in the *mathematical-definition* sense, while the rest of the paper uses it in the *Lean* sense. Consider "Problem formulation" or "Conjecturing as theory selection" to avoid confusion.

15. **Weak "monster conjecture" example.** `α ≤ 0.07 n²` (l.105) is extremely loose (α can be ≈ n), so it doesn't illustrate overfitting-by-accumulating-terms. Use an example with many additive terms/constants.

16. **One uncited bib entry:** `jacobs2020graph` is in the bib but never cited — cite or drop.

17. **Recurring grammar/typo fixes:** "altough" (l.114); "is not build from scratch" → built (l.150); "such deep cross-entropy" → "such as" (l.138, 150); "hypothetised" → hypothesised (l.82); "authoritative data source" → sources (l.723); "which are attempted by automated theorem provers" (l.63, broken clause). A full proofreading pass is warranted — the density of these undercuts the paper's trust theme.

18. **Stale log.** The committed `itat_pipeline.log` shows *all* citations undefined (the `.bbl` wasn't regenerated in the last compile). Run `bibtex` + two `pdflatex` passes and confirm zero undefined references before submitting.

---

## D. What is working well (keep)

- The **negative-result framing** (§5.3, Discussion) is the paper's strongest asset — honest, well-defended, and backed by the surveys. Don't dilute it.
- **Validation by rediscovery**: independently recovering the Aouchiche–Hansen counterexample to the published optimal score (5 decimals) and recovering Sumner's theorem are convincing correctness signals.
- The **theory-selection / rolling-adversarial-audit** framing (§3) gives the engineering a clean conceptual spine.
- The **reproducibility appendix** (file-by-file mapping, canonical-backend + cross-validate gate) is exemplary for a systems paper.

---

## Suggested revision order (highest leverage first)

1. Fix the 5 undefined citations + rerun bibtex (issues 2, 18) — *15 min, unblocks compile.*
2. Reconcile abstract vs. body on formalization + soften "closed loop" (issues 3, 8) — *core credibility.*
3. Write the Conclusion (issue 1).
4. Fix all numeric inconsistencies and the "four/five" + dangling contribution (issues 4, 5, 6).
5. Resolve system naming and define/remove the Devil's Advocate filter (issues 7, 9).
6. Full proofreading pass + front matter + artefact link (issues 11, 13, 17).
