#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python.exe >/dev/null 2>&1; then
  PYTHON_BIN="python.exe"
elif command -v py.exe >/dev/null 2>&1; then
  PYTHON_BIN="py.exe -3"
else
  echo "No Python executable found. Set PYTHON=/path/to/python and rerun." >&2
  exit 127
fi

required_docs=(
  "README.md"
  "docs/design_summary.md"
  "docs/model_card.md"
  "docs/data_card.md"
  "docs/benchmark_report.md"
  "docs/limitations.md"
  "docs/roadmap.md"
  "docs/release_v0.1.md"
)

for path in "${required_docs[@]}"; do
  test -f "$path"
done

$PYTHON_BIN -m pytest
bash scripts/verify_goal1.sh
bash scripts/verify_goal2.sh
bash scripts/verify_goal3.sh
bash scripts/verify_goal4.sh
bash scripts/verify_goal4_real_smoke.sh
bash scripts/verify_goal5.sh
bash scripts/verify_goal6.sh
bash scripts/verify_goal7.sh

echo "HyCell-JEPA v0.1 release acceptance passed."
