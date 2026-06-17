# Expression-tree conjecturing (Conjecturing / Dalmatian)

Integrates the Larson & Van Cleemput `Conjecturing` package (the reference
implementation of Fajtlowicz's Dalmatian heuristic) into the pipeline. Unlike
the in-house linear/product sweep, this searches over full **expression trees**
(sum, difference, product, ratio, power, root, max, min, floor/ceil) of the
invariants.

- `conjecturing.py` — the upstream Sage interface (vendored).
- `expressions`     — the compiled C search engine (vendored binary).
- `run_conjecturing.sage` — our driver: builds graph objects natively in Sage
  (all connected graphs `n<=CONJ_MAX_GENG` via `nauty_geng`, plus a library of
  larger named graphs), defines an exact invariant battery, injects the
  classical **known bounds as a `theory`** (so only strictly more significant
  conjectures survive), runs upper- and lower-bound Dalmatian searches, and then
  applies an **adversarial filter** against a pool of structure-targeted graphs
  (barbells, lollipops, spiders, complete bipartite, alpha=2 complements,
  random regular) that lie outside the generation set.

## Run
    ./run.sh                                   # n<=7, 8s per search
    CONJ_MAX_GENG=6 CONJ_TIME=5 ./run.sh       # quicker

## Output
- `results/conjecturing_survivors.json` — bounds that held on the whole pool.
- `results/conjecturing_refuted.json`   — bounds refuted, with a g6 witness.

Operator set is restricted to algebraic operators only; transcendental ones
(sin/cos/exp/log/...) are excluded because over a finite object set they only
overfit.

The upstream package is from https://github.com/nvcleemp/conjecturing
(GNU GPL); see `_conjecturing_pkg/` for the full source and `c/` build.

## Property-based (boolean) conjecturing
`run_property_conjecturing.sage` generates **sufficient conditions** for a graph
property: statements `P_1 & ... & P_k -> Q` over boolean predicates
(regular, planar, claw-free, chordal, 2-/3-connected, Dirac threshold, vertex-
transitive, even order, ...) using the logical operators `~ & | ->`. Dirac's
theorem is supplied as theory; survivors are adversarially filtered. It recovers
genuine theorems (e.g. Sumner: claw-free + even order => perfect matching) plus
plausible Hamiltonicity conditions. Output:
`results/property_conjecturing_{survivors,refuted}.json`.

    ./run.sh                                  # numeric expression-tree engine
    SAGE=$HOME/miniconda3/envs/sage/bin/sage \
      env PATH="$PWD:$PATH" "$SAGE" run_property_conjecturing.sage   # boolean engine
