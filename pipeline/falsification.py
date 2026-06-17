"""
pipeline/falsification.py — Stage 2: Iterative Falsification Loop

Four complementary falsification strategies:

  Z3Falsifier           — SAT/SMT encoding of small graphs in Z3.
  MCTSFalsifier         — UCT bandit search over edge modifications.
  VNSFalsifier          — Variable Neighborhood Search.
  CrossEntropyFalsifier — Probabilistic edge-distribution optimisation.

FalsificationOrchestrator runs all four in sequence and returns the first
counterexample found (or None if all strategies fail).
"""

from __future__ import annotations

import logging
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np

from config import Config, CONFIG
from conjecture import Conjecture, Counterexample
from graphs.invariants import evaluate_all, evaluate_fast, evaluate_named, INVARIANTS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class FalsificationResult:
    falsified: bool = False
    counterexample_graph: Optional[nx.Graph] = None
    counterexample_name: str = ""
    invariant_values: Dict[str, float] = field(default_factory=dict)
    violation: float = 0.0          # |slack| when negative
    strategy_used: str = ""
    time_s: float = 0.0

    def to_counterexample(self) -> Optional[Counterexample]:
        if not self.falsified or self.counterexample_graph is None:
            return None
        G = self.counterexample_graph
        return Counterexample(
            graph_name=self.counterexample_name,
            n_vertices=G.number_of_nodes(),
            n_edges=G.number_of_edges(),
            invariant_values=self.invariant_values,
            violation_magnitude=self.violation,
            edge_list=list(G.edges()),
        )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _evaluate_conjecture(
    G: nx.Graph, conjecture: Conjecture
) -> Tuple[Optional[bool], Optional[float]]:
    """
    Return (holds, slack) for a conjecture evaluated on G.
    slack < 0  ⟹  conjecture violated  ⟹  G is a counterexample.
    """
    if conjecture.inequality is None:
        return None, None
    # Evaluate exactly the invariants this conjecture reads — including the
    # hypothesis boolean and any multivariable RHS terms, which the fast subset
    # would otherwise omit (leaving the conjecture untestable).
    inv = evaluate_named(G, conjecture.inequality.referenced_invariants())
    holds = conjecture.inequality.evaluate(inv)
    slack = conjecture.inequality.slack(inv)
    return holds, slack


def _result_from_graph(
    G: nx.Graph, conjecture: Conjecture, strategy: str, t: float
) -> Optional[FalsificationResult]:
    """Build a FalsificationResult if G violates the conjecture, else None."""
    holds, slack = _evaluate_conjecture(G, conjecture)
    if holds is False and slack is not None:
        inv = evaluate_all(G)
        return FalsificationResult(
            falsified=True,
            counterexample_graph=G.copy(),
            counterexample_name=f"cex_{strategy}",
            invariant_values=inv,
            violation=abs(slack),
            strategy_used=strategy,
            time_s=t,
        )
    return None


# ---------------------------------------------------------------------------
# Z3 Falsifier
# ---------------------------------------------------------------------------

class Z3Falsifier:
    """
    SAT/SMT-based falsifier using the z3-solver Python package.

    For a conjecture  inv_a(G) ≤ coeff·inv_b(G) + offset, we search for a
    graph G on n vertices (n ∈ {5, …, cfg.z3_max_n}) such that
        inv_a(G) > coeff·inv_b(G) + offset.

    Supported invariant pairs (those with compact SMT encodings):
      α (independence), ω (clique), χ (chromatic), γ (domination), ν (matching),
      n, m, Δ, δ

    For unsupported pairs the method returns None immediately (caller tries VNS/CE).
    """

    SUPPORTED = {"alpha", "omega", "chi", "gamma", "nu", "n", "m", "Delta", "delta"}

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def falsify(self, conjecture: Conjecture) -> Optional[FalsificationResult]:
        if not self.cfg.z3_enabled:
            return None
        if conjecture.inequality is None:
            return None
        ineq = conjecture.inequality
        if ineq.extra_terms or ineq.hypothesis:
            # The SMT encoding below only models a single inv_a ≤ c·inv_b + off
            # bound; multivariable / class-conditioned conjectures are left to
            # the search-based falsifiers (MCTS / VNS / CE).
            logger.debug("[Z3] Multivariable/conditioned conjecture — skipping")
            return None
        if ineq.inv_a not in self.SUPPORTED or ineq.inv_b not in self.SUPPORTED:
            logger.debug("[Z3] Unsupported invariant pair (%s, %s) — skipping", ineq.inv_a, ineq.inv_b)
            return None

        try:
            import z3
        except ImportError:
            logger.warning("[Z3] z3-solver not installed — skipping Z3 falsification")
            return None

        t0 = time.time()
        logger.debug("[Z3] Trying to falsify: %s", conjecture.statement)

        for n in range(4, self.cfg.z3_max_n + 1):
            G = self._z3_search(conjecture, n, z3)
            if G is not None:
                t = time.time() - t0
                res = _result_from_graph(G, conjecture, "z3", t)
                if res:
                    logger.info("[Z3] Counterexample found (n=%d) in %.2fs", n, t)
                    return res

        logger.debug("[Z3] No counterexample found up to n=%d", self.cfg.z3_max_n)
        return None

    # --------------------------------------------------------------- encoding

    def _z3_search(
        self, conjecture: Conjecture, n: int, z3
    ) -> Optional[nx.Graph]:
        """
        Encode graph on n vertices + negated conjecture, call Z3, decode graph.
        """
        solver = z3.Solver()
        solver.set("timeout", self.cfg.z3_timeout_ms)

        ineq = conjecture.inequality

        # -- Edge variables --
        e: Dict[Tuple[int, int], z3.BoolRef] = {}
        for i in range(n):
            for j in range(i + 1, n):
                e[(i, j)] = z3.Bool(f"e_{i}_{j}")

        def edge(u: int, v: int):
            if u == v:
                return z3.BoolVal(False)
            return e[(min(u, v), max(u, v))]

        # -- Degree integer variables (used by Δ, δ, m) --
        deg = [z3.Int(f"d_{v}") for v in range(n)]
        for v in range(n):
            solver.add(
                deg[v] == z3.Sum([z3.If(edge(v, u), 1, 0) for u in range(n) if u != v])
            )
            solver.add(deg[v] >= 0)

        # -- Invariant bounds --
        inv_a_var = z3.Int("inv_a")
        inv_b_var = z3.Int("inv_b")

        ok = self._encode_lower_bound(inv_a_var, ineq.inv_a, n, e, deg, edge, solver, z3)
        if not ok:
            return None
        ok = self._encode_upper_bound(inv_b_var, ineq.inv_b, n, e, deg, edge, solver, z3)
        if not ok:
            return None

        # -- Negate the conjecture: inv_a > coeff * inv_b + offset --
        solver.add(
            z3.ToReal(inv_a_var) > ineq.coeff_b * z3.ToReal(inv_b_var) + ineq.offset
        )

        result = solver.check()
        if result != z3.sat:
            return None

        model = solver.model()
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for (i, j), var in e.items():
            if z3.is_true(model.eval(var)):
                G.add_edge(i, j)
        return G

    # -- encoding helpers --

    def _encode_lower_bound(
        self, var, inv_name: str, n: int, e, deg, edge, solver, z3
    ) -> bool:
        """Encode: var ≤ inv_name(G)  (so a violation requires inv_a > rhs)."""
        if inv_name == "n":
            solver.add(var == n)
        elif inv_name == "m":
            solver.add(var == z3.Sum([z3.If(e[k], 1, 0) for k in e]))
        elif inv_name == "Delta":
            solver.add(var == z3.If(n == 0, 0, z3.Max(*deg) if n > 1 else deg[0]))
        elif inv_name == "delta":
            solver.add(var == z3.If(n == 0, 0, z3.Min(*deg) if n > 1 else deg[0]))
        elif inv_name == "alpha":
            self._encode_independence(var, n, e, edge, solver, z3, direction="lower")
        elif inv_name == "omega":
            self._encode_clique(var, n, e, edge, solver, z3, direction="lower")
        elif inv_name == "chi":
            # χ ≥ ω ≥ var; we can only encode a lower bound via clique
            self._encode_clique(var, n, e, edge, solver, z3, direction="lower")
        elif inv_name == "gamma":
            self._encode_domination(var, n, e, edge, solver, z3, direction="lower")
        elif inv_name == "nu":
            self._encode_matching(var, n, e, edge, solver, z3, direction="lower")
        else:
            return False
        return True

    def _encode_upper_bound(
        self, var, inv_name: str, n: int, e, deg, edge, solver, z3
    ) -> bool:
        """Encode: var ≥ inv_name(G)  (so conjecture_rhs = coeff*var+offset ≥ coeff*inv_b+offset)."""
        if inv_name == "n":
            solver.add(var == n)
        elif inv_name == "m":
            solver.add(var == z3.Sum([z3.If(e[k], 1, 0) for k in e]))
        elif inv_name == "Delta":
            solver.add(var == z3.If(n == 0, 0, z3.Max(*deg) if n > 1 else deg[0]))
        elif inv_name == "delta":
            solver.add(var == z3.If(n == 0, 0, z3.Min(*deg) if n > 1 else deg[0]))
        elif inv_name == "alpha":
            self._encode_independence(var, n, e, edge, solver, z3, direction="upper")
        elif inv_name == "omega":
            self._encode_clique(var, n, e, edge, solver, z3, direction="upper")
        elif inv_name == "chi":
            self._encode_coloring_upper(var, n, e, edge, solver, z3)
        elif inv_name == "gamma":
            self._encode_domination(var, n, e, edge, solver, z3, direction="upper")
        elif inv_name == "nu":
            self._encode_matching(var, n, e, edge, solver, z3, direction="upper")
        else:
            return False
        return True

    def _encode_independence(self, var, n, e, edge, solver, z3, direction):
        """
        α(G) encoded via independent-set indicator variables.
        direction="lower"  →  var ≤ α(G)   (there exists an IS of size ≥ var)
        direction="upper"  →  var ≥ α(G)   (no IS of size > var — approximated by
                                              finding the max IS size with a counter)
        We use a shared integer variable 'alpha_val' + IS indicators.
        """
        x = [z3.Bool(f"is_{i}_{id(var)}") for i in range(n)]
        alpha_val = z3.Sum([z3.If(x[i], 1, 0) for i in range(n)])
        # Independence constraint
        for i in range(n):
            for j in range(i + 1, n):
                solver.add(z3.Implies(z3.And(x[i], x[j]), z3.Not(edge(i, j))))
        if direction == "lower":
            solver.add(var <= alpha_val)
        else:
            # var ≥ α: we encode that no IS of size > var exists
            # (hard to encode exactly; we encode var == alpha_val for the IS found)
            solver.add(var == alpha_val)

    def _encode_clique(self, var, n, e, edge, solver, z3, direction):
        y = [z3.Bool(f"cl_{i}_{id(var)}") for i in range(n)]
        omega_val = z3.Sum([z3.If(y[i], 1, 0) for i in range(n)])
        for i in range(n):
            for j in range(i + 1, n):
                solver.add(z3.Implies(z3.And(y[i], y[j]), edge(i, j)))
        if direction == "lower":
            solver.add(var <= omega_val)
        else:
            solver.add(var == omega_val)

    def _encode_coloring_upper(self, var, n, e, edge, solver, z3):
        """
        χ(G) ≤ var: encode a proper var-colouring (var is fixed to a small value).
        Since var is a Z3 Int, we try each concrete value k = 1..n.
        We create colour variables parameterised on k and use a disjunction.
        For performance we pick k = min(n, 4) as an upper bound attempt.
        """
        k_max = min(n, 5)
        # Try each k and assert χ ≤ k for some k
        color_constraints = []
        for k in range(1, k_max + 1):
            c = [[z3.Bool(f"col_{v}_{col}_{k}_{id(var)}") for col in range(k)] for v in range(n)]
            # Each vertex has exactly one colour
            per_vertex = [z3.PbEq([(c[v][col], 1) for col in range(k)], 1) for v in range(n)]
            # No monochromatic edges
            no_conflict = [
                z3.Implies(edge(i, j), z3.Not(z3.And(c[i][col], c[j][col])))
                for i in range(n)
                for j in range(i + 1, n)
                for col in range(k)
            ]
            feasible = z3.And(*per_vertex, *no_conflict)
            color_constraints.append(z3.And(var >= k, var <= k, feasible))
        solver.add(z3.Or(*color_constraints))

    def _encode_domination(self, var, n, e, edge, solver, z3, direction):
        d = [z3.Bool(f"dom_{i}_{id(var)}") for i in range(n)]
        dom_size = z3.Sum([z3.If(d[i], 1, 0) for i in range(n)])
        for v in range(n):
            dominated = z3.Or(d[v], *[z3.And(d[u], edge(u, v)) for u in range(n) if u != v])
            solver.add(dominated)
        if direction == "lower":
            solver.add(var <= dom_size)
        else:
            solver.add(var == dom_size)

    def _encode_matching(self, var, n, e, edge, solver, z3, direction):
        me = {(i, j): z3.Bool(f"me_{i}_{j}_{id(var)}") for i in range(n) for j in range(i + 1, n)}
        # Matching edges must be actual edges
        for (i, j), mv in me.items():
            solver.add(z3.Implies(mv, edge(i, j)))
        # Each vertex in at most one matching edge
        for v in range(n):
            incident = [me[(min(v, u), max(v, u))] for u in range(n) if u != v]
            solver.add(z3.PbLe([(m, 1) for m in incident], 1))
        nu_val = z3.Sum([z3.If(mv, 1, 0) for mv in me.values()])
        if direction == "lower":
            solver.add(var <= nu_val)
        else:
            solver.add(var == nu_val)


# ---------------------------------------------------------------------------
# MCTS Falsifier
# ---------------------------------------------------------------------------

class _MCTSNode:
    __slots__ = ("graph", "parent", "children", "visits", "total_reward")

    def __init__(self, graph: nx.Graph, parent: Optional["_MCTSNode"] = None):
        self.graph = graph.copy()
        self.parent = parent
        self.children: List["_MCTSNode"] = []
        self.visits: int = 0
        self.total_reward: float = 0.0

    def ucb(self, c: float) -> float:
        if self.visits == 0:
            return math.inf
        if self.parent is None or self.parent.visits == 0:
            return self.total_reward / self.visits
        exploitation = self.total_reward / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def is_leaf(self) -> bool:
        return len(self.children) == 0


class MCTSFalsifier:
    """
    UCT (Monte Carlo Tree Search) over the space of n-vertex graphs.

    State    : graph (edge set)
    Action   : add or remove a random edge
    Reward   : −slack(conjecture, G)   (negative slack → conjecture violated → high reward)
    """

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def falsify(self, conjecture: Conjecture) -> Optional[FalsificationResult]:
        if conjecture.inequality is None:
            return None

        t0 = time.time()
        logger.debug("[MCTS] Searching for counterexample to: %s", conjecture.statement)

        n = self.cfg.mcts_n_vertices
        root_G = nx.erdos_renyi_graph(n, 0.4, seed=42)
        root = _MCTSNode(root_G)

        best_violation: float = 0.0
        best_G: Optional[nx.Graph] = None

        for it in range(self.cfg.mcts_iterations):
            # Selection
            node = self._select(root)
            # Expansion
            child = self._expand(node)
            # Simulation (rollout)
            reward, G_sim = self._simulate(child, conjecture)
            # Backpropagation
            self._backpropagate(child, reward)

            # Track best violation
            if reward > best_violation:
                best_violation = reward
                best_G = G_sim

            # Early exit if counterexample found
            if reward > 0:
                t = time.time() - t0
                if best_G is not None:
                    res = _result_from_graph(best_G, conjecture, "mcts", t)
                    if res:
                        logger.info("[MCTS] Counterexample found at iteration %d", it)
                        return res

        logger.debug("[MCTS] No counterexample in %d iterations", self.cfg.mcts_iterations)
        return None

    def _select(self, node: _MCTSNode) -> _MCTSNode:
        while not node.is_leaf():
            node = max(node.children, key=lambda n: n.ucb(self.cfg.mcts_c))
        return node

    def _expand(self, node: _MCTSNode) -> _MCTSNode:
        G = node.graph.copy()
        nodes = list(G.nodes())
        if len(nodes) < 2:
            return node
        # Generate 3 candidate edge-flip children, attach all
        for _ in range(3):
            G2 = G.copy()
            u, v = random.sample(nodes, 2)
            if G2.has_edge(u, v):
                G2.remove_edge(u, v)
            else:
                G2.add_edge(u, v)
            child = _MCTSNode(G2, parent=node)
            node.children.append(child)
        return random.choice(node.children)

    def _simulate(
        self, node: _MCTSNode, conjecture: Conjecture
    ) -> Tuple[float, nx.Graph]:
        G = node.graph.copy()
        nodes = list(G.nodes())
        best_reward = -math.inf
        best_G = G.copy()
        # Random rollout: k random flips from current state
        for _ in range(8):
            if len(nodes) >= 2:
                u, v = random.sample(nodes, 2)
                if G.has_edge(u, v):
                    G.remove_edge(u, v)
                else:
                    G.add_edge(u, v)
            _, slack = _evaluate_conjecture(G, conjecture)
            reward = -slack if slack is not None else 0.0
            if reward > best_reward:
                best_reward = reward
                best_G = G.copy()
        return best_reward, best_G

    def _backpropagate(self, node: Optional[_MCTSNode], reward: float) -> None:
        while node is not None:
            node.visits += 1
            node.total_reward += reward
            node = node.parent


# ---------------------------------------------------------------------------
# VNS Falsifier
# ---------------------------------------------------------------------------

class VNSFalsifier:
    """
    Variable Neighborhood Search for graph counterexamples.

    Neighbourhoods (by increasing size k):
      k=1  : flip 1 random edge
      k=2  : flip 2 random edges
      k=3  : flip 3 random edges
      k=4  : rewire a random vertex (disconnect + reconnect randomly)

    Accepts any improvement in slack-minimisation; shakes to a larger
    neighbourhood when stuck and restarts when all neighbourhoods exhausted.
    """

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def falsify(self, conjecture: Conjecture) -> Optional[FalsificationResult]:
        if conjecture.inequality is None:
            return None

        t0 = time.time()
        logger.debug("[VNS] Searching: %s", conjecture.statement)

        def objective(G: nx.Graph) -> float:
            _, slack = _evaluate_conjecture(G, conjecture)
            return -slack if slack is not None else math.inf  # maximise

        n_vertices = random.randint(6, 12)
        G_cur = nx.erdos_renyi_graph(n_vertices, 0.4, seed=random.randint(0, 9999))
        obj_cur = objective(G_cur)
        k_max = self.cfg.vns_k_max

        for iteration in range(self.cfg.vns_iterations):
            k = (iteration % k_max) + 1
            G_new = self._shake(G_cur, k)
            G_opt = self._local_search(G_new, conjecture, objective, steps=15)
            obj_new = objective(G_opt)

            if obj_new > obj_cur:
                G_cur = G_opt
                obj_cur = obj_new
            elif obj_new == obj_cur and random.random() < 0.1:
                G_cur = G_opt  # accept sideways move occasionally

            if obj_cur > 0:
                t = time.time() - t0
                res = _result_from_graph(G_cur, conjecture, "vns", t)
                if res:
                    logger.info("[VNS] Counterexample found at iteration %d", iteration)
                    return res

            # Occasional restart with a fresh random graph
            if iteration % 100 == 99:
                n2 = random.randint(5, 13)
                G_cur = nx.erdos_renyi_graph(n2, random.uniform(0.2, 0.7),
                                             seed=random.randint(0, 99999))
                obj_cur = objective(G_cur)

        logger.debug("[VNS] No counterexample in %d iterations", self.cfg.vns_iterations)
        return None

    def _shake(self, G: nx.Graph, k: int) -> nx.Graph:
        G2 = G.copy()
        nodes = list(G2.nodes())
        if len(nodes) < 2:
            return G2
        if k <= self.cfg.vns_k_max - 1:
            # Flip k edges
            for _ in range(k):
                u, v = random.sample(nodes, 2)
                if G2.has_edge(u, v):
                    G2.remove_edge(u, v)
                else:
                    G2.add_edge(u, v)
        else:
            # Rewire: remove all edges from a random vertex and reconnect
            v = random.choice(nodes)
            nbrs = list(G2.neighbors(v))
            G2.remove_edges_from([(v, u) for u in nbrs])
            new_d = max(1, random.randint(0, len(nodes) - 1))
            for u in random.sample([x for x in nodes if x != v], min(new_d, len(nodes) - 1)):
                G2.add_edge(v, u)
        return G2

    def _local_search(
        self, G: nx.Graph, conjecture: Conjecture, obj_fn, steps: int
    ) -> nx.Graph:
        best = G.copy()
        best_val = obj_fn(best)
        nodes = list(G.nodes())
        for _ in range(steps):
            if len(nodes) < 2:
                break
            u, v = random.sample(nodes, 2)
            G2 = best.copy()
            if G2.has_edge(u, v):
                G2.remove_edge(u, v)
            else:
                G2.add_edge(u, v)
            val = obj_fn(G2)
            if val > best_val:
                best = G2
                best_val = val
        return best


# ---------------------------------------------------------------------------
# Cross-Entropy Falsifier
# ---------------------------------------------------------------------------

class CrossEntropyFalsifier:
    """
    Cross-entropy method for counterexample discovery.

    Maintains a probability distribution p ∈ [0,1]^(n choose 2) over edges.
    Samples graphs, evaluates them, keeps the elite fraction, updates p.

    The update rule:
        p_e ← mean of elite_samples[:, e]
    smoothed towards 0.5 to avoid premature convergence.
    """

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def falsify(self, conjecture: Conjecture) -> Optional[FalsificationResult]:
        if conjecture.inequality is None:
            return None

        t0 = time.time()
        n = self.cfg.ce_n_vertices
        logger.debug("[CE] Cross-entropy search (n=%d): %s", n, conjecture.statement)

        n_edges = n * (n - 1) // 2
        edge_idx = [(i, j) for i in range(n) for j in range(i + 1, n)]
        p = np.full(n_edges, 0.5)

        N = self.cfg.ce_population
        elite_k = max(1, int(N * self.cfg.ce_elite_frac))
        rng = np.random.default_rng(seed=99)

        for it in range(self.cfg.ce_iterations):
            # Sample N graphs
            samples = rng.random((N, n_edges)) < p
            rewards = np.zeros(N)

            for s_idx, mask in enumerate(samples):
                G = nx.Graph()
                G.add_nodes_from(range(n))
                for e_idx, present in enumerate(mask):
                    if present:
                        G.add_edge(*edge_idx[e_idx])
                _, slack = _evaluate_conjecture(G, conjecture)
                rewards[s_idx] = -slack if slack is not None else 0.0

            # Identify elite samples
            thresh = np.sort(rewards)[-elite_k]
            elite_mask = rewards >= thresh
            elite_samples = samples[elite_mask]

            # Update distribution (smoothed)
            p_new = elite_samples.mean(axis=0)
            p = 0.7 * p_new + 0.3 * p  # smoothing

            # Check best sample
            best_idx = int(np.argmax(rewards))
            if rewards[best_idx] > 0:
                t = time.time() - t0
                G_best = nx.Graph()
                G_best.add_nodes_from(range(n))
                for e_idx, present in enumerate(samples[best_idx]):
                    if present:
                        G_best.add_edge(*edge_idx[e_idx])
                res = _result_from_graph(G_best, conjecture, "cross_entropy", t)
                if res:
                    logger.info("[CE] Counterexample found at iteration %d", it)
                    return res

        logger.debug("[CE] No counterexample in %d iterations", self.cfg.ce_iterations)
        return None


# ---------------------------------------------------------------------------
# Adversarial Falsifier (structure-targeted pool)
# ---------------------------------------------------------------------------

class AdversarialFalsifier:
    """
    Test the conjecture against a fixed pool of structure-targeted graphs with
    exact invariant values (barbells, clique+tail, spiders, class generators, …).
    Refutes loose database-only bounds (δ ≤ λ+5, χ ≤ avg_deg+3) instantly.

    Returns None when disabled or when the conjecture uses an invariant the pool
    cannot certify (those fall through to the search-based falsifiers).
    """

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg

    def falsify(self, conjecture: Conjecture) -> Optional[FalsificationResult]:
        if not getattr(self.cfg, "adversarial_enabled", True):
            return None
        if conjecture.inequality is None:
            return None
        from pipeline.adversarial import AdversarialPool
        t0 = time.time()
        pool = AdversarialPool.shared(self.cfg)
        G = pool.refute(conjecture.inequality)
        if G is None:
            return None
        res = _result_from_graph(G, conjecture, "adversarial", time.time() - t0)
        if res:
            logger.info("[Adversarial] counterexample found (n=%d)", G.number_of_nodes())
        return res


# ---------------------------------------------------------------------------
# Orchestrator for all strategies
# ---------------------------------------------------------------------------

class FalsificationOrchestrator:
    """
    Run Adversarial → Z3 → MCTS → VNS → Cross-Entropy in sequence until one
    succeeds. On success, the counterexample graph is returned for database
    re-ingestion. The adversarial pool runs first: it is cheap and catches the
    structural artifacts the search heuristics tend to miss.
    """

    def __init__(self, cfg: Config = CONFIG):
        self.cfg = cfg
        self.adversarial = AdversarialFalsifier(cfg)
        self.z3      = Z3Falsifier(cfg)
        self.mcts    = MCTSFalsifier(cfg)
        self.vns     = VNSFalsifier(cfg)
        self.ce      = CrossEntropyFalsifier(cfg)

    def test(self, conjecture: Conjecture) -> FalsificationResult:
        """
        Return a FalsificationResult (falsified=True|False).
        Updates conjecture.status in place.
        """
        strategies = [
            ("Adversarial",  self.adversarial.falsify),
            ("Z3",           self.z3.falsify),
            ("MCTS",         self.mcts.falsify),
            ("VNS",          self.vns.falsify),
            ("CrossEntropy", self.ce.falsify),
        ]
        for name, fn in strategies:
            logger.debug("[Falsifier] Trying %s for %s", name, conjecture.id)
            try:
                result = fn(conjecture)
            except Exception as exc:
                logger.warning("[Falsifier] %s raised: %s", name, exc)
                result = None

            if result is not None and result.falsified:
                cex = result.to_counterexample()
                if cex is not None:
                    conjecture.mark_falsified(cex)
                return result

        # All strategies failed — conjecture survived
        conjecture.mark_survived()
        return FalsificationResult(falsified=False)
