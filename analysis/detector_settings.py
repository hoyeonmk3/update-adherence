# -*- coding: utf-8 -*-
"""Table 6 of the paper: context-level UA under the threshold and embedding-space settings of the retirement rule.
Rows 1-4: nomic-embed-text at thresholds 0.85, 0.90, 0.92 (operating), 0.95, with the Correct counts of Batch A and
Batch B, UC recall and CCR (means over the 24 Update Conflict scenarios), and F/N recall where measured.
Rows 5-8: bge-small-en-v1.5 and gte-small with the thresholds unchanged (0.92) or mapped to the matching F/N quantiles.
Run from the repository root: python analysis/detector_settings.py
"""
import collections
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import RESULTS, J, ledger, context_category, batch, md_table


def ua_counts(records, key):
    tot = collections.Counter()
    for x in records:
        b = batch(x["scenario_id"])
        for c in x[key]:
            cat = context_category(c)
            tot["n"] += 1
            tot["n" + b] += 1
            if cat == "Correct":
                tot["c"] += 1
                tot["c" + b] += 1
    return tot


def fmt_ua(t):
    return "%d/%d (%.1f%%)" % (t["c"], t["n"], 100.0 * t["c"] / t["n"])


def means(records):
    return st.mean(float(x["recall"]) for x in records), st.mean(float(x["ccr"]) for x in records)


def main():
    rows = []
    op = ledger("behavior_EpSemSupersession.json")
    fn_recall = {
        "0.85": st.mean(float(x["recall"]) for x in J(RESULTS / "ss085_fn.json")),
        "0.92": st.mean(float(x["recall"]) for x in ledger("behavior_EpSemSupersession_fn_canonical.json")),
    }
    for th, src, key in [("0.85", "sweep_th85.json", "ua"), ("0.90", "sweep_th90.json", "ua"), ("0.92", None, "context_ua"), ("0.95", "sweep_th95.json", "ua")]:
        rec = op if src is None else J(RESULTS / src)
        t = ua_counts(rec, key)
        r, c = means(rec)
        label = "0.92, operating" if th == "0.92" else th
        fnr = "%.3f" % fn_recall[th] if th in fn_recall else "Not measured"
        rows.append(["nomic-embed-text", label, fmt_ua(t), "%d/%d" % (t["cA"], t["nA"]), "%d/%d" % (t["cB"], t["nB"]), "%.3f" % r, "%.3f" % c, fnr])
    cal = J(RESULTS / "calib_map.json")["map"]
    for emb, name in [("bge", "bge-small-en-v1.5"), ("gte", "gte-small")]:
        for mode in ("fixed", "quantile"):
            uc = ledger("altemb_%s_%s_uc.json" % (emb, mode))
            fn = ledger("altemb_%s_%s_fn.json" % (emb, mode))
            t = ua_counts(uc, "context_ua")
            r, c = means(uc)
            thr = "0.92, unchanged" if mode == "fixed" else "%.3f, mapped" % float(cal[emb]["supersession"])
            rows.append([name, thr, fmt_ua(t), "Not computed", "Not computed", "%.3f" % r, "%.3f" % c, "%.3f" % st.mean(float(x["recall"]) for x in fn)])
    txt = "### Table 6. Context-level UA under the threshold and embedding-space settings\n\n" + md_table(
        ["Embedder", "Threshold", "Context-level UA", "Batch A", "Batch B", "UC recall", "UC CCR", "F/N recall"], rows)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
