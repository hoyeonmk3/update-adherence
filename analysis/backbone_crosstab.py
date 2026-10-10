# -*- coding: utf-8 -*-
"""Table 8 of the paper and the cross-model paragraph: EpSem-SS under Qwen2.5-14B and Phi-3 Medium.
Context categories and NewOnly answers under each backbone, binary and full-category agreement, the category
shift of each event, and the Phi-3 answer decomposition. EpSem and EpSem-F under Phi-3 from the canonical file.
Run from the repository root: python analysis/backbone_crosstab.py
"""
import collections
import glob
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ua_common import RESULTS, J, CATEGORIES, ANSWERS, scenarios, targets, ledger, context_category, strict_score, md_table


def per_event(fn, S):
    ctx, ans = {}, {}
    for x in ledger(fn):
        tg = targets(S[x["scenario_id"]])
        for c in x["context_ua"]:
            ctx[(x["scenario_id"], c["gt_id"])] = context_category(c)
        for b in x["behavior"]:
            ans[(x["scenario_id"], b["gt_id"])] = strict_score(x["answer_text"], tg[b["gt_id"]])
    return ctx, ans


def main():
    S = scenarios()
    q_ctx, q_ans = per_event("behavior_EpSemSupersession.json", S)
    p_ctx, p_ans = per_event("behavior_EpSemSupersession_phi3.json", S)
    keys = sorted(q_ctx)
    assert keys == sorted(p_ctx) and len(keys) == 45
    rows = []
    for name, ctx, ans in [("Qwen2.5-14B", q_ctx, q_ans), ("Phi-3 Medium", p_ctx, p_ans)]:
        cc = collections.Counter(ctx.values())
        rows.append([name] + [cc[c] for c in CATEGORIES] + ["%d/45" % sum(1 for v in ans.values() if v == "NewOnly")])
    out = ["### Table 8. EpSem-SS under the two backbones\n", md_table(["Backbone"] + CATEGORIES + ["NewOnly answers"], rows), ""]
    binary = sum(1 for k in keys if (q_ctx[k] == "Correct") == (p_ctx[k] == "Correct"))
    full = sum(1 for k in keys if q_ctx[k] == p_ctx[k])
    shift = collections.Counter((q_ctx[k], p_ctx[k]) for k in keys if q_ctx[k] != p_ctx[k])
    out.append("Binary Correct/not-Correct agreement %d/45, full-category agreement %d/45" % (binary, full))
    b = sum(1 for k in keys if q_ctx[k] == "Correct" and p_ctx[k] != "Correct")
    c = sum(1 for k in keys if q_ctx[k] != "Correct" and p_ctx[k] == "Correct")
    from math import comb
    n = b + c
    p_exact = min(1.0, 2.0 * sum(comb(n, i) for i in range(0, min(b, c) + 1)) / (2 ** n)) if n else 1.0
    out.append("Discordant events: Correct under Qwen only %d, under Phi-3 only %d; McNemar exact two-sided p = %.2f (Article S1)" % (b, c, p_exact))
    out.append("Category shifts Qwen -> Phi-3: " + ", ".join("%s -> %s: %d" % (a, b, n) for (a, b), n in sorted(shift.items())))
    dec = collections.Counter((p_ctx[k], p_ans[k]) for k in keys)
    out.append("Phi-3 answers by context category: " + ", ".join("%s -> %s: %d" % (c, a, dec[(c, a)]) for c in CATEGORIES for a in ANSWERS if dec[(c, a)]))
    # EpSem and EpSem-F under Phi-3 from the canonical file, if the UA flags are recorded there
    for f in glob.glob(str(RESULTS / "canonical" / "holdout_phi3_medium_*.json")):
        d = J(f)
        for cfg in ("EpSemMemory", "EpSemFiltered", "EpSemSupersession"):
            cc = collections.Counter()
            for x in d.get(cfg, []):
                ua = x.get("ua")
                details = ua.get("details", []) if isinstance(ua, dict) else (ua or [])
                for c in details:
                    cc[context_category(c)] += 1
            out.append("Phi-3 canonical %s: Correct %d of %d (C/SR/SO/L %d/%d/%d/%d)" % (cfg, cc["Correct"], sum(cc.values()), cc["Correct"], cc["Stale-Retained"], cc["Stale-Only"], cc["Lost"]))
    txt = "\n".join(out)
    print(txt)
    return txt


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
