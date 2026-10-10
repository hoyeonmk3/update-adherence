# -*- coding: utf-8 -*-
"""Data behind Figs. 3, 4, and 5 of the paper.
fig3_context_outcomes.csv: context categories of the 45 update events for the five primary configurations.
fig4_two_scores.csv: context-level UA and strict answer-level UA (%) for the eight configurations of Fig. 4;
    the Mem0 context score uses distinguishing value tokens anywhere in the retrieved context (paraphrased records).
fig5_similarity.csv: the 70 revision pairs with their nomic-embed-text similarity, wording form, and context outcome.
Run from the repository root: python analysis/figure_data.py
"""
import collections
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import ROOT, RESULTS, J, CATEGORIES, TOKEN_RE, scenarios, targets, ledger, context_category, strict_score, norm

FIG = ROOT / "figures" / "data"
PRIMARY = [("Naive", "behavior_NaiveMemory.json"), ("RAG", "behavior_RagMemory.json"), ("EpSem", "behavior_EpSemMemory.json"),
           ("EpSem-F", "behavior_EpSemFiltered.json"), ("EpSem-SS", "behavior_EpSemSupersession.json")]
EXTRA = [("LWW", "behavior_LWWMemory.json"), ("TS-Read", "behavior_TSRead.json"), ("Mem0", "behavior_Mem0_v3.json")]


def value_token_flags(context_text, target):
    """Mem0 context rule: distinguishing value tokens of the revised and original sentence anywhere in the context."""
    ot, nt = set(TOKEN_RE.findall(target["old_value"])), set(TOKEN_RE.findall(target["new_value"]))
    c = norm(context_text)
    has_new = any(re.search(re.escape(norm(t)), c) for t in sorted(nt - ot))
    has_old = any(re.search(re.escape(norm(t)), c) for t in sorted(ot - nt))
    return {"has_new": has_new, "has_old": has_old}


def main():
    S = scenarios()
    FIG.mkdir(parents=True, exist_ok=True)
    cats, ctx_ua, ans_ua = {}, {}, {}
    for name, fn in PRIMARY + EXTRA:
        ct = collections.Counter()
        new_only = 0
        n = 0
        for x in ledger(fn):
            tg = targets(S[x["scenario_id"]])
            for c in x["context_ua"]:
                flags = value_token_flags(x["context_text"], tg[c["gt_id"]]) if name == "Mem0" else c
                ct[context_category(flags)] += 1
            for b in x["behavior"]:
                n += 1
                if strict_score(x["answer_text"], tg[b["gt_id"]]) == "NewOnly":
                    new_only += 1
        cats[name] = ct
        ctx_ua[name] = 100.0 * ct["Correct"] / 45
        ans_ua[name] = 100.0 * new_only / 45
    with open(FIG / "fig3_context_outcomes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["configuration", "correct", "stale_retained", "stale_only", "lost"])
        for name, _ in PRIMARY:
            w.writerow([name] + [cats[name][c] for c in CATEGORIES])
    with open(FIG / "fig4_two_scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["configuration", "context_level_ua_pct", "strict_answer_level_ua_pct"])
        for name, _ in PRIMARY + EXTRA:
            w.writerow([name, "%.1f" % ctx_ua[name], "%.1f" % ans_ua[name]])
    with open(FIG / "fig5_similarity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["scenario", "gt_id", "condition", "form", "similarity", "context_outcome"])
        form = {"explicit": "explicit", "T1": "transition-marked", "T2": "bare", "T3": "conversational"}
        for r in J(RESULTS / "dp2_sims.json"):
            w.writerow([r["scenario"], r["gt_id"], r["cond"], form.get(r["cond"], r["cond"]), "%.4f" % r["sim"], r["outcome"]])
    lines = ["### Fig. 3 context outcomes and Fig. 4 two scores\n", "| Configuration | C/SR/SO/L | Context-level UA % | Strict answer-level UA % |", "|---|---|---:|---:|"]
    for name, _ in PRIMARY + EXTRA:
        c = cats[name]
        lines.append("| %s | %d/%d/%d/%d | %.1f | %.1f |" % (name, c["Correct"], c["Stale-Retained"], c["Stale-Only"], c["Lost"], ctx_ua[name], ans_ua[name]))
    txt = "\n".join(lines)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
