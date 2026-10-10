# -*- coding: utf-8 -*-
"""Retention and compression over the 72 scenarios (Results, "Retention and Compression"; Figs. 6, 7, 8).
Per-scenario recall and CCR of the five primary configurations come from the canonical files:
Batch A (holdout_v4): Naive, RAG, EpSem, EpSem-F from v4_holdout_20260601_023636.json and EpSem-SS from
v4_holdout_20260602_215257.json (the rerun with the final supersession module); Batch B from v5_holdout_merged.json.
Writes figures/data/fig6_means.csv, fig7a_recall_by_length.csv, fig7b_recall_by_type.csv, fig8_scenario_recall_ccr.csv
and prints the paired EpSem-SS minus EpSem-F differences with bootstrap intervals (10,000 resamples, seed 20260812).
Run from the repository root: python analysis/retention_summary.py
"""
import csv
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import ROOT, RESULTS, J, md_table

CANON = RESULTS / "canonical"
FIG = ROOT / "figures" / "data"
PRIMARY = [("Naive", "NaiveMemory"), ("RAG", "RagMemory"), ("EpSem", "EpSemMemory"), ("EpSem-F", "EpSemFiltered"), ("EpSem-SS", "EpSemSupersession")]
TYPES = [("FORGETTING", "forgetting"), ("NOISE_TOLERANCE", "noise_tolerance"), ("UPDATE_CONFLICT", "update_conflict")]


def per_scenario():
    a = J(CANON / "v4_holdout_20260601_023636.json")
    a_ss = J(CANON / "v4_holdout_20260602_215257.json")
    b = J(CANON / "v5_holdout_merged.json")
    data = {}
    for name, key in PRIMARY:
        recs = (a_ss[key] if key == "EpSemSupersession" else a[key]) + b[key]
        data[name] = {x["scenario_id"]: (float(x["recall"]), float(x["ccr"]), x["scenario_type"], int(x["total_turns"])) for x in recs}
        assert len(data[name]) == 72, (name, len(data[name]))
    return data


def main():
    data = per_scenario()
    scen = sorted(data["EpSem-SS"])
    FIG.mkdir(parents=True, exist_ok=True)
    out = []
    # Fig 6 means
    rows = []
    with open(FIG / "fig6_means.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["configuration", "recall_mean", "ccr_mean"])
        for name, _ in PRIMARY:
            r = st.mean(data[name][s][0] for s in scen)
            c = st.mean(data[name][s][1] for s in scen)
            w.writerow([name, "%.4f" % r, "%.4f" % c])
            rows.append([name, "%.3f" % r, "%.3f" % c])
    out.append("### Fig. 6 means over 72 scenarios\n")
    out.append(md_table(["Configuration", "Recall", "CCR"], rows))
    out.append("")
    # Fig 7a by length, 7b by type
    with open(FIG / "fig7a_recall_by_length.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["configuration", "t200", "t500", "t1000"])
        for name, _ in PRIMARY:
            w.writerow([name] + ["%.4f" % st.mean(v[0] for v in data[name].values() if v[3] == L) for L in (200, 500, 1000)])
    with open(FIG / "fig7b_recall_by_type.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["configuration"] + [t[1] for t in TYPES])
        for name, _ in PRIMARY:
            w.writerow([name] + ["%.4f" % st.mean(v[0] for v in data[name].values() if v[2] == t) for t, _ in TYPES])
    rows = [[name] + ["%.3f" % st.mean(v[0] for v in data[name].values() if v[3] == L) for L in (200, 500, 1000)] + ["%.3f" % st.mean(v[0] for v in data[name].values() if v[2] == t) for t, _ in TYPES] for name, _ in PRIMARY]
    out.append("### Fig. 7 recall by length and by type\n")
    out.append(md_table(["Configuration", "200", "500", "1000", "Forgetting", "Noise Tolerance", "Update Conflict"], rows))
    out.append("")
    # Fig 8 per scenario
    with open(FIG / "fig8_scenario_recall_ccr.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["configuration", "scenario_id", "total_turns", "scenario_type", "recall", "ccr"])
        for name, _ in PRIMARY:
            for s in scen:
                r, c, t, L = data[name][s]
                w.writerow([name, s, L, t, "%.6f" % r, "%.4f" % c])
    ss = data["EpSem-SS"]
    perfect = sum(1 for s in scen if ss[s][0] >= 1.0)
    below = [(s, ss[s][0]) for s in scen if ss[s][0] < 1.0]
    out.append("EpSem-SS at recall 1.000 in %d of 72 scenarios, minimum %.3f; below 1.000: %s" % (perfect, min(v[0] for v in ss.values()), ", ".join("%s %.3f" % b for b in below)))
    # paired differences SS - F and bootstrap
    gain = [ss[s][0] - data["EpSem-F"][s][0] for s in scen]
    cost = [data["EpSem-F"][s][1] - ss[s][1] for s in scen]
    pos, neg, tie = sum(1 for g in gain if g > 1e-12), sum(1 for g in gain if g < -1e-12), sum(1 for g in gain if abs(g) <= 1e-12)
    rng = random.Random(20260812)
    idx = list(range(72))
    samples = [[rng.choice(idx) for _ in range(72)] for _ in range(10000)]

    def ci(vals):
        m = sorted(sum(vals[i] for i in s) / 72 for s in samples)
        return m[249], m[9749]

    out.append("Paired recall difference EpSem-SS minus EpSem-F: positive %d, negative %d, tied %d; mean %.4f, bootstrap 95%% interval %.3f to %.3f" % (pos, neg, tie, sum(gain) / 72, *ci(gain)))
    out.append("Paired CCR difference EpSem-F minus EpSem-SS: mean %.4f, bootstrap 95%% interval %.3f to %.3f" % (sum(cost) / 72, *ci(cost)))
    txt = "\n".join(out)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
