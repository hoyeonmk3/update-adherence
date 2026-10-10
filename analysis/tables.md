# Tables and figure data reproduced from results/

### Table 5. Contribution of each rule on the 24 Update Conflict scenarios

| Configuration | Context outcomes (C/SR/SO/L) | Archive operations | UC recall | UC CCR |
|---|---|---|---|---|
| SS-noRetire | 0/45/0/0 | 0 | 1.000 | 0.792 |
| EpSem-SS | 14/26/5/0 | 43 | 0.973 | 0.854 |
| LWW | 14/26/5/0 | 554 | 0.973 | 0.854 |
| TS-Read | 14/31/0/0 | 0 | 1.000 | 0.846 |

F/N scenarios (48): EpSem-SS archive operations 88, mean recall 1.000; LWW archive operations 936, mean recall 1.000
LWW UC archive operations that repeat a non-ground-truth message verbatim: 510 of 554

### Table 6. Context-level UA under the threshold and embedding-space settings

| Embedder | Threshold | Context-level UA | Batch A | Batch B | UC recall | UC CCR | F/N recall |
|---|---|---|---|---|---|---|---|
| nomic-embed-text | 0.85 | 43/45 (95.6%) | 24/25 | 19/20 | 1.000 | 0.857 | 1.000 |
| nomic-embed-text | 0.90 | 28/45 (62.2%) | 17/25 | 11/20 | 0.983 | 0.856 | Not measured |
| nomic-embed-text | 0.92, operating | 14/45 (31.1%) | 11/25 | 3/20 | 0.973 | 0.854 | 1.000 |
| nomic-embed-text | 0.95 | 0/45 (0.0%) | 0/25 | 0/20 | 0.932 | 0.853 | Not measured |
| bge-small-en-v1.5 | 0.92, unchanged | 6/45 (13.3%) | Not computed | Not computed | 0.939 | 0.850 | 1.000 |
| bge-small-en-v1.5 | 0.874, mapped | 43/45 (95.6%) | Not computed | Not computed | 0.995 | 0.858 | 1.000 |
| gte-small | 0.92, unchanged | 45/45 (100.0%) | Not computed | Not computed | 0.994 | 0.863 | 0.998 |
| gte-small | 0.973, mapped | 2/45 (4.4%) | Not computed | Not computed | 0.939 | 0.855 | 1.000 |

### Table 7. Update outcomes and revision similarity by domain (EpSem-SS, Qwen2.5-14B)

| Domain | Events | Similarity median (range) | Context-level UA | Strict answer-level UA | Recall (pooled) |
|---|---|---|---|---|---|
| Engineering | 12 | 0.8959 (0.8473–0.9198) | 0/12 | 8/12 | 59/60 (0.983) |
| Medical | 11 | 0.9213 (0.8766–0.9419) | 6/11 | 7/11 | 61/63 (0.968) |
| Legal | 9 | 0.9209 (0.8436–0.9471) | 5/9 | 8/9 | 25/26 (0.962) |
| Financial | 8 | 0.9113 (0.8599–0.9317) | 2/8 | 7/8 | 46/47 (0.979) |
| General | 5 | 0.9113 (0.8906–0.9299) | 1/5 | 4/5 | 31/31 (1.000) |
| All | 45 | 0.9094 (0.8436–0.9471) | 14/45 | 34/45 | 222/227 (0.978) |

### Table 8. EpSem-SS under the two backbones

| Backbone | Correct | Stale-Retained | Stale-Only | Lost | NewOnly answers |
|---|---|---|---|---|---|
| Qwen2.5-14B | 14 | 26 | 5 | 0 | 34/45 |
| Phi-3 Medium | 12 | 10 | 23 | 0 | 14/45 |

Binary Correct/not-Correct agreement 43/45, full-category agreement 27/45
Discordant events: Correct under Qwen only 2, under Phi-3 only 0; McNemar exact two-sided p = 0.50 (Article S1)
Category shifts Qwen -> Phi-3: Correct -> Stale-Only: 2, Stale-Retained -> Stale-Only: 16
Phi-3 answers by context category: Correct -> NewOnly: 10, Correct -> Both: 1, Correct -> Neither: 1, Stale-Retained -> NewOnly: 4, Stale-Retained -> Both: 4, Stale-Retained -> OldOnly: 1, Stale-Retained -> Neither: 1, Stale-Only -> OldOnly: 23
Phi-3 canonical EpSemMemory: Correct 1 of 45 (C/SR/SO/L 1/24/20/0)
Phi-3 canonical EpSemFiltered: Correct 2 of 45 (C/SR/SO/L 2/23/20/0)
Phi-3 canonical EpSemSupersession: Correct 12 of 45 (C/SR/SO/L 12/10/23/0)

### Table 9. Strict answer-level UA under three answer prompts

| Configuration | Verbatim listing | Own words | No form instruction |
|---|---|---|---|
| Naive | 14 (31.1%) | 11 (24.4%) | 10 (22.2%) |
| RAG | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| EpSem | 21 (46.7%) | 5 (11.1%) | 2 (4.4%) |
| EpSem-F | 24 (53.3%) | 6 (13.3%) | 7 (15.6%) |
| EpSem-SS | 34 (75.6%) | 22 (48.9%) | 18 (40.0%) |
| LWW | 35 (77.8%) | 22 (48.9%) | 18 (40.0%) |

### Naive, NewOnly 14 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Correct | 6 | 5 | 0 | 0 | 1 |
| Stale-Retained | 18 | 9 | 9 | 0 | 0 |
| Lost | 21 | 0 | 0 | 0 | 21 |

### RAG, NewOnly 0 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Lost | 45 | 0 | 0 | 0 | 45 |

### EpSem, NewOnly 21 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Stale-Retained | 30 | 21 | 9 | 0 | 0 |
| Stale-Only | 9 | 0 | 0 | 9 | 0 |
| Lost | 6 | 0 | 0 | 0 | 6 |

### EpSem-F, NewOnly 24 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Stale-Retained | 30 | 24 | 6 | 0 | 0 |
| Stale-Only | 9 | 0 | 0 | 9 | 0 |
| Lost | 6 | 0 | 0 | 0 | 6 |

### EpSem-SS, NewOnly 34 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Correct | 14 | 14 | 0 | 0 | 0 |
| Stale-Retained | 26 | 20 | 6 | 0 | 0 |
| Stale-Only | 5 | 0 | 0 | 5 | 0 |

### LWW, NewOnly 35 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Correct | 14 | 13 | 0 | 0 | 1 |
| Stale-Retained | 26 | 22 | 4 | 0 | 0 |
| Stale-Only | 5 | 0 | 0 | 5 | 0 |

### TS-Read, NewOnly 39 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Correct | 14 | 13 | 0 | 0 | 1 |
| Stale-Retained | 31 | 26 | 5 | 0 | 0 |

### EpSem-SS (Phi-3), NewOnly 14 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Correct | 12 | 10 | 1 | 0 | 1 |
| Stale-Retained | 10 | 4 | 4 | 1 | 1 |
| Stale-Only | 23 | 0 | 0 | 23 | 0 |

### Mem0, NewOnly 6 of 45

| Context | Events | NewOnly | Both | OldOnly | Neither |
|---|---|---|---|---|---|
| Correct | 2 | 2 | 0 | 0 | 0 |
| Stale-Only | 2 | 2 | 0 | 0 | 0 |
| Lost | 41 | 2 | 0 | 5 | 34 |


### A. Naive and RAG context categories by conversation length

Naive
| Turns | Correct | Stale-Retained | Stale-Only | Lost |
|---|---|---|---|---|
| 200 | 2 | 11 | 0 | 2 |
| 500 | 2 | 5 | 0 | 8 |
| 1000 | 2 | 2 | 0 | 11 |

RAG
| Turns | Correct | Stale-Retained | Stale-Only | Lost |
|---|---|---|---|---|
| 200 | 0 | 0 | 0 | 15 |
| 500 | 0 | 0 | 0 | 15 |
| 1000 | 0 | 0 | 0 | 15 |

### B. Similarity bands (outcome codes C, SR, SO)

| Set | Band | Outcome | Events |
|---|---|---|---|
| explicit | 0.85 to 0.92 | SO | 5 |
| explicit | 0.85 to 0.92 | SR | 24 |
| explicit | above 0.92 | C | 14 |
| explicit | below 0.85 | SR | 2 |
| implicit | 0.85 to 0.92 | SO | 5 |
| implicit | 0.85 to 0.92 | SR | 10 |
| implicit | above 0.92 | C | 8 |
| implicit | above 0.92 | SO | 1 |
| implicit | below 0.85 | SR | 1 |

### C. Implicit Stale-Only events and the rule event at the update turn

- hold-out-U002_impT2 gt_008 form=T2 sim=0.9447 events_at_update=[] new_value_in_context=False
- hold-out-U003_impT3 gt_007 form=T3 sim=0.916 events_at_update=[(162, 'conflict_detected')] new_value_in_context=False
- hold-out-U004_impT1 gt_007 form=T1 sim=0.9185 events_at_update=[(116, 'conflict_detected')] new_value_in_context=False
- hold-out-U006_impT3 gt_002 form=T3 sim=0.8642 events_at_update=[(116, 'conflict_detected')] new_value_in_context=False
- hold-out-U011_impT2 gt_012 form=T2 sim=0.898 events_at_update=[(908, 'conflict_detected')] new_value_in_context=False
- hold-out-U012_impT3 gt_004 form=T3 sim=0.8777 events_at_update=[(664, 'conflict_detected')] new_value_in_context=False

### D. EpSem-SS Update Conflict scenarios with recall below 1.000

hold-out-U006 (0.923), hold-out-U012 (0.875), hold-out-U020 (0.800), hold-out-U021 (0.875), hold-out-U024 (0.875)

### E. The five rejected explicit revisions and the recorded conflict judgments

- hold-out-U006 gt_002 sim=0.886 turn 116: {"content": "Update to previous requirement: Minimum wall thickness shall be 404mm (replaces the earlier specific", "reason": "The existing constraint specifies a minimum wall thickness of 452mm, which is a stricter requirement than the new statement proposing a minimum wall thickness of 404mm. Sinc
- hold-out-U012 gt_004 sim=0.8783 turn 664: The new statement explicitly reduces the minimum medication interval from 225 hours to 158 hours, which is a contradiction of the existing constraint.
- hold-out-U020 gt_005 sim=0.865 turn 476: The new statement explicitly replaces the earlier specification, changing the arbitration venue from the 240 jurisdiction to the 252 jurisdiction. This directly contradicts the existing constraint.
- hold-out-U021 gt_008 sim=0.9184 turn 936: The new statement explicitly replaces the existing interest rate cap of 436% with a higher value of 515%, which directly contradicts the original requirement.
- hold-out-U024 gt_006 sim=0.9011 turn 836: The new statement explicitly reduces the minimum surgical margin from 171mm to 152mm, which directly contradicts the existing constraint that mandates a minimum of 171mm.

### Fig. 6 means over 72 scenarios

| Configuration | Recall | CCR |
|---|---|---|
| Naive | 0.344 | 0.437 |
| RAG | 0.000 | 0.982 |
| EpSem | 0.882 | 0.825 |
| EpSem-F | 0.882 | 0.905 |
| EpSem-SS | 0.991 | 0.856 |

### Fig. 7 recall by length and by type

| Configuration | 200 | 500 | 1000 | Forgetting | Noise Tolerance | Update Conflict |
|---|---|---|---|---|---|---|
| Naive | 0.706 | 0.258 | 0.068 | 0.373 | 0.312 | 0.346 |
| RAG | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| EpSem | 0.862 | 0.910 | 0.873 | 0.903 | 0.891 | 0.852 |
| EpSem-F | 0.862 | 0.910 | 0.873 | 0.903 | 0.891 | 0.852 |
| EpSem-SS | 1.000 | 0.988 | 0.984 | 1.000 | 1.000 | 0.973 |

EpSem-SS at recall 1.000 in 67 of 72 scenarios, minimum 0.800; below 1.000: hold-out-U006 0.923, hold-out-U012 0.875, hold-out-U020 0.800, hold-out-U021 0.875, hold-out-U024 0.875
Paired recall difference EpSem-SS minus EpSem-F: positive 42, negative 0, tied 30; mean 0.1091, bootstrap 95% interval 0.082 to 0.138
Paired CCR difference EpSem-F minus EpSem-SS: mean 0.0491, bootstrap 95% interval 0.034 to 0.065

### Fig. 3 context outcomes and Fig. 4 two scores

| Configuration | C/SR/SO/L | Context-level UA % | Strict answer-level UA % |
|---|---|---:|---:|
| Naive | 6/18/0/21 | 13.3 | 31.1 |
| RAG | 0/0/0/45 | 0.0 | 0.0 |
| EpSem | 0/30/9/6 | 0.0 | 46.7 |
| EpSem-F | 0/30/9/6 | 0.0 | 53.3 |
| EpSem-SS | 14/26/5/0 | 31.1 | 75.6 |
| LWW | 14/26/5/0 | 31.1 | 77.8 |
| TS-Read | 14/31/0/0 | 31.1 | 86.7 |
| Mem0 | 1/6/4/34 | 2.2 | 13.3 |
