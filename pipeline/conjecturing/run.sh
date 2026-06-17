#!/usr/bin/env bash
# Launch the expression-tree (Dalmatian) conjecturing engine.
# Usage: ./run.sh            # full run, connected graphs n<=7, 8s/search
#        CONJ_MAX_GENG=6 CONJ_TIME=5 ./run.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SAGE="${SAGE:-$HOME/miniconda3/envs/sage/bin/sage}"
export PATH="$HERE:$PATH"          # make the bundled `expressions` binary visible
exec "$SAGE" "$HERE/run_conjecturing.sage"
