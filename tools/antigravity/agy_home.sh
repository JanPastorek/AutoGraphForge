#!/bin/bash
# agy_home.sh — build an isolated HOME for agy with a deny-by-default policy.
#
#   agy_home.sh DEST WORKSPACE WRITE_RULE_SUFFIX READ_RULE_SUFFIX \
#               [--cmd /abs/cmd]... [--read /abs/path]... [--rule 'type(target)']...
#
# The user's real ~/.gemini/antigravity-cli/settings.json allows cp, mv, cat,
# python3 and more — enough for an agent to overwrite the verifier. agy only adds
# allow-rules, it cannot subtract them, so the isolation has to come from a
# separate HOME whose settings allow exactly: the listed commands, writes under
# the workspace, and reads under the workspace plus the listed paths.
#
# DEST must be private and outside the workspace (the job uses node-local /tmp):
# it holds a copy of the OAuth token, and a settings file the agents must not be
# able to rewrite.
set -euo pipefail
DEST="$1"; WS="$2"; WSUF="$3"; RSUF="$4"; shift 4
CMDS=(); READS=(); RULES=()
while [ $# -gt 0 ]; do
  case "$1" in
    --cmd)  CMDS+=("$2"); shift 2 ;;
    --read) READS+=("$2"); shift 2 ;;
    --rule) RULES+=("$2"); shift 2 ;;
    *) echo "agy_home.sh: unknown argument $1" >&2; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)"
SRC="$(grep -m1 '^AGF_AGY_CONFIG=' "$ROOT/handoff/.agf_env" 2>/dev/null | cut -d= -f2-)"
[ -f "$SRC/antigravity-oauth-token" ] || { echo "agy_home.sh: no agy config at '$SRC'" >&2; exit 2; }
CFG="$DEST/.gemini/antigravity-cli"
umask 077
mkdir -p "$CFG"
for f in antigravity-oauth-token installation_id; do
  [ -f "$SRC/$f" ] && install -m 600 "$SRC/$f" "$CFG/$f"
done
# agy writes a helper (`bin/agentapi`) into its config directory before it can
# run any shell command, so these must be private, writable copies. A link to the
# real directory broke command execution as soon as the sandbox mounted it
# read-only (probe 84823: "failed to write agentapi script: read-only file
# system") — and a copy means the real config directory need not be mounted.
for d in bin builtin; do
  [ -e "$SRC/$d" ] && cp -a "$SRC/$d" "$CFG/$d"
done

python3 - "$CFG/settings.json" "$SRC/settings.json" "$WS" "$WSUF" "$RSUF" \
    "${#CMDS[@]}" "${#READS[@]}" "${CMDS[@]}" "${READS[@]}" "${RULES[@]}" <<'PY'
import json, sys
out, src, ws, wsuf, rsuf, ncmd, nread, *rest = sys.argv[1:]
nc, nr = int(ncmd), int(nread)
cmds, reads, rules = rest[:nc], rest[nc:nc + nr], rest[nc + nr:]
allow = ([f"command({c})" for c in cmds]
         + [f"write_file({ws}{wsuf})", f"read_file({ws}{rsuf})"]
         + [f"read_file({r}{rsuf})" for r in reads]
         + list(rules))
cfg = {"permissions": {"allow": allow}, "trustedWorkspaces": [ws]}
try:
    model = json.load(open(src)).get("model")
    if model:
        cfg["model"] = model
except Exception:
    pass
json.dump(cfg, open(out, "w"), indent=2)
print("agy policy:", json.dumps(allow))
PY
