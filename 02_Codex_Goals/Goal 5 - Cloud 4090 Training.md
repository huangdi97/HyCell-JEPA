# Goal 5 - Cloud 4090 Training

Copy and paste this into Codex:

```text
/goal Add cloud RTX 4090 training workflow, result packaging, cloud guide, and Makefile targets.

Objective:
Create a controlled cloud experiment workflow for HyCell-JEPA on an RTX 4090 instance. This goal should make cloud runs reproducible, cost-aware, and easy to package, without starting large training by default.

Before coding:
- Read AGENTS.md, README.md, docs/PROJECT_BRIEF.md, docs/cloud_4090_guide.md, docs/model_card.md, docs/benchmark_report.md, and docs/progress_log.md.
- Inspect existing configs, scripts, and training code.
- Do not run cloud jobs automatically.
- Do not download huge datasets automatically.

Scope:
1. Add cloud training config for RTX 4090.
2. Add run_cloud_experiment.sh with explicit arguments and safe defaults.
3. Add package_results.py to collect configs, logs, metrics, plots, and small summaries.
4. Add Makefile targets for local smoke, cloud smoke, package results, and tests.
5. Expand docs/cloud_4090_guide.md with setup, run, package, download, and shutdown workflow.
6. Add tests for package_results.py and config validation where practical.

Suggested files:
- configs/cloud_4090.yaml
- scripts/run_cloud_experiment.sh
- scripts/package_results.py
- Makefile
- tests/test_package_results.py

Constraints:
- Do not start remote jobs automatically.
- Keep default cloud run small.
- Make cost controls explicit.
- Package only small result artifacts.
- Keep outputs in outputs/.
- Avoid storing secrets in the repo.

Definition of done:
1. Cloud config documents RTX 4090 assumptions and safe defaults.
2. Cloud run script is executable in Unix-like environments and has clear help text.
3. Result packaging script creates a small archive or folder manifest.
4. Makefile targets are documented.
5. Cloud guide includes cost-control and shutdown steps.
6. Tests pass locally.

Verification commands:
python scripts/package_results.py --help
make help
make test
find . -maxdepth 3 -type f | sort
git status

Before finishing:
Update docs/progress_log.md with files changed, commands run, known limitations, and the next recommended step.
```
