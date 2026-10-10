# -*- coding: utf-8 -*-
"""Event-level breakdowns quoted in the Results text.
A. Naive and RAG context categories by conversation length (first subsection).
B. Similarity bands of the 45 explicit and 25 implicit events relative to the 0.85 and 0.92 screens (detection subsection).
C. The implicit Stale-Only events: which carry a conflict event at the update turn and which carry none (the one
   bare restatement above the threshold that the classifier did not store).
D. EpSem-SS scenarios with recall below 1.000 (the five rejection scenarios).
Run from the repository root: python analysis/event_breakdowns.py
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import RESULTS, J, scenarios, targets, ledger, context_category, md_table


def by_length(fn):
    ct = collections.Counter()
    for x in ledger(fn):
        for c in x["context_ua"]:
            ct[(int(x["total_turns"]), context_category(c))] += 1
    return ct


def main():
    S = scenarios()
    out = ["### A. Naive and RAG context categories by conversation length\n"]
    for name, fn in [("Naive", "behavior_NaiveMemory.json"), ("RAG", "behavior_RagMemory.json")]:
        ct = by_length(fn)
        rows = [[L] + [ct[(L, c)] for c in ("Correct", "Stale-Retained", "Stale-Only", "Lost")] for L in (200, 500, 1000)]
        out.append(name)
        out.append(md_table(["Turns", "Correct", "Stale-Retained", "Stale-Only", "Lost"], rows))
        out.append("")
    sims = J(RESULTS / "dp2_sims.json")

    def band(s):
        return "below 0.85" if s <= 0.85 else ("0.85 to 0.92" if s <= 0.92 else "above 0.92")

    ct = collections.Counter()
    for r in sims:
        ct[("explicit" if r["cond"] == "explicit" else "implicit", band(r["sim"]), r["outcome"])] += 1
    out.append("### B. Similarity bands (outcome codes C, SR, SO)\n")
    out.append(md_table(["Set", "Band", "Outcome", "Events"], [[*k, v] for k, v in sorted(ct.items())]))
    out.append("")
    out.append("### C. Implicit Stale-Only events and the rule event at the update turn\n")
    upd = {(r["scenario"], r["gt_id"]): r for r in sims}
    for x in ledger("behavior_EpSemSupersession_imp.json"):
        tg = targets(S[x["scenario_id"]])
        for c in x["context_ua"]:
            if context_category(c) != "Stale-Only":
                continue
            r = upd.get((x["scenario_id"], c["gt_id"]), {})
            u = r.get("upd", "")[:40]
            ev = [(e["turn"], e["type"]) for e in x["supersession_events"] if u and u in str(e.get("data"))]
            new_in = str(tg[c["gt_id"]]["new_value"]) in x["context_text"]
            out.append("- %s %s form=%s sim=%s events_at_update=%s new_value_in_context=%s" % (x["scenario_id"], c["gt_id"], r.get("cond"), r.get("sim"), ev, new_in))
    out.append("")
    out.append("### D. EpSem-SS Update Conflict scenarios with recall below 1.000\n")
    ss = ledger("behavior_EpSemSupersession.json")
    out.append(", ".join("%s (%.3f)" % (x["scenario_id"], float(x["recall"])) for x in ss if float(x["recall"]) < 1.0))
    out.append("")
    out.append("### E. The five rejected explicit revisions and the recorded conflict judgments\n")
    import json as _json
    for x in ss:
        tg = targets(S[x["scenario_id"]])
        for c in x["context_ua"]:
            if context_category(c) != "Stale-Only":
                continue
            r = upd.get((x["scenario_id"], c["gt_id"]), {})
            u = r.get("upd", "")[:40]
            for e in x["supersession_events"]:
                if e.get("type") == "conflict_detected" and u and u in str(e.get("data")):
                    d = e.get("data")
                    try:
                        d = _json.loads(d) if isinstance(d, str) else d
                    except Exception:
                        d = {"reason": str(d)}
                    out.append("- %s %s sim=%s turn %s: %s" % (x["scenario_id"], c["gt_id"], r.get("sim"), e.get("turn"), str(d.get("reason", ""))[:300]))
    txt = "\n".join(out)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
