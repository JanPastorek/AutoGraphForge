# Teamwork Project Prompt — Draft

> Status: Launched
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: Standard proof pipeline

Settle an open graph-theory conjecture in Lean 4 — prove or refute `(nontrivial) ⇒ order ≤ 2 * edge_cover_number` with a kernel-checked proof.

Working directory: /mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_a23c41a0
Integrity mode: development

## Requirements

### R1. Formally Settle Candidate Conjecture
Replace the `sorry` in exactly one of `theorem prove_a23c41a0 : Candidate` or `theorem refute_a23c41a0 : ¬ Candidate` in `Challenge_a23c41a0.lean` in place. Leave the other theorem untouched with its `sorry`.

### R2. Lean Submission and Sandbox Constraints
- Maintain strict integrity: change nothing above the first `theorem` line (imports, options, `Candidate`).
- Helper lemmas must be placed after `Candidate` as top-level definitions/lemmas.
- No `sorry`, `admit`, `axiom`, `native_decide`, `namespace`, `section`, `variable`, `notation`, `macro`, `syntax`, `IO`, or metaprogramming.
- Allowed axioms in elaborated results are strictly limited to `propext`, `Classical.choice`, and/or `Quot.sound`.
- Sandbox rules: do not run `lake`; Mathlib and the parent Lean project are read-only.

### R3. Summary Report
Produce `REPORT.md` in the working directory documenting the settled direction (proven or refuted), the key mathematical idea, and the complete output from the verification script.

## Verification Resources
- Verification script: `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_a23c41a0.lean`
- Computable invariant reference: `reference/GraphInvariantsComputable.lean`

## Acceptance Criteria

### Verification & Compliance
- [ ] `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_a23c41a0.lean` exits with code 0.
- [ ] Axiom audit output shows only `propext`, `Classical.choice`, and/or `Quot.sound` for the completed theorem.
- [ ] Exactly one target theorem has its `sorry` eliminated; the unproven theorem retains its `sorry`.
- [ ] `REPORT.md` is present in the working directory with the required sections and execution output.
