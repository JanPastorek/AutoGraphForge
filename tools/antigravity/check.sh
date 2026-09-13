#!/bin/bash
# check.sh — the ONLY command an agent may run.
#
#   /abs/path/tools/antigravity/check.sh FILE.lean
#
# Lives outside every agent workspace and is hashed by guard.sh: agents can
# write inside their workspace, so a checker kept there could be rewritten into
# anything. It screens the file first (tools/antigravity_handoff.py lint), because
# Lean elaboration can itself run shell commands; then elaborates it with bare
# `lean` and an explicit LEAN_PATH, and prints every theorem's axioms. Nothing
# here depends on $HOME — agents run under a private one — and `lake` is never
# involved (in this project lake deletes Mathlib when it cannot re-clone).
set -uo pipefail
f="${1:?usage: check.sh FILE.lean}"
[ -f "$f" ] || { echo "CHECK: no such file: $f"; exit 2; }

ROOT="$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)"
# Tool paths come from a protected file, not from the home directory: agents run
# under a private HOME, and on compute nodes `getent passwd` reports a different
# home (/home/<user>@ad…) than the one the tools live in.
ENVF="$ROOT/handoff/.agf_env"
export ELAN_HOME="$(grep -m1 '^AGF_ELAN_HOME=' "$ENVF" 2>/dev/null | cut -d= -f2-)"
LEAN="$ELAN_HOME/bin/lean"
[ -x "$LEAN" ] || { echo "CHECK: lean not found (ELAN_HOME='$ELAN_HOME' from $ENVF)"; exit 2; }
PY="$ROOT/.venv/bin/python"
LP_FILE="$ROOT/handoff/.agf_lean_path"
[ -s "$LP_FILE" ] || { echo "CHECK: missing $LP_FILE"; exit 2; }
export LEAN_PATH="$(cat "$LP_FILE")"

orig="$(ls "$ROOT"/benchmark/challenges_*/"$(basename "$f")" 2>/dev/null | head -1)"
if ! "$PY" "$ROOT/tools/antigravity_handoff.py" lint ${orig:+--original "$orig"} "$f"; then
  echo "CHECK: refused to elaborate — remove the construct named above."
  exit 3
fi

tmp="$(mktemp --suffix=.lean)"
cp "$f" "$tmp"
for t in $(grep -oE '^theorem +[A-Za-z0-9_]+' "$f" | awk '{print $2}'); do
  echo "#print axioms $t" >> "$tmp"
done
timeout 1800 "$LEAN" "$tmp"
rc=$?
rm -f "$tmp"
if [ $rc -eq 0 ]; then
  echo "CHECK: elaborated. Allowed axioms: propext, Classical.choice, Quot.sound."
  echo "       'sorryAx' in a list above means that theorem is unfinished."
else
  echo "CHECK: FAILED (exit $rc)"
fi
exit $rc
