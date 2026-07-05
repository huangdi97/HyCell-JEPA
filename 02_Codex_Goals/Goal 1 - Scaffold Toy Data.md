# Goal 1 - Scaffold Toy Data

Copy and paste this into Codex:

```text
/goal Scaffold the HyCell-JEPA toy data, gene set scoring, and evidence graph layer.

Objective:
Create the first runnable engineering pipeline for HyCell-JEPA using small toy single-cell perturbation data. This goal should not implement neural model training yet. It should create deterministic toy data, gene set scoring, an evidence graph representation, tests, configs, and CLI scripts.

Before coding:
- Read AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/limitations.md, docs/design_summary.md, and docs/progress_log.md.
- Do not delete existing files unless clearly unnecessary.
- Do not download data.
- Keep generated outputs small and inside outputs/.

Scope:
1. Create a small Python package under src/hycell/.
2. Add a toy HDF-like single-cell perturbation dataset generator.
3. Add small marker gene sets for senescence, proliferation, ECM/remodeling, stress/inflammation, reprogramming/plasticity, and viability/QC proxy.
4. Add gene set scoring over the toy expression table.
5. Add a lightweight evidence graph that links actions, readouts, assumptions, and limitations.
6. Add CLI entry points in scripts/.
7. Add configs in configs/.
8. Add focused tests in tests/.
9. Update docs/progress_log.md and any relevant docs.

Suggested files:
- configs/toy_data.yaml
- configs/gene_sets.yaml
- scripts/make_toy_data.py
- scripts/score_gene_sets.py
- scripts/build_evidence_graph.py
- src/hycell/__init__.py
- src/hycell/toy_data.py
- src/hycell/gene_sets.py
- src/hycell/evidence_graph.py
- tests/test_toy_data.py
- tests/test_gene_sets.py
- tests/test_evidence_graph.py

Constraints:
- Toy data is engineering validation only.
- Do not claim any biological discovery.
- Keep data tiny enough to inspect in git if needed, but prefer generated outputs in outputs/.
- Every script must have a CLI entry point.
- Keep the toy pipeline runnable.

Definition of done:
1. Toy data can be generated deterministically from a config.
2. Gene set scores can be computed from the generated toy data.
3. Evidence graph can be built from toy data and scores.
4. Tests cover generation, scoring, and graph construction.
5. Documentation states toy data limitations clearly.
6. No neural model code is implemented in this goal.

Verification commands:
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/build_evidence_graph.py --scores outputs/toy_data/gene_set_scores.csv
pytest
find . -maxdepth 3 -type f | sort
git status

Before finishing:
Update docs/progress_log.md with files changed, commands run, known limitations, and the next recommended step.
```
