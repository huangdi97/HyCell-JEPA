# Progress Log

## How To Update
- Add a dated entry after each meaningful Codex goal or manual work session.
- Record files created or changed, commands run, known limitations, and the recommended next step.
- Keep entries factual. Do not present toy-data behavior as biological discovery.

## Current Status
Bootstrap scaffold complete. The repository now has project memory, Obsidian control files, Codex goal prompts, and initial documentation. No model code or data pipeline has been implemented yet.

## Current Milestone
Milestone 0: project memory and workflow scaffold.

## Next Action
Run Goal 1: scaffold toy single-cell perturbation data, gene set scoring, and evidence graph.

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
