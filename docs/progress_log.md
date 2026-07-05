# Progress Log

## How To Update
- Add a dated entry after each meaningful Codex goal or manual work session.
- Record files created or changed, commands run, known limitations, and the recommended next step.
- Keep entries factual. Do not present toy-data behavior as biological discovery.

## Current Status
Goal 1 packaging fix complete. The repository now has valid src-layout Python packaging, requirements installation, a deterministic toy HDF-like perturbation data generator, gene set scoring, an evidence graph builder, CLI scripts, configs, and focused tests. No neural model code has been implemented yet.

## Current Milestone
Milestone 1: toy data, gene set scoring, and evidence graph.

## Next Action
Run Goal 2: implement the Bio-State Encoder, Action Encoder, Context Encoder, and JEPA Transition Core on top of the toy pipeline.

## Entries

### 2026-07-05 - Bootstrap scaffold

Created the initial project memory system, Obsidian/Codex workflow files, and documentation scaffold for the HyCell-JEPA MVP.

Files created:
- `AGENTS.md`
- `00_Control/HyCell-JEPA 控制台.md`
- `02_Codex_Goals/Goal 1 - Scaffold Toy Data.md`
- `02_Codex_Goals/Goal 2 - Encoder JEPA.md`
- `02_Codex_Goals/Goal 3 - Adapter Verifier Planner Demo.md`
- `02_Codex_Goals/Goal 4 - Real Data Integration.md`
- `02_Codex_Goals/Goal 5 - Cloud 4090 Training.md`
- `03_Progress/2026-07-05.md`
- `05_Experiments/Experiment Template.md`
- `06_Bugs/Bug Template.md`
- `docs/PROJECT_BRIEF.md`
- `docs/benchmark_report.md`
- `docs/cloud_4090_guide.md`
- `docs/data_card.md`
- `docs/design_summary.md`
- `docs/limitations.md`
- `docs/model_card.md`
- `docs/real_data_integration.md`

Files updated:
- `README.md`
- `docs/progress_log.md`

Directories created:
- `00_Control/`
- `01_Design/`
- `02_Codex_Goals/`
- `03_Progress/`
- `04_Data/`
- `05_Experiments/`
- `06_Bugs/`
- `07_Reading/`
- `08_Decisions/`
- `docs/`
- `configs/`
- `scripts/`
- `src/hycell/`
- `tests/`
- `outputs/`

Commands run:

```bash
rg --files
git status --short
Get-ChildItem -Force
Get-Content -Raw README.md
find . -maxdepth 3 -type f | sort
git status
```

Known limitations:
- This is a scaffold only; no toy data, model code, benchmarks, or demo have been implemented yet.
- No data was downloaded.
- No biological claims can be made from this repository state.
- The Obsidian control filename was created as `HyCell-JEPA 控制台.md` because the pasted text contained mojibake with a Windows-invalid `?` character.
- Empty directories exist locally but are not listed by `git status` until files are added inside them.

Next recommended step:
Run `02_Codex_Goals/Goal 1 - Scaffold Toy Data.md` to create the toy single-cell perturbation dataset, gene set scoring, and evidence graph.

### 2026-07-05 - Goal 1 toy data, scoring, and evidence graph

Created the first runnable toy engineering pipeline for HyCell-JEPA. The pipeline generates deterministic HDF-like toy single-cell perturbation data, scores compact gene sets, and builds a lightweight evidence graph linking actions, readouts, assumptions, and limitations.

Files created:
- `configs/toy_data.yaml`
- `configs/gene_sets.yaml`
- `pytest.ini`
- `scripts/make_toy_data.py`
- `scripts/score_gene_sets.py`
- `scripts/build_evidence_graph.py`
- `src/hycell/__init__.py`
- `src/hycell/config.py`
- `src/hycell/toy_data.py`
- `src/hycell/gene_sets.py`
- `src/hycell/evidence_graph.py`
- `tests/conftest.py`
- `tests/test_toy_data.py`
- `tests/test_gene_sets.py`
- `tests/test_evidence_graph.py`

Files updated:
- `.gitignore`
- `README.md`
- `docs/data_card.md`
- `docs/progress_log.md`

Generated outputs:
- `outputs/toy_data/toy_cells.csv`
- `outputs/toy_data/gene_set_scores.csv`
- `outputs/toy_data/evidence_graph.json`

Commands run:

```bash
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/build_evidence_graph.py --scores outputs/toy_data/gene_set_scores.csv
pytest
find . -maxdepth 3 -type f | sort
git status
```

Known limitations:
- Toy data is deterministic engineering validation only and is not biological evidence.
- The configs use YAML-compatible JSON syntax so the current pipeline can run without external dependencies.
- The evidence graph summarizes configured toy behavior and limitations; it is not a knowledge graph of real biology.
- No neural model, HDF adapter, verifier, planner, benchmark, Streamlit demo, or real-data loader has been implemented yet.

Next recommended step:
Run `02_Codex_Goals/Goal 2 - Encoder JEPA.md` to add compact encoders and the JEPA transition core.

### 2026-07-05 - Goal 1 packaging verification fix

Failure:
- `pip install -e .` failed because the repository had no `pyproject.toml` or `setup.py`.
- `pip install -r requirements.txt` failed because `requirements.txt` did not exist.
- Packaging verification also required `python scripts/make_toy_data.py --n_cells 10000 --n_genes 2000 --out data/processed/toy_cells.npz`, but the toy-data CLI only supported config-driven CSV output.

Fix:
- Added `pyproject.toml` for a src-layout package named `hycell-jepa`.
- Added `requirements.txt` with editable package install plus pytest.
- Added deterministic NPZ matrix generation mode to `scripts/make_toy_data.py` and `src/hycell/toy_data.py`.
- Added test coverage for the NPZ writer.
- Kept the existing config-driven CSV toy pipeline intact.

Files created:
- `pyproject.toml`
- `requirements.txt`

Files updated:
- `scripts/make_toy_data.py`
- `src/hycell/toy_data.py`
- `tests/test_toy_data.py`
- `docs/progress_log.md`

Commands run:

```bash
pip install -e .
pip install -r requirements.txt
pytest
python scripts/make_toy_data.py --n_cells 10000 --n_genes 2000 --out data/processed/toy_cells.npz
```

Known limitations:
- `data/processed/toy_cells.npz` is generated toy engineering data and remains ignored by git.
- The NPZ matrix is for packaging and loader smoke verification only, not biological evidence.
- No neural model, HDF adapter, verifier, planner, benchmark, Streamlit demo, or real-data loader was added in this fix.

Next recommended step:
Proceed to Goal 2 only after committing or otherwise preserving the Goal 1 packaging fix.
