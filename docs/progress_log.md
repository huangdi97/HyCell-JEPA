# Progress Log

## How To Update
- Add a dated entry after each meaningful Codex goal or manual work session.
- Record files created or changed, commands run, known limitations, and the recommended next step.
- Keep entries factual. Do not present toy-data behavior as biological discovery.

## Current Status
Goal 3 verification fix complete. The repository now has the toy data/scoring pipeline, compact JEPA model, HDF Adapter, Biological Verifier, Target-State Planner, benchmark CLIs, package-level Streamlit demo, expected local artifacts, and focused tests.

## Current Milestone
Milestone 3: end-to-end toy MVP loop.

## Next Action
Run Goal 4: real data integration scaffolding with h5ad/csv/npz loaders, schema validation, HDF aging adapter, and perturbation adapter.

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

### 2026-07-05 - Goal 2 compact encoders and toy JEPA transition core

Created the first minimal modeling layer on top of the toy data and gene set scoring pipeline. The implementation uses deterministic NumPy encoders and a ridge-regression transition head for compact belief-state prediction.

Files created:
- `configs/jepa_toy.yaml`
- `scripts/train_jepa.py`
- `scripts/evaluate_jepa.py`
- `src/hycell/datasets.py`
- `src/hycell/encoders.py`
- `src/hycell/jepa.py`
- `src/hycell/training.py`
- `tests/test_encoders.py`
- `tests/test_jepa.py`
- `tests/test_training_smoke.py`

Files updated:
- `src/hycell/__init__.py`
- `docs/model_card.md`
- `docs/benchmark_report.md`
- `docs/progress_log.md`

Generated outputs:
- `outputs/jepa_toy/toy_jepa_model.npz`
- `outputs/jepa_toy/toy_jepa_metadata.json`
- `outputs/jepa_toy/toy_jepa_metrics.json`
- `outputs/jepa_toy/toy_jepa_eval_metrics.json`

Commands run:

```bash
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/train_jepa.py --config configs/jepa_toy.yaml
python scripts/evaluate_jepa.py --config configs/jepa_toy.yaml
pytest
find . -maxdepth 3 -type f | sort
git status
```

Metrics observed:
- Training transitions: 6
- Held-out eval transitions: 2
- Training MSE: `0.000000375`
- Held-out eval MSE: `0.058339536`
- All-transition evaluation MSE: `0.014585165`
- Tests: 16 passed

Known limitations:
- The model predicts compact toy gene-set readouts only, not full transcriptomes.
- The transition core is a small deterministic ridge-regression smoke model, not a production neural model.
- Metrics are toy engineering validation only and are not biological evidence.
- HDF Adapter, Biological Verifier, Target-State Planner, benchmark script, Streamlit demo, and real-data loaders are still pending.

Next recommended step:
Run `02_Codex_Goals/Goal 3 - Adapter Verifier Planner Demo.md` after preserving the Goal 2 changes.

### 2026-07-05 - Goal 2 local training verification fix

Failure:
- `pytest` passed with 16 tests, but local verification expected a missing `scripts/train_encoder.py`.
- `python scripts/train_jepa.py --config configs/train_local.yaml` failed because `configs/train_local.yaml` did not exist.
- The config loader only handled JSON syntax, so real YAML local configs were not supported.
- Local verification expected standard artifact paths under `outputs/checkpoints/`, `outputs/embeddings/`, and `outputs/reports/`.

Fix:
- Added `scripts/train_encoder.py` for compact encoder training.
- Added `configs/train_local.yaml` with lightweight local defaults and exact artifact paths.
- Updated `src/hycell/config.py` to load JSON and YAML safely, with a small fallback parser for the local YAML subset if PyYAML is unavailable.
- Added `pyyaml>=6.0` to `pyproject.toml` and `requirements.txt`.
- Updated training utilities to auto-prepare missing toy scores from existing small configs, write `outputs/checkpoints/best_encoder.pt`, `outputs/checkpoints/best_jepa.pt`, `outputs/embeddings/embeddings.npy`, and `outputs/reports/metrics.json`.
- Added tests for local YAML config loading and encoder artifact writing.

Files created:
- `configs/train_local.yaml`
- `scripts/train_encoder.py`

Files updated:
- `src/hycell/config.py`
- `src/hycell/training.py`
- `tests/test_training_smoke.py`
- `pyproject.toml`
- `requirements.txt`
- `docs/progress_log.md`

Commands run:

```bash
pytest
python scripts/train_encoder.py --config configs/train_local.yaml
python scripts/train_jepa.py --config configs/train_local.yaml
```

Metrics observed:
- Tests: 18 passed
- Encoder embeddings shape: `(8, 12)`
- JEPA training transitions: 6
- JEPA eval transitions: 2
- JEPA train MSE: `0.000000375`
- JEPA eval MSE: `0.058339536`

Known limitations:
- The `.pt` checkpoint files contain small NumPy `npz` payloads with `.pt` filenames for local verification compatibility; this is not a PyTorch training stack.
- Training remains a compact toy engineering smoke path over gene-set readouts, not biological validation.
- No diffusion model, 18,000-gene transcriptome generator, cloud training workflow, HDF adapter, verifier, planner, or demo was added in this fix.
- Generated artifacts under `outputs/` and `data/processed/` remain ignored and should not be committed.

Next recommended step:
Proceed to Goal 3 after preserving the Goal 2 local training fix.

### 2026-07-05 - Goal 2.5 JEPA checkpoint compatibility fix

Fixed Goal 3 compatibility expectations before starting adapter, verifier, planner, or demo work.

What was fixed:
- JEPA training now writes the Goal 3-facing checkpoint path `outputs/checkpoints/best_jepa.pt`.
- JEPA training now writes the Goal 3-facing report path `outputs/reports/jepa_metrics.json`.
- Backward-compatible artifacts under `outputs/jepa_toy/` are still written.
- `configs/train_local.yaml` now includes `jepa_metrics_path`.
- Smoke tests now assert that JEPA training creates the expected compatibility checkpoint and report files.

Files updated:
- `configs/train_local.yaml`
- `scripts/train_jepa.py`
- `src/hycell/training.py`
- `tests/test_training_smoke.py`
- `docs/progress_log.md`

Commands run:

```bash
pytest
python scripts/train_encoder.py --config configs/train_local.yaml
python scripts/train_jepa.py --config configs/train_local.yaml
test -f outputs/checkpoints/best_jepa.pt
test -f outputs/reports/jepa_metrics.json
```

Known limitations:
- The `.pt` checkpoint remains a lightweight NumPy payload with a `.pt` filename for compatibility, not a PyTorch checkpoint.
- This fix does not implement Goal 3 components: no HDF Adapter, Biological Verifier, Target-State Planner, benchmark script, or Streamlit demo.
- Generated artifacts under `outputs/` remain ignored and should not be committed.

Next recommended step:
Start Goal 3 using `outputs/checkpoints/best_encoder.pt`, `outputs/checkpoints/best_jepa.pt`, `outputs/embeddings/embeddings.npy`, and `outputs/reports/jepa_metrics.json` as the local compatibility artifacts.

### 2026-07-05 - Goal 3 HDF adapter, verifier, planner, benchmark, and demo

Completed the first end-to-end toy MVP loop on compact gene-set states. The flow maps toy HDF contexts/actions, predicts next compact states with the JEPA core, verifies toy constraints, plans over short action sequences, writes a benchmark report, and launches a Streamlit demo.

Files created:
- `configs/benchmark_toy.yaml`
- `configs/demo.yaml`
- `scripts/benchmark_toy.py`
- `scripts/demo_app.py`
- `src/hycell/hdf_adapter.py`
- `src/hycell/verifier.py`
- `src/hycell/planner.py`
- `src/hycell/benchmark.py`
- `tests/test_hdf_adapter.py`
- `tests/test_verifier.py`
- `tests/test_planner.py`
- `tests/test_benchmark_smoke.py`

Files updated:
- `src/hycell/__init__.py`
- `README.md`
- `docs/model_card.md`
- `docs/benchmark_report.md`
- `docs/limitations.md`
- `docs/progress_log.md`

Generated outputs:
- `outputs/benchmark_toy/benchmark_report.json`

Commands run:

```bash
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/train_jepa.py --config configs/jepa_toy.yaml
python scripts/benchmark_toy.py --config configs/benchmark_toy.yaml
python -m compileall scripts src
pytest
streamlit run scripts/demo_app.py
find . -maxdepth 3 -type f | sort
git status
```

Benchmark/demo status:
- Benchmark transitions: 8
- Benchmark transition MSE: `0.014585165`
- Verifier status counts: `{"warn": 8}`
- Planner sequence for configured target: `regeneration -> control`
- Planner final distance: `0.183562100`
- Streamlit demo launched headlessly and returned HTTP 200 before shutdown.
- Tests: 25 passed

Known limitations:
- Toy verifier warnings are designed to prevent overinterpretation; they are not biological validation.
- Planner output is a toy software sequence, not a recommendation or protocol.
- Streamlit smoke verification checked launch/serve behavior, not full browser interaction.
- No real-data loader, schema validator, perturbation adapter, or clinical/biological recommendation system has been added.

Next recommended step:
Run `02_Codex_Goals/Goal 4 - Real Data Integration.md` after preserving the Goal 3 changes.

### 2026-07-05 - Goal 3 CLI and Streamlit compatibility fix

Failure:
- `pytest` passed, but local verification expected `scripts/eval_benchmark.py`, which did not exist.
- Local verification expected `scripts/run_planner.py`, which did not exist.
- Local verification expected `streamlit run src/hycell/demo/app.py`; the package-level demo path did not exist and Streamlit was not declared as a dependency.

Fix:
- Added `scripts/eval_benchmark.py`, accepting `--checkpoint` and writing `outputs/reports/benchmark_report.md` plus `outputs/reports/benchmark_metrics.json`.
- Added `scripts/run_planner.py`, accepting `--checkpoint`, `--state`, and `--target`, and writing `outputs/reports/planner_report.md` plus `outputs/reports/top_k_actions.json`.
- Added `src/hycell/demo/app.py` and `src/hycell/demo/__init__.py` as a package-level Streamlit demo path.
- Added `streamlit>=1.37` to `pyproject.toml` and `requirements.txt`.
- Added Top-K planner support and tests for the compatibility CLIs and package demo import.

Files created:
- `scripts/eval_benchmark.py`
- `scripts/run_planner.py`
- `src/hycell/demo/__init__.py`
- `src/hycell/demo/app.py`

Files updated:
- `src/hycell/planner.py`
- `tests/test_benchmark_smoke.py`
- `pyproject.toml`
- `requirements.txt`
- `docs/progress_log.md`

Commands run:

```bash
pytest
python scripts/eval_benchmark.py --checkpoint outputs/checkpoints/best_jepa.pt
python scripts/run_planner.py --checkpoint outputs/checkpoints/best_jepa.pt --state aged_hdf --target rejuvenated_repair
python -c "import streamlit; print(streamlit.__version__)"
```

Outputs verified:
- `outputs/reports/benchmark_report.md`
- `outputs/reports/benchmark_metrics.json`
- `outputs/reports/planner_report.md`
- `outputs/reports/top_k_actions.json`

Known limitations:
- The benchmark and planner remain toy engineering validation only.
- Planner Top-K actions are not recommendations, protocols, or biological discovery claims.
- The package demo depends on Streamlit being installed from project dependencies.
- No real data integration, dataset download, h5ad loader, perturbation adapter, or clinical/biological recommendation system was added.

Next recommended step:
After preserving this compatibility fix, proceed to Goal 4 real-data integration scaffolding.
