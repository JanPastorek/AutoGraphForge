"""
pipeline/orchestrator.py — top-level pipeline coordinator

Wires together all four stages and manages:
  - The iterative falsification feedback loop (counterexamples → db)
  - Progress logging
  - JSON result serialisation
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from config import Config, CONFIG
from conjecture import Conjecture, ConjectureStatus
from graphs.database import GraphDatabase
from legacy.autoformalization import GraphOfThoughtFormalizer
from pipeline.falsification import FalsificationOrchestrator
from legacy.hypothesis_gen import FunSearchGenerator, TxGraffitiGenerator
from pipeline.theorem_prover import NeuralProverClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------------

@dataclass
class PipelineReport:
    total_generated: int = 0
    falsified: int = 0
    survived: int = 0
    formalized: int = 0
    proven: int = 0
    proof_failed: int = 0
    counterexamples_fed_back: int = 0
    elapsed_s: float = 0.0
    conjectures: List[Conjecture] = field(default_factory=list)

    def summary_str(self) -> str:
        lines = [
            "=" * 60,
            "  CONJECTURE PIPELINE REPORT",
            "=" * 60,
            f"  Generated           : {self.total_generated}",
            f"  Falsified           : {self.falsified}",
            f"  Survived falsif.    : {self.survived}",
            f"  Formalized (Lean 4) : {self.formalized}",
            f"  Proven              : {self.proven}",
            f"  Proof failed        : {self.proof_failed}",
            f"  CEX fed back to db  : {self.counterexamples_fed_back}",
            f"  Total time          : {self.elapsed_s:.1f}s",
            "=" * 60,
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "total_generated": self.total_generated,
            "falsified": self.falsified,
            "survived": self.survived,
            "formalized": self.formalized,
            "proven": self.proven,
            "proof_failed": self.proof_failed,
            "counterexamples_fed_back": self.counterexamples_fed_back,
            "elapsed_s": self.elapsed_s,
            "conjectures": [c.to_dict() for c in self.conjectures],
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info("Report saved to %s", path)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class ConjecturePipeline:
    """
    Autonomous graph theory conjecture pipeline.

    Stages
    ------
    1. Hypothesis generation (TxGraffiti + FunSearch)
    2. Iterative falsification loop (Z3 + MCTS + VNS + CrossEntropy)
       └─ feedback: counterexamples → graph database
    3. Autoformalization (Graph-of-Thought → Lean 4)
    4. Theorem proving (Goedel-Prover / DeepSeek-Prover-V2 stubs)

    Usage
    -----
    >>> pipeline = ConjecturePipeline.build(cfg)
    >>> report = pipeline.run()
    >>> print(report.summary_str())
    """

    def __init__(
        self,
        db: GraphDatabase,
        hyp_gen_txg: TxGraffitiGenerator,
        hyp_gen_fun: FunSearchGenerator,
        falsifier: FalsificationOrchestrator,
        formalizer: GraphOfThoughtFormalizer,
        prover: NeuralProverClient,
        cfg: Config = CONFIG,
    ):
        self.db = db
        self.txg = hyp_gen_txg
        self.fun = hyp_gen_fun
        self.falsifier = falsifier
        self.formalizer = formalizer
        self.prover = prover
        self.cfg = cfg

    # ------------------------------------------------------------ factory --

    @classmethod
    def build(cls, cfg: Config = CONFIG) -> "ConjecturePipeline":
        import os
        logger.info("Building graph database…")
        paths = [p for p in (cfg.db_csv_paths or ()) if os.path.isfile(p)]
        if paths:
            logger.info("Loading persistent dataset(s): %s", ", ".join(paths))
            db = GraphDatabase.from_csv(paths, verbose=cfg.verbose)
        else:
            logger.info("No persistent dataset found — building synthetic database.")
            db = GraphDatabase.build(
                random_count=cfg.db_random_graphs,
                seed=cfg.db_random_seed,
                verbose=cfg.verbose,
            )
        logger.info("%s", db.summary())
        return cls(
            db=db,
            hyp_gen_txg=TxGraffitiGenerator(db, cfg),
            hyp_gen_fun=FunSearchGenerator(db, cfg),
            falsifier=FalsificationOrchestrator(cfg),
            formalizer=GraphOfThoughtFormalizer(cfg),
            prover=NeuralProverClient(cfg),
            cfg=cfg,
        )

    # --------------------------------------------------------------- run --

    def run(self) -> PipelineReport:
        t0 = time.time()
        report = PipelineReport()

        # ── Stage 1: Hypothesis generation ──────────────────────────────
        logger.info("\n[Stage 1] Hypothesis Generation")
        conjectures: List[Conjecture] = []

        txg_conjectures = self.txg.generate()
        logger.info("  TxGraffiti: %d conjectures", len(txg_conjectures))
        conjectures.extend(txg_conjectures)

        if self.cfg.use_funsearch:
            fun_conjectures = self.fun.generate()
            logger.info("  FunSearch : %d conjectures", len(fun_conjectures))
            conjectures.extend(fun_conjectures)

        report.total_generated = len(conjectures)
        logger.info("  Total     : %d conjectures generated", report.total_generated)

        # ── Stage 2: Iterative falsification loop ────────────────────────
        logger.info("\n[Stage 2] Falsification Loop (%d passes)", self.cfg.falsification_rounds)
        survived: List[Conjecture] = []

        for round_idx in range(self.cfg.falsification_rounds):
            active = [c for c in conjectures if c.status == ConjectureStatus.PROPOSED]
            if not active:
                break
            logger.info("  Round %d: testing %d conjectures", round_idx + 1, len(active))

            for c in active:
                result = self.falsifier.test(c)
                if result.falsified and result.counterexample_graph is not None:
                    self.db.add_counterexample(
                        result.counterexample_graph,
                        persist_path=getattr(self.cfg, "counterexample_csv", None),
                    )
                    report.counterexamples_fed_back += 1
                    logger.info(
                        "    ✗ [%s] FALSIFIED by %s — counterexample saved to db",
                        c.id, result.strategy_used,
                    )
                else:
                    logger.info(
                        "    ✓ [%s] survived: %s", c.id, c.statement[:60]
                    )

            # Re-generate after database augmentation on all but last round
            if round_idx < self.cfg.falsification_rounds - 1 and report.counterexamples_fed_back > 0:
                logger.info("  Re-generating conjectures with augmented db…")
                new_txg = self.txg.generate()
                new_proposed = [c for c in new_txg if c.status == ConjectureStatus.PROPOSED]
                conjectures.extend(new_proposed)

        survived = [c for c in conjectures if c.status == ConjectureStatus.SURVIVED]
        report.falsified = sum(1 for c in conjectures if c.status == ConjectureStatus.FALSIFIED)
        report.survived = len(survived)
        logger.info(
            "  Result: %d falsified, %d survived", report.falsified, report.survived
        )

        # ── Stage 3: Autoformalization ───────────────────────────────────
        logger.info("\n[Stage 3] Autoformalization (%d conjectures)", len(survived))
        for c in survived:
            lean_stmt = self.formalizer.formalize(c)
            if lean_stmt:
                logger.info("    ✓ [%s] formalized", c.id)
            else:
                logger.info("    ✗ [%s] formalization failed", c.id)

        formalized = [c for c in survived if c.status == ConjectureStatus.FORMALIZED]
        report.formalized = len(formalized)
        logger.info("  %d/%d conjectures formalized", report.formalized, len(survived))

        # ── Stage 4: Theorem proving ─────────────────────────────────────
        logger.info("\n[Stage 4] Theorem Proving (%d conjectures)", len(formalized))
        for c in formalized:
            resp = self.prover.prove(c)
            if resp.success:
                logger.info("    ✓ [%s] PROVED by %s", c.id, resp.model_name)
            else:
                logger.info("    ✗ [%s] proof failed: %s", c.id, (resp.error or "")[:80])

        report.proven = sum(1 for c in conjectures if c.status == ConjectureStatus.PROVEN)
        report.proof_failed = sum(
            1 for c in conjectures if c.status == ConjectureStatus.PROOF_FAILED
        )

        # ── Finalise ─────────────────────────────────────────────────────
        report.elapsed_s = time.time() - t0
        report.conjectures = conjectures
        return report

    # --------------------------------------------------------- utilities --

    def save_report(self, report: PipelineReport, path: Optional[str] = None) -> Path:
        if path is None:
            os.makedirs(self.cfg.output_dir, exist_ok=True)
            path = os.path.join(self.cfg.output_dir, "conjecture_report.json")
        out = Path(path)
        report.save(out)
        # Also write a plain-text summary
        txt_path = out.with_suffix(".txt")
        txt_path.write_text(report.summary_str() + "\n\n" + self._conj_detail(report), encoding="utf-8")
        logger.info("Plain-text summary → %s", txt_path)
        return out

    @staticmethod
    def _conj_detail(report: PipelineReport) -> str:
        lines = []
        for c in report.conjectures:
            lines.append(f"[{c.id}] {c.status.value.upper():12s} | {c.statement[:80]}")
            if c.lean_statement:
                first_line = c.lean_statement.splitlines()[0]
                lines.append(f"          Lean: {first_line}")
            if c.counterexample:
                cex = c.counterexample
                lines.append(
                    f"          CEX : n={cex.n_vertices}, m={cex.n_edges}, "
                    f"violation={cex.violation_magnitude:.3f}"
                )
        return "\n".join(lines)
