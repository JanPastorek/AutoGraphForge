# Teamwork Project Prompt — Draft

> Status: Ready for launch — awaiting user approval
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: Standard proof pipeline

Settle the graph-theory conjecture defined by `Candidate` (`(nontrivial) ⇒ radius ≤ total_domination_number`) in Lean 4 by either proving or refuting it with a kernel-checked proof.

Working directory: /mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_2a2555cc
Integrity mode: development

## Requirements

### R1. Conjecture Settlement
Settle the conjecture defined by `Candidate` in [Challenge_2a2555cc.lean](file:///mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_2a2555cc/Challenge_2a2555cc.lean) by replacing the `sorry` in exactly ONE of:
- `theorem prove_2a2555cc : Candidate`
- `theorem refute_2a2555cc : ¬ Candidate`
The other theorem must remain untouched with its original `sorry`.

### R2. Sandbox and Formal Verification Rules
- Do not modify anything above line 15 in `Challenge_2a2555cc.lean` (imports, options, `Candidate` definition).
- All helper lemmas/definitions must be placed after `Candidate` as top-level `theorem`, `lemma`, or `def`.
- No `sorry`, `admit`, `axiom`, `native_decide`, `namespace`, `section`, `variable`, `notation`, `macro`, `syntax`, `IO`, or metaprogramming.
- The elaborated proof must only depend on allowed axioms: `propext`, `Classical.choice`, and `Quot.sound`.
- Invariants are referenced from `reference/GraphInvariantsComputable.lean` (namespace `GraphCalc`).
- Validation must be executed using `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_2a2555cc.lean`. Do not run `lake`.

### R3. Final Summary Report
Create a `REPORT.md` file in the working directory documenting:
- The direction settled (`prove` or `refute`)
- The key mathematical rationale or counterexample structure
- The final output from `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_2a2555cc.lean`

## Acceptance Criteria

### Lean Verification
- [ ] `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_2a2555cc.lean` executes and outputs `LINT: ok`.
- [ ] Exactly one target theorem (`prove_2a2555cc` or `refute_2a2555cc`) lists only allowed axioms (`propext`, `Classical.choice`, `Quot.sound`) with no `sorryAx`.
- [ ] The untouched theorem retains `sorryAx` among its axioms.
- [ ] No prohibited keywords, axioms, or metaprogramming constructs appear in the solution file.

### Deliverables
- [ ] `REPORT.md` is present in the working directory and documents the direction settled, mathematical approach, and the complete `check.sh` output.

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*
