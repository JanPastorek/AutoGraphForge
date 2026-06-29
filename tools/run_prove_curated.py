#!/usr/bin/env python3
"""
tools/run_prove_curated.py — prove the curated classical inequalities with the
DeepSeek-Prover-V2-671B vLLM server + tools/prover_shim.py.

Mirrors tools/run_prove.py's CONFIG wiring (point the prover backend at the
shim) but runs the curated-theorem entry point instead of the survivor reprove,
so one vLLM serve can do both (curated baseline + machine-generated survivors).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG


def main():
    CONFIG.prover_api_url = os.environ.get("SHIM_URL", "http://127.0.0.1:8800")
    CONFIG.prover_backends = ("lean", "deepseek-671b")
    import tools.prove_curated as m
    return m.main()


if __name__ == "__main__":
    sys.exit(main())
