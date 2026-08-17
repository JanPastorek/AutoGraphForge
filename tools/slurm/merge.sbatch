#!/bin/bash
#SBATCH --job-name=merge_shards
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=results/merge_%j.log
#SBATCH --error=results/merge_%j.log

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

# ---------------------------------------------------------------------------
# Back up first. The merge overwrites results/cegis_results.json and
# cegis_survivors.dill in place, and now also *drops* survivors refuted by
# another shard's witnesses — so the previous run must stay recoverable.
# database/hard_seed/graphs.g6 is appended to, so it is saved too.
# ---------------------------------------------------------------------------
BACKUP="results/backup_$(date +%Y%m%dT%H%M%S)"
mkdir -p "$BACKUP"
for f in results/cegis_results.json results/cegis_survivors.dill \
         results/lifted.json database/hard_seed/graphs.g6; do
    if [ -e "$f" ]; then
        cp -a "$f" "$BACKUP/$(basename "$f")"
        echo "backed up $f -> $BACKUP/$(basename "$f")"
    else
        echo "note: $f absent, nothing to back up"
    fi
done
# Record what produced the backup so it can be told apart from later ones.
{
    echo "backed up before tools/merge_shards.py"
    echo "slurm_job=${SLURM_JOB_ID:-none}"
    echo "date=$(date -Is)"
    echo "git=$(git rev-parse --short HEAD 2>/dev/null || echo 'not a git repo')"
} > "$BACKUP/PROVENANCE"
echo "backup complete: $BACKUP"

.venv/bin/python tools/merge_shards.py --shards 5

echo "merge finished; previous results are in $BACKUP"
