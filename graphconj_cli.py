#!/usr/bin/env python3
"""
graphconj_cli.py — the single entry point for the package.

    graphconj cegis   [--rounds N] [--prove-top N] [--reprove] ...
    graphconj prove   [--curated | --demo] [--k N]
    graphconj precompute-battery [...]
    graphconj build-db [...]

Replaces the historical scatter of entry points (main.py / discover.py /
run_parallel.py — now under legacy/). CEGIS is the canonical pipeline; see
docs/MIGRATION.md for the legacy→CEGIS feature map.
"""
from __future__ import annotations

import argparse
import sys


def _cmd_cegis(argv):
    import run_cegis
    return run_cegis.main(argv)


def _cmd_prove(argv):
    ap = argparse.ArgumentParser(prog="graphconj prove")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--curated", action="store_true",
                   help="prove a few curated universally-true theorems (chain check)")
    g.add_argument("--demo", action="store_true",
                   help="prove the simplest supported pipeline survivors")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args(argv)
    if args.demo:
        import tools.prove_demo as m
        return m.main(["--k", str(args.k)])
    import tools.prove_curated as m          # default: curated
    return m.main()


def _cmd_precompute(argv):
    import tools.precompute_battery as m
    return m.main(argv) if hasattr(m, "main") else m.__dict__.get("main", lambda a: 0)(argv)


def _cmd_build_db(argv):
    import build_database as m
    return m.main(argv) if hasattr(m, "main") else 0


_COMMANDS = {
    "cegis": _cmd_cegis,
    "prove": _cmd_prove,
    "precompute-battery": _cmd_precompute,
    "build-db": _cmd_build_db,
}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(
        prog="graphconj", description="CEGIS graph-theory conjecturing pipeline.")
    ap.add_argument("command", choices=sorted(_COMMANDS), help="subcommand to run")
    # parse only the command; the rest is forwarded verbatim
    args, rest = ap.parse_known_args(argv)
    return _COMMANDS[args.command](rest)


if __name__ == "__main__":
    sys.exit(main() or 0)
