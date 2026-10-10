# Superseded Mem0 results

`behavior_Mem0.json` and `behavior_Mem0_patched.json` were produced on 2026-08-11/12 with the serving engine's default context window of 4,096 tokens. The extraction prompt of mem0ai 2.0.17 is about 8.4k tokens, so every one of the 1,522 library calls ran on a truncated prompt (the Ollama server log recorded `truncating input prompt ... limit=4096` for each). The numbers in these files (exact-string recall 0.066, value-token 11/3/4/30, behavior-level 4 of 45) are therefore not a measurement of Mem0 and are kept only as a record.

The corrected measurement is `results/behavior_Mem0_v3.json` (runner `run_mem0_arm_v3.py`, context window 16,384 tokens, per-call `prompt_eval_count` in `results/calls_mem0_v3.jsonl`, server-log truncation delta 0 in `results/behavior_Mem0_v3.meta.json`).
