# Reproducibility notes

## What is deterministic

Scoring is deterministic given the generated outputs. Both UA stages use literal rules (exact canonical sentences in the assembled context, parameter-anchored distinguishing value tokens in the answer) and no language-model judge, so every table of the paper is recomputed exactly from `results/` by `analysis/make_tables.py` on any machine.

Generation is deterministic only on the pinned stack. The runners request temperature 0 and seed 42 wherever the interface exposes them, and a repeated EpSem-SS run on the 24 Update Conflict scenarios (`results/behavior_EpSemSupersession_rerun.json`) reproduced the canonical contexts, answers, event outcomes, recall, and CCR exactly. A different Ollama version, model build, or GPU numeric kernel can change generated text, and a similarity judgment that sits near the detector threshold can then flip.

## Pinned stack of the reported runs

| Item | Setting |
|---|---|
| Serving engine | Ollama 0.24.0 (the runners stop on a version mismatch) |
| Primary backbone | `qwen2.5:14b-instruct-q4_K_M`, Q4_K_M, digest 7cdf5a0187d5 |
| Second backbone | `phi3:medium`, Q4_0, digest cf611a26b048 |
| Embedding model | `nomic-embed-text`, F16, 768 dimensions, digest 0a109f422b47 |
| Decoding | Temperature 0, seed 42 where exposed; the Mem0 library interface exposes no seed |
| Context windows | 4,096 tokens for engine and answer calls, 16,384 tokens for every Mem0 library call |
| Compaction interval | 10 turns (`config.yaml`) |
| Hardware | Mac Mini M4 Pro, 24 GB unified memory |
| Operating system | macOS 26.6 recorded for the Mem0 run (`results/behavior_Mem0_v3.meta.json`) |
| Runtime | Python 3.9.6 for the engines; Python 3.12.13, mem0ai 2.0.17, ollama client 0.6.2, qdrant-client 1.19.0 for the Mem0 run |

## Integrity

`MANIFEST.sha256` lists the SHA-256 of every file under `engine/`, `scenarios/`, `results/`, and `figures/data/`. Verify with `shasum -a 256 -c MANIFEST.sha256`. The engine files are identical in every executable statement to the engine of the reported runs. The runners were rewritten from the archived execution tree to repository-relative paths, so the `runner_sha256` fields inside the result files refer to the execution copies, not to the files in `runners/`.

## Mem0 run

`runners/run_mem0_arm_v3.py` issues every mem0ai 2.0.17 library call with a 16,384-token context window, records `prompt_eval_count` per call (`results/calls_mem0_v3.jsonl`, 1,360 calls), and compares the truncation counters of the Ollama server log before and after the run (`results/behavior_Mem0_v3.meta.json`, delta 0). The two earlier runs in `results/superseded/` were made with the default 4,096-token window, under which the extraction prompt of the library (about 8,400 tokens) was truncated on every call; they are kept as a record only.

## Canonical snapshots of Batch A

`results/canonical/v4_holdout_20260601_023636.json` holds the Batch A run of all five primary configurations. EpSem-SS was rerun on Batch A after the supersession module reached its final form, and that rerun, `v4_holdout_20260602_215257.json`, is the EpSem-SS record the paper uses. The EpSem-SS entries of the 06-01 file predate the final module and are not reported anywhere.
