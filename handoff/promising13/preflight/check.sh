#!/bin/bash
# check.sh — the only checker agents should use.
#
#   ./check.sh Challenge_<id>.lean
#
# Elaborates the file against the AutoGraphForge Lean layer with bare `lean` and
# an explicit LEAN_PATH, then prints the axioms of every theorem in it. `lake` is
# never involved: in this project lake deletes Mathlib when it cannot re-clone.
set -uo pipefail
f="${1:?usage: ./check.sh Challenge_<id>.lean}"
here="$(cd "$(dirname "$0")" && pwd)"
src="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
export LEAN_PATH="$(cat "$here/lean_path.txt")"
LEAN="$HOME/.elan/bin/lean"

tmp="$(mktemp --suffix=.lean)"
cp "$src" "$tmp"
for t in $(grep -oE '^theorem +[A-Za-z0-9_]+' "$src" | awk '{print $2}'); do
  echo "#print axioms $t" >> "$tmp"
done

timeout "${CHECK_TIMEOUT:-1800}" "$LEAN" "$tmp"
rc=$?
rm -f "$tmp"
if [ $rc -eq 0 ]; then
  echo "CHECK: elaborated. Allowed axioms: propext, Classical.choice, Quot.sound."
  echo "       'sorryAx' in a list above means that theorem is unfinished."
else
  echo "CHECK: FAILED (exit $rc)"
fi
exit $rc
