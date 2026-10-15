#!/usr/bin/env python3
"""Regenerate every released scenario file into a directory of your choice and compare it with scenarios/.

Steps (no model is called):
    1. Batch A, 36 conversations   generator/scenario_generator.py      -> OUT/holdout_v4
    2. Batch B, 36 conversations   generator/generate_v5_scenarios.py   -> OUT/holdout_v5
    3. implicit variants, 12       generator/derive_implicit.py          -> OUT/implicit  (derived from OUT/holdout_v4)
    4. scenarios/fn/ (the 48 Forgetting and Noise Tolerance conversations) is checked as a copy of the batch files.

The expected file set of every directory is fixed (36, 36, 12, and 48 names). A released directory that is
missing, a missing or extra file on either side, or a file that differs is a failure. Files are compared
byte for byte first and then as parsed JSON; "same content, different bytes" is reported but is not a failure.
Exit status 0 only when every check passes.

Usage (from the repository root):
    python generator/regenerate_scenarios.py --output-dir /tmp/ua_regen
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generator"
RELEASED = ROOT / "scenarios"

EXPECTED = {
    "holdout_v4": {f"{t}{n:03d}_v4.json" for t in "FNU" for n in range(1, 13)},
    "holdout_v5": {f"{t}{n:03d}_v5.json" for t in "FNU" for n in range(13, 25)},
    "implicit": {f"U{n:03d}_impT{(n - 1) % 3 + 1}.json" for n in range(1, 13)},
}
EXPECTED_FN = {name for d in ("holdout_v4", "holdout_v5") for name in EXPECTED[d] if name[0] in "FN"}
RUN_LOG = "generation_log.json"  # written by the Batch B generator beside its output; not part of the released set


def run(cmd, cwd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    print("$", " ".join(str(c) for c in cmd))
    r = subprocess.run([str(c) for c in cmd], cwd=str(cwd), env=env, capture_output=True, text=True, encoding="utf-8")
    for line in (r.stdout or "").strip().splitlines()[-3:]:
        print("   ", line)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit(f"command failed with exit status {r.returncode}")


def same_file(a: Path, b: Path) -> str:
    x, y = a.read_bytes(), b.read_bytes()
    if x == y:
        return "identical"
    try:
        if json.loads(x.decode("utf-8")) == json.loads(y.decode("utf-8")):
            return "same content"
    except (UnicodeDecodeError, ValueError):
        pass
    return "DIFFERENT"


def compare_dir(new_dir: Path, released_dir: Path, expected: set, label: str, allowed_extra=(RUN_LOG,)) -> int:
    failures = 0
    if not released_dir.is_dir():
        print(f"{label}: released directory {released_dir} is missing")
        return len(expected)
    released = {p.name for p in released_dir.glob("*.json")}
    new = {p.name for p in new_dir.glob("*.json")} - set(allowed_extra)
    for name in sorted(expected - released):
        print(f"   MISSING from the released set: {name}"); failures += 1
    for name in sorted(released - expected):
        print(f"   UNEXPECTED file in the released set: {name}"); failures += 1
    for name in sorted(expected - new):
        print(f"   MISSING from the regenerated set: {name}"); failures += 1
    for name in sorted(new - expected):
        print(f"   UNEXPECTED file in the regenerated set: {name}"); failures += 1
    counts = {"identical": 0, "same content": 0, "DIFFERENT": 0}
    for name in sorted(expected & released & new):
        verdict = same_file(new_dir / name, released_dir / name)
        counts[verdict] += 1
        if verdict != "identical":
            print(f"   {verdict}: {name}")
    failures += counts["DIFFERENT"]
    print(f"{label}: expected {len(expected)}, released {len(released)}, regenerated {len(new)}, "
          f"identical {counts['identical']}, same content {counts['same content']}, different {counts['DIFFERENT']}, "
          f"failures {failures}")
    return failures


def check_fn_copies() -> int:
    """scenarios/fn/ must hold exactly the 48 Forgetting and Noise Tolerance files of both batches, unchanged."""
    fn_dir = RELEASED / "fn"
    if not fn_dir.is_dir():
        print(f"scenarios/fn: directory {fn_dir} is missing")
        return len(EXPECTED_FN)
    actual = {p.name for p in fn_dir.glob("*.json")}
    failures = 0
    for name in sorted(EXPECTED_FN - actual):
        print(f"   MISSING from scenarios/fn: {name}"); failures += 1
    for name in sorted(actual - EXPECTED_FN):
        print(f"   UNEXPECTED file in scenarios/fn: {name}"); failures += 1
    identical = 0
    for name in sorted(EXPECTED_FN & actual):
        source = RELEASED / ("holdout_v4" if name.endswith("_v4.json") else "holdout_v5") / name
        if not source.is_file():
            print(f"   batch file missing for fn/{name}: {source}"); failures += 1
            continue
        verdict = same_file(fn_dir / name, source)
        if verdict == "DIFFERENT":
            print(f"   DIFFERENT from the batch file: fn/{name}"); failures += 1
        else:
            identical += 1
            if verdict != "identical":
                print(f"   same content, different bytes: fn/{name}")
    print(f"scenarios/fn: expected {len(EXPECTED_FN)}, present {len(actual)}, matching the batch files {identical}, failures {failures}")
    return failures


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Regenerate all scenario files and compare them with scenarios/")
    ap.add_argument("--output-dir", required=True, help="directory for the regenerated files (created if missing)")
    args = ap.parse_args()
    out = Path(args.output_dir).resolve()
    for sub in ("holdout_v4", "holdout_v5", "implicit"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    run([sys.executable, GEN / "scenario_generator.py", "--output-dir", out / "holdout_v4"], cwd=ROOT)
    run([sys.executable, GEN / "generate_v5_scenarios.py", "--output-dir", out / "holdout_v5"], cwd=ROOT)
    run([sys.executable, GEN / "derive_implicit.py", "--base-dir", out / "holdout_v4", "--output-dir", out / "implicit"], cwd=ROOT)

    print()
    failures = 0
    failures += compare_dir(out / "holdout_v4", RELEASED / "holdout_v4", EXPECTED["holdout_v4"], "Batch A (scenarios/holdout_v4)")
    failures += compare_dir(out / "holdout_v5", RELEASED / "holdout_v5", EXPECTED["holdout_v5"], "Batch B (scenarios/holdout_v5)")
    failures += compare_dir(out / "implicit", RELEASED / "implicit", EXPECTED["implicit"], "implicit variants (scenarios/implicit)")
    failures += check_fn_copies()
    print()
    print("RESULT:", "all regenerated files match the released files" if failures == 0 else f"{failures} failure(s)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
