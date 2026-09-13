# Teamwork Project Prompt — Draft

> Status: Completed
> Goal: Settle Lean 4 graph theory conjecture Challenge_1facfd37
> Requested team: Proof pipeline

Settle open graph-theory conjecture `Candidate` (`(nontrivial) ⇒ independence_number ≤ edge_cover_number`) in Lean 4.

Working directory: /mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_1facfd37
Integrity mode: benchmark

## Requirements

### R1. Formal Resolution
Settle the conjecture by replacing `sorry` in `prove_1facfd37` or `refute_1facfd37` in `Challenge_1facfd37.lean` without modifying lines above `Candidate`.

### R2. Kernel Verification
Verify the result using the Lean 4 checker script `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_1facfd37.lean` with only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).

### R3. Final Report
Provide `REPORT.md` describing the direction settled, key mathematical idea, and final checker output.

## Acceptance Criteria

### Lean Verification
- [x] Lean 4 elaboration succeeds with code 0
- [x] No `sorryAx` in `prove_1facfd37`
- [x] Only standard axioms used
- [x] REPORT.md written
