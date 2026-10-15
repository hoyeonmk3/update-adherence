#!/usr/bin/env bash
# Recompute every table and figure value of the paper from the released result files. No model call is made.
# Run from the repository root: bash reproduce.sh
# Needs Python 3.10 or later with the packages of requirements.txt (SciPy optional, see README).
# Any failing step stops the script with a non-zero exit status.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python}"
echo "[1/3] integrity of the released files"
"$PY" analysis/verify_manifest.py
echo "[2/3] tables, cross-tabulations, event breakdowns, retention summary, figure data"
"$PY" analysis/make_tables.py > /dev/null
echo "written: analysis/tables.md, figures/data/*.csv"
echo "[3/3] independent checks"
log="$(mktemp -d)"
"$PY" analysis/behavior_strict_by_domain.py > "$log/domain.txt"
tail -n 12 "$log/domain.txt"
"$PY" analysis/prompt_ablation_aggregate.py > "$log/prompt.txt"
head -n 20 "$log/prompt.txt"
"$PY" analysis/mem0_v3_summary.py > "$log/mem0.txt"
tail -n 8 "$log/mem0.txt"
"$PY" analysis/offline_analyses.py > /dev/null
echo "written: analysis/offline_analyses_report.md"
rm -rf "$log"
echo "done"
