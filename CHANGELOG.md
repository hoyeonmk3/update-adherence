# Changelog

## v1.1 (2026-10-15)

Reproducibility additions requested during the PeerJ Computer Science pre-review checks. No scenario, result, engine, or figure-data file changed, so `MANIFEST.sha256` is unchanged.

- `generator/regenerate_scenarios.py`: regenerates all 84 scenario files into a chosen directory and compares them with `scenarios/` (byte for byte, then as parsed JSON) against fixed expected file sets; also checks that `scenarios/fn/` holds exactly the 48 Forgetting and Noise Tolerance files of the two batches. Any missing, unexpected, or differing file gives exit status 1.
- `generator/derive_implicit.py`: the derivation of the 12 implicit-revision variants from the Batch A Update Conflict scenarios, which was not released with v1.0.
- `generator/generate_v5_scenarios.py`: `--output-dir` option (the output location was fixed before), run log written with UTF-8, console output without non-ASCII symbols, a scenario counted only after its file is written, exit status 1 when any scenario failed.
- `analysis/verify_manifest.py`: manifest check with the Python standard library, for machines without `shasum` or `sha256sum`.
- `reproduce.sh`: every step now stops the script on failure (the manifest check and the analysis scripts could fail silently before); uses the Python verifier; `PYTHON` environment variable selects the interpreter.
- Both generators and `analysis/offline_analyses.py` write LF line endings on every platform, so regenerated files are byte-identical to the released files on Windows as well.
- `runners/probe_llm_calls.py`: the call probe failed at import time (`Path` used before it was imported) and pointed at a wrong default scenario path; both fixed.
- `requirements.txt`: Python 3.10 or later stated for the offline steps, SciPy listed as optional (Wilcoxon p-values of the offline report only).
- README: title in sentence case, section "Regenerating the scenarios" with the scenario file structure, dependency split between offline steps and model runners, Windows example, contributing note, development note, citation for v1.1. `docs/reproducibility.md` gained the regeneration section and the verifier. `CITATION.cff` updated to v1.1 with the v1.0 and concept DOIs kept.

## v1.0 (2026-10-10)

Initial release: benchmark scenarios, event records of every reported run, frozen memory engine, runners, and scoring and analysis scripts. Archived at https://doi.org/10.5281/zenodo.23280325.
