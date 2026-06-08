# Graph Report - .  (2026-06-07)

## Corpus Check
- Corpus is ~11,854 words - fits in a single context window. You may not need a graph.

## Summary
- 299 nodes · 763 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 191 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]

## God Nodes (most connected - your core abstractions)
1. `Conjecture` - 55 edges
2. `Config` - 47 edges
3. `GraphDatabase` - 33 edges
4. `ConjectureStatus` - 31 edges
5. `FunSearchGenerator` - 28 edges
6. `Graph` - 27 edges
7. `GraphOfThoughtFormalizer` - 26 edges
8. `TxGraffitiGenerator` - 26 edges
9. `FalsificationOrchestrator` - 23 edges
10. `NeuralProverClient` - 20 edges

## Surprising Connections (you probably didn't know these)
- `GraphOfThoughtFormalizer` --rationale_for--> `Graph-of-Thought autoformalization`  [EXTRACTED]
  pipeline/autoformalization.py → PIPELINE_DESCRIPTION.md
- `TxGraffitiGenerator` --rationale_for--> `Dalmatian heuristic (dominance filter)`  [EXTRACTED]
  pipeline/hypothesis_gen.py → PIPELINE_DESCRIPTION.md
- `FunSearchGenerator` --rationale_for--> `FunSearch (LLM program-evolution)`  [EXTRACTED]
  pipeline/hypothesis_gen.py → PIPELINE_DESCRIPTION.md
- `Counterexample` --uses--> `Config`  [INFERRED]
  pipeline/falsification.py → config.py
- `Inequality` --uses--> `Config`  [INFERRED]
  pipeline/hypothesis_gen.py → config.py

## Import Cycles
- 1-file cycle: `pipeline/hypothesis_gen.py -> pipeline/hypothesis_gen.py`
- 1-file cycle: `pipeline/orchestrator.py -> pipeline/orchestrator.py`
- 1-file cycle: `pipeline/falsification.py -> pipeline/falsification.py`
- 1-file cycle: `pipeline/autoformalization.py -> pipeline/autoformalization.py`
- 1-file cycle: `pipeline/theorem_prover.py -> pipeline/theorem_prover.py`

## Hyperedges (group relationships)
- **Falsification Strategies** — pipeline_falsification_Z3Falsifier, pipeline_falsification_MCTSFalsifier, pipeline_falsification_VNSFalsifier, pipeline_falsification_CrossEntropyFalsifier [EXTRACTED 1.00]
- **Pipeline Stages (generation→falsify→formalize→prove)** — pipeline_hypothesis_gen_TxGraffitiGenerator, pipeline_hypothesis_gen_FunSearchGenerator, pipeline_falsification_FalsificationOrchestrator, pipeline_autoformalization_GraphOfThoughtFormalizer, pipeline_theorem_prover_NeuralProverClient [EXTRACTED 1.00]

## Communities (15 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.13
Nodes (34): ArgumentParser, Config, config.py — centralised configuration for the conjecture pipeline. All knobs are, ConjectureStatus, FalsificationOrchestrator, FunSearchGenerator, GraphOfThoughtFormalizer, INVARIANTS / FAST_INVARIANTS / BOOLEANS (+26 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (24): Counterexample, A concrete graph that refutes a conjecture., Counterexample, evaluate_all(), evaluate_fast(), Evaluate all (or a chosen subset of) invariants on G.     Skips any that raise o, Evaluate only the fast invariant subset., CrossEntropyFalsifier (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (19): Inequality, Represents:  coeff_a · inv_a(G)  ≤  coeff_b · inv_b(G)  +  offset      Both inv_, Return True if the inequality holds, False if violated, None if data missing., rhs − lhs.  Negative → violated; zero → tight; positive → slack., Inequality, FunSearchGenerator, Config, Conjecture (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.11
Nodes (19): NeuralProverClient (ensemble), BaseProver, DeepSeekProverV2, GoedelProver, LeanSubprocessProver, ProverResponse, Config, Conjecture (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.10
Nodes (36): algebraic_connectivity(), average_degree(), _backtrack_coloring(), chromatic_number(), clique_cover_number(), clique_number(), diameter(), domination_number() (+28 more)

### Community 5 - "Community 5"
Cohesion: 0.11
Nodes (22): GraphDatabase, GraphEntry, graphs/database.py — graph database with pre-computed invariant vectors., _bull(), _butterfly(), _caterpillar(), _cricket(), _diamond() (+14 more)

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (11): _extract_lean_block(), _got_decomposition_prompt(), _looks_valid(), Conjecture, pipeline/autoformalization.py — Stage 3: Autoformalization  Translates informal, Returns a Lean 4 theorem string (with `sorry` proof), or None on failure., Formalize a list; returns those successfully formalized., Produce a best-effort Lean 4 statement without an LLM call,         for TxGraffi (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.24
Nodes (7): SAT/SMT-based falsifier using the z3-solver Python package.      For a conjectur, Encode graph on n vertices + negated conjecture, call Z3, decode graph., Encode: var ≤ inv_name(G)  (so a violation requires inv_a > rhs)., Encode: var ≥ inv_name(G)  (so conjecture_rhs = coeff*var+offset ≥ coeff*inv_b+o, α(G) encoded via independent-set indicator variables.         direction="lower", χ(G) ≤ var: encode a proper var-colouring (var is fixed to a small value)., Z3Falsifier

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (4): Conjecture, conjecture.py — core data model for the graph-theory conjecture pipeline.  Class, Central data object flowing through the pipeline.      Lifecycle     ---------, Enum

## Knowledge Gaps
- **5 isolated node(s):** `CONFIG singleton`, `Conjecture (data model)`, `Inequality (structured conjecture)`, `Counterexample (data model)`, `DeepSeek-Prover-V2`
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Conjecture` connect `Community 8` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Why does `Config` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.193) - this node is a cross-community bridge._
- **Why does `GraphDatabase` connect `Community 5` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 38 inferred relationships involving `Conjecture` (e.g. with `Counterexample` and `FalsificationOrchestrator`) actually correct?**
  _`Conjecture` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `Config` (e.g. with `ArgumentParser` and `Counterexample`) actually correct?**
  _`Config` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `GraphDatabase` (e.g. with `FalsificationOrchestrator` and `FunSearchGenerator`) actually correct?**
  _`GraphDatabase` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `ConjectureStatus` (e.g. with `ArgumentParser` and `FalsificationOrchestrator`) actually correct?**
  _`ConjectureStatus` has 25 INFERRED edges - model-reasoned connections that need verification._