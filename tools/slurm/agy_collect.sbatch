#!/bin/bash
#SBATCH --job-name=agy_collect
#SBATCH --partition=cpu_short
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:20:00
#SBATCH --output=results/agy_collect_%j.log
#SBATCH --error=results/agy_collect_%j.log

# Runs once the whole attempt array has ended, however it ended
# (--dependency=afterany): lifts guard.sh's write-protection and summarises
# every task's verdict in one table.
set -uo pipefail
cd "$SLURM_SUBMIT_DIR"
PART="${PARTITION:-promising13}"
tools/antigravity/guard.sh unlock "$PART"

.venv/bin/python - "$PART" <<'PY'
import collections, glob, json, os, sys
part = sys.argv[1]
index = {i["id"]: i["statement"]
         for i in json.load(open(f"benchmark/challenges_{part}/index.json"))}
rows, tally = [], collections.Counter()
for tid, stmt in index.items():
    ws = f"handoff/{part}/task_{tid}"
    status, reason = ("not started" if not os.path.isdir(ws) else "no verdict"), ""
    if os.path.exists(f"{ws}/STATUS"):
        status = open(f"{ws}/STATUS").read().strip()
    vf = f"{ws}/solved/verification_{part}.json"
    if os.path.exists(vf):
        for r in json.load(open(vf)):
            status = r["status"] + (f" ({r['direction']})" if r.get("direction") else "")
            reason = r.get("reason", "")
    tally[status.split(" ")[0]] += 1
    rows.append({"id": tid, "status": status, "reason": reason, "statement": stmt,
                 "report": os.path.exists(f"{ws}/REPORT.md")})
for r in rows:
    print(f"{r['id']}  {r['status']:22s} {r['statement'][:72]}")
    if r["reason"]:
        print(f"          {r['reason']}")
print("\n" + ", ".join(f"{k}: {v}" for k, v in tally.most_common()))
json.dump(rows, open(f"handoff/{part}/summary.json", "w"), indent=1)
print(f"-> handoff/{part}/summary.json")
PY
