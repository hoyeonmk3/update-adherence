#!/usr/bin/env bash
# Recompute every table and figure value of the paper from the released result files. No model call is made.
# Run from the repository root: bash reproduce.sh
set -e
cd "$(dirname "$0")"
echo "[1/3] integrity of the released files"
shasum -a 256 -c MANIFEST.sha256 --quiet && echo "manifest OK"
echo "[2/3] tables, cross-tabulations, event breakdowns, retention summary, figure data"
python analysis/make_tables.py > /dev/null
echo "written: analysis/tables.md, figures/data/*.csv"
echo "[3/3] independent checks"
python analysis/behavior_strict_by_domain.py | tail -n 12
python analysis/prompt_ablation_aggregate.py | head -n 20
python analysis/mem0_v3_summary.py | tail -n 8
python analysis/offline_analyses.py > /dev/null && echo "written: analysis/offline_analyses_report.md"
echo "done"
