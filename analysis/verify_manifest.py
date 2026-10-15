#!/usr/bin/env python3
"""Verify MANIFEST.sha256 with the Python standard library.

Reads every "<sha256> *<path>" line of MANIFEST.sha256, hashes the file at <path> relative to the repository
root, and reports each missing or changed file. Exit status 0 when every listed file is present and unchanged,
1 otherwise. Equivalent to `shasum -a 256 -c MANIFEST.sha256` or `sha256sum -c MANIFEST.sha256`, for
machines without those tools.

Usage (from the repository root): python analysis/verify_manifest.py
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"


def main() -> int:
    if not MANIFEST.is_file():
        print(f"MANIFEST.sha256 not found at {MANIFEST}")
        return 1
    listed = verified = 0
    problems = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, name = line.split(None, 1)
        name = name.strip().lstrip("*")
        listed += 1
        path = ROOT / name
        if not path.is_file():
            problems.append(f"MISSING  {name}")
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest.lower():
            problems.append(f"CHANGED  {name}")
            continue
        verified += 1
    for p in problems:
        print(p)
    print(f"manifest: {listed} files listed, {verified} verified, {len(problems)} missing or changed")
    return 0 if listed and not problems else 1


if __name__ == "__main__":
    sys.exit(main())
