#!/bin/bash
# guard.sh — protect the Lean layer and the verifier while agents run.
#
#   tools/antigravity/guard.sh lock   [PARTITION]   # prints REF_SHA for sbatch
#   tools/antigravity/guard.sh unlock [PARTITION]
#
# `lock` hashes everything a false claim could be edited into agreement with —
# the Lean definitions and their oleans, the verifier chain, the challenges —
# makes those files read-only, and makes every directory under lean_project/.lake
# read-only so that a stray `lake` cannot delete Mathlib.
#
# Read-only is only a guard against accidents: an agent running as this user can
# chmod it back. The hashes are the real protection — the attempt job re-checks
# them against a reference whose own digest arrives through the job environment.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PART="${2:-promising13}"
REF="$ROOT/handoff/$PART/.integrity.sha256"
LP="lean_project"

protected() {
  ls $LP/LeanProject/*.lean \
     $LP/.lake/build/lib/lean/LeanProject.olean \
     $LP/.lake/build/lib/lean/LeanProject/*.olean \
     tools/antigravity_handoff.py tools/prover_eval/w16.py \
     pipeline/theorem_prover.py config.py tools/antigravity/check.sh \
     tools/antigravity/agy_home.sh tools/antigravity/sandbox.sh \
     handoff/.agf_lean_path handoff/.agf_env \
     benchmark/challenges_$PART/*.lean benchmark/challenges_$PART/index.json
}

cd "$ROOT"
case "${1:-}" in
  lock)
    mkdir -p "$(dirname "$REF")"
    [ -f "$REF" ] && chmod u+w "$REF"
    protected | xargs sha256sum > "$REF"
    protected | xargs chmod a-w
    find "$LP/.lake" -type d -exec chmod a-w {} +
    chmod a-w "$REF"
    echo "locked $(wc -l < "$REF") files; lean_project/.lake is read-only"
    echo "REF_SHA=$(sha256sum "$REF" | cut -d' ' -f1)"
    ;;
  unlock)
    find "$LP/.lake" -type d -exec chmod u+w {} +
    protected | xargs chmod u+w
    [ -f "$REF" ] && chmod u+w "$REF"
    echo "unlocked"
    ;;
  *)
    echo "usage: $0 lock|unlock [PARTITION]"; exit 2 ;;
esac
