"""Offline analyses on the released result files (no model calls).
A. Domain breakdown of the Update Conflict results (store level, behavior level, recall)
B. Threshold selection with a validation/test split (Batch A half vs Batch B half)
C. Store-level scoring sensitivity (exact-string vs value-token rules)
D. RAG retrieval settings (k=5, k=20, reformulated query)
E. Wilson confidence intervals and Wilcoxon zero differences
Run from the repository root: python3 analysis/offline_analyses.py  (writes analysis/offline_analyses_report.md)
"""
import json, glob, re, math, collections, os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
R1 = ROOT / "results"; CANON = ROOT / "results" / "canonical"; DS = ROOT / "scenarios"
sys.path.insert(0, str(ROOT / "analysis"))
from behavior_strict_by_domain import strict_score  # noqa

def J(p): return json.load(open(p, encoding="utf-8"))

# ---------- scenarios ----------
scen = {}; half = {}
for f in sorted(glob.glob(str(DS / "holdout_v*" / "*.json"))):
    s = J(f); scen[s["scenario_id"]] = s
    half[s["scenario_id"]] = "A" if "holdout_v4" in f.replace("\\", "/") else "B"
dom = {k: v["domain"] for k, v in scen.items()}
ua_t = {k: v["evaluation_protocol"].get("ua_targets", []) for k, v in scen.items()}
DOMS = ["ENGINEERING", "MEDICAL", "LEGAL", "FINANCE", "GENERAL"]

def cat(has_new, has_old):
    if has_new and not has_old: return "UA"
    if has_new and has_old: return "StaleRet"
    if has_old: return "StaleOnly"
    return "Lost"

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))

ARMS = {"Naive": "behavior_NaiveMemory.json", "RAG": "behavior_RagMemory.json", "EpSem": "behavior_EpSemMemory.json",
        "EpSem-F": "behavior_EpSemFiltered.json", "EpSem-SS": "behavior_EpSemSupersession.json",
        "LWW": "behavior_LWWMemory.json", "TS-Read": "behavior_TSRead.json", "EpSem-SS (Phi-3)": "behavior_EpSemSupersession_phi3.json",
        "Mem0 (v3)": "behavior_Mem0_v3.json"}

def load_arm(fn):
    return [x for x in J(R1 / fn) if "error" not in x]

out = []
P = out.append

# ---------- A. per-domain ----------
P("## A. Domain breakdown on the Update Conflict scenarios (store level, exact-string rule)\n")
P("| Arm | " + " | ".join(DOMS) + " | All |"); P("|---|" + "---|" * (len(DOMS) + 1))
for arm, fn in ARMS.items():
    rows = load_arm(fn); c = collections.defaultdict(collections.Counter)
    for x in rows:
        d = dom[x["scenario_id"]]
        for u in x["context_ua"]: c[d][cat(u["has_new"], u["has_old"])] += 1; c[d]["n"] += 1
    tot = collections.Counter()
    for d in DOMS: tot.update(c[d])
    P(f"| {arm} | " + " | ".join(f"{c[d]['UA']}/{c[d]['n']}" for d in DOMS) + f" | {tot['UA']}/{tot['n']} ({100*tot['UA']/max(tot['n'],1):.1f}%) |")
P("\nEpSem-SS failure split by domain (UA / Stale-Retained / Stale-Only / Lost):\n")
rows = load_arm(ARMS["EpSem-SS"]); c = collections.defaultdict(collections.Counter)
for x in rows:
    d = dom[x["scenario_id"]]
    for u in x["context_ua"]: c[d][cat(u["has_new"], u["has_old"])] += 1
P("| Domain | UA | Stale-Retained | Stale-Only | Lost | events | Wilson 95% |"); P("|---|---|---|---|---|---|---|")
for d in DOMS:
    n = sum(c[d].values()); lo, hi = wilson(c[d]["UA"], n)
    P(f"| {d} | {c[d]['UA']} | {c[d]['StaleRet']} | {c[d]['StaleOnly']} | {c[d]['Lost']} | {n} | {lo:.0f}–{hi:.0f}% |")

P("\nBehavior-level UA by domain (strict answer-line rule of the paper, verbatim-listing prompt):\n")
P("| Arm | " + " | ".join(DOMS) + " | All |"); P("|---|" + "---|" * (len(DOMS) + 1))
for arm, fn in ARMS.items():
    rows = load_arm(fn); c = collections.defaultdict(collections.Counter)
    for x in rows:
        d = dom[x["scenario_id"]]; tg = {t["gt_id"]: t for t in ua_t[x["scenario_id"]]}
        for b in x["behavior"]:
            c[d]["n"] += 1
            if strict_score(x["answer_text"], tg[b["gt_id"]]) == "NewOnly": c[d]["UA"] += 1
    tot = collections.Counter()
    for d in DOMS: tot.update(c[d])
    P(f"| {arm} | " + " | ".join(f"{c[d]['UA']}/{c[d]['n']}" for d in DOMS) + f" | {tot['UA']}/{tot['n']} ({100*tot['UA']/max(tot['n'],1):.1f}%) |")

P("\nRecall by domain (UC-24, ground-truth constraints found / total):\n")
P("| Arm | " + " | ".join(DOMS) + " |"); P("|---|" + "---|" * len(DOMS))
for arm, fn in ARMS.items():
    rows = load_arm(fn); f = collections.Counter(); g = collections.Counter()
    for x in rows: d = dom[x["scenario_id"]]; f[d] += x["found"]; g[d] += x["total_gt"]
    P(f"| {arm} | " + " | ".join(f"{f[d]}/{g[d]} ({f[d]/max(g[d],1):.3f})" for d in DOMS) + " |")

def canon_rows(model):
    v5 = J(CANON / "v5_holdout_merged.json")[model]
    if model == "EpSemSupersession":
        v4 = J(CANON / "v4_holdout_20260602_215257.json")[model]
    else:
        v4 = J(CANON / "v4_holdout_20260601_023636.json")[model]
    return v4 + v5
P("\nScenario-mean recall by domain, all 72 scenarios (canonical runs):\n")
P("| Config | " + " | ".join(DOMS) + " | All |"); P("|---|" + "---|" * (len(DOMS) + 1))
for model, name in [("NaiveMemory", "Naive"), ("RagMemory", "RAG"), ("EpSemMemory", "EpSem"), ("EpSemFiltered", "EpSem-F"), ("EpSemSupersession", "EpSem-SS")]:
    rows = canon_rows(model); acc = collections.defaultdict(list)
    for x in rows: acc[x["domain"]].append(x["recall"])
    allr = [v for d in DOMS for v in acc[d]]
    P(f"| {name} | " + " | ".join(f"{sum(acc[d])/len(acc[d]):.3f} (n={len(acc[d])})" for d in DOMS) + f" | {sum(allr)/len(allr):.4f} |")

# ---------- B. validation split ----------
P("\n## B. Threshold selection with a validation/test split (half A = Batch A, U001–U012; half B = Batch B, U013–U024)\n")
sweep = {0.85: J(R1 / "sweep_th85.json"), 0.90: J(R1 / "sweep_th90.json"), 0.95: J(R1 / "sweep_th95.json")}
sweep[0.92] = [{"scenario_id": x["scenario_id"], "recall": x["recall"], "ua": x["context_ua"]} for x in load_arm(ARMS["EpSem-SS"])]
fn085 = J(R1 / "ss085_fn.json")
ss_canon = canon_rows("EpSemSupersession")
P("| Threshold | UA half A | UA half B | UA all | UC recall A | UC recall B | F/N recall (all 48) |"); P("|---|---|---|---|---|---|---|")
for th in sorted(sweep):
    c = collections.Counter(); rec = collections.defaultdict(list)
    for x in sweep[th]:
        h = half[x["scenario_id"]]; rec[h].append(x["recall"])
        for u in x["ua"]: c[h + "_n"] += 1; c[h + "_ua"] += (1 if u["has_new"] and not u["has_old"] else 0)
    if th == 0.85: fnr = sum(x["recall"] for x in fn085) / len(fn085)
    elif th == 0.92: fnr = sum(x["recall"] for x in ss_canon if x["scenario_type"] != "UPDATE_CONFLICT") / 48
    else: fnr = float("nan")
    P(f"| {th:.2f} | {c['A_ua']}/{c['A_n']} ({100*c['A_ua']/c['A_n']:.1f}%) | {c['B_ua']}/{c['B_n']} ({100*c['B_ua']/c['B_n']:.1f}%) | {c['A_ua']+c['B_ua']}/{c['A_n']+c['B_n']} | {sum(rec['A'])/len(rec['A']):.3f} | {sum(rec['B'])/len(rec['B']):.3f} | {fnr:.3f} |")
P("\nF/N recall is available at 0.85 (ss085_fn.json) and 0.92 (canonical). F/N recall by half at 0.85: " +
  ", ".join(f"{h}={sum(x['recall'] for x in fn085 if half[x['scenario_id']]==h)/24:.3f}" for h in ["A", "B"]))
# selection rule, computed: maximize validation-half UA among thresholds whose F/N recall was measured and equals 1.000
fn_known = {0.85: sum(x["recall"] for x in fn085) / len(fn085), 0.92: sum(x["recall"] for x in ss_canon if x["scenario_type"] != "UPDATE_CONFLICT") / 48}
eligible = [th for th, r in fn_known.items() if abs(r - 1.0) < 1e-9]
ua_half = {}
for th in sorted(sweep):
    c = collections.Counter()
    for x in sweep[th]:
        h = half[x["scenario_id"]]
        for u in x["ua"]: c[h + "_n"] += 1; c[h + "_ua"] += (1 if u["has_new"] and not u["has_old"] else 0)
    ua_half[th] = {h: (c[h + "_ua"], c[h + "_n"]) for h in ["A", "B"]}
P(f"Selection rule: maximize validation-half store-level UA subject to F/N recall = 1.000. F/N recall is measured at {sorted(fn_known)} only, so the eligible candidates are {sorted(eligible)}.")
for val, test in [("A", "B"), ("B", "A")]:
    pick = max(eligible, key=lambda th: ua_half[th][val][0] / ua_half[th][val][1])
    k, n = ua_half[pick][test]
    P(f"  validate on half {val} -> pick {pick:.2f}; held-out half {test}: {k}/{n} = {100*k/n:.1f}%")

# ---------- C. value-token store-level ----------
P("\n## C. Store-level scoring sensitivity: exact-string vs value-token rules (UC-24)\n")
TOKEN_RE = re.compile(r"[A-Za-z0-9°%/\.]+")
def vt_flags(context, old_v, new_v, line_rule):
    ot, nt = set(TOKEN_RE.findall(old_v)), set(TOKEN_RE.findall(new_v))
    old_only, new_only = sorted(ot - nt), sorted(nt - ot)
    ow, nw = old_v.split(), new_v.split(); k = 0
    while k < min(len(ow), len(nw)) and ow[k] == nw[k]: k += 1
    phrase = " ".join(ow[:k]).strip()
    lines = [l for l in context.split("\n") if (not line_rule) or (phrase and phrase in l)]
    text = "\n".join(lines) if line_rule else context
    hn = any(re.search(re.escape(t), text) for t in new_only)
    ho = any(re.search(re.escape(t), text) for t in old_only)
    return hn, ho
P("| Arm | exact: UA/SR/SO/Lost | value-token (anywhere): UA/SR/SO/Lost | value-token (same line as parameter phrase): UA/SR/SO/Lost |"); P("|---|---|---|---|")
for arm, fn in ARMS.items():
    rows = load_arm(fn); ce = collections.Counter(); ca = collections.Counter(); cl = collections.Counter()
    for x in rows:
        tg = {t["gt_id"]: t for t in ua_t[x["scenario_id"]]}
        for u in x["context_ua"]:
            ce[cat(u["has_new"], u["has_old"])] += 1
            t = tg[u["gt_id"]]
            ca[cat(*vt_flags(x["context_text"], t["old_value"], t["new_value"], False))] += 1
            cl[cat(*vt_flags(x["context_text"], t["old_value"], t["new_value"], True))] += 1
    f = lambda c: f"{c['UA']}/{c['StaleRet']}/{c['StaleOnly']}/{c['Lost']}"
    P(f"| {arm} | {f(ce)} | {f(ca)} | {f(cl)} |")

# ---------- D. RAG configurations ----------
P("\n## D. RAG retrieval settings (UC-24 store and behavior level; recall on all 72 where available)\n")
P("| RAG setting | file | recall (UC-24) | recall (72) | store UA | behavior UA (strict) |"); P("|---|---|---|---|---|---|")
for name, fn in [("k=5 (canonical)", "behavior_RagMemory.json"), ("k=20", "behavior_RagMemory_ragk20.json"), ("query reformulated with domain keywords, k=5", "behavior_RagMemory_ragreform.json")]:
    rows = [x for x in J(R1 / fn) if "error" not in x]
    uc = [x for x in rows if x["scenario_id"] in dom and scen[x["scenario_id"]]["scenario_type"] == "UPDATE_CONFLICT"]
    r_uc = sum(x["found"] for x in uc) / sum(x["total_gt"] for x in uc)
    r_all = (sum(x["recall"] for x in rows) / len(rows)) if len(rows) == 72 else float("nan")
    ua = sum(1 for x in uc for u in x["context_ua"] if u["has_new"] and not u["has_old"]); n = sum(len(x["context_ua"]) for x in uc)
    bua = 0
    for x in uc:
        tg = {t["gt_id"]: t for t in ua_t[x["scenario_id"]]}
        bua += sum(1 for b in x["behavior"] if strict_score(x.get("answer_text", ""), tg[b["gt_id"]]) == "NewOnly")
    P(f"| {name} | {fn} | {r_uc:.3f} | {r_all:.3f} | {ua}/{n} | {bua}/{n} |")

# ---------- E. statistics ----------
P("\n## E. Statistics\n")
ss = {x["scenario_id"]: x["recall"] for x in canon_rows("EpSemSupersession")}
ef = {x["scenario_id"]: x["recall"] for x in canon_rows("EpSemFiltered")}
d = [ss[k] - ef[k] for k in ss if k in ef]
zeros = sum(1 for v in d if abs(v) < 1e-12); pos = sum(1 for v in d if v > 1e-12); neg = sum(1 for v in d if v < -1e-12)
P(f"Wilcoxon (EpSem-SS vs EpSem-F per-scenario recall, n={len(d)}): zero differences = {zeros}, positive = {pos}, negative = {neg}. "
  f"Rank-biserial 1.000 follows from negative = 0 among the {pos} discordant pairs (zeros excluded under the standard 'wilcox' zero method).")
try:
    from scipy.stats import wilcoxon
    for zm in ["wilcox", "pratt", "zsplit"]:
        try: P(f"  scipy wilcoxon zero_method={zm}: p = {wilcoxon(d, zero_method=zm).pvalue:.2e}")
        except Exception as e: P(f"  scipy wilcoxon zero_method={zm}: {e}")
except ImportError: P("  (scipy not installed; p-values not recomputed)")
for label, k, n in [("EpSem-SS store UA (Qwen)", 14, 45), ("EpSem-SS store UA (Phi-3)", 12, 45), ("EpSem-SS behavior UA verbatim", 34, 45), ("EpSem-SS behavior UA own-words", 22, 45), ("EpSem-SS behavior UA no-form", 18, 45), ("Naive store UA", 6, 45)]:
    lo, hi = wilson(k, n); P(f"Wilson 95% CI {label}: {k}/{n} = {100*k/n:.1f}% [{lo:.1f}, {hi:.1f}]")

Path(ROOT / "analysis" / "offline_analyses_report.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out))
