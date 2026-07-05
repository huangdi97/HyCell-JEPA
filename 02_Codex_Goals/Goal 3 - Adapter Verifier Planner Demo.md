# Goal 3 - Adapter Verifier Planner Demo

Copy and paste this into Codex:

```text
/goal Implement the HDF Adapter, Biological Verifier, Target-State Planner, benchmark script, and Streamlit demo.

Objective:
Complete the first end-to-end HyCell-JEPA MVP loop on toy data: adapt HDF-like context, predict compact state transitions, verify biological plausibility constraints, plan toward target states, benchmark the flow, and expose it through a Streamlit demo.

Before coding:
- Read AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/design_summary.md, docs/limitations.md, docs/model_card.md, docs/benchmark_report.md, docs/progress_log.md, and existing code.
- Run or inspect Goal 1 and Goal 2 verification outputs.
- Do not download data.
- Do not present toy behavior as biological discovery.

Scope:
1. Implement an HDF Adapter that provides HDF-specific action/context mappings for aging, regeneration, and partial reprogramming toy scenarios.
2. Implement a Biological Verifier with explicit rules and warnings.
3. Implement a Target-State Planner over small action sequences.
4. Add benchmark script for toy end-to-end behavior.
5. Add Streamlit demo for toy state, action, prediction, verifier, and planner outputs.
6. Add tests for adapter, verifier, planner, benchmark smoke behavior, and demo-import smoke behavior.
7. Update docs/model_card.md, docs/benchmark_report.md, docs/limitations.md, and docs/progress_log.md.

Suggested files:
- configs/benchmark_toy.yaml
- configs/demo.yaml
- scripts/benchmark_toy.py
- scripts/demo_app.py
- src/hycell/hdf_adapter.py
- src/hycell/verifier.py
- src/hycell/planner.py
- src/hycell/benchmark.py
- tests/test_hdf_adapter.py
- tests/test_verifier.py
- tests/test_planner.py
- tests/test_benchmark_smoke.py

Constraints:
- Streamlit demo must clearly show toy/engineering status.
- Keep benchmark outputs small and in outputs/.
- Avoid clinical or biological claims.
- Keep all scripts CLI-runnable.
- Keep tests focused and fast.

Definition of done:
1. HDF Adapter maps toy HDF scenarios into model inputs.
2. Biological Verifier returns structured pass/warn/fail outputs.
3. Planner proposes action sequences toward target compact states.
4. Benchmark script writes metrics/report artifacts.
5. Streamlit demo launches and imports cleanly.
6. Tests pass.
7. Documentation clearly states limitations.

Verification commands:
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/train_jepa.py --config configs/jepa_toy.yaml
python scripts/benchmark_toy.py --config configs/benchmark_toy.yaml
python -m compileall scripts src
pytest
streamlit run scripts/demo_app.py
find . -maxdepth 3 -type f | sort
git status

Before finishing:
Update docs/progress_log.md with files changed, commands run, benchmark/demo status, known limitations, and the next recommended step.
```
