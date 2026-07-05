# Goal 4 - Real Data Integration

Copy and paste this into Codex:

```text
/goal Add real data integration scaffolding for h5ad/csv/npz loaders, AnnData schema validation, HDF aging adapter, and perturbation adapter.

Objective:
Prepare HyCell-JEPA to ingest real single-cell perturbation datasets without downloading large data automatically. This goal should add loaders, validators, adapters, documentation, and tests using tiny fixtures only.

Before coding:
- Read AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/data_card.md, docs/real_data_integration.md, docs/limitations.md, and docs/progress_log.md.
- Inspect existing toy data and model code.
- Do not download large datasets.
- Do not commit real datasets.

Scope:
1. Add h5ad, csv, and npz loader interfaces.
2. Add AnnData schema validator with clear error messages.
3. Add HDF aging adapter for dataset metadata mapping.
4. Add perturbation adapter for canonical action labels.
5. Add tiny test fixtures or generated fixtures only.
6. Add CLI validation script.
7. Update docs/data_card.md and docs/real_data_integration.md.

Suggested files:
- configs/real_data_schema.yaml
- scripts/validate_dataset.py
- src/hycell/data_loaders.py
- src/hycell/schema.py
- src/hycell/perturbation_adapter.py
- tests/test_data_loaders.py
- tests/test_schema.py
- tests/test_perturbation_adapter.py

Constraints:
- No automatic huge downloads.
- No large files.
- Keep loaders explicit about required and optional fields.
- Preserve original dataset labels alongside canonical labels.
- Fail clearly on ambiguous schema.

Definition of done:
1. Loader interfaces support h5ad/csv/npz or degrade with clear dependency messages.
2. Schema validator checks required fields and reports actionable errors.
3. HDF aging adapter maps validated metadata to MVP context conventions.
4. Perturbation adapter maps dataset-specific perturbations to canonical actions.
5. Tests pass using tiny fixtures.
6. Real data documentation is updated.

Verification commands:
python scripts/validate_dataset.py --help
pytest
find . -maxdepth 3 -type f | sort
git status

Before finishing:
Update docs/progress_log.md with files changed, commands run, known limitations, and the next recommended step.
```
