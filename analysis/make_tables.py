# -*- coding: utf-8 -*-
"""Reproduce Tables 5 to 9 of the paper and the figure data from the released result files, and write analysis/tables.md.
Table 5: rule_contribution.py        Table 6: detector_settings.py        Table 7: domain breakdown (here)
Table 8: backbone_crosstab.py        Table 9: answer prompts (here, from the prompt-ablation ledgers)
Also runs context_answer_crosstab.py, event_breakdowns.py, retention_summary.py, figure_data.py.
Run from the repository root: python analysis/make_tables.py
"""
import collections
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import ROOT, RESULTS, J, scenarios, targets, ledger, context_category, strict_score, md_table
import rule_contribution, detector_settings, backbone_crosstab, context_answer_crosstab, event_breakdowns, retention_summary, figure_data

DOMS = [("ENGINEERING", "Engineering"), ("MEDICAL", "Medical"), ("LEGAL", "Legal"), ("FINANCE", "Financial"), ("GENERAL", "General")]


def table7(S):
    sims = {(r["scenario"], r["gt_id"]): r["sim"] for r in J(RESULTS / "dp2_sims.json") if r["cond"] == "explicit"}
    ss = ledger("behavior_EpSemSupersession.json")
    per = collections.defaultdict(lambda: {"sims": [], "ctx": 0, "ans": 0, "n": 0, "found": 0, "gt": 0})
    allrow = {"sims": [], "ctx": 0, "ans": 0, "n": 0, "found": 0, "gt": 0}
    for x in ss:
        d = S[x["scenario_id"]]["domain"]
        tg = targets(S[x["scenario_id"]])
        for c in x["context_ua"]:
            k = (x["scenario_id"], c["gt_id"])
            for acc in (per[d], allrow):
                acc["sims"].append(sims[k])
                acc["n"] += 1
                acc["ctx"] += context_category(c) == "Correct"
                acc["ans"] += strict_score(x["answer_text"], tg[c["gt_id"]]) == "NewOnly"
        for acc in (per[d], allrow):
            acc["found"] += int(x["found"])
            acc["gt"] += int(x["total_gt"])
    rows = []
    for key, name in DOMS + [(None, "All")]:
        a = allrow if key is None else per[key]
        s = sorted(a["sims"])
        rows.append([name, a["n"], "%.4f (%.4f–%.4f)" % (st.median(s), s[0], s[-1]), "%d/%d" % (a["ctx"], a["n"]), "%d/%d" % (a["ans"], a["n"]), "%d/%d (%.3f)" % (a["found"], a["gt"], a["found"] / a["gt"])])
    return "### Table 7. Update outcomes and revision similarity by domain (EpSem-SS, Qwen2.5-14B)\n\n" + md_table(
        ["Domain", "Events", "Similarity median (range)", "Context-level UA", "Strict answer-level UA", "Recall (pooled)"], rows)


def table9(S):
    arms = [("Naive", "behavior_NaiveMemory_prompt_ablation.json"), ("RAG", "behavior_RagMemory_prompt_ablation.json"), ("EpSem", "behavior_EpSemMemory_prompt_ablation.json"),
            ("EpSem-F", "behavior_EpSemFiltered_prompt_ablation.json"), ("EpSem-SS", "behavior_EpSemSupersession_prompt_ablation.json"), ("LWW", "behavior_LWWMemory_prompt_ablation.json")]
    rows = []
    for name, fn in arms:
        cnt = collections.Counter()
        n = 0
        for x in ledger(fn):
            tg = targets(S[x["scenario_id"]])
            prompts = x["answer_prompts"]
            for b in x["behavior"]:
                n += 1
                for p in prompts:
                    ans = x["answers_by_prompt"][p] if isinstance(x["answers_by_prompt"], dict) else x["answers_by_prompt"][prompts.index(p)]
                    if strict_score(ans, tg[b["gt_id"]]) == "NewOnly":
                        cnt[p] += 1
        rows.append([name] + ["%d (%.1f%%)" % (cnt[p], 100.0 * cnt[p] / n) for p in ("p0", "p1", "p2")])
    return "### Table 9. Strict answer-level UA under three answer prompts\n\n" + md_table(["Configuration", "Verbatim listing", "Own words", "No form instruction"], rows)


def main():
    S = scenarios()
    parts = [rule_contribution.main(), detector_settings.main(), table7(S), backbone_crosstab.main(), table9(S),
             context_answer_crosstab.main(), event_breakdowns.main(), retention_summary.main(), figure_data.main()]
    txt = "# Tables and figure data reproduced from results/\n\n" + "\n\n".join(parts) + "\n"
    (ROOT / "analysis" / "tables.md").write_text(txt, encoding="utf-8", newline="\n")
    print("\nwrote analysis/tables.md")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
