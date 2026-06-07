#!/usr/bin/env python3
"""
main.py — entry point for the autonomous graph-theory conjecture pipeline.

Usage
-----
  python main.py [options]

  python main.py --help

  # Quick demo (no API key needed)
  python main.py --no-funsearch --no-lean --n-conjectures 10

  # Full run (requires ANTHROPIC_API_KEY)
  python main.py --n-conjectures 20 --output results/run1.json
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Autonomous Graph Theory Conjecture Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Generation
    gen = p.add_argument_group("Hypothesis generation")
    gen.add_argument("--n-conjectures", type=int, default=20,
                     help="Max TxGraffiti conjectures to generate (default: 20)")
    gen.add_argument("--no-funsearch", action="store_true",
                     help="Disable FunSearch LLM generation (useful without API key)")
    gen.add_argument("--funsearch-n", type=int, default=5,
                     help="FunSearch: conjectures per LLM call (default: 5)")

    # Database
    db = p.add_argument_group("Graph database")
    db.add_argument("--db-random", type=int, default=15,
                    help="Extra random graphs in the database (default: 15)")
    db.add_argument("--db-max-n", type=int, default=12,
                    help="Max vertex count for random database graphs (default: 12)")
    db.add_argument("--db-seed", type=int, default=42,
                    help="Random seed for database construction (default: 42)")

    # Falsification
    fal = p.add_argument_group("Falsification")
    fal.add_argument("--no-z3", action="store_true",
                     help="Disable Z3 falsification (fallback to MCTS/VNS/CE)")
    fal.add_argument("--mcts-iter", type=int, default=800,
                     help="MCTS iterations per conjecture (default: 800)")
    fal.add_argument("--vns-iter", type=int, default=600,
                     help="VNS iterations per conjecture (default: 600)")
    fal.add_argument("--falsify-rounds", type=int, default=2,
                     help="Falsification feedback rounds (default: 2)")

    # Formalization / proving
    form = p.add_argument_group("Autoformalization & proving")
    form.add_argument("--no-lean", action="store_true",
                      help="Disable Lean 4 autoformalization")
    form.add_argument("--lean-binary", type=str, default="lean",
                      help="Path to Lean 4 binary (default: 'lean')")
    form.add_argument("--prover-url", type=str, default="",
                      help="Neural prover API endpoint (optional)")

    # Output
    out = p.add_argument_group("Output")
    out.add_argument("--output", type=str, default="results/conjecture_report.json",
                     help="Path for JSON report (default: results/conjecture_report.json)")
    out.add_argument("--verbose", action="store_true", default=True,
                     help="Verbose logging (default: on)")
    out.add_argument("--quiet", action="store_true",
                     help="Suppress most logging")
    out.add_argument("--log-level", choices=["DEBUG","INFO","WARNING","ERROR"],
                     default="INFO")

    # API
    p.add_argument("--api-key", type=str, default="",
                   help="Anthropic API key (overrides ANTHROPIC_API_KEY env var)")
    p.add_argument("--model", type=str, default="claude-opus-4-6",
                   help="LLM model to use (default: claude-opus-4-6)")

    return p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Logging
    level = logging.WARNING if args.quiet else getattr(logging, args.log_level)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("main")

    # Build config
    from config import Config
    cfg = Config(
        anthropic_api_key=args.api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        model=args.model,
        txgraffiti_max_conjectures=args.n_conjectures,
        funsearch_conjectures=args.funsearch_n,
        use_funsearch=not args.no_funsearch,
        db_random_graphs=args.db_random,
        db_max_vertices=args.db_max_n,
        db_random_seed=args.db_seed,
        z3_enabled=not args.no_z3,
        mcts_iterations=args.mcts_iter,
        vns_iterations=args.vns_iter,
        falsification_rounds=args.falsify_rounds,
        lean_binary=args.lean_binary,
        prover_api_url=args.prover_url,
        output_dir=str(Path(args.output).parent),
        verbose=not args.quiet,
    )

    if not args.quiet:
        print(banner())

    if not cfg.anthropic_api_key:
        logger.warning(
            "ANTHROPIC_API_KEY not set — FunSearch and autoformalization will run "
            "in heuristic/stub mode."
        )

    # Build and run pipeline
    from pipeline.orchestrator import ConjecturePipeline
    logger.info("Building pipeline…")
    pipeline = ConjecturePipeline.build(cfg)

    logger.info("Running pipeline…")
    report = pipeline.run()

    # Save and display
    out_path = pipeline.save_report(report, args.output)
    print(report.summary_str())

    if not args.quiet:
        _print_conjecture_table(report.conjectures)

    print(f"\nFull report → {out_path}")
    return 0


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def banner() -> str:
    return r"""
 ╔══════════════════════════════════════════════════════════╗
 ║   Autonomous Graph Theory Conjecture Pipeline            ║
 ║   Stages: TxGraffiti → Falsification → Lean4 → Prover   ║
 ╚══════════════════════════════════════════════════════════╝
"""


def _print_conjecture_table(conjectures) -> None:
    from conjecture import ConjectureStatus

    status_icon = {
        ConjectureStatus.PROPOSED:    "○",
        ConjectureStatus.FALSIFIED:   "✗",
        ConjectureStatus.SURVIVED:    "~",
        ConjectureStatus.FORMALIZED:  "◆",
        ConjectureStatus.PROVEN:      "✓",
        ConjectureStatus.PROOF_FAILED:"!",
    }

    print("\n  Conjecture summary:")
    print(f"  {'ID':8s}  {'Gen':10s}  {'Status':12s}  Statement")
    print("  " + "-" * 75)
    for c in conjectures:
        icon = status_icon.get(c.status, "?")
        stmt = c.statement[:55] + ("…" if len(c.statement) > 55 else "")
        print(f"  {c.id:8s}  {c.generation_method:10s}  "
              f"{icon} {c.status.value:10s}  {stmt}")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
