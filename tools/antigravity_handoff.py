#!/usr/bin/env python
"""tools/antigravity_handoff.py — run the prover benchmark through Antigravity.

Antigravity's `/teamwork-preview` is a slash command inside its IDE, not an API,
so the integration is a file handoff: export the challenges, run the team over
them there, drop what comes back into a directory, verify it here.

The verification deliberately reuses the *same* path as the seven-model
campaign — `LeanSubprocessProver._run_lean(..., audit_axioms=True)` over a
challenge file whose `prove`/`refute` declarations are two directions of one
`Candidate` — so the result is directly comparable to that baseline rather than
being a differently-scored number.

Why that matters here specifically: every formalization bug this repository has
found produced an *apparent success*. A model "proved" three items that were
`Fin 0` artefacts; another exploited `minCard`'s 0 fallback on an undefined
invariant. A stronger agent team is more likely to find such holes, not less, so
nothing is counted as resolved unless the kernel accepts it under an axiom
audit, and `--strict` additionally re-checks that the accepted direction agrees
with the ground-truth label the benchmark carries.

Usage:
    python tools/antigravity_handoff.py export --partition gold --out handoff/
    # ... run /teamwork-preview over handoff/, save results into handoff/solved/
    python tools/antigravity_handoff.py verify --partition gold --dir handoff/solved
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG  # noqa: E402

BRIEF = """\
# AutoGraphForge — prover benchmark handoff

Each `Challenge_<id>.lean` states one conjecture once, as `Candidate`, and asks
for **either** direction:

    theorem prove_<id>  :   Candidate := by sorry
    theorem refute_<id> : ¬ Candidate := by sorry

Close exactly one, editing the file in place and keeping its name. Leave the
other declaration untouched, `sorry` and all — the verifier removes it.

What makes a result count:

* Nothing above the first `theorem` may change: imports, options, `Candidate`.
  Helper lemmas go after `Candidate`, as top-level `theorem`/`lemma`/`def`.
* The chosen theorem keeps its exact name and type. The verifier re-checks the
  type by elaborating `_root_.prove_<id> : _root_.Candidate` itself.
* No `sorry`, `admit`, `axiom`, `native_decide`, `namespace`, `section`,
  `variable`, custom `notation`/`macro`/`syntax`, or metaprogramming; only
  `propext`, `Classical.choice` and `Quot.sound` may appear among the axioms.
* Never run `lake` in this project — it deletes Mathlib.

`decide` evaluates the invariants on an explicit small graph
(`GraphCalc.ofEdges n [(0, 1), ...]`), so a refutation is usually a witness plus
`decide`. Ground truth is withheld. {n} items in this partition.
"""


def _index(bench: str, partition: str):
    path = os.path.join(bench, f"challenges_{partition}", "index.json")
    if not os.path.exists(path):
        raise SystemExit(f"no challenge index at {path} — run "
                         f"tools/prover_eval/challenge.py --partition {partition}")
    return json.load(open(path)), os.path.dirname(path)


def do_export(args) -> int:
    index, src = _index(args.benchmark, args.partition)
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(os.path.join(args.out, "solved"), exist_ok=True)
    import shutil
    for item in index:
        shutil.copy(os.path.join(src, item["file"]), os.path.join(args.out, item["file"]))
    with open(os.path.join(args.out, "README.md"), "w") as fh:
        fh.write(BRIEF.format(n=len(index)))
    # The labels stay on this side of the handoff.
    with open(os.path.join(args.out, ".ground_truth.json"), "w") as fh:
        json.dump({i["id"]: {"label": i["label"], "witness_g6": i.get("witness_g6"),
                             "statement": i["statement"]} for i in index}, fh, indent=1)
    print(f"exported {len(index)} challenges → {args.out}")
    print(f"  brief:       {os.path.join(args.out, 'README.md')}")
    print(f"  put results in: {os.path.join(args.out, 'solved')}")
    return 0


def _candidate_of(text: str):
    """The `abbrev Candidate : Prop := …` body, normalised for comparison."""
    m = re.search(r"abbrev\s+Candidate\s*:\s*Prop\s*:=(.*?)(?=\n\ntheorem )", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


# ── admissibility ─────────────────────────────────────────────────────────────
#
# An answer is compiled as the *returned file*, helper lemmas included — pasting
# only the proof body back into the original, as the model campaign did, drops
# every lemma a real proof needs and turns a correct proof into "unresolved".
#
# Compiling the returned file is only sound if nothing in it can change what is
# being proved. The checks below close the routes that exist in Lean for that:
# editing `Candidate` or anything it elaborates against; extending its term past
# where it ended (a term does not stop at a newline); re-declaring `Candidate` or
# the target inside a namespace; adding `variable` hypotheses the target silently
# absorbs; redefining the tokens `Candidate` parses as; and bypassing the kernel.
# The target's type is then re-checked by Lean itself, and the axiom audit rejects
# `sorryAx` and anything non-standard.

_CMD_START = ("theorem", "lemma", "def", "abbrev", "example", "instance", "open",
              "set_option", "attribute", "noncomputable", "private", "protected",
              "@[", "#check", "#print", "structure", "inductive", "class")

_FORBIDDEN_CMD = re.compile(
    r"(?m)^\s*(?:(?:private|protected|noncomputable|local|scoped)\s+)*"
    r"(namespace|section|variable|universe|notation\w*|infixl?|infixr|prefix|postfix|"
    r"macro\w*|syntax\w*|declare_syntax_cat|elab\w*|initialize|builtin_initialize|"
    r"run_cmd|run_elab|run_meta)\b")

# Lean elaboration can run arbitrary code: `#eval IO.Process.run …`, `run_cmd`,
# a user `elab`, an `@[init]` hook. Agents are only allowed to run the checker,
# and the verifier compiles their files with full user privileges, so anything
# that reaches IO or the metaprogramming API is refused *before* Lean sees the
# file — that refusal is what makes "only check.sh may run" an actual boundary.
_FORBIDDEN_TOKEN = re.compile(
    r"\b(native_decide|ofReduceBool|trustCompiler|skipKernelTC|implemented_by|"
    r"extern|axiom|unsafe\w*|run_tac|run_cmd|run_elab|run_meta|addDecl\w*|"
    r"Lean|\w*IO|System|Process|MetaM|CoreM|TermElabM|CommandElabM|TacticM|"
    r"macro\w*|elab\w*|syntax\w*|notation\w*|initialize|builtin_initialize)\b"
    r"|#eval|#exit|\bdebug\.|@\[\s*(?:init|builtin_init|command_elab|term_elab|"
    r"tactic|extern|implemented_by)")

_ALLOWED_IMPORTS = {"Mathlib", "LeanProject.GraphInvariantsComputable",
                    "LeanProject.GraphInvariants"}


def _norm(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n"))


def _strip_comments(src: str) -> str:
    src = re.sub(r"/-.*?-/", " ", src, flags=re.S)
    return re.sub(r"--[^\n]*", " ", src)


def _prefix(original: str):
    """Everything up to the first theorem: imports, options, `Candidate`."""
    i = original.find("abbrev Candidate")
    j = original.find("\n\ntheorem ", i) if i >= 0 else -1
    return original[:j] if j >= 0 else None


def structural_check(original: str, returned: str):
    """(ok, reason): may the returned file be compiled as an answer at all?"""
    orig, ret = _norm(original), _norm(returned)
    pre = _prefix(orig)
    if pre is None:
        return False, "original challenge is malformed"
    if not ret.startswith(pre):
        return False, "statement changed: text above the first theorem differs"
    rest = ret[len(pre):]
    if rest and not rest.startswith("\n"):
        return False, "statement changed: Candidate's last line was extended"
    code = _strip_comments(rest)
    head = code.lstrip()
    if head and not head.startswith(_CMD_START):
        return False, "statement changed: Candidate continues past its original end"
    m = _FORBIDDEN_CMD.search(code)
    if m:
        return False, f"forbidden command `{m.group(1)}`"
    m = _FORBIDDEN_TOKEN.search(code)
    if m:
        return False, f"forbidden construct `{m.group(0)}`"
    return True, ""


def lint_text(text: str, original=None):
    """(ok, reason) for any Lean file an agent asks to elaborate.

    A challenge file is held to `structural_check` against its original. Any
    other file (scratch lemmas) gets the same code-execution screen plus an
    import whitelist, since `import` is the other way to pull in code.
    """
    if original is not None:
        return structural_check(original, text)
    code = _strip_comments(_norm(text))
    for m in re.finditer(r"(?m)^\s*import\s+(\S+)", code):
        if m.group(1) not in _ALLOWED_IMPORTS:
            return False, f"import `{m.group(1)}` is not allowed"
    m = _FORBIDDEN_CMD.search(code)
    if m:
        return False, f"forbidden command `{m.group(1)}`"
    m = _FORBIDDEN_TOKEN.search(code)
    if m:
        return False, f"forbidden construct `{m.group(0)}`"
    return True, ""


def solution_file(returned: str, ident: str, direction: str):
    """The returned file prepared to check one direction, or None.

    The other direction's untouched `sorry` block is removed, and a declaration
    is appended that forces Lean to confirm the target has exactly the type
    asked for — `_root_`-qualified, so a same-named `Candidate` or target in some
    other namespace cannot stand in for it.
    """
    ret = _norm(returned)
    other = "refute" if direction == "prove" else "prove"
    header = {"prove": rf"(?m)^theorem\s+prove_{ident}\s*:\s*Candidate\s*:=",
              "refute": rf"(?m)^theorem\s+refute_{ident}\s*:\s*¬\s*Candidate\s*:="}
    pristine = {"prove": f"theorem prove_{ident} : Candidate := by\n  sorry",
                "refute": f"theorem refute_{ident} : ¬ Candidate := by\n  sorry"}
    if not re.search(header[direction], _strip_comments(ret)):
        return None
    if pristine[direction] in ret:
        return None
    body = ret.replace(pristine[other], "")
    ty = "_root_.Candidate" if direction == "prove" else "¬ _root_.Candidate"
    return (body.rstrip() + "\n\n-- verifier: the target must have exactly this type\n"
            f"theorem agf_verify_{direction} : {ty} := _root_.{direction}_{ident}\n")


def do_verify(args) -> int:
    from pipeline.theorem_prover import LeanSubprocessProver
    from tools.prover_eval.w16 import is_timeout

    index, src = _index(args.benchmark, args.partition)
    truth = {}
    gt = os.path.join(os.path.dirname(args.dir.rstrip("/")), ".ground_truth.json")
    if os.path.exists(gt):
        truth = json.load(open(gt))

    CONFIG.lean_timeout_s = args.timeout
    lean = LeanSubprocessProver(CONFIG)
    if not lean._available:
        print("ERROR: no Lean available — cannot verify.")
        return 2

    results, counts = [], collections.Counter()
    for item in index:
        ident, fname = item["id"], item["file"]
        path = os.path.join(args.dir, fname)
        if not os.path.exists(path):
            continue
        returned = open(path).read()
        original = open(os.path.join(src, fname)).read()
        rec = {"id": ident, "statement": item["statement"],
               "label": (truth.get(ident) or {}).get("label", item.get("label"))}

        ok, why = structural_check(original, returned)
        if not ok:
            rec.update(status="rejected", reason=why)
            counts["rejected"] += 1
            print(f"  {ident}  REJECTED — {why}")
            results.append(rec)
            continue

        verified, timed_out = [], False
        for direction in ("prove", "refute"):
            sol = solution_file(returned, ident, direction)
            if sol is None:
                continue
            good, log = lean._run_lean(sol, audit_axioms=True)
            if good:
                verified.append(direction)
            else:
                timed_out = timed_out or is_timeout(log)
                rec[f"{direction}_log_tail"] = log.strip()[-800:]

        if len(verified) == 2:
            # Both `Candidate` and `¬ Candidate` accepted means the environment
            # proves False. Never report that as a resolution.
            rec.update(status="INCONSISTENT", reason="both directions kernel-verified")
            counts["INCONSISTENT"] += 1
            print(f"  {ident}  !!! BOTH DIRECTIONS VERIFIED — inconsistency, investigate")
        elif verified:
            d = verified[0]
            expected = {"true": "prove", "false": "refute"}.get(str(rec["label"]).lower())
            if args.strict and expected and d != expected:
                rec.update(status="wrong_direction", direction=d)
                counts["wrong_direction"] += 1
                print(f"  {ident}  WRONG DIRECTION: {d} but label={rec['label']}")
            else:
                rec.update(status="resolved", direction=d)
                counts["resolved"] += 1
                print(f"  {ident}  RESOLVED by {d}")
        else:
            status = "timeout" if timed_out else "unresolved"
            rec.update(status=status)
            counts[status] += 1
            print(f"  {ident}  {status}")
        results.append(rec)

    out = os.path.join(args.dir, f"verification_{args.partition}.json")
    json.dump(results, open(out, "w"), indent=1)
    print(f"\npartition '{args.partition}': {len(index)} items, {len(results)} files returned")
    for k in ("resolved", "unresolved", "timeout", "rejected", "wrong_direction",
              "INCONSISTENT"):
        print(f"  {k:16s}: {counts[k]}")
    print(f"  -> {out}")
    return 0


def do_lint(args) -> int:
    try:
        text = open(args.file).read()
    except Exception as e:
        print(f"LINT: cannot read {args.file}: {e}")
        return 2
    original = open(args.original).read() if args.original else None
    ok, why = lint_text(text, original)
    print("LINT: ok" if ok else f"LINT: REJECTED — {why}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export"); e.set_defaults(fn=do_export)
    e.add_argument("--benchmark", default="benchmark")
    e.add_argument("--partition", default="gold")
    e.add_argument("--out", default="handoff")
    v = sub.add_parser("verify"); v.set_defaults(fn=do_verify)
    v.add_argument("--benchmark", default="benchmark")
    v.add_argument("--partition", default="gold")
    v.add_argument("--dir", required=True)
    v.add_argument("--timeout", type=int, default=3600,
                   help="seconds per Lean check; decide-heavy refutations can need minutes")
    v.add_argument("--strict", action="store_true", default=True,
                   help="reject a resolution whose direction contradicts the label")
    li = sub.add_parser("lint"); li.set_defaults(fn=do_lint)
    li.add_argument("--original", default=None,
                    help="the untouched challenge, when FILE is one")
    li.add_argument("file")
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
