# Cloud RTX 4090 Guide

## Status
Placeholder guide for future cloud experiments.

## Target Hardware
- RTX 4090 cloud instance.
- Approximate cost assumption: 2 CNY/hour.

## Planned Workflow
1. Prepare a small config in `configs/`.
2. Upload code and small required inputs.
3. Run the cloud experiment script.
4. Package results.
5. Download only configs, logs, metrics, small plots, and model summaries.
6. Update `docs/progress_log.md`.

## Planned Files
- `configs/cloud_4090.yaml`
- `scripts/run_cloud_experiment.sh`
- `scripts/package_results.py`

## Cost Controls
- Use short smoke runs first.
- Keep batch sizes and epochs explicit.
- Stop instances after runs finish.
- Do not start large training by default.
