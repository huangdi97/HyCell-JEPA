# Acceptance Contracts

This file defines the exact repository contracts Codex must verify before marking a HyCell-JEPA goal complete. A goal is not complete just because tests pass; the named CLI files, configs, docs, generated-output behavior, and verification commands must also work in the current worktree.

## Shared Contract For Every Goal
- Read `AGENTS.md`, `README.md`, relevant docs, and the active goal file before changing code.
- Keep generated artifacts in `outputs/` or another ignored generated-data path.
- Do not download datasets automatically.
- Do not commit generated outputs, caches, checkpoints, large datasets, or local logs.
- Keep every script named in the goal as a runnable CLI entry point.
- Run the goal-specific verifier when it exists.
- Run `pytest` before claiming completion.
- Run `find . -maxdepth 3 -type f | sort` and `git status` before final handoff unless a goal file explicitly replaces those commands.
- Update `docs/progress_log.md` with files changed, commands run, known limitations, and the next recommended step.

## Goal 1 Contract - Toy Data, Scoring, Evidence Graph
Goal 1 is complete only when all of the following are true:

Required files:
- `pyproject.toml`
- `requirements.txt`
- `configs/toy_data.yaml`
- `configs/gene_sets.yaml`
- `scripts/make_toy_data.py`
- `scripts/score_gene_sets.py`
- `scripts/build_evidence_graph.py`
- `src/hycell/toy_data.py`
- `src/hycell/gene_sets.py`
- `src/hycell/evidence_graph.py`
- `tests/test_toy_data.py`
- `tests/test_gene_sets.py`
- `tests/test_evidence_graph.py`

Required behavior:
- Package metadata exists so editable installs and dependency installs have an authoritative source.
- Toy CSV data can be generated deterministically from `configs/toy_data.yaml`.
- Toy NPZ generation mode exists for local compatibility checks without requiring a large default output.
- Gene set scores can be generated from the toy CSV output.
- The evidence graph can be generated from toy scores.
- Generated data lands in ignored output/data paths.
- Toy-data documentation states that outputs are engineering validation only.

Required verification:

```bash
bash scripts/verify_goal1.sh
pytest
find . -maxdepth 3 -type f | sort
git status
```

## Goal 2 Contract - Encoders And JEPA Core
Goal 2 is complete only when Goal 1 still passes and all of the following are true:

Required files:
- `configs/jepa_toy.yaml`
- `configs/train_local.yaml`
- `scripts/train_encoder.py`
- `scripts/train_jepa.py`
- `scripts/evaluate_jepa.py`
- `src/hycell/datasets.py`
- `src/hycell/encoders.py`
- `src/hycell/jepa.py`
- `src/hycell/training.py`
- `tests/test_encoders.py`
- `tests/test_jepa.py`
- `tests/test_training_smoke.py`

Required behavior:
- Encoder training writes `outputs/checkpoints/best_encoder.pt` and `outputs/embeddings/embeddings.npy`.
- JEPA training writes the documented compatibility artifacts under `outputs/checkpoints/` and `outputs/reports/`.
- The config loader supports the repository's local config syntax and fails clearly when files are missing.
- Evaluation writes metrics to `outputs/`.
- Tests cover shapes, deterministic smoke behavior, config loading, and artifact creation.

Required verification:

```bash
bash scripts/verify_goal2.sh
pytest
find . -maxdepth 3 -type f | sort
git status
```

## Goal 3 Contract - Adapter, Verifier, Planner, Benchmark, Demo
Goal 3 is complete only when Goal 2 still passes and all of the following are true:

Required files:
- `configs/benchmark_toy.yaml`
- `configs/demo.yaml`
- `scripts/benchmark_toy.py`
- `scripts/eval_benchmark.py`
- `scripts/run_planner.py`
- `scripts/demo_app.py`
- `src/hycell/hdf_adapter.py`
- `src/hycell/verifier.py`
- `src/hycell/planner.py`
- `src/hycell/benchmark.py`
- `src/hycell/demo/app.py`
- `tests/test_hdf_adapter.py`
- `tests/test_verifier.py`
- `tests/test_planner.py`
- `tests/test_benchmark_smoke.py`

Required behavior:
- HDF adapter maps toy HDF scenarios into model inputs.
- Biological verifier returns structured pass/warn/fail outputs.
- Planner writes top-k toy action reports and never presents actions as biological recommendations.
- Benchmark CLI writes metrics/report artifacts.
- Both demo paths import or launch cleanly when Streamlit is installed.
- Documentation states toy/demo limitations clearly.

Required verification:

```bash
bash scripts/verify_goal3.sh
pytest
find . -maxdepth 3 -type f | sort
git status
```

## Goal 4 Contract - Real Data Integration
Goal 4 must not be started until the Goal 1, Goal 2, and Goal 3 verifier scripts pass in the current worktree.

When started, Goal 4 is complete only when all of the following are true:

Required files:
- `configs/real_data_schema.yaml`
- `scripts/validate_dataset.py`
- `src/hycell/data_loaders.py`
- `src/hycell/schema.py`
- `src/hycell/perturbation_adapter.py`
- `tests/test_data_loaders.py`
- `tests/test_schema.py`
- `tests/test_perturbation_adapter.py`

Required behavior:
- Loader interfaces support `.h5ad`, `.csv`, and `.npz`, or fail with clear optional-dependency messages.
- Schema validation reports missing observation fields, missing gene identifiers, shape mismatches, and ambiguous labels clearly.
- Perturbation mapping preserves original dataset labels alongside canonical action labels.
- HDF aging metadata maps into MVP context conventions without claiming biological interpretation.
- Tests use only tiny generated fixtures.
- No real dataset is downloaded or committed.

Required verification:

```bash
bash scripts/verify_goal4.sh
pytest
find . -maxdepth 3 -type f | sort
git status
```

## Goal 4.5 Contract - Real Data Smoke Test
Goal 4.5 is complete only when Goal 4 remains valid and all of the following are true:

Required files:
- `scripts/inspect_dataset.py`
- `scripts/preprocess_data.py`
- `docs/real_data_smoke_test.md`
- `scripts/verify_goal4_real_smoke.sh`
- `tests/test_real_data_smoke.py`

Required behavior:
- Inspect and preprocess CLIs work with tiny local `.csv`, `.npz`, or `.h5ad` candidates through the Goal 4 loader interfaces.
- If no local dataset is provided or a path is missing, the CLIs fail gracefully with a clear no-download message.
- The smoke verifier creates only tiny local fixtures under ignored output paths.
- The toy pipeline remains runnable.
- No real dataset is downloaded or committed.
- No Goal 5 cloud training workflow is implemented.

Required verification:

```bash
bash scripts/verify_goal4_real_smoke.sh
pytest
find . -maxdepth 3 -type f | sort
git status
```

## Goal 5 Contract - Cloud RTX 4090 Workflow
Goal 5 is complete only when Goal 4.5 remains valid and all of the following are true:

Required files:
- `configs/cloud_4090.yaml`
- `scripts/run_cloud_experiment.sh`
- `scripts/package_results.py`
- `Makefile`
- `tests/test_package_results.py`

Required behavior:
- Cloud config documents RTX 4090 assumptions, runtime limits, and safe defaults.
- Cloud scripts do not start remote jobs or download large datasets automatically.
- Result packaging collects only small configs, logs, metrics, plots, and summaries.
- Make targets include help, tests, local smoke, cloud smoke, and package results.
- Cloud guide includes setup, cost controls, shutdown, packaging, and download steps.
- Secrets are never stored in the repo.

Required verification:

```bash
python scripts/package_results.py --help
make help
make test
find . -maxdepth 3 -type f | sort
git status
```
