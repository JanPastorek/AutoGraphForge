# Teamwork Project Prompt — Draft

> Status: Completed — Victory Confirmed
> Goal: Multi-agent execution completed successfully
> Requested team: Standard proof pipeline

Settle the open graph-theory conjecture in Lean 4 — prove or refute `Candidate: (nontrivial) ⇒ 2 ≤ sub_total_domination_number` — with a kernel-checked proof.

Working directory: /mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_8ca1b27c
Integrity mode: development

## Requirements

### R1. Settle Conjecture in Lean 4
Replace the `sorry` in exactly one of `theorem prove_8ca1b27c : Candidate` or `theorem refute_8ca1b27c : ¬ Candidate` in [Challenge_8ca1b27c.lean](file:///mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_8ca1b27c/Challenge_8ca1b27c.lean), editing the file in place. Leave the other theorem untouched with its `sorry`.

### R2. Adhere to Formal Verification Constraints
Ensure the Lean file complies with all hard verification rules:
- Do not modify any code above the first `theorem` line (imports, options, `Candidate`).
- Place all helper lemmas after `Candidate` as top-level declarations.
- No `sorry`, `admit`, `axiom`, `native_decide`, `namespace`, `section`, `variable`, `notation`, `macro`, `syntax`, `IO`, or metaprogramming.
- The environment is sandboxed: the working directory is writable, but the Lean project and Mathlib are read-only. Never run `lake`.

### R3. Produce Verification Report
When finished, write `REPORT.md` in the working directory documenting the settled direction (proven or refuted), the core mathematical idea/argument, and the complete checker output.

## Acceptance Criteria

### Verification & Correctness
- [x] `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_8ca1b27c.lean` executes cleanly with exit code 0.
- [x] Lean kernel reports only allowed axioms (`propext`, `Classical.choice`, `Quot.sound`) for the settled theorem.
- [x] Exactly one target theorem is completed; the other theorem retains its unmodified `sorry`.
- [x] [REPORT.md](file:///mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_8ca1b27c/REPORT.md) exists and details the outcome, mathematical reasoning, and checker results.

---
*Execution complete. All criteria verified by independent Victory Auditor.*
