#!/bin/bash
#SBATCH --job-name=agy_attempt
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=results/agy_attempt_%A_%a.log
#SBATCH --error=results/agy_attempt_%A_%a.log

# One Antigravity `/teamwork-preview` attempt per conjecture, as an array task.
#
#   sbatch tools/slurm/agy_permission_probe.sbatch        # must print POLICY HOLDS
#   tools/antigravity/guard.sh lock promising13            # prints REF_SHA
#   sbatch --array=0-12%1 --export=ALL,REF_SHA=<sha>,PROBE_JOB=<probe id> \
#          tools/slurm/agy_attempt.sbatch
#
# Security model — no permission bypass anywhere:
#
#  * The boundary is a bubblewrap sandbox (tools/antigravity/sandbox.sh): the
#    agents' filesystem holds only this workspace and the private agy home
#    (writable) plus read-only system, toolchain and checker trees; the rest of
#    $HOME, the repository and the munge socket are absent. agy's own rules
#    confine its commands but — as probes 84810/84813 showed — not its file
#    tools, so they are kept only as a second layer.
#  * agy runs under a private HOME on node-local /tmp; the user's real agy config
#    is never consulted or mounted. Inside the sandbox agy's own permissions are
#    broad on purpose (see the agy_home.sh call below). This is exactly the
#    configuration the probe job tested; the task refuses to start unless that
#    probe's verdict is on record.
#  * The checker screens every file before Lean elaborates it, because Lean
#    elaboration can itself run shell commands.
#  * The Lean definitions, oleans, verifier chain, checker, policy builder and
#    challenges are hashed at lock time and re-checked before the agents start
#    and before any verdict, against a reference whose own digest arrives through
#    the job environment. SLURM runs a spooled copy of this script, so editing it
#    mid-run changes nothing either.

set -uo pipefail
cd "$SLURM_SUBMIT_DIR"
ROOT="$PWD"
PART="${PARTITION:-promising13}"
HOURS="${AGY_HOURS:-11}"
REF="$ROOT/handoff/$PART/.integrity.sha256"
IDX="benchmark/challenges_$PART/index.json"
AGY="$(grep -m1 '^AGF_AGY=' "$ROOT/handoff/.agf_env" 2>/dev/null | cut -d= -f2-)"
[ -x "$AGY" ] || { echo "agy not found at '$AGY' — refusing to run"; exit 1; }
CHECK="$ROOT/tools/antigravity/check.sh"

integrity() {
  [ -n "${REF_SHA:-}" ] || { echo "REF_SHA not set"; return 1; }
  [ "$(sha256sum "$REF" | cut -d' ' -f1)" = "$REF_SHA" ] || { echo "integrity reference file altered"; return 1; }
  ( cd "$ROOT" && sha256sum --quiet -c "$REF" )
}

# -- the probe must have established the policy ------------------------------
PLOG="results/agy_probe_${PROBE_JOB:-none}.log"
PDIR="results/agy_probe_${PROBE_JOB:-none}"
if ! grep -q "^VERDICT: POLICY HOLDS" "$PLOG" 2>/dev/null; then
  if [ "${PROBE_ACCEPT_INCONCLUSIVE:-0}" = 1 ] && grep -q "^VERDICT: no failures" "$PLOG" 2>/dev/null; then
    echo "probe had inconclusive tests; accepted explicitly (PROBE_ACCEPT_INCONCLUSIVE=1)"
  else
    echo "no passing permission probe on record ($PLOG) — refusing to run"; exit 1
  fi
fi
SUF="$(cat "$PDIR/chosen_rule_suffix.txt")"
[ -n "$SUF" ] || { echo "probe chose no rule suffix — refusing to run"; exit 1; }
[ "$(cat "$PDIR/sandbox_mode.txt" 2>/dev/null)" = bwrap ] || { echo "probe did not establish the bubblewrap sandbox — refusing to run"; exit 1; }
[ "$(cat "$PDIR/policy_mode.txt" 2>/dev/null)" = broad-in-sandbox ] || { echo "probe did not test the broad in-sandbox policy — refusing to run"; exit 1; }

F=$(.venv/bin/python -c "import json,sys;print(json.load(open(sys.argv[1]))[int(sys.argv[2])]['file'])" "$IDX" "$SLURM_ARRAY_TASK_ID")
STMT=$(.venv/bin/python -c "import json,sys;print(json.load(open(sys.argv[1]))[int(sys.argv[2])]['statement'])" "$IDX" "$SLURM_ARRAY_TASK_ID")
ID="${F#Challenge_}"; ID="${ID%.lean}"
WS="$ROOT/handoff/$PART/task_$ID"

echo "=== task $SLURM_ARRAY_TASK_ID on $(hostname): $F ==="
echo "conjecture: $STMT"
echo "policy: bubblewrap sandbox + agy rule suffix '$SUF', probe job ${PROBE_JOB}"
integrity || { echo "Lean layer / verifier not intact before start — refusing to run"; exit 1; }

mkdir -p "$WS/solved" "$WS/reference"
cp "benchmark/challenges_$PART/$F" "$WS/$F"; chmod u+w "$WS/$F"
# The probe showed agy's file tools cannot be confined to a directory with a
# plain path rule, so agents get no read access outside the workspace at all.
# What they need is copied in. Editing the copy changes nothing: the checker and
# the verifier elaborate against the real, hash-protected oleans.
cp "$ROOT/lean_project/LeanProject/GraphInvariantsComputable.lean" "$WS/reference/"

PRIV="$(mktemp -d /tmp/agyhome.XXXXXX)"; chmod 700 "$PRIV"
trap 'rm -rf "$PRIV"' EXIT TERM INT          # removes the token copy, however we exit
# Broad permissions inside the sandbox. In headless mode one denied tool call
# ends the whole run: task 0 of array 84825 died at its first step, a ListDir of
# the workspace root that the narrow rules did not cover, and teamwork routinely
# uses ordinary shell commands too. Breadth costs nothing at the boundary — the
# probe's direct tests run arbitrary commands inside the sandbox and none reach
# anything outside it — so agy's rules are not what confines the agents.
"$ROOT/tools/antigravity/agy_home.sh" "$PRIV" "$WS" "$SUF" "$SUF" \
    --rule 'command(*)' --rule 'read_file(*)' --rule 'write_file(*)' \
    --rule 'read_url(*)' --rule 'execute_url(*)'
SBX=("$ROOT/tools/antigravity/sandbox.sh" --ws "$WS" --home "$PRIV" --part "$PART" --)

echo "--- preflight: the untouched challenge must pass the checker inside the sandbox ---"
if ! "${SBX[@]}" "$CHECK" "$WS/$F" > "$WS/preflight.log" 2>&1; then
  echo "preflight FAILED"; tail -30 "$WS/preflight.log"; exit 1
fi
echo "preflight ok"

read -r -d '' PROMPT <<EOP
/teamwork-preview Settle one open graph-theory conjecture in Lean 4 — PROVE it or REFUTE it — with a kernel-checked proof.

This is an unattended batch run: no human is present and nobody will answer. Do not ask for confirmation, approval, or review of any draft or plan — launch the team immediately, choose the formal proof pipeline yourself, and keep working until the conjecture is settled. (Array 84835, task 4 stopped after drafting the team prompt and asking the user to confirm launch.)

The file $F in the current directory defines \`Candidate\`, the conjecture
    $STMT
Replace the \`sorry\` in exactly ONE of \`theorem prove_$ID : Candidate\` or \`theorem refute_$ID : ¬ Candidate\`, editing that file in place.

The invariants are defined in reference/GraphInvariantsComputable.lean (namespace GraphCalc) — a copy of what Lean actually uses; read it. To find Mathlib lemmas, put #check, example or exact? in a scratch .lean file here and run the checker on it. Because the invariants are computable, \`decide\` evaluates them on an explicit small graph built with \`GraphCalc.ofEdges n [(0, 1), ...]\` — so a refutation is usually a counterexample graph plus \`decide\`, while a proof needs a general argument about all finite graphs.

Check Lean files with: $CHECK <file.lean>
It screens the file, elaborates it against the real definitions, and prints each theorem's axioms. You work inside a sandbox: this directory is writable, the Lean project and Mathlib are read-only, and ordinary shell commands are available. Never run lake. Scratch files may be created in this directory.

Hard rules — a result that breaks any of them is discarded:
- Change nothing above the first \`theorem\` line (imports, options, \`Candidate\`). Put helper lemmas after \`Candidate\`, as top-level theorem/lemma/def.
- Keep the chosen theorem's name and header exactly; leave the other theorem untouched, with its sorry.
- No sorry, admit, axiom, native_decide, namespace, section, variable, notation, macro, syntax, IO, or any metaprogramming. Only propext, Classical.choice and Quot.sound may appear among the axioms.

When finished, write REPORT.md here: the direction settled (or that neither was), the key mathematical idea, and the final checker output.
EOP

cd "$WS"
echo "--- agy /teamwork-preview, up to ${HOURS}h ---"
timeout $(( HOURS * 3600 + 900 )) "${SBX[@]}" \
    "$AGY" -p "$PROMPT" --effort high \
    ${AGY_MODEL:+--model "$AGY_MODEL"} \
    --print-timeout "${HOURS}h" --output-format text --log-file "$WS/agy.log" \
    > "$WS/agy_output.txt" 2>&1
echo "agy exit: $?"
cd "$ROOT"

# keep the run's own records for audit — never the token
mkdir -p "$WS/agy_state"
for x in conversations brain log cli.log history.jsonl; do
  [ -e "$PRIV/.gemini/antigravity-cli/$x" ] && cp -r "$PRIV/.gemini/antigravity-cli/$x" "$WS/agy_state/" 2>/dev/null
done
rm -rf "$PRIV"

if ! integrity; then
  echo "LEAN LAYER OR VERIFIER MODIFIED DURING THE RUN — result not trusted"
  echo tampered > "$WS/STATUS"; exit 3
fi

cp "$WS/$F" "$WS/solved/$F"
echo "--- kernel verification ---"
.venv/bin/python -u tools/antigravity_handoff.py verify \
    --partition "$PART" --dir "$WS/solved" --timeout 3600
