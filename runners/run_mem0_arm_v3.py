"""Mem0 external-system arm, v3: context-window-corrected measurement.

The earlier Mem0 runs (``results/superseded/behavior_Mem0*.json``) were made with the
serving engine's default context window of 4,096 tokens. The extraction prompt of
mem0ai 2.0.17 is about 8.4k tokens, so every library call ran on a truncated prompt
(``truncating input prompt`` in the Ollama server log). This runner keeps the guard
(Ollama 0.24.0), the configuration, and ``run_one`` of ``run_mem0_arm.py`` and changes
only the following.

(1) Every chat call issued by the mem0 library is made with ``options.num_ctx = NUM_CTX``
    by wrapping the Ollama client inside this process. The library files are not modified.
(2) ``prompt_eval_count`` and ``eval_count`` of every call are written to
    ``results/calls_mem0_v3.jsonl`` so that truncation can be ruled out per call.
(3) The four-line fact-parser normalization of ``run_mem0_arm_patched.py`` is applied to
    every scenario from the start.
(4) If ``--server-log`` points at the Ollama server log, the counts of ``truncating input
    prompt`` and ``context shift`` lines before and after the run are recorded in the
    ``.meta.json`` file. A run passes when both deltas are zero.
(5) Outputs go to ``results/behavior_Mem0_v3.json`` (+ ``.meta.json``) and the vector store
    to ``mem0_store_v3/``. The meta file records SHA-256 digests of this runner, of
    ``run_mem0_arm.py``, and of the mem0 library files that define the calls.

The answer-generation call (``base.gen_answer``) is left exactly as in every other arm; its
prompt stays within the default window.

Usage:
    python3 run_mem0_arm_v3.py                          # 24 Update Conflict scenarios
    python3 run_mem0_arm_v3.py --smoke U001 --max-turns 20
    python3 run_mem0_arm_v3.py --server-log /path/to/ollama_serve.log
"""
import sys
sys.dont_write_bytecode = True
import json as _stdlib_json, hashlib, time, shutil, gc, traceback, subprocess, platform, os
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)
REPO = Path(__file__).resolve().parent
os.chdir(REPO)
sys.path.insert(0, str(REPO))

import requests
import run_mem0_arm as base  # guard (Ollama 0.24.0), configuration, run_one, gen_answer, behavior_score
import mem0.memory.main as _mm
import mem0.llms.ollama as _mlo
import mem0.configs.prompts as _mprompts
from mem0.llms.ollama import OllamaLLM

NUM_CTX = 16384
LOG_PATTERNS = ["truncating input prompt", "input truncated", "context shift", "n_discard"]
DATA_DIRS = [Path("scenarios/holdout_v4"), Path("scenarios/holdout_v5")]


# ---------- (3) fact-parser normalization (identical to run_mem0_arm_patched.py) ----------
class _JsonProxy:
    """json replacement for mem0.memory.main: normalizes loads only, delegates the rest."""

    def loads(self, s, **kw):
        obj = _stdlib_json.loads(s, **kw)
        if isinstance(obj, dict) and isinstance(obj.get("memory"), list):
            obj["memory"] = [m if isinstance(m, dict) else {"text": str(m)}
                             for m in obj["memory"]]
        return obj

    def __getattr__(self, name):
        return getattr(_stdlib_json, name)


_mm.json = _JsonProxy()


# ---------- (1)(2) num_ctx injection and per-call token accounting ----------
CUR = {"scenario": None, "calls": 0, "calls_log": None}
_orig_init = OllamaLLM.__init__


def _init(self, config=None):
    _orig_init(self, config)
    orig_chat = self.client.chat

    def chat(**params):
        opts = dict(params.get("options") or {})
        opts["num_ctx"] = NUM_CTX
        params["options"] = opts
        t0 = time.perf_counter()
        resp = orig_chat(**params)
        rec = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "scenario": CUR["scenario"],
            "prompt_chars": sum(len(m.get("content", "")) for m in params.get("messages", [])),
            "prompt_eval_count": getattr(resp, "prompt_eval_count", None),
            "eval_count": getattr(resp, "eval_count", None),
            "num_ctx": NUM_CTX,
            "format": params.get("format"),
            "wall_s": round(time.perf_counter() - t0, 1),
        }
        CUR["calls"] += 1
        if CUR["calls_log"]:
            with open(CUR["calls_log"], "a") as f:
                f.write(_stdlib_json.dumps(rec) + "\n")
        return resp

    self.client.chat = chat


OllamaLLM.__init__ = _init


# ---------- (4) server-log check ----------
def log_counts(server_log):
    if not server_log or not Path(server_log).exists():
        return None
    out = {}
    for p in LOG_PATTERNS:
        r = subprocess.run(["grep", "-c", "-i", p, server_log], capture_output=True, text=True)
        out[p] = int((r.stdout or "0").strip() or 0)
    return out


# ---------- (5) stamp ----------
def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stamp():
    import importlib.metadata as md
    return {
        "runner_sha256": sha256(__file__),
        "base_runner_sha256": sha256(REPO / "run_mem0_arm.py"),
        "mem0_ollama_llm_sha256": sha256(_mlo.__file__),
        "mem0_prompts_sha256": sha256(_mprompts.__file__),
        "mem0ai": md.version("mem0ai"), "ollama_client": md.version("ollama"),
        "qdrant_client": md.version("qdrant-client"),
        "python": platform.python_version(), "platform": platform.platform(),
        "ollama_server": requests.get(f"{base.OLLAMA}/api/version", timeout=10).json().get("version"),
        "gen_model": base.GEN_MODEL, "embedder": "nomic-embed-text", "batch": base.BATCH,
        "search_k": base.SEARCH_K, "num_ctx_extraction": NUM_CTX,
        "num_ctx_answer": "server default (unchanged, parity with the other arms)",
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", type=str, default=None, help="scenario id substring, e.g. U001")
    ap.add_argument("--max-turns", type=int, default=None, help="smoke only: feed the first N turns")
    ap.add_argument("--server-log", type=str, default=None, help="Ollama server log for the truncation check")
    args = ap.parse_args()
    tag = "smoke" if args.smoke else "v3"

    base.STORE_DIR = f"mem0_store_{tag}"
    out = Path("results") / f"behavior_Mem0_{tag}.json"
    meta_path = out.with_suffix(".meta.json")
    CUR["calls_log"] = str(Path("results") / f"calls_mem0_{tag}.jsonl")
    Path("results").mkdir(exist_ok=True)
    shutil.rmtree(base.STORE_DIR, ignore_errors=True)
    Path(CUR["calls_log"]).unlink(missing_ok=True)

    scenarios = []
    for d in DATA_DIRS:
        scenarios += sorted(d.glob("U0*.json"))
    if args.smoke:
        scenarios = [s for s in scenarios if args.smoke in s.name]

    meta = {"stamp": stamp(), "started": datetime.now().isoformat(timespec="seconds"),
            "n_scenarios": len(scenarios), "max_turns": args.max_turns,
            "server_log": args.server_log, "log_counts_before": log_counts(args.server_log)}
    with open(meta_path, "w") as f:
        _stdlib_json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"Mem0 arm v3 ({tag}): {len(scenarios)} scenarios | num_ctx={NUM_CTX} | {meta['started']}")
    print(f"[stamp] {meta['stamp']}")
    print(f"[log] before={meta['log_counts_before']}")

    results = []
    for i, p in enumerate(scenarios):
        with open(p) as f:
            sc = _stdlib_json.load(f)
        if args.max_turns:
            sc = dict(sc)
            sc["turns"] = sc["turns"][:args.max_turns]
        CUR["scenario"] = sc["scenario_id"]
        print(f"  [{i+1}/{len(scenarios)}] {sc['scenario_id']} ({sc['total_turns']}T) ...", end="", flush=True)
        try:
            r = base.run_one(sc)
            r["patched"] = True
            r["num_ctx_extraction"] = NUM_CTX
            cu = r["context_ua"]
            ok = sum(1 for x in cu if x["has_new"] and not x["has_old"])
            bh = r["behavior"]
            bok = sum(1 for x in bh if x["new_tokens_hit"] and not x["old_tokens_hit"])
            print(f" R={r['recall']:.3f} ctxUA={ok}/{len(cu)} behUA*={bok}/{len(bh)} t={r['replay_s']}s calls={CUR['calls']}")
            results.append(r)
        except Exception as e:
            print(f" ERROR {e}")
            traceback.print_exc()
            results.append({"scenario_id": sc["scenario_id"], "error": str(e), "patched": True})
        gc.collect()
        with open(out, "w") as f:
            _stdlib_json.dump(results, f, ensure_ascii=False, indent=1)

    meta["finished"] = datetime.now().isoformat(timespec="seconds")
    meta["log_counts_after"] = log_counts(args.server_log)
    if meta["log_counts_before"] is not None and meta["log_counts_after"] is not None:
        meta["log_delta"] = {k: meta["log_counts_after"][k] - meta["log_counts_before"][k] for k in LOG_PATTERNS}
        verdict = "PASS" if all(v == 0 for v in meta["log_delta"].values()) else "FAIL"
    else:
        meta["log_delta"] = None
        verdict = "NOT CHECKED (no --server-log)"
    meta["calls_total"] = CUR["calls"]
    with open(meta_path, "w") as f:
        _stdlib_json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"[log] after={meta['log_counts_after']} delta={meta['log_delta']} -> {verdict}")
    print(f"MEM0 ARM V3 DONE ({tag}) {meta['finished']}")


if __name__ == "__main__":
    main()
