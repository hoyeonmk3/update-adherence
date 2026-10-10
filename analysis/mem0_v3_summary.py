"""Summary of the Mem0 v3 measurement (context window 16,384 tokens): truncation check, token statistics,
exact-string and value-token store-level outcomes, strict behavior-level outcomes, and the domain breakdown.
Store-level value-token rule: a distinguishing token anywhere in the assembled context (the rule used for
Mem0 in the paper). Behavior level: the strict answer-line rule of behavior_strict_by_domain.py.
Run from the repository root: python3 analysis/mem0_v3_summary.py
"""
import json, glob, re, collections, sys, statistics
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent; R3 = ROOT / "results"; DS = ROOT / "scenarios"
sys.path.insert(0, str(ROOT / "analysis"))
from behavior_strict_by_domain import strict_score, TOKEN_RE  # noqa
def J(p): return json.load(open(p, encoding="utf-8"))
S = {}
for f in glob.glob(str(DS / "holdout_v*" / "*.json")):
    d = J(f); S[d["scenario_id"]] = d
DOMS = ["ENGINEERING", "MEDICAL", "LEGAL", "FINANCE", "GENERAL"]

def vt_anywhere(context, old_v, new_v):
    ot, nt = set(TOKEN_RE.findall(old_v)), set(TOKEN_RE.findall(new_v))
    hn = any(re.search(re.escape(t), context) for t in sorted(nt - ot))
    ho = any(re.search(re.escape(t), context) for t in sorted(ot - nt))
    return hn, ho
def cat(hn, ho): return "UA" if hn and not ho else "StaleRet" if hn and ho else "StaleOnly" if ho else "Lost"

meta = J(R3 / "behavior_Mem0_v3.meta.json")
rows = J(R3 / "behavior_Mem0_v3.json")
err = [x for x in rows if "error" in x]; ok = [x for x in rows if "error" not in x]
print(f"scenarios: {len(rows)} ok={len(ok)} error={len(err)} {[e['scenario_id'] for e in err]}")
print(f"started {meta['started']} finished {meta.get('finished')} calls_total={meta.get('calls_total')} log_delta={meta.get('log_delta')}")
calls = [json.loads(l) for l in open(R3 / "calls_mem0_v3.jsonl", encoding="utf-8")]
pe = [c["prompt_eval_count"] for c in calls if c["prompt_eval_count"]]
print(f"calls={len(calls)} prompt_eval_count min/median/max = {min(pe)}/{statistics.median(pe):.0f}/{max(pe)}  (>4096: {sum(p>4096 for p in pe)})  eval_count median {statistics.median([c['eval_count'] for c in calls if c['eval_count']]):.0f}")

found = sum(x["found"] for x in ok); gt = sum(x["total_gt"] for x in ok)
print(f"exact-string recall (UC-24 GT): {found}/{gt} = {found/gt:.3f} | scenario-mean recall {statistics.mean(x['recall'] for x in ok):.3f} | mean CCR {statistics.mean(x['ccr'] for x in ok):.3f}")

ce = collections.Counter(); ca = collections.Counter(); bd = collections.defaultdict(collections.Counter); cdom = collections.defaultdict(collections.Counter)
cb = collections.Counter()
for x in ok:
    tg = {t["gt_id"]: t for t in S[x["scenario_id"]]["evaluation_protocol"]["ua_targets"]}; d = S[x["scenario_id"]]["domain"]
    for u in x["context_ua"]:
        t = tg[u["gt_id"]]
        ce[cat(u["has_new"], u["has_old"])] += 1
        k = cat(*vt_anywhere(x["context_text"], t["old_value"], t["new_value"])); ca[k] += 1; cdom[d][k] += 1; cdom[d]["n"] += 1
    for b in x["behavior"]:
        k = strict_score(x["answer_text"], tg[b["gt_id"]]); cb[k] += 1; bd[d][k] += 1; bd[d]["n"] += 1
n = sum(ce.values())
f = lambda c: f"UA {c['UA']} / Stale-Retained {c['StaleRet']} / Stale-Only {c['StaleOnly']} / Lost {c['Lost']}  (has_new={c['UA']+c['StaleRet']})"
print(f"store-level exact-string ({n} events): {f(ce)}")
print(f"store-level value-token anywhere ({n} events): {f(ca)}")
print(f"behavior-level strict ({n} events): NewOnly {cb['NewOnly']} ({100*cb['NewOnly']/n:.1f}%) / Both {cb['Both']} / OldOnly {cb['OldOnly']} / Neither {cb['Neither']}")
print("\n| Domain | store UA (value-token) | SR | SO | Lost | behavior UA (strict) |"); print("|---|---|---|---|---|---|")
for d in DOMS:
    print(f"| {d} | {cdom[d]['UA']}/{cdom[d]['n']} | {cdom[d]['StaleRet']} | {cdom[d]['StaleOnly']} | {cdom[d]['Lost']} | {bd[d]['NewOnly']}/{bd[d]['n']} |")
print("\nSuperseded (truncated-prompt) run for reference only: exact recall 0.066, value-token 3/8/4/30, behavior 4/45, CCR 0.920 (results/superseded/).")
