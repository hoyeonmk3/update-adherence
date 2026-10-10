# -*- coding: utf-8 -*-
"""Write MANIFEST.sha256 for the released engine, scenarios, results, and figure data.
Run from the repository root: python analysis/make_manifest.py
Verify with: shasum -a 256 -c MANIFEST.sha256
"""
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROOTS = ["engine", "scenarios", "results", "figures/data"]


def main():
    lines = []
    for r in ROOTS:
        for dp, dn, fn in os.walk(ROOT / r):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in sorted(fn):
                if f.endswith(".pyc"):
                    continue
                p = Path(dp) / f
                rel = p.relative_to(ROOT).as_posix()
                h = hashlib.sha256(p.read_bytes()).hexdigest()
                lines.append("%s *%s" % (h, rel))
    lines.sort(key=lambda l: l.split("*", 1)[1])
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("MANIFEST.sha256 written, %d entries" % len(lines))


if __name__ == "__main__":
    main()
