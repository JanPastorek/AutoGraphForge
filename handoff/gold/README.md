# AutoGraphForge — prover benchmark handoff

Each `Challenge_<id>.lean` states one conjecture once, as `Candidate`, and asks
for **either** direction:

    theorem prove_<id>  :   Candidate := by sorry
    theorem refute_<id> : ¬ Candidate := by sorry

Close exactly one. Return the whole file with that `sorry` replaced, keeping the
file name. Leave the other declaration alone — the verifier drops it.

Rules that make a result count:

* The file must compile against `LeanProject.GraphInvariantsComputable` with no
  `sorry`, no new `axiom`, and no `native_decide`.
* Do not edit `Candidate`. The verifier re-derives it from this repository and
  rejects a file whose `Candidate` differs, because a changed statement is the
  most common way an apparent proof turns out to be about something else.
* `decide` is usually the whole proof for a refutation: pick a witness graph and
  let the kernel evaluate. Witnesses above ~10 vertices stop being feasible.

Ground truth is withheld deliberately. 58 items in this partition.
