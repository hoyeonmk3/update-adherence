"""Behavior-level UA by domain under the strict answer-line rule of the paper (same rule as prompt_ablation_aggregate.py).
Validation: the per-arm totals must reproduce Fig. 9 (Naive 14, RAG 0, EpSem 21, EpSem-F 24, EpSem-SS 34, LWW 35, TS-Read 39, Phi-3 14, Mem0 v3 6).
Run from the repository root: python3 analysis/behavior_strict_by_domain.py
"""
import json, glob, re, collections, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent; R1 = ROOT / "results"; DS = ROOT / "scenarios"
def J(p): return json.load(open(p, encoding="utf-8"))
S = {}
for f in glob.glob(str(DS / "holdout_v*" / "*.json")):
    d = J(f); S[d["scenario_id"]] = d
TOKEN_RE = re.compile(r"[A-Za-z0-9°%/\.]+")
def norm(s): return re.sub(r"\s+", " ", s.replace("°", "°")).strip().lower()
def param_phrase(old, new):
    ow, nw = old.split(), new.split(); i = 0
    while i < min(len(ow), len(nw)) and ow[i] == nw[i]: i += 1
    return " ".join(ow[:i])
def strict_score(answer, tgt):
    old_v, new_v = tgt["old_value"], tgt["new_value"]
    ot, nt = set(TOKEN_RE.findall(old_v)), set(TOKEN_RE.findall(new_v))
    new_only, old_only = sorted(nt - ot), sorted(ot - nt)
    phrase = norm(param_phrase(old_v, new_v)); short = " ".join(phrase.split()[:3])
    lines = [norm(l) for l in answer.split("\n") if l.strip()]
    def hit(toks):
        for l in lines:
            if (phrase and phrase in l) or (short and short in l):
                if any(re.search(re.escape(norm(t)), l) for t in toks): return True
        return False
    n, o = hit(new_only), hit(old_only)
    return "NewOnly" if n and not o else ("Both" if n and o else ("OldOnly" if o else "Neither"))
ARMS = [("Naive", "behavior_NaiveMemory.json", 14), ("RAG", "behavior_RagMemory.json", 0), ("EpSem", "behavior_EpSemMemory.json", 21),
        ("EpSem-F", "behavior_EpSemFiltered.json", 24), ("EpSem-SS", "behavior_EpSemSupersession.json", 34), ("LWW", "behavior_LWWMemory.json", 35),
        ("TS-Read", "behavior_TSRead.json", 39), ("EpSem-SS (Phi-3)", "behavior_EpSemSupersession_phi3.json", 14), ("Mem0 (v3)", "behavior_Mem0_v3.json", 6)]
DOMS = ["ENGINEERING", "MEDICAL", "LEGAL", "FINANCE", "GENERAL"]
def load_arm(fn):
    return [x for x in J(R1 / fn) if "error" not in x]
if __name__ == "__main__":
    print("| Arm | " + " | ".join(DOMS) + " | All | Fig.9/paper | Both/OldOnly/Neither |"); print("|---|" + "---|" * (len(DOMS) + 3))
    for name, fn, canon in ARMS:
        c = collections.defaultdict(collections.Counter); tot = collections.Counter()
        for x in load_arm(fn):
            d = S[x["scenario_id"]]["domain"]; tg = {t["gt_id"]: t for t in S[x["scenario_id"]]["evaluation_protocol"]["ua_targets"]}
            for b in x["behavior"]:
                cat = strict_score(x["answer_text"], tg[b["gt_id"]]); c[d][cat] += 1; c[d]["n"] += 1; tot[cat] += 1; tot["n"] += 1
        flag = "" if tot["NewOnly"] == canon else " ✗"
        print(f"| {name} | " + " | ".join(f"{c[d]['NewOnly']}/{c[d]['n']}" for d in DOMS) + f" | {tot['NewOnly']}/{tot['n']} ({100*tot['NewOnly']/tot['n']:.1f}%) | {canon}{flag} | {tot['Both']}/{tot['OldOnly']}/{tot['Neither']} |")
