#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the duplication / dependency gate (advisory).

Reads the capability index (tooling/capability-index/generate.py output) and flags
exported symbols that appear under the same name in more than one file. A recurring
distinctive name is a lead that the same capability was built twice and should be a
shared helper; the flag is for a human to confirm on inspection, not an automatic
verdict. Conventional names that are expected to recur (CLI `main`, dunders, `setup`)
are ignored so the signal is not drowned in boilerplate.

It pairs with the discovery agent: the agent reasons over the index with fresh eyes
before construction; this gate is the deterministic backstop that names the concrete
collisions. The agent proposes; this reports; neither builds the index nor blocks.

Advisory first: always exits 0, emits a `passes` verdict and the flags. Enforcement (if
any) is skill-instructed; the gate's job is to surface real duplication, not to halt.

Usage:
    python3 tooling/duplication/check.py .capability-index.json
    python3 tooling/duplication/check.py .capability-index.json --text
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Names expected to recur across files; recurrence here is convention, not duplication.
IGNORE = {
    "main", "__init__", "__main__", "setup", "run", "handler", "cli",
    "__repr__", "__str__", "__eq__", "__hash__", "__call__", "__enter__", "__exit__",
}


def _symbol_names(entry) -> list:
    syms = (entry or {}).get("symbols") or []
    out = []
    for s in syms:
        if isinstance(s, str):
            out.append(s)
        elif isinstance(s, dict):
            n = s.get("name") or s.get("symbol")
            if n:
                out.append(n)
    return out


def find_duplicates(exports: dict, ignore=None) -> list:
    """Pure. Return [{symbol, files:[...]}] for non-convention symbols in 2+ files."""
    ignore = ignore if ignore is not None else IGNORE
    by_symbol = {}
    for path, entry in (exports or {}).items():
        for name in _symbol_names(entry):
            if name in ignore or name.startswith("__"):
                continue
            by_symbol.setdefault(name, set()).add(path)
    dups = [{"symbol": s, "files": sorted(fs)} for s, fs in by_symbol.items() if len(fs) > 1]
    return sorted(dups, key=lambda d: (-len(d["files"]), d["symbol"]))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Duplication gate over the capability index. Advisory; never blocks.")
    p.add_argument("index", nargs="?", default=".capability-index.json",
                   help="path to the capability index JSON (default: .capability-index.json)")
    p.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    args = p.parse_args(argv)

    idx_path = Path(args.index)
    if not idx_path.exists():
        msg = "capability index not found at {0}; generate it first ".format(args.index) + \
              "(tooling/capability-index/generate.py . --out .capability-index.json)"
        if args.text:
            sys.stdout.write(msg + "\n")
        else:
            sys.stdout.write(json.dumps({"passes": True, "duplicates": [], "note": msg}) + "\n")
        return 0

    index = json.loads(idx_path.read_text(encoding="utf-8"))
    dups = find_duplicates(index.get("exports") or {})
    result = {"passes": len(dups) == 0, "duplicate_count": len(dups), "duplicates": dups}

    if args.text:
        if not dups:
            sys.stdout.write("no duplicate exported symbols (excluding conventional names)\n")
        else:
            sys.stdout.write("duplicate exported symbol names (confirm on inspection):\n")
            for d in dups:
                sys.stdout.write("  {0}  in {1} files: {2}\n".format(
                    d["symbol"], len(d["files"]), ", ".join(d["files"])))
    else:
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
