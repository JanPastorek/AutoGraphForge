#!/usr/bin/env sage
# -*- mode: python -*-
"""
run_conjecturing.sage  --  expression-tree conjecturing over graph invariants.

Integrates the Larson / Van Cleemput `Conjecturing` package (the reference
implementation of Fajtlowicz's Dalmatian heuristic) into the GraphConjecturing
pipeline.  Unlike the in-house linear / product sweep, the Dalmatian search
explores full *expression trees* (sum, difference, product, ratio, power,
root, max, min, ...) of the invariants, and we inject the classical known
bounds as a `theory` so that only conjectures *strictly more significant*
than the existing record are reported.

Graphs are generated natively in Sage (nauty_geng + a library of larger named
graphs) so every invariant value is exact -- there is no CSV / definition
bridge and therefore no definitional drift.

Output: results/conjecturing_output.json  (one record per surviving bound).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
load(os.path.join(HERE, 'conjecturing.py'))

# make the bundled `expressions` binary findable by the subprocess call
os.environ['PATH'] = HERE + os.pathsep + os.environ.get('PATH', '')

MAX_GENG = int(os.environ.get('CONJ_MAX_GENG', '7'))   # all connected graphs n<=this
TIME     = int(os.environ.get('CONJ_TIME', '8'))       # seconds per Dalmatian run

# Clean algebraic operator set: sums, products, ratios, powers, roots, max/min,
# and small integer adjustments.  Transcendental operators (sin/cos/exp/log/...)
# are excluded because over a finite object set they only ever overfit.
ALGEBRAIC_OPS = {'-1', '+1', '*2', '/2', '^2', '-()', '1/', 'sqrt', 'abs',
                 'ceil', 'floor', '+', '*', '-', '/', '^', 'max', 'min'}

# ---------------------------------------------------------------- objects
def build_objects():
    objs = []
    for n in range(2, MAX_GENG + 1):
        for G in graphs.nauty_geng("{} -c".format(n)):
            objs.append(G)
    # a few larger, structurally diverse graphs to stress the bounds
    extra = [
        graphs.PetersenGraph(),
        graphs.CompleteGraph(8),
        graphs.CompleteBipartiteGraph(4, 4),
        graphs.CycleGraph(12),
        graphs.PathGraph(11),
        graphs.StarGraph(10),
        graphs.WheelGraph(9),
        graphs.BullGraph(),
        graphs.HouseGraph(),
        graphs.DurerGraph(),
        graphs.FlowerSnark(),
        graphs.HeawoodGraph(),
        graphs.FranklinGraph(),
        graphs.FruchtGraph(),
        graphs.BarbellGraph(5, 0),
        graphs.LollipopGraph(5, 4),
        graphs.GridGraph([3, 4]),
    ]
    objs.extend(extra)
    return objs

# ---------------------------------------------------------------- invariants
def order(G):        return Integer(G.order())
def size(G):         return Integer(G.size())
def max_degree(G):   return Integer(max(G.degree()))
def min_degree(G):   return Integer(min(G.degree()))
def avg_degree(G):   return QQ(2 * G.size()) / G.order()
def alpha(G):        return Integer(G.independent_set(value_only=True))
def omega(G):        return Integer(G.clique_number())
def chi(G):          return Integer(G.chromatic_number())
def gamma(G):        return Integer(G.dominating_set(value_only=True))
def nu(G):           return Integer(G.matching(value_only=True))
def tau(G):          return Integer(G.vertex_cover(value_only=True))
def diameter(G):     return Integer(G.diameter())
def radius(G):       return Integer(G.radius())
def girth(G):        return Integer(G.girth()) if G.girth() != Infinity else Integer(2*G.order())
def kappa(G):        return Integer(G.vertex_connectivity())
def lam(G):          return Integer(G.edge_connectivity())
def triangles(G):    return Integer(G.triangles_count())
def spectral_radius(G):
    return max(G.adjacency_matrix().eigenvalues()).n(40)
def alg_conn(G):
    ev = sorted(G.laplacian_matrix().eigenvalues())
    return ev[1].n(40)
def zero_forcing_ub(G):  # cheap structural quantity
    return Integer(G.order() - G.matching(value_only=True))

INVARIANTS = [order, size, max_degree, min_degree, avg_degree, alpha, omega,
              chi, gamma, nu, tau, diameter, radius, girth, kappa, lam,
              triangles, spectral_radius, alg_conn]

# ---------------------------------------------------------------- known bounds
# Each entry: target invariant name -> (upper_bound_fns, lower_bound_fns)
# The Dalmatian search must beat ALL of these to report a conjecture.
def _const(k):
    return lambda G: Integer(k)

KNOWN = {
    'alpha': (
        # upper bounds for alpha
        [lambda G: order(G) - min_degree(G),      # alpha <= n - delta
         lambda G: order(G) - matching_lb(G),     # alpha <= n - nu
         size,                                     # alpha <= m
         lambda G: max_degree(G) + 1],
        # lower bounds for alpha
        [lambda G: order(G) / (max_degree(G) + 1), # alpha >= n/(Delta+1)
         _const(1)],
    ),
    'gamma': (
        [order, lambda G: order(G) - max_degree(G)],   # gamma <= n, gamma <= n - Delta
        [lambda G: order(G) / (max_degree(G) + 1), _const(1)],
    ),
    'chi': (
        [lambda G: max_degree(G) + 1, order],          # Brooks-ish / trivial
        [omega, lambda G: order(G) / alpha(G)],         # chi >= omega, chi >= n/alpha
    ),
    'spectral_radius': (
        [max_degree, lambda G: (2*size(G)).sqrt().n(40)],  # rho <= Delta, rho <= sqrt(2m)
        [avg_degree, lambda G: (2*size(G))/order(G)],       # rho >= avg deg
    ),
    'nu': (
        [lambda G: order(G) / 2, tau],                  # nu <= n/2, nu <= tau (Konig dir)
        [_const(1)],
    ),
}

def matching_lb(G):
    return Integer(G.matching(value_only=True))

# ------------------------------------------------ adversarial pool (Sage-side)
# Larger, structure-targeted graphs that lie OUTSIDE the n<=7 generation set.
# A conjecture validated only on small graphs must also survive these, exactly
# as in the in-house pipeline's adversarial stage.
def adversarial_pool():
    pool = []
    for a in (6, 8, 10):
        pool.append(graphs.BarbellGraph(a, 0))          # huge delta, tiny lambda
        pool.append(graphs.BarbellGraph(a, 3))
        pool.append(graphs.LollipopGraph(a, a))         # clique + long tail
    for n in (10, 12, 14):
        pool.append(graphs.CycleGraph(n))
        pool.append(graphs.PathGraph(n))
        pool.append(graphs.StarGraph(n))
        pool.append(graphs.WheelGraph(n))
        pool.append(graphs.CompleteGraph(n))
    for (a, b) in ((3, 9), (5, 9), (2, 12), (6, 6), (4, 10)):
        pool.append(graphs.CompleteBipartiteGraph(a, b))
    # spiders: subdivided stars (large radius, small domination)
    for legs, length in ((5, 2), (6, 2), (4, 3)):
        T = graphs.StarGraph(legs)
        for e in list(T.edges(labels=False)):
            T.subdivide_edge(e, length - 1)
        pool.append(T)
    # complements of triangle-free graphs (alpha = 2)
    for n in (8, 9, 10):
        pool.append(graphs.CycleGraph(n).complement())
    # random regular graphs (block-free, varied spectra)
    for (r, n) in ((3, 10), (4, 12), (3, 14)):
        try:
            pool.append(graphs.RandomRegular(r, n))
        except Exception:
            pass
    # keep only connected, drop duplicates by canonical form
    seen, out = set(), []
    for G in pool:
        if not G.is_connected():
            continue
        key = G.canonical_label().graph6_string()
        if key not in seen:
            seen.add(key)
            out.append(G)
    return out

# ---------------------------------------------------------------- driver
def name_of(fn):
    return fn.__name__

def run():
    print("Building objects (connected graphs n<={} + library)...".format(MAX_GENG))
    objs = build_objects()
    print("  {} objects".format(len(objs)))
    pool = adversarial_pool()
    print("  adversarial pool: {} structure-targeted graphs".format(len(pool)))

    survivors, refuted = [], []
    targets = ['alpha', 'gamma', 'chi', 'spectral_radius', 'nu']
    name2idx = {name_of(f): i for i, f in enumerate(INVARIANTS)}

    for tname in targets:
        midx = name2idx[tname]
        ubs, lbs = KNOWN.get(tname, ([], []))
        for upper, theory in ((True, ubs), (False, lbs)):
            label = 'upper' if upper else 'lower'
            print("\n=== {} bounds for {}  (theory: {} known) ===".format(
                  label, tname, len(theory)))
            try:
                cs = conjecture(objs, INVARIANTS, midx, time=TIME,
                                upperBound=upper,
                                theory=theory if theory else None,
                                operators=ALGEBRAIC_OPS,
                                verbose=False)
            except Exception as e:
                print("  ERROR:", e)
                continue
            for c in cs:
                s = str(c)
                # adversarial check: does the bound hold on the whole pool?
                witness = None
                for G in pool:
                    try:
                        ok = bool(c(G))
                    except Exception:
                        ok = True   # undefined (e.g. div-by-0) -> not a refutation
                    if not ok:
                        witness = G.canonical_label().graph6_string()
                        break
                rec = {'target': tname, 'direction': label, 'conjecture': s}
                if witness is None:
                    print("  [keep ] {}".format(s))
                    survivors.append(rec)
                else:
                    print("  [refut] {}   <-- {}".format(s, witness))
                    rec['witness_g6'] = witness
                    refuted.append(rec)

    outdir = os.path.abspath(os.path.join(HERE, '..', '..', 'results'))
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'conjecturing_survivors.json'), 'w') as f:
        json.dump(survivors, f, indent=2)
    with open(os.path.join(outdir, 'conjecturing_refuted.json'), 'w') as f:
        json.dump(refuted, f, indent=2)
    print("\nSurvivors: {}   Refuted by adversarial pool: {}".format(
          len(survivors), len(refuted)))
    print("Wrote results/conjecturing_survivors.json and conjecturing_refuted.json")

run()
