# Graph Database

This document describes the graph corpus that feeds Stage 1 (hypothesis
generation) and Stage 2 (falsification) of the conjecture pipeline, and how to
regenerate it.

## What gets built

`build_database.py` streams every graph source through the invariant battery in
[graphs/invariants.py](graphs/invariants.py) and writes one row per graph to
`database/graph_database.csv` (git-ignored).

Columns: `idx, source, name, n, m, g6,` then every numeric invariant
(`n, m, chi, alpha, omega, gamma, nu, Delta, delta, kappa, lambda, diam, rad,
alg, tri`) and Boolean property (`bipartite, planar, regular, eulerian,
chordal, tree`). Each graph is stored as a graph6 string so rows can be
rehydrated into networkx without recomputation.

Graphs with more than `--full-invariant-max` (default 40) vertices receive only
the fast invariant subset; the spectral and max-flow connectivity invariants are
too slow on large graphs and are left blank for those rows.

## Sources

| Source | Loader | Notes |
|---|---|---|
| Named graphs | `generators.named_graphs` | ~50 classical graphs (taken whole) |
| Nauty corpus n≤8 | `loaders.load_nauty` | all non-isomorphic graphs, taken whole |
| Nauty corpus n=9 | `loaders` | sampled (`--nauty9-cap`, default 5000 of 274668) |
| Cographs | `loaders.load_cographs` | `cographs/*.g6` |
| Minimal Cayley | `loaders.load_minimal_cayley` | `minimal_cayley/*.g6` |
| Cages | `loaders.load_cages` | valid `cages*.g6` only (see corruption note) |
| Minimal Ramsey | `loaders.load_minimal_ramsey` | `Ramseygraphs_*.g6(.gz)`, capped per file |
| Strongly regular | `loaders.load_srg` | Spence adjacency-matrix `.txt`/`.bz2`, capped per file |
| House of Graphs | `loaders.load_hog` | `hog_all_28859_graphs.g6`, sampled (`--hog-cap`) |
| Minimally rigid | `loaders.load_minimally_rigid` | zipped g6, sampled per member, `n ≤ --rigid-max-n` |

Large classes are reservoir-sampled so the build stays tractable; small/medium
classes are taken in full.

### Corruption note

`cages/cages_*.g6` (120 files) and `minimal_ramsey/R(*,*).g6` (12 files) are
saved HTML error pages, **not** graph data — they were downloaded incorrectly.
The loaders detect and skip any file whose contents start with an HTML doctype,
and the valid re-uploaded files (`cagesk*g*.g6`, `k*_g*_n*.g6`,
`Ramseygraphs_*.g6`) are used instead. Re-download the originals to recover the
skipped files.

## Nauty (`geng`)

All non-isomorphic graphs up to 9 vertices live in `generated_nauty/`
(`graphs_Nv_all.g6` and `graphs_Nv_connected.g6`). Counts match OEIS A000088 /
A001349 exactly:

| n | all | connected |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 1 |
| 3 | 4 | 2 |
| 4 | 11 | 6 |
| 5 | 34 | 21 |
| 6 | 156 | 112 |
| 7 | 1044 | 853 |
| 8 | 12346 | 11117 |
| 9 | 274668 | 261080 |

`geng` was compiled from the official nauty 2.8.9 source
(<https://pallini.di.uniroma1.it>) with the local MinGW gcc; the build script is
[.build/build_nauty.sh](.build/build_nauty.sh) and the binary is
`.build/geng.exe` (git-ignored).

Regenerate:

```bash
for n in $(seq 1 9); do
  .build/geng.exe -q  $n > graphs/generated_nauty/graphs_${n}v_all.g6
  .build/geng.exe -cq $n > graphs/generated_nauty/graphs_${n}v_connected.g6
done
```

## Building / rebuilding the database

```bash
# default caps (~minutes)
python build_database.py

# include every House-of-Graphs and 9-vertex graph (slow, large)
python build_database.py --hog-cap 0 --nauty9-cap 0

# skip the giant minimally-rigid class
python build_database.py --no-rigid

# custom output location
python build_database.py --out database/my_db.csv
```

See `python build_database.py --help` for all per-class cap flags.
