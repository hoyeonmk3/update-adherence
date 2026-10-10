# -*- coding: utf-8 -*-
"""Context category x strict answer category for every arm (Results, "From Memory Context to Generated Answer").
Expected totals (NewOnly): Naive 14, RAG 0, EpSem 21, EpSem-F 24, EpSem-SS 34, LWW 35, TS-Read 39, EpSem-SS (Phi-3) 14, Mem0 6.
Run from the repository root: python analysis/context_answer_crosstab.py
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import ARMS, CATEGORIES, ANSWERS, scenarios, targets, ledger, context_category, strict_score, md_table

EXPECTED = {"Naive": 14, "RAG": 0, "EpSem": 21, "EpSem-F": 24, "EpSem-SS": 34, "LWW": 35, "TS-Read": 39, "EpSem-SS (Phi-3)": 14, "Mem0": 6}


def crosstab(name, fn, S):
    ct = collections.Counter()
    for x in ledger(fn):
        tg = targets(S[x["scenario_id"]])
        cx = {c["gt_id"]: context_category(c) for c in x["context_ua"]}
        for b in x["behavior"]:
            ct[(cx[b["gt_id"]], strict_score(x["answer_text"], tg[b["gt_id"]]))] += 1
    return ct


def main():
    S = scenarios()
    out = []
    for name, fn, _ in ARMS:
        ct = crosstab(name, fn, S)
        rows = []
        for c in CATEGORIES:
            n = sum(v for (cc, _), v in ct.items() if cc == c)
            if n:
                rows.append([c, n] + [ct[(c, a)] for a in ANSWERS])
        total = sum(v for (_, a), v in ct.items() if a == "NewOnly")
        flag = "" if total == EXPECTED[name] else "  (expected %d)" % EXPECTED[name]
        out.append("### %s, NewOnly %d of 45%s\n" % (name, total, flag))
        out.append(md_table(["Context", "Events"] + ANSWERS, rows))
        out.append("")
    txt = "\n".join(out)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
