#!/bin/bash
# sandbox.sh — run a command in a bubblewrap sandbox that contains only what an
# Antigravity attempt needs.
#
#   sandbox.sh --ws DIR --home DIR --part PARTITION [--ro PATH]... -- CMD [ARGS...]
#
# Why this exists: agy's permission rules confine its shell commands but not its
# file tools. The permission probe (job 84813) had agents write, edit and read
# outside the workspace under every rule form, with no permission check logged.
# So the boundary has to be the filesystem the agents can see, and this script
# builds it:
#
#   writable   the workspace (--ws) and the private agy home (--home)
#   read-only  /usr /etc and the libc trees; agy; the Lean toolchain and
#              lean_project (a stray `lake` cannot delete Mathlib); the checker,
#              its Python venv and code; this partition's challenges
#   absent     everything else — the rest of $HOME (~/.ssh, the real OAuth token,
#              other projects), the repository's results and handoff trees, and
#              /run, which is where the munge socket lives: without it nothing in
#              here can submit SLURM jobs
#
# agy's own policy file inside --home stays writable: agy rewrites it atomically
# at startup, and a read-only mount on top broke that (probe 84823). It is only a
# second layer — an agent that widened agy's rules would still be confined to
# this filesystem. The real agy config directory is not mounted at all: the
# private home carries its own copies of what agy needs. Network is shared: agy
# needs it.
set -euo pipefail
ROOT="$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)"
ENVF="$ROOT/handoff/.agf_env"
agf() { grep -m1 "^$1=" "$ENVF" | cut -d= -f2-; }
AGY="$(agf AGF_AGY)"; ELAN="$(agf AGF_ELAN_HOME)"; CFG="$(agf AGF_AGY_CONFIG)"

WS=""; HOMEDIR=""; PART=""; EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --ws)   WS="$(readlink -f "$2")"; shift 2 ;;
    --home) HOMEDIR="$(readlink -f "$2")"; shift 2 ;;
    --part) PART="$2"; shift 2 ;;
    --ro)   p="$(readlink -f "$2")"; EXTRA+=(--ro-bind "$p" "$p"); shift 2 ;;
    --)     shift; break ;;
    *) echo "sandbox.sh: unknown argument $1" >&2; exit 2 ;;
  esac
done
if [ -z "$WS" ] || [ -z "$HOMEDIR" ] || [ -z "$PART" ] || [ $# -eq 0 ]; then
  echo "usage: sandbox.sh --ws DIR --home DIR --part PARTITION [--ro PATH]... -- CMD" >&2; exit 2
fi
[ -d "$WS" ] && [ -d "$HOMEDIR" ] || { echo "sandbox.sh: --ws and --home must exist" >&2; exit 2; }
case "$WS/" in
  "$ROOT/lean_project/"*|"$ROOT/tools/"*|"$ROOT/.venv/"*|"$ELAN/"*|"$CFG/"*)
    echo "sandbox.sh: refusing a workspace inside a protected tree" >&2; exit 2 ;;
esac

SYS=(--ro-bind /usr /usr --ro-bind /etc /etc)
for d in /bin /sbin /lib /lib64; do
  if [ -L "$d" ]; then SYS+=(--symlink "$(readlink "$d")" "$d")
  elif [ -d "$d" ]; then SYS+=(--ro-bind "$d" "$d"); fi
done

exec bwrap \
  --die-with-parent --new-session \
  --unshare-pid --unshare-ipc --unshare-uts --unshare-cgroup-try \
  "${SYS[@]}" \
  --proc /proc --dev /dev \
  --tmpfs /tmp --tmpfs /var/tmp --tmpfs /run \
  --ro-bind "$AGY" "$AGY" \
  --ro-bind "$ELAN" "$ELAN" \
  --ro-bind "$ROOT/lean_project" "$ROOT/lean_project" \
  --ro-bind "$ROOT/.venv" "$ROOT/.venv" \
  --ro-bind "$ROOT/tools" "$ROOT/tools" \
  --ro-bind "$ROOT/pipeline" "$ROOT/pipeline" \
  --ro-bind "$ROOT/config.py" "$ROOT/config.py" \
  --ro-bind "$ROOT/benchmark/challenges_$PART" "$ROOT/benchmark/challenges_$PART" \
  --ro-bind "$ENVF" "$ENVF" \
  --ro-bind "$ROOT/handoff/.agf_lean_path" "$ROOT/handoff/.agf_lean_path" \
  "${EXTRA[@]}" \
  --bind "$HOMEDIR" "$HOMEDIR" \
  --bind "$WS" "$WS" \
  --chdir "$WS" \
  --clearenv \
  --setenv HOME "$HOMEDIR" --setenv PATH /usr/bin:/bin \
  --setenv USER "$(id -un)" --setenv LANG C.UTF-8 --setenv TMPDIR /tmp \
  -- "$@"
