# -*- coding: utf-8 -*-
"""Shared loaders and scoring rules for the offline analyses.

Everything here reads the released files only. No model call is made.
- scenarios(): all scenario files keyed by scenario_id (Batch A, Batch B, implicit variants, F/N subset)
- ledger(name): a per-event ledger from results/ (behavior_*.json), error records dropped
- context_category(record): Correct / Stale-Retained / Stale-Only / Lost from the exact-string flags
- strict_score(answer, target): NewOnly / Both / OldOnly / Neither under the strict answer rule of the paper
- batch(scenario_id): "A" for Batch A (U001-U012), "B" for Batch B (U013-U024)
"""
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SCEN = ROOT / "scenarios"

ARMS = [  # paper name, ledger file, configuration key in canonical files
    ("Naive", "behavior_NaiveMemory.json", "NaiveMemory"),
    ("RAG", "behavior_RagMemory.json", "RagMemory"),
    ("EpSem", "behavior_EpSemMemory.json", "EpSemMemory"),
    ("EpSem-F", "behavior_EpSemFiltered.json", "EpSemFiltered"),
    ("EpSem-SS", "behavior_EpSemSupersession.json", "EpSemSupersession"),
    ("LWW", "behavior_LWWMemory.json", None),
    ("TS-Read", "behavior_TSRead.json", None),
    ("EpSem-SS (Phi-3)", "behavior_EpSemSupersession_phi3.json", None),
    ("Mem0", "behavior_Mem0_v3.json", None),
]
CATEGORIES = ["Correct", "Stale-Retained", "Stale-Only", "Lost"]
ANSWERS = ["NewOnly", "Both", "OldOnly", "Neither"]
TOKEN_RE = re.compile(r"[A-Za-z0-9°%/\.]+")


def J(path):
    return json.load(open(path, encoding="utf-8"))


def scenarios():
    out = {}
    for sub in ("holdout_v4", "holdout_v5", "implicit", "fn"):
        for f in glob.glob(str(SCEN / sub / "*.json")):
            d = J(f)
            if isinstance(d, dict) and "scenario_id" in d:
                out[d["scenario_id"]] = d
    return out


def targets(scenario):
    return {t["gt_id"]: t for t in scenario["evaluation_protocol"].get("ua_targets", [])}


def ledger(name):
    return [x for x in J(RESULTS / name) if isinstance(x, dict) and "error" not in x]


def context_category(c):
    """c has has_new / has_old (exact canonical-sentence presence in the assembled context)."""
    if c["has_new"] and not c["has_old"]:
        return "Correct"
    if c["has_new"] and c["has_old"]:
        return "Stale-Retained"
    if c["has_old"]:
        return "Stale-Only"
    return "Lost"


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def param_phrase(old, new):
    ow, nw = old.split(), new.split()
    i = 0
    while i < min(len(ow), len(nw)) and ow[i] == nw[i]:
        i += 1
    return " ".join(ow[:i])


def strict_score(answer, target):
    """Strict answer rule: a distinguishing value token counts only on an answer line that carries the
    parameter anchor (common word prefix of the two constraint sentences, or its first three words)."""
    old_v, new_v = target["old_value"], target["new_value"]
    ot, nt = set(TOKEN_RE.findall(old_v)), set(TOKEN_RE.findall(new_v))
    new_only, old_only = sorted(nt - ot), sorted(ot - nt)
    phrase = norm(param_phrase(old_v, new_v))
    short = " ".join(phrase.split()[:3])
    lines = [norm(l) for l in answer.split("\n") if l.strip()]

    def hit(tokens):
        for l in lines:
            if (phrase and phrase in l) or (short and short in l):
                if any(re.search(re.escape(norm(t)), l) for t in tokens):
                    return True
        return False

    n, o = hit(new_only), hit(old_only)
    if n and not o:
        return "NewOnly"
    if n and o:
        return "Both"
    if o:
        return "OldOnly"
    return "Neither"


def batch(scenario_id):
    m = re.search(r"U(\d{3})", scenario_id)
    return "A" if m and int(m.group(1)) <= 12 else "B"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)
