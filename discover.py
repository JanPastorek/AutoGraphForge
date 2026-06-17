#!/usr/bin/env python3
"""
discover.py — autoconjecturing with (a) adversarial counterexample filtering and
(b) product/ratio conjectures.

Pipeline
--------
1. Propose candidate inequalities on the exhaustive n ≤ 9 census (exact values).
     * linear   :  f ≤ c·g + b
     * product  :  t ≤ c·(f·g) + b   and   f·g ≤ c·t + b      (t ∈ {n, m})
   (ratios are linear and already covered:  f/g ≤ c  ⟺  f ≤ c·g.)
2. Keep the tight, non-trivial ones.
3. ADVERSARIAL FILTER: test every survivor on a pool of structure-targeted
   graphs built to break loose bounds — barbells (large δ, small λ), cliques
   with sparse tails (high χ/ω, low avg-deg), spiders (high radius, low γ),
   plus class generators and larger orders. Anything refuted is discarded.
   (This is what kills δ ≤ λ+5, χ ≤ avg_deg+3, etc.)
4. Report the survivors, flagging the classical ones.

Only invariants we can compute *exactly and fast* are used, so the adversarial
test is sound.
"""
from __future__ import annotations

import itertools
import random

import networkx as nx
import numpy as np
from networkx.algorithms.clique import max_weight_clique

import graphs.invariants as I

rng = random.Random(2025)
EPS = 1e-9

# ── exact, fast invariants usable by the adversarial verifier ─────────────
def exact_alpha(G):
    return max_weight_clique(nx.complement(G), weight=None)[1]

def exact_gamma(G):
    nodes = list(G); n = len(nodes)
    for k in range(1, n + 1):
        for s in itertools.combinations(nodes, k):
            dom = set(s)
            for v in s:
                dom.update(G.neighbors(v))
            if len(dom) == n:
                return k
    return n

def inv_exact(G, need_gamma=True):
    n = G.number_of_nodes(); m = G.number_of_edges()
    d = {
        "n": n, "m": m,
        "alpha": exact_alpha(G), "omega": max_weight_clique(G, weight=None)[1],
        "chi": I.chromatic_number(G), "nu": I.matching_number(G),
        "Delta": I.max_degree(G), "delta": I.min_degree(G),
        "kappa": I.vertex_connectivity(G), "lambda": I.edge_connectivity(G),
        "diam": I.diameter(G), "rad": I.radius(G),
        "tri": I.number_of_triangles(G),
        "degeneracy": max(nx.core_number(G).values()) if m else 0,
        "ind_dom": min(len(c) for c in nx.find_cliques(nx.complement(G))),
    }
    d["avg_deg"] = 2 * m / n if n else 0
    d["vertex_cover"] = n - d["alpha"]
    if need_gamma and n <= 14:
        d["gamma"] = exact_gamma(G)
    return d


# ── adversarial pool: structure-targeted graphs (incl. artifact-breakers) ─
def adversarial_graphs():
    # barbells: large δ, tiny λ  → break δ ≤ λ + c
    for k in range(3, 11):
        for p in range(0, 4):
            yield nx.barbell_graph(k, p)
    # lollipops & clique+tail: high χ/ω, low avg-deg  → break χ ≤ avg_deg + c
    for k in range(3, 9):
        for tail in range(1, 12):
            yield nx.lollipop_graph(k, tail)
    # spiders / subdivided stars: high radius, low γ  → break rad ≤ c·γ
    for legs in range(3, 6):
        for L in range(2, 6):
            G = nx.Graph(); nid = 1
            for _ in range(legs):
                prev = 0
                for _ in range(L):
                    G.add_edge(prev, nid); prev = nid; nid += 1
            yield G
    # complete split graphs (clique + independent set)
    for a in range(2, 8):
        for b in range(2, 8):
            G = nx.complete_graph(a)
            for v in range(a, a + b):
                for u in rng.sample(range(a), rng.randint(1, a)):
                    G.add_edge(v, u)
            yield G
    # class generators + random
    for _ in range(250):
        n = rng.randint(6, 18); dreg = rng.randint(2, min(n - 1, 6))
        if (n * dreg) % 2 == 0:
            try:
                yield nx.random_regular_graph(dreg, n, seed=rng.randint(0, 1 << 30))
            except Exception:
                pass
    for _ in range(250):
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        yield nx.bipartite.random_graph(a, b, rng.uniform(.2, .9), seed=rng.randint(0, 1 << 30))
    for _ in range(250):  # k-trees (chordal)
        n = rng.randint(6, 18); k = rng.randint(1, 4)
        G = nx.complete_graph(k + 1); cliques = [tuple(range(k + 1))]
        for v in range(k + 1, n):
            base = rng.choice(cliques); att = rng.sample(base, k)
            for u in att:
                G.add_edge(v, u)
            cliques.append(tuple(att) + (v,))
        yield G
    for _ in range(250):  # complement of triangle-free → α = 2
        n = rng.randint(6, 14); H = nx.gnp_random_graph(n, rng.uniform(.2, .6), seed=rng.randint(0, 1 << 30))
        ch = True
        while ch:
            ch = False
            for a, b, c in itertools.combinations(H.nodes(), 3):
                if H.has_edge(a, b) and H.has_edge(b, c) and H.has_edge(a, c):
                    H.remove_edge(a, b); ch = True; break
        yield nx.complement(H)
    for _ in range(300):
        n = rng.randint(6, 18)
        yield nx.gnp_random_graph(n, rng.uniform(.1, .8), seed=rng.randint(0, 1 << 30))
    for n in range(3, 24):
        yield nx.path_graph(n); yield nx.cycle_graph(n)
    for n in range(3, 12):
        yield nx.complete_graph(n); yield nx.wheel_graph(n); yield nx.star_graph(n)


print("Building adversarial pool…", flush=True)
POOL = []
seen = set()
for G in adversarial_graphs():
    if G.number_of_nodes() < 2 or G.number_of_nodes() > 20 or not nx.is_connected(G):
        continue
    h = nx.weisfeiler_lehman_graph_hash(G)
    if h in seen:
        continue
    seen.add(h)
    POOL.append(inv_exact(G))
print(f"  pool: {len(POOL)} distinct connected adversarial graphs\n", flush=True)


def adversarial_ok(slack, need):
    """Return (survived, worst_slack, n_tight, counterexample_dict)."""
    worst = float("inf"); tight = 0; cex = None
    for d in POOL:
        if not need <= d.keys():
            continue
        s = slack(d)
        if s < worst:
            worst = s
        if abs(s) < 1e-9:
            tight += 1
        if s < -1e-9:
            cex = d
            return False, s, tight, cex
    return True, worst, tight, None


# ── propose on the exact census (sampled for the product sweep) ───────────
import csv, sys
csv.field_size_limit(sys.maxsize)
CENSUS = "database/census_le9.csv"
CORE = ["alpha", "omega", "chi", "gamma", "nu", "kappa", "lambda", "delta",
        "Delta", "rad", "diam", "ind_dom"]
rows = []
with open(CENSUS) as fh:
    for r in csv.DictReader(fh):
        try:
            rows.append({k: float(r[k]) for k in (CORE + ["n", "m"]) if r.get(k) not in ("", None)})
        except Exception:
            pass
rows = [r for r in rows if all(k in r for k in CORE + ["n", "m"])]
print(f"Proposing on {len(rows)} exact census graphs (n ≤ 9)\n", flush=True)
arr = {k: np.array([r[k] for r in rows]) for k in CORE + ["n", "m"]}

# factor set for products, including the Δ+1 / δ+1 shifts of greedy/domination
FACTORS = [(c, 0) for c in CORE] + [("Delta", 1), ("delta", 1)]
def fval(d, fac):
    name, sh = fac
    return d.get(name, np.nan) + sh
def flabel(fac):
    name, sh = fac
    return f"({name}+{sh})" if sh else name

COEFFS = [0.5, 1.0, 2.0]
candidates = []   # (label, kind, need, slack_fn)

# product conjectures:  t ≤ c·(f·g) + b   and   f·g ≤ c·t + b
for fa, fb in itertools.combinations_with_replacement(FACTORS, 2):
    Pf = fval(arr, fa) * fval(arr, fb)
    for t in ("n", "m"):
        T = arr[t]
        for c in COEFFS:
            # t ≤ c·P + b   (product lower-bounds t)
            b = float(np.max(T - c * Pf))
            slk = c * Pf + b - T
            if -2.5 <= b <= 2.5 and slk.min() > -EPS and (np.abs(slk) < 1e-9).any() and slk.max() > 1e-9:
                lbl = f"{t} ≤ {c:g}·{flabel(fa)}·{flabel(fb)}" + (f" + {b:g}" if abs(b) > 1e-9 else "")
                need = {fa[0], fb[0], t}
                fa_, fb_, c_, b_, t_ = fa, fb, c, b, t
                candidates.append((lbl, "product", need,
                    (lambda d, fa_=fa_, fb_=fb_, c_=c_, b_=b_, t_=t_:
                        c_ * fval(d, fa_) * fval(d, fb_) + b_ - d[t_])))
            # P ≤ c·t + b   (product bounded above by t)
            b2 = float(np.max(Pf - c * T))
            slk2 = c * T + b2 - Pf
            if -2.5 <= b2 <= 2.5 and slk2.min() > -EPS and (np.abs(slk2) < 1e-9).any() and slk2.max() > 1e-9:
                lbl = f"{flabel(fa)}·{flabel(fb)} ≤ {c:g}·{t}" + (f" + {b2:g}" if abs(b2) > 1e-9 else "")
                need = {fa[0], fb[0], t}
                fa_, fb_, c_, b_, t_ = fa, fb, c, b2, t
                candidates.append((lbl, "product", need,
                    (lambda d, fa_=fa_, fb_=fb_, c_=c_, b_=b_, t_=t_:
                        c_ * d[t_] + b_ - fval(d, fa_) * fval(d, fb_))))

print(f"Product candidates holding on the census: {len(candidates)}", flush=True)

# also re-check a few standing LINEAR conjectures through the adversarial filter
LINEAR = [
    ("rad ≤ α", {"rad", "alpha"}, lambda d: d["alpha"] - d["rad"]),
    ("rad ≤ ν", {"rad", "nu"}, lambda d: d["nu"] - d["rad"]),
    ("rad ≤ 1.5·γ", {"rad", "gamma"}, lambda d: 1.5 * d["gamma"] - d["rad"]),
    ("δ ≤ λ + 5 (DB artifact)", {"delta", "lambda"}, lambda d: d["lambda"] + 5 - d["delta"]),
    ("χ ≤ avg_deg + 3 (DB artifact)", {"chi", "avg_deg"}, lambda d: d["avg_deg"] + 3 - d["chi"]),
]

# ── adversarial filtering ─────────────────────────────────────────────────
def dedupe(cands):
    out, seen = [], set()
    for c in sorted(cands, key=lambda x: x[0]):
        if c[0] in seen:
            continue
        seen.add(c[0]); out.append(c)
    return out

survivors, refuted = [], 0
for lbl, kind, need, slack in dedupe(candidates):
    ok, worst, tight, cex = adversarial_ok(slack, need)
    if ok:
        survivors.append((lbl, worst, tight))
    else:
        refuted += 1
survivors.sort(key=lambda x: -x[2])

print(f"\nAfter adversarial filter: {len(survivors)} product conjectures survive, "
      f"{refuted} refuted by targeted graphs\n")
print("=" * 74)
print("  PRODUCT CONJECTURES surviving census + adversarial search")
print("=" * 74)
for lbl, worst, tight in survivors[:40]:
    print(f"   {lbl:42s}  worst slack {worst:+.2f}, tight on {tight} adversarial graphs")

print("\n" + "=" * 74)
print("  LINEAR conjectures through the same adversarial filter")
print("=" * 74)
for lbl, need, slack in LINEAR:
    ok, worst, tight, cex = adversarial_ok(slack, need)
    if ok:
        print(f"   ✓ {lbl:34s} survived (worst slack {worst:+.1f}, tight {tight})")
    else:
        print(f"   ✗ {lbl:34s} REFUTED — counterexample n={cex['n']} "
              f"(δ={cex.get('delta')},λ={cex.get('lambda')},χ={cex.get('chi')},"
              f"avg_deg={cex.get('avg_deg'):.2f})")
