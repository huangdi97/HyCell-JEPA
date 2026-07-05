# Goal 2 - Encoder JEPA

Copy and paste this into Codex:

```text
/goal Implement the HyCell-JEPA Bio-State Encoder, Action Encoder, Context Encoder, and JEPA Transition Core for the toy pipeline.

Objective:
Add the first minimal neural/ML modeling layer for HyCell-JEPA on top of the toy data and gene set scoring pipeline. This goal should keep the model compact, deterministic enough for tests, and runnable on the local RTX 4060 Ti or CPU for smoke tests.

Before coding:
- Read AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/design_summary.md, docs/model_card.md, docs/benchmark_report.md, docs/progress_log.md, and the current toy data/scoring code.
- Verify Goal 1 outputs or create them with the documented commands.
- Do not download data.
- Do not implement full transcriptome diffusion.

Scope:
1. Add Bio-State Encoder for compact gene set/readout features.
2. Add Action Encoder for canonical perturbation/action labels.
3. Add Context Encoder for timepoint, condition, or toy context metadata.
4. Add JEPA Transition Core that predicts next compact belief state from b_t, a_t, c_t, and h_t placeholder/adapter input.
5. Add training and evaluation scripts with CLI entry points.
6. Add configs for toy model training.
7. Add tests for tensor shapes, deterministic small training, config loading, and CLI smoke behavior.
8. Update docs/model_card.md, docs/benchmark_report.md, and docs/progress_log.md.

Suggested files:
- configs/jepa_toy.yaml
- scripts/train_jepa.py
- scripts/evaluate_jepa.py
- src/hycell/encoders.py
- src/hycell/jepa.py
- src/hycell/training.py
- src/hycell/datasets.py
- tests/test_encoders.py
- tests/test_jepa.py
- tests/test_training_smoke.py

Constraints:
- Keep the model small.
- Keep default training fast.
- Do not use huge datasets or external downloads.
- Outputs go in outputs/.
- Toy results are engineering validation only.
- Every major module must have tests.

Definition of done:
1. Encoders produce documented compact embeddings.
2. JEPA Transition Core predicts next belief-state features for toy data.
3. Training script runs a small smoke training job.
4. Evaluation script writes small metrics to outputs/.
5. Tests pass locally.
6. docs/model_card.md and docs/benchmark_report.md reflect the implemented placeholder model and toy benchmark status.

Verification commands:
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/train_jepa.py --config configs/jepa_toy.yaml
python scripts/evaluate_jepa.py --config configs/jepa_toy.yaml
pytest
find . -maxdepth 3 -type f | sort
git status

Before finishing:
Update docs/progress_log.md with files changed, commands run, metrics observed, known limitations, and the next recommended step.
```
