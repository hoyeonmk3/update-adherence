# -*- coding: utf-8 -*-
"""Table 5 of the paper: contribution of each rule on the 24 Update Conflict scenarios.
Rows SS-noRetire, EpSem-SS, LWW, TS-Read: context outcomes (C/SR/SO/L), archive operations, UC recall, UC CCR.
Also the archive operations and recall of EpSem-SS and LWW on the 48 Forgetting and Noise Tolerance scenarios,
and the breakdown of the LWW archive operations (exact repetitions of messages outside the ground truth).
Run from the repository root: python analysis/rule_contribution.py
"""
import collections
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import RESULTS, J, scenarios, ledger, context_category, md_table


def cats(records, key="context_ua"):
    ct = collections.Counter()
    for x in records:
        for c in x[key]:
            ct[context_category(c)] += 1
    return "%d/%d/%d/%d" % (ct["Correct"], ct["Stale-Retained"], ct["Stale-Only"], ct["Lost"])


def archives(records):
    return sum(1 for x in records for e in x.get("supersession_events", []) if e.get("type") == "supersession")


def means(records):
    return st.mean(float(x["recall"]) for x in records), st.mean(float(x["ccr"]) for x in records)


def lww_repetitions(records, S):
    """Archive operations of LWW triggered by a message that is not a ground-truth constraint and that recurs
    verbatim in the conversation (the always-affirmative judgment archives the earlier identical record).
    The event data carries the incoming message as new_content."""
    n_rep = 0
    n_total = 0
    for x in records:
        s = S[x["scenario_id"]]
        gt = set(g if isinstance(g, str) else g.get("content", "") for g in s.get("ground_truth_constraints", []))
        texts = collections.Counter((t.get("text") or t.get("content") or "").strip() for t in s["turns"])
        for e in x.get("supersession_events", []):
            if e.get("type") != "supersession":
                continue
            n_total += 1
            d = e.get("data")
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except Exception:
                    d = {}
            new = (d.get("new_content") or "").strip() if isinstance(d, dict) else ""
            if new and new not in gt and texts.get(new, 0) >= 2:
                n_rep += 1
    return n_rep, n_total


def main():
    S = scenarios()
    nor = [x for x in J(RESULTS / "a3_noretire.json") if x["scenario_type"] == "UPDATE_CONFLICT"]
    ss = ledger("behavior_EpSemSupersession.json")
    lww = ledger("behavior_LWWMemory.json")
    ts = ledger("behavior_TSRead.json")
    rows = [
        ["SS-noRetire", cats(nor, "ua"), 0] + ["%.3f" % v for v in means(nor)],
        ["EpSem-SS", cats(ss), archives(ss)] + ["%.3f" % v for v in means(ss)],
        ["LWW", cats(lww), archives(lww)] + ["%.3f" % v for v in means(lww)],
        ["TS-Read", cats(ts), 0] + ["%.3f" % v for v in means(ts)],
    ]
    out = ["### Table 5. Contribution of each rule on the 24 Update Conflict scenarios\n",
           md_table(["Configuration", "Context outcomes (C/SR/SO/L)", "Archive operations", "UC recall", "UC CCR"], rows), ""]
    ssfn = ledger("behavior_EpSemSupersession_fn_canonical.json")
    lwwfn = ledger("behavior_LWWMemory_fn.json")
    out.append("F/N scenarios (48): EpSem-SS archive operations %d, mean recall %.3f; LWW archive operations %d, mean recall %.3f"
               % (archives(ssfn), means(ssfn)[0], archives(lwwfn), means(lwwfn)[0]))
    rep, tot = lww_repetitions(lww, S)
    out.append("LWW UC archive operations that repeat a non-ground-truth message verbatim: %d of %d" % (rep, tot))
    txt = "\n".join(out)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
