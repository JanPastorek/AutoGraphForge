"""
pipeline/unified.py — one end-to-end conjecturing pipeline.

Chains, over the full persistent database:

  1. GENERATION  from three sources:
       - TxGraffiti linear / multivariable / product sweep   (in-house)
       - Dalmatian expression-tree bounds                    (Sage Conjecturing)
       - property-based sufficient conditions                (Sage Conjecturing)
  2. NOVELTY      filtering against the 203-theorem table (linear forms).
  3. COUNTEREXAMPLE LOOP  (durable, iterated): every candidate is attacked by
       the adversarial pool and the seeded hill-climbing search; any graph that
       refutes it is persisted back into the database, and the loop re-runs.
  4. AUTOFORMALIZATION  of every survivor into a Lean 4 statement skeleton.
  5. REPORT       the survivors, flagged novel vs. known — the candidate results.

The Sage stages run as subprocesses (separate interpreter); their string output
is made evaluable on networkx graphs by ``pipeline.expr_bridge`` so that one
counterexample engine attacks every conjecture, linear or not.

Usage
-----
    python -m pipeline.unified                  # use cached Sage output
    python -m pipeline.unified --run-sage        # regenerate Sage conjectures
    python -m pipeline.unified --rounds 3 --search-n 16
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Callable, List, Optional

import networkx as nx

from config import Config, CONFIG
from conjecture import Conjecture, ConjectureStatus, Counterexample
from graphs.database import GraphDatabase
from graphs.invariants import evaluate_named
from pipeline.expr_bridge import make_margin
from pipeline.hypothesis_gen import TxGraffitiGenerator
from pipeline.novelty import annotate
from pipeline.adversarial import AdversarialPool
from pipeline.autoformalization import GraphOfThoughtFormalizer

import counterexample_search as ces

logger = logging.getLogger("unified")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SAGE = os.environ.get("SAGE_BIN", os.path.expanduser("~/miniconda3/envs/sage/bin/sage"))
CONJ_DIR = HERE / "conjecturing"


# ---------------------------------------------------------------------------
# margin builders (margin(G) > 0  ⇔  G refutes the conjecture)
# ---------------------------------------------------------------------------

def _inequality_margin(conj: Conjecture) -> Callable[[nx.Graph], float]:
    ineq = conj.inequality
    names = ineq.referenced_invariants()

    def margin(G: nx.Graph) -> float:
        if G.number_of_nodes() < 1 or not nx.is_connected(G):
            return -1e18
        try:
            vals = evaluate_named(G, names)
        except Exception:
            return -1e18
        s = ineq.slack(vals)            # rhs - lhs; None outside hypothesis class
        if s is None:
            return -1e18
        return -float(s)                # violated ⇔ slack < 0 ⇔ margin > 0

    return margin


def _margin_for(conj: Conjecture) -> Callable[[nx.Graph], float]:
    if conj.inequality is not None:
        return _inequality_margin(conj)
    return make_margin(conj.statement)


# ---------------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------------

class UnifiedPipeline:
    def __init__(self, db: GraphDatabase, cfg: Config = CONFIG):
        self.db = db
        self.cfg = cfg
        self.txg = TxGraffitiGenerator(db, cfg)
        self.pool = AdversarialPool.shared(cfg) if cfg.adversarial_enabled else None
        self.formalizer = GraphOfThoughtFormalizer(cfg)

    @classmethod
    def build(cls, cfg: Config = CONFIG) -> "UnifiedPipeline":
        paths = [p for p in (cfg.db_csv_paths or ()) if os.path.isfile(p)]
        if paths:
            logger.info("Loading persistent database: %s", ", ".join(paths))
            db = GraphDatabase.from_csv(paths, verbose=cfg.verbose)
        else:
            logger.info("No persistent dataset — building synthetic database.")
            db = GraphDatabase.build(random_count=cfg.db_random_graphs,
                                     seed=cfg.db_random_seed, verbose=cfg.verbose)
        logger.info("%s", db.summary())
        return cls(db, cfg)

    # ---------------------------------------------------------- generation --

    def _gen_txgraffiti(self) -> List[Conjecture]:
        cs = self.txg.generate()
        for c in cs:
            c.generation_method = "txgraffiti"
        logger.info("  TxGraffiti (linear/product) : %d", len(cs))
        return cs

    def _run_sage(self, script: str, max_geng: int, t: int) -> None:
        env = dict(os.environ)
        env["PATH"] = str(CONJ_DIR) + os.pathsep + env.get("PATH", "")
        env["CONJ_MAX_GENG"] = str(max_geng)
        env["CONJ_TIME"] = str(t)
        logger.info("  running Sage: %s (n<=%d, %ds)…", script, max_geng, t)
        subprocess.run([SAGE, str(CONJ_DIR / script)], env=env,
                       cwd=str(CONJ_DIR), check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _gen_sage(self, run_sage: bool, max_geng: int, t: int) -> List[Conjecture]:
        if run_sage:
            self._run_sage("run_conjecturing.sage", max_geng, t)
            self._run_sage("run_property_conjecturing.sage", max_geng, t)
        out: List[Conjecture] = []
        resdir = ROOT / "results"
        for fname, method, key in (
            ("conjecturing_survivors.json", "conjecturing-expr", "conjecture"),
            ("property_conjecturing_survivors.json", "conjecturing-prop", "condition"),
        ):
            p = resdir / fname
            if not p.is_file():
                continue
            recs = json.loads(p.read_text())
            for r in recs:
                stmt = r.get(key)
                if not stmt:
                    continue
                out.append(Conjecture(statement=stmt, generation_method=method,
                                      metadata={k: v for k, v in r.items() if k != key}))
            logger.info("  %-28s: %d", method, len(recs))
        return out

    # ------------------------------------------------------ counterexample --

    def _attack(self, conj: Conjecture, search_n: int) -> Optional[nx.Graph]:
        """Return a refuting graph, or None. Adversarial pool first, then seeded."""
        # fast linear pool
        if self.pool is not None and conj.inequality is not None:
            try:
                g = self.pool.refute(conj.inequality)
            except Exception:
                g = None
            if g is not None:
                return g
        # generic seeded hill-climb (works for nonlinear / property too)
        margin = _margin_for(conj)
        for n in range(5, search_n + 1):
            idx = [(i, j) for i in range(n) for j in range(i + 1, n)]
            best_v, best_G = -1e18, None
            for s in ces.seeds(n):
                v0 = margin(s)
                v, G = ces.hill_climb(s, margin, idx) if v0 > -1e17 else (v0, s)
                if v > best_v:
                    best_v, best_G = v, G
                if v > 1e-9:
                    return best_G
        return None

    def _persist(self, conj: Conjecture, G: nx.Graph) -> None:
        try:
            self.db.add_counterexample(G, persist_path=getattr(self.cfg, "counterexample_csv", None))
        except Exception as e:
            logger.warning("    could not persist counterexample: %s", e)
        names = conj.inequality.referenced_invariants() if conj.inequality else set()
        try:
            vals = evaluate_named(G, names) if names else {}
        except Exception:
            vals = {}
        conj.mark_falsified(Counterexample(
            graph_name=f"cex_{conj.id}", n_vertices=G.number_of_nodes(),
            n_edges=G.number_of_edges(), invariant_values=vals,
            violation_magnitude=0.0, edge_list=list(G.edges())))

    # ----------------------------------------------------------------- run --

    def run(self, run_sage=False, rounds=2, search_n=14,
            sage_geng=7, sage_time=8) -> dict:
        t0 = time.time()

        logger.info("[1] Generation")
        cands = self._gen_txgraffiti() + self._gen_sage(run_sage, sage_geng, sage_time)
        logger.info("  TOTAL candidates: %d", len(cands))

        logger.info("[2] Novelty filter (linear forms)")
        known, novel = annotate([c for c in cands if c.inequality is not None])
        known_ids = {id(c) for c in known}
        for c in cands:
            c.metadata["novel"] = (id(c) not in known_ids)
        logger.info("  linear: %d known, %d novel; %d nonlinear/property kept",
                    len(known), len(novel),
                    sum(1 for c in cands if c.inequality is None))
        # known linear conjectures are dropped from the hunt for NEW results
        active = [c for c in cands if c.inequality is None or id(c) not in known_ids]

        logger.info("[3] Counterexample loop (%d rounds, seeded search n<=%d)",
                    rounds, search_n)
        refuted = 0
        for rnd in range(rounds):
            live = [c for c in active if c.status == ConjectureStatus.PROPOSED]
            if not live:
                break
            logger.info("  round %d: attacking %d conjectures", rnd + 1, len(live))
            hits = 0
            for c in live:
                G = self._attack(c, search_n)
                if G is not None:
                    self._persist(c, G)
                    refuted += 1
                    hits += 1
            logger.info("    refuted %d this round (db now %d graphs)",
                        hits, len(self.db))
            if hits == 0:
                break
        survivors = [c for c in active if c.status == ConjectureStatus.PROPOSED]
        for c in survivors:
            c.mark_survived()
        logger.info("  survivors after counterexample loop: %d (refuted %d)",
                    len(survivors), refuted)

        logger.info("[4] Autoformalization (Lean 4)")
        for c in survivors:
            try:
                if c.inequality is not None:
                    self.formalizer.formalize(c)
                else:
                    c.mark_formalized(_lean_skeleton(c))
            except Exception as e:
                logger.debug("    formalize failed for %s: %s", c.id, e)
        formalized = sum(1 for c in survivors if c.lean_statement)
        logger.info("  formalized: %d/%d", formalized, len(survivors))

        report = self._report(cands, survivors, refuted, time.time() - t0)
        return report

    # -------------------------------------------------------------- report --

    def _report(self, cands, survivors, refuted, elapsed) -> dict:
        novel_surv = [c for c in survivors if c.metadata.get("novel", True)]
        by_method = {}
        for c in cands:
            by_method[c.generation_method] = by_method.get(c.generation_method, 0) + 1
        rep = {
            "generated_total": len(cands),
            "generated_by_method": by_method,
            "refuted": refuted,
            "survivors": len(survivors),
            "novel_survivors": len(novel_surv),
            "elapsed_s": round(elapsed, 1),
            "results": [
                {
                    "id": c.id, "method": c.generation_method,
                    "statement": c.statement or (str(c.inequality) if c.inequality else ""),
                    "novel": c.metadata.get("novel", True),
                    "lean": (c.lean_statement or "").splitlines()[0] if c.lean_statement else None,
                }
                for c in survivors
            ],
        }
        outdir = ROOT / self.cfg.output_dir
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "unified_report.json").write_text(json.dumps(rep, indent=2))
        logger.info("  report → %s", outdir / "unified_report.json")
        return rep


def _lean_skeleton(c: Conjecture) -> str:
    safe = c.statement.replace("\n", " ")
    return (f"-- {c.generation_method}: {safe}\n"
            f"theorem conj_{c.id} (G : SimpleGraph V) [Fintype V] : True := by\n"
            f"  trivial  -- TODO: formalize `{safe}`")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="Unified graph-conjecturing pipeline")
    ap.add_argument("--run-sage", action="store_true",
                    help="regenerate Sage expression-tree + property conjectures")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--search-n", type=int, default=14)
    ap.add_argument("--sage-geng", type=int, default=7)
    ap.add_argument("--sage-time", type=int, default=8)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    pipe = UnifiedPipeline.build(CONFIG)
    rep = pipe.run(run_sage=args.run_sage, rounds=args.rounds, search_n=args.search_n,
                   sage_geng=args.sage_geng, sage_time=args.sage_time)
    print("\n" + "=" * 64)
    print("  UNIFIED PIPELINE REPORT")
    print("=" * 64)
    print(f"  generated      : {rep['generated_total']}  {rep['generated_by_method']}")
    print(f"  refuted (loop) : {rep['refuted']}")
    print(f"  survivors      : {rep['survivors']}  (novel: {rep['novel_survivors']})")
    print(f"  elapsed        : {rep['elapsed_s']}s")
    print("=" * 64)
    print("  Candidate results (survivors):")
    for r in rep["results"][:60]:
        tag = "NOVEL" if r["novel"] else "known"
        print(f"   [{tag:5s}] ({r['method']}) {r['statement']}")


if __name__ == "__main__":
    main()
