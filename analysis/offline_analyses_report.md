## A. Domain breakdown on the Update Conflict scenarios (store level, exact-string rule)

| Arm | ENGINEERING | MEDICAL | LEGAL | FINANCE | GENERAL | All |
|---|---|---|---|---|---|---|
| Naive | 2/12 | 3/11 | 0/9 | 1/8 | 0/5 | 6/45 (13.3%) |
| RAG | 0/12 | 0/11 | 0/9 | 0/8 | 0/5 | 0/45 (0.0%) |
| EpSem | 0/12 | 0/11 | 0/9 | 0/8 | 0/5 | 0/45 (0.0%) |
| EpSem-F | 0/12 | 0/11 | 0/9 | 0/8 | 0/5 | 0/45 (0.0%) |
| EpSem-SS | 0/12 | 6/11 | 5/9 | 2/8 | 1/5 | 14/45 (31.1%) |
| LWW | 0/12 | 6/11 | 5/9 | 2/8 | 1/5 | 14/45 (31.1%) |
| TS-Read | 0/12 | 6/11 | 5/9 | 2/8 | 1/5 | 14/45 (31.1%) |
| EpSem-SS (Phi-3) | 0/12 | 5/11 | 5/9 | 2/8 | 0/5 | 12/45 (26.7%) |
| Mem0 (v3) | 0/12 | 0/11 | 2/9 | 0/8 | 0/5 | 2/45 (4.4%) |

EpSem-SS failure split by domain (UA / Stale-Retained / Stale-Only / Lost):

| Domain | UA | Stale-Retained | Stale-Only | Lost | events | Wilson 95% |
|---|---|---|---|---|---|---|
| ENGINEERING | 0 | 11 | 1 | 0 | 12 | 0–24% |
| MEDICAL | 6 | 3 | 2 | 0 | 11 | 28–79% |
| LEGAL | 5 | 3 | 1 | 0 | 9 | 27–81% |
| FINANCE | 2 | 5 | 1 | 0 | 8 | 7–59% |
| GENERAL | 1 | 4 | 0 | 0 | 5 | 4–62% |

Behavior-level UA by domain (strict answer-line rule of the paper, verbatim-listing prompt):

| Arm | ENGINEERING | MEDICAL | LEGAL | FINANCE | GENERAL | All |
|---|---|---|---|---|---|---|
| Naive | 2/12 | 4/11 | 4/9 | 3/8 | 1/5 | 14/45 (31.1%) |
| RAG | 0/12 | 0/11 | 0/9 | 0/8 | 0/5 | 0/45 (0.0%) |
| EpSem | 4/12 | 4/11 | 3/9 | 5/8 | 5/5 | 21/45 (46.7%) |
| EpSem-F | 6/12 | 5/11 | 3/9 | 5/8 | 5/5 | 24/45 (53.3%) |
| EpSem-SS | 8/12 | 7/11 | 8/9 | 7/8 | 4/5 | 34/45 (75.6%) |
| LWW | 10/12 | 8/11 | 7/9 | 7/8 | 3/5 | 35/45 (77.8%) |
| TS-Read | 12/12 | 10/11 | 8/9 | 7/8 | 2/5 | 39/45 (86.7%) |
| EpSem-SS (Phi-3) | 3/12 | 4/11 | 5/9 | 2/8 | 0/5 | 14/45 (31.1%) |
| Mem0 (v3) | 1/12 | 0/11 | 3/9 | 2/8 | 0/5 | 6/45 (13.3%) |

Recall by domain (UC-24, ground-truth constraints found / total):

| Arm | ENGINEERING | MEDICAL | LEGAL | FINANCE | GENERAL |
|---|---|---|---|---|---|
| Naive | 17/60 (0.283) | 25/63 (0.397) | 11/26 (0.423) | 21/47 (0.447) | 4/31 (0.129) |
| RAG | 0/60 (0.000) | 0/63 (0.000) | 0/26 (0.000) | 0/47 (0.000) | 0/31 (0.000) |
| EpSem | 58/60 (0.967) | 57/63 (0.905) | 20/26 (0.769) | 31/47 (0.660) | 28/31 (0.903) |
| EpSem-F | 58/60 (0.967) | 57/63 (0.905) | 20/26 (0.769) | 31/47 (0.660) | 28/31 (0.903) |
| EpSem-SS | 59/60 (0.983) | 61/63 (0.968) | 25/26 (0.962) | 46/47 (0.979) | 31/31 (1.000) |
| LWW | 59/60 (0.983) | 61/63 (0.968) | 25/26 (0.962) | 46/47 (0.979) | 31/31 (1.000) |
| TS-Read | 60/60 (1.000) | 63/63 (1.000) | 26/26 (1.000) | 47/47 (1.000) | 31/31 (1.000) |
| EpSem-SS (Phi-3) | 54/60 (0.900) | 59/63 (0.937) | 24/26 (0.923) | 41/47 (0.872) | 26/31 (0.839) |
| Mem0 (v3) | 5/60 (0.083) | 3/63 (0.048) | 3/26 (0.115) | 0/47 (0.000) | 0/31 (0.000) |

Scenario-mean recall by domain, all 72 scenarios (canonical runs):

| Config | ENGINEERING | MEDICAL | LEGAL | FINANCE | GENERAL | All |
|---|---|---|---|---|---|---|
| Naive | 0.336 (n=18) | 0.361 (n=18) | 0.455 (n=12) | 0.403 (n=12) | 0.161 (n=12) | 0.3440 |
| RAG | 0.000 (n=18) | 0.000 (n=18) | 0.000 (n=12) | 0.000 (n=12) | 0.000 (n=12) | 0.0000 |
| EpSem | 0.971 (n=18) | 0.946 (n=18) | 0.827 (n=12) | 0.675 (n=12) | 0.914 (n=12) | 0.8818 |
| EpSem-F | 0.971 (n=18) | 0.946 (n=18) | 0.827 (n=12) | 0.675 (n=12) | 0.914 (n=12) | 0.8818 |
| EpSem-SS | 0.996 (n=18) | 0.986 (n=18) | 0.983 (n=12) | 0.990 (n=12) | 1.000 (n=12) | 0.9909 |

## B. Threshold selection with a validation/test split (half A = Batch A, U001–U012; half B = Batch B, U013–U024)

| Threshold | UA half A | UA half B | UA all | UC recall A | UC recall B | F/N recall (all 48) |
|---|---|---|---|---|---|---|
| 0.85 | 24/25 (96.0%) | 19/20 (95.0%) | 43/45 | 1.000 | 1.000 | 1.000 |
| 0.90 | 17/25 (68.0%) | 11/20 (55.0%) | 28/45 | 0.983 | 0.983 | nan |
| 0.92 | 11/25 (44.0%) | 3/20 (15.0%) | 14/45 | 0.983 | 0.963 | 1.000 |
| 0.95 | 0/25 (0.0%) | 0/20 (0.0%) | 0/45 | 0.918 | 0.946 | nan |

F/N recall is available at 0.85 (ss085_fn.json) and 0.92 (canonical). F/N recall by half at 0.85: A=1.000, B=1.000
Selection rule: maximize validation-half store-level UA subject to F/N recall = 1.000. F/N recall is measured at [0.85, 0.92] only, so the eligible candidates are [0.85, 0.92].
  validate on half A -> pick 0.85; held-out half B: 19/20 = 95.0%
  validate on half B -> pick 0.85; held-out half A: 24/25 = 96.0%

## C. Store-level scoring sensitivity: exact-string vs value-token rules (UC-24)

| Arm | exact: UA/SR/SO/Lost | value-token (anywhere): UA/SR/SO/Lost | value-token (same line as parameter phrase): UA/SR/SO/Lost |
|---|---|---|---|
| Naive | 6/18/0/21 | 7/20/1/17 | 6/18/0/21 |
| RAG | 0/0/0/45 | 0/0/1/44 | 0/0/0/45 |
| EpSem | 0/30/9/6 | 1/30/9/5 | 0/30/9/6 |
| EpSem-F | 0/30/9/6 | 1/30/9/5 | 0/30/9/6 |
| EpSem-SS | 14/26/5/0 | 12/28/5/0 | 14/26/5/0 |
| LWW | 14/26/5/0 | 12/28/5/0 | 14/26/5/0 |
| TS-Read | 14/31/0/0 | 12/33/0/0 | 14/31/0/0 |
| EpSem-SS (Phi-3) | 12/10/23/0 | 10/13/22/0 | 12/10/23/0 |
| Mem0 (v3) | 2/0/2/41 | 1/6/4/34 | 2/2/1/40 |

## D. RAG retrieval settings (UC-24 store and behavior level; recall on all 72 where available)

| RAG setting | file | recall (UC-24) | recall (72) | store UA | behavior UA (strict) |
|---|---|---|---|---|---|
| k=5 (canonical) | behavior_RagMemory.json | 0.000 | nan | 0/45 | 0/45 |
| k=20 | behavior_RagMemory_ragk20.json | 0.000 | 0.000 | 0/45 | 0/45 |
| query reformulated with domain keywords, k=5 | behavior_RagMemory_ragreform.json | 0.000 | 0.000 | 0/45 | 0/45 |

## E. Statistics

Wilcoxon (EpSem-SS vs EpSem-F per-scenario recall, n=72): zero differences = 30, positive = 42, negative = 0. Rank-biserial 1.000 follows from negative = 0 among the 42 discordant pairs (zeros excluded under the standard 'wilcox' zero method).
  scipy wilcoxon zero_method=wilcox: p = 1.33e-08
  scipy wilcoxon zero_method=pratt: p = 2.66e-10
  scipy wilcoxon zero_method=zsplit: p = 8.69e-10
Wilson 95% CI EpSem-SS store UA (Qwen): 14/45 = 31.1% [19.5, 45.7]
Wilson 95% CI EpSem-SS store UA (Phi-3): 12/45 = 26.7% [16.0, 41.0]
Wilson 95% CI EpSem-SS behavior UA verbatim: 34/45 = 75.6% [61.3, 85.8]
Wilson 95% CI EpSem-SS behavior UA own-words: 22/45 = 48.9% [35.0, 63.0]
Wilson 95% CI EpSem-SS behavior UA no-form: 18/45 = 40.0% [27.0, 54.5]
Wilson 95% CI Naive store UA: 6/45 = 13.3% [6.3, 26.2]
