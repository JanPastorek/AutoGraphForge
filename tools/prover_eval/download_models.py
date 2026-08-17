#!/usr/bin/env python
"""tools/prover_eval/download_models.py — fetch prover weights at pinned revisions.

Every download is pinned to the commit sha resolved at fetch time and recorded
in ``model_manifest.json``. A benchmark result that cannot name the exact
weights it ran against is not reproducible, and "latest on main" silently
changes underneath a multi-week evaluation.

DeepSeek-Prover-V2-671B is deliberately absent. It is ~689 GB, the one prior
attempt in this repository failed before the server came up, and nothing in the
current benchmark needs it: the binding constraint is how much of the corpus can
be *stated* in Lean, not how large the prover is.

Usage:
    python tools/prover_eval/download_models.py [--only NAME] [--root DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

MODELS = [
    "Pythagoras-LM/Pythagoras-Prover-4B",
    "deepseek-ai/DeepSeek-Prover-V2-7B",
    "Goedel-LM/Goedel-Prover-V2-8B",
    "Goedel-LM/Goedel-Prover-V2-32B",
    "m-a-p/OProver-8B",
    "m-a-p/OProver-32B",
    "mistralai/Leanstral-1.5-119B-A6B",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get(
        "MODEL_ROOT", os.path.join(os.getcwd(), ".hf_cache")))
    ap.add_argument("--only", default="", help="substring filter on repo id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from huggingface_hub import model_info, snapshot_download

    root = args.root
    os.makedirs(root, exist_ok=True)
    manifest_path = os.path.join(root, "model_manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        manifest = json.load(open(manifest_path))

    todo = [r for r in MODELS if args.only.lower() in r.lower()]
    print(f"{len(todo)} model(s) -> {root}")

    for repo in todo:
        local = os.path.join(root, repo.split("/")[-1])
        info = model_info(repo)
        if not info.sha:
            print(f"  SKIP {repo}: could not resolve a revision")
            continue
        if manifest.get(repo, {}).get("revision") == info.sha \
                and os.path.isdir(local):
            print(f"  have {repo} @ {info.sha[:12]}")
            continue
        print(f"  fetch {repo} @ {info.sha[:12]} -> {local}")
        if args.dry_run:
            continue
        snapshot_download(repo_id=repo, revision=info.sha, local_dir=local)
        manifest[repo] = {"revision": info.sha, "local_dir": local}
        # Written after each model so an interrupted run keeps what it earned.
        with open(manifest_path, "w") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)

    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
