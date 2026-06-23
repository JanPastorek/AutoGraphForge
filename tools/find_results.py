#!/usr/bin/env python3
"""Run the improved CEGIS pipeline to surface NOVEL survivors (uses gen cache;
bigdb tier off to avoid the in-progress precompute write)."""
import sys
from config import CONFIG
CONFIG.refute_use_bigdb = False        # precompute mid-write; hog tier covers big graphs
import run_cegis
sys.exit(run_cegis.main(sys.argv[1:]))
