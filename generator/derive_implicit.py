#!/usr/bin/env python3
"""Derive the 12 implicit-revision variants (scenarios/implicit/) from the 12 Batch A Update Conflict scenarios.

Only the explicit update utterances are reworded. Turn indices, roles, distractor turns, ground truth,
update schedule, and evaluation protocol are copied unchanged. The wording form follows the scenario number:

    U001, U004, U007, U010 -> T1 (transition-marked)  "<canonical sentence> going forward."
    U002, U005, U008, U011 -> T2 (bare)               "<canonical sentence>."
    U003, U006, U009, U012 -> T3 (conversational)     "Let's work with this from here: <canonical sentence>."

An explicit update in Batch A reads
    "Update to previous requirement: <canonical sentence> (replaces the earlier specification)."
and every such utterance in a scenario is reworded. The variant gets scenario_id "hold-out-U0xx_impT<n>"
and an added field "implicit_tier".

Usage (from the repository root):
    python generator/derive_implicit.py --base-dir scenarios/holdout_v4 --output-dir /tmp/implicit
    python generator/derive_implicit.py --base-dir scenarios/holdout_v4 --output-dir /tmp/implicit --check scenarios/implicit

--check compares every written file with the released file of the same name (bytes, then parsed JSON).
No model is called.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXPLICIT = re.compile(r"^Update to previous requirement: (.+?) \(replaces the earlier specification\)\.?$")
TIER_FORM = {
    1: "{x} going forward.",
    2: "{x}.",
    3: "Let's work with this from here: {x}.",
}
BASE_IDS = [f"U{n:03d}" for n in range(1, 13)]


def tier_of(base_id: str) -> int:
    n = int(base_id[1:])
    return (n - 1) % 3 + 1


def derive(scenario: dict, base_id: str) -> dict:
    tier = tier_of(base_id)
    out = json.loads(json.dumps(scenario, ensure_ascii=False))  # deep copy, key order kept
    out["scenario_id"] = f"hold-out-{base_id}_impT{tier}"
    n = 0
    for turn in out["turns"]:
        m = EXPLICIT.match(turn.get("content", ""))
        if m:
            turn["content"] = TIER_FORM[tier].format(x=m.group(1).rstrip("."))
            n += 1
    if n == 0:
        raise ValueError(f"{base_id}: no explicit update utterance found")
    out["implicit_tier"] = f"T{tier}"
    return out


def write_json(path: Path, obj: dict) -> None:
    # Same serialization as the released files: one-space indent, UTF-8, LF, no trailing newline.
    text = json.dumps(obj, ensure_ascii=False, indent=1)
    path.write_bytes(text.encode("utf-8"))


def compare(written: Path, released: Path) -> str:
    a, b = written.read_bytes(), released.read_bytes()
    if a == b:
        return "identical"
    if json.loads(a.decode("utf-8")) == json.loads(b.decode("utf-8")):
        return "same content, different bytes"
    return "DIFFERENT"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Derive the implicit-revision variants from the Batch A scenarios")
    ap.add_argument("--base-dir", default="scenarios/holdout_v4", help="directory holding U001_v4.json to U012_v4.json")
    ap.add_argument("--output-dir", required=True, help="directory for the 12 derived files")
    ap.add_argument("--check", default=None, help="released directory to compare against (e.g. scenarios/implicit)")
    args = ap.parse_args()

    base_dir, out_dir = Path(args.base_dir), Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bad = 0
    for base_id in BASE_IDS:
        src = base_dir / f"{base_id}_v4.json"
        scenario = json.loads(src.read_text(encoding="utf-8"))
        variant = derive(scenario, base_id)
        name = f"{base_id}_impT{tier_of(base_id)}.json"
        write_json(out_dir / name, variant)
        line = f"  {name}"
        if args.check:
            verdict = compare(out_dir / name, Path(args.check) / name)
            line += f"  {verdict}"
            if verdict == "DIFFERENT":
                bad += 1
        print(line)
    print(f"written: {len(BASE_IDS)} files to {out_dir.resolve()}")
    if args.check:
        print("check:", "all match" if bad == 0 else f"{bad} file(s) differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
