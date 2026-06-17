#!/usr/bin/env sage
# -*- mode: python -*-
"""
run_property_conjecturing.sage  --  property-based (boolean) conjecturing.

Implements the "sufficient-condition" mode of automated conjecturing (the
boolean counterpart of TxGraffiti's invariant inequalities, and the
`propertyBasedConjecture` entry point of the Larson / Van Cleemput package).
Instead of numeric bounds it produces statements of the form

    (property_A AND property_B AND ...) ==> main_property

i.e. machine-discovered *sufficient conditions* for a target graph property,
built from a pool of boolean predicates with the logical operators
~ (not), & (and), | (or), ^ (xor), -> (implies).

As elsewhere in the pipeline, known sufficient conditions are supplied as a
`theory` (so only more general conditions survive), and every surviving
implication is then checked against an adversarial pool of structure-targeted
graphs that lie outside the generation set.

Output: results/property_conjecturing_{survivors,refuted}.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
load(os.path.join(HERE, 'conjecturing.py'))
os.environ['PATH'] = HERE + os.pathsep + os.environ.get('PATH', '')

MAX_GENG = int(os.environ.get('CONJ_MAX_GENG', '7'))
TIME     = int(os.environ.get('CONJ_TIME', '8'))

# ---------------------------------------------------------------- objects
def build_objects():
    objs = []
    for n in range(3, MAX_GENG + 1):
        for G in graphs.nauty_geng("{} -c".format(n)):
            objs.append(G)
    objs += [graphs.PetersenGraph(), graphs.CompleteGraph(7),
             graphs.CompleteBipartiteGraph(4, 4), graphs.CycleGraph(10),
             graphs.WheelGraph(8), graphs.HeawoodGraph(), graphs.FruchtGraph(),
             graphs.DodecahedralGraph(), graphs.MoebiusKantorGraph()]
    return objs

# ---------------------------------------------------------------- properties
def is_regular(G):          return G.is_regular()
def is_bipartite(G):        return G.is_bipartite()
def is_planar(G):           return G.is_planar()
def is_claw_free(G):        return not G.subgraph_search(graphs.StarGraph(3), induced=True)
def is_chordal(G):          return G.is_chordal()
def is_eulerian(G):         return G.is_eulerian()
def is_vertex_transitive(G):return G.is_vertex_transitive()
def is_tree(G):             return G.is_tree()
def is_two_connected(G):    return (G.vertex_connectivity() >= 2)
def is_three_connected(G):  return (G.vertex_connectivity() >= 3)
def is_dirac(G):            return (2 * min(G.degree()) >= G.order())   # Dirac threshold
def is_self_complementary(G):
    return G.is_isomorphic(G.complement())
def has_even_order(G):      return (G.order() % 2 == 0)

# targets
def is_hamiltonian(G):      return G.is_hamiltonian()
def has_perfect_matching(G):
    return (2 * G.matching(value_only=True) == G.order())

PROPERTIES = [is_regular, is_bipartite, is_planar, is_claw_free, is_chordal,
              is_eulerian, is_vertex_transitive, is_tree, is_two_connected,
              is_three_connected, is_dirac, is_self_complementary,
              has_even_order, is_hamiltonian, has_perfect_matching]

# known sufficient conditions for the targets (theory): only more general survive
KNOWN = {
    'is_hamiltonian': [is_dirac],                 # Dirac's theorem
    'has_perfect_matching': [],
}

BOOL_OPS = {'~', '&', '|', '->'}   # drop xor; keep the readable logical core

# ---------------------------------------------------------------- adversarial
def adversarial_pool():
    pool = []
    for a in (5, 7):
        pool.append(graphs.BarbellGraph(a, 0))
        pool.append(graphs.LollipopGraph(a, a))
    for n in (8, 10, 12):
        pool += [graphs.CycleGraph(n), graphs.PathGraph(n), graphs.StarGraph(n),
                 graphs.WheelGraph(n), graphs.CompleteGraph(n)]
    for (a, b) in ((3, 8), (4, 4), (2, 9), (5, 6)):
        pool.append(graphs.CompleteBipartiteGraph(a, b))
    for n in (8, 10):
        pool.append(graphs.CycleGraph(n).complement())
    for (r, n) in ((3, 10), (4, 12)):
        try:
            pool.append(graphs.RandomRegular(r, n))
        except Exception:
            pass
    seen, out = set(), []
    for G in pool:
        if not G.is_connected():
            continue
        k = G.canonical_label().graph6_string()
        if k not in seen:
            seen.add(k); out.append(G)
    return out

# ---------------------------------------------------------------- driver
def run():
    objs = build_objects()
    pool = adversarial_pool()
    print("objects: {}   adversarial pool: {}".format(len(objs), len(pool)))
    name2idx = {f.__name__: i for i, f in enumerate(PROPERTIES)}

    survivors, refuted = [], []
    for target in ('is_hamiltonian', 'has_perfect_matching'):
        midx = name2idx[target]
        theory = KNOWN.get(target, [])
        print("\n=== sufficient conditions for {}  (theory: {}) ===".format(
              target, len(theory)))
        try:
            cs = propertyBasedConjecture(objs, PROPERTIES, midx, time=TIME,
                                         sufficient=True,
                                         theory=theory if theory else None,
                                         operators=BOOL_OPS, verbose=False)
        except Exception as e:
            print("  ERROR:", e); continue
        for c in cs:
            s = str(c)
            witness = None
            for G in pool:
                try:
                    ok = bool(c(G))
                except Exception:
                    ok = True
                if not ok:
                    witness = G.canonical_label().graph6_string(); break
            rec = {'target': target, 'condition': s}
            if witness is None:
                print("  [keep ] {}".format(s)); survivors.append(rec)
            else:
                print("  [refut] {}   <-- {}".format(s, witness))
                rec['witness_g6'] = witness; refuted.append(rec)

    outdir = os.path.abspath(os.path.join(HERE, '..', '..', 'results'))
    os.makedirs(outdir, exist_ok=True)
    json.dump(survivors, open(os.path.join(outdir, 'property_conjecturing_survivors.json'), 'w'), indent=2)
    json.dump(refuted,   open(os.path.join(outdir, 'property_conjecturing_refuted.json'),   'w'), indent=2)
    print("\nSurvivors: {}   Refuted: {}".format(len(survivors), len(refuted)))

run()
