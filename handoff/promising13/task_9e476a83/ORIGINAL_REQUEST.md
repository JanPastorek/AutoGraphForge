# Original User Request

## 2026-09-11T14:45:23Z

# Teamwork Project Prompt

Settle one open graph-theory conjecture in Lean 4 — PROVE it or REFUTE it — with a kernel-checked proof.

The file Challenge_9e476a83.lean in the current directory defines `Candidate`, the conjecture
    (nontrivial) ⇒ 2 ≤ total_domination_number
Replace the `sorry` in exactly ONE of `theorem prove_9e476a83 : Candidate` or `theorem refute_9e476a83 : ¬ Candidate`, editing that file in place.

Working directory: /mnt/home/japake298/project/GraphConjecturing/handoff/promising13/task_9e476a83
Integrity mode: development

The invariants are defined in reference/GraphInvariantsComputable.lean (namespace GraphCalc) — a copy of what Lean actually uses; read it. To find Mathlib lemmas, put #check, example or exact? in a scratch .lean file here and run the checker on it. Because the invariants are computable, `decide` evaluates them on an explicit small graph built with `GraphCalc.ofEdges n [(0, 1), ...]` — so a refutation is usually a counterexample graph plus `decide`, while a proof needs a general argument about all finite graphs.

Check Lean files with: /mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh <file.lean>
It screens the file, elaborates it against the real definitions, and prints each theorem's axioms. You work inside a sandbox: this directory is writable, the Lean project and Mathlib are read-only, and ordinary shell commands are available. Never run lake. Scratch files may be created in this directory.

## Requirements

### R1. Settle Candidate in Challenge_9e476a83.lean
Replace the `sorry` in exactly ONE of `theorem prove_9e476a83 : Candidate` or `theorem refute_9e476a83 : ¬ Candidate`, editing that file in place. Leave the other theorem untouched with its `sorry`.

### R2. Adhere Strictly to Hard Rules
- Change nothing above the first `theorem` line (imports, options, `Candidate`). Put helper lemmas after `Candidate`, as top-level theorem/lemma/def.
- Keep the chosen theorem's name and header exactly.
- No `sorry`, `admit`, `axiom`, `native_decide`, `namespace`, `section`, `variable`, `notation`, `macro`, `syntax`, `IO`, or metaprogramming. Only `propext`, `Classical.choice`, and `Quot.sound` may appear among the axioms.
- Never run `lake`.

### R3. Generate Report
When finished, write `REPORT.md` in the working directory documenting:
- The direction settled (or that neither was).
- The key mathematical idea.
- The final checker output.

## Acceptance Criteria

### Verification
- [ ] `/mnt/home/japake298/project/GraphConjecturing/tools/antigravity/check.sh Challenge_9e476a83.lean` succeeds with exit code 0.
- [ ] Axiom list for the settled theorem contains only `propext`, `Classical.choice`, and `Quot.sound` (no `sorryAx`).
- [ ] The untouched theorem retains `sorryAx`.
- [ ] `REPORT.md` exists and details direction, proof concept, and check.sh output.
