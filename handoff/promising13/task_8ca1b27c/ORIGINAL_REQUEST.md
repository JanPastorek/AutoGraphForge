# Original User Request

## Initial Request — 2026-09-11T14:33:50Z

Settle the open graph-theory conjecture in Lean 4 — prove or refute `Candidate: (nontrivial) ⇒ 2 ≤ sub_total_domination_number` — with a kernel-checked proof.

Working directory: /mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_8ca1b27c
Integrity mode: development

## Requirements

### R1. Settle Conjecture in Lean 4
Replace the `sorry` in exactly one of `theorem prove_8ca1b27c : Candidate` or `theorem refute_8ca1b27c : ¬ Candidate` in Challenge_8ca1b27c.lean, editing the file in place. Leave the other theorem untouched with its `sorry`.

The invariants are defined in reference/GraphInvariantsComputable.lean (namespace GraphCalc). To find Mathlib lemmas, put #check, example or exact? in a scratch .lean file here and run the checker on it. Because the invariants are computable, decide evaluates them on an explicit small graph built with GraphCalc.ofEdges n [(0, 1), ...] — so a refutation is usually a counterexample graph plus decide, while a proof needs a general argument about all finite graphs.

### R2. Adhere to Formal Verification Constraints
Check Lean files with: /mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh <file.lean>
Ensure the Lean file complies with all hard verification rules:
- Do not modify any code above the first theorem line (imports, options, Candidate).
- Place all helper lemmas after Candidate as top-level declarations.
- Keep the chosen theorem's name and header exactly; leave the other theorem untouched, with its sorry.
- No sorry, admit, axiom, native_decide, namespace, section, variable, notation, macro, syntax, IO, or metaprogramming. Only propext, Classical.choice and Quot.sound may appear among the axioms.
- The environment is sandboxed: the working directory is writable, but the Lean project and Mathlib are read-only. Never run lake. Scratch files may be created in this directory.

### R3. Produce Verification Report
When finished, write REPORT.md in the working directory documenting the settled direction (proven or refuted), the core mathematical idea/argument, and the complete checker output.

## Acceptance Criteria

### Verification & Correctness
- [ ] /mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_8ca1b27c.lean executes cleanly with exit code 0.
- [ ] Lean kernel reports only allowed axioms (propext, Classical.choice, Quot.sound) for the settled theorem.
- [ ] Exactly one target theorem is completed; the other theorem retains its unmodified sorry.
- [ ] REPORT.md exists and details the outcome, mathematical reasoning, and checker results.
