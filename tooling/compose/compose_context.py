#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
compose_context.py - the deterministic context composition tool.

The context memory layer's one mechanism per horizon (synthesis 7.2). Every agent's
context is assembled in one fixed order, and nothing else:

  1. North star (always first)  - durable intent, the longest horizon. Why the work
     exists. Versioned, changed only at phase boundaries.
  2. Manifest slice (this checkpoint) - the working set. The catalogs, decision
     frameworks, and constitution articles this checkpoint consults, resolved from
     project-manifest.yaml.
  3. Open log items (relevant)  - the handoff horizon. Cross-feature observations from
     PROJECT-LOG.md that are still open (not yet promoted to an ADR).

The agent never sees its task without first seeing why it exists. Intent stays
human-authored (the north-star file, the manifest); composition stays deterministic and
auditable (this tool). The order is also cache-favorable: most-stable content first
(north star), then the stable per-checkpoint slice, then the volatile open items last,
so the cacheable prefix is maximal.

It is a tool, not a hook; you run it and read or inject its output. It never blocks.

The four canonical checkpoints (C1..C4) map 1:1 by position to the manifest's
workflow.checkpoints list, per the manifest's own contract.

Usage:
    uv run --with pyyaml python3 tooling/compose/compose_context.py \\
        --checkpoint C1 --north-star NORTH-STAR.md \\
        --manifest project-manifest.yaml --log PROJECT-LOG.md

Exit code is always 0 (advisory).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHECKPOINT_ORDER = ["C1", "C2", "C3", "C4"]
_RE_LOG_ENTRY = re.compile(r"^###\s+(.*\S)\s*$")
_RE_PROMOTED = re.compile(r"->\s*Promoted to ADR", re.IGNORECASE)


def slice_for_checkpoint(manifest: dict, checkpoint: str) -> dict:
    """Resolve the manifest slice for a canonical checkpoint (C1..C4) by position."""
    # The manifest wraps everything under a top-level `manifest:` key, with
    # workflow.checkpoints beneath it. Tolerate a few shapes for robustness.
    root = (manifest or {}).get("manifest") or (manifest or {})
    cps = ((root.get("workflow") or {}).get("checkpoints")) or []
    if not cps:
        cps = (((root.get("governance") or {}).get("workflow") or {}).get("checkpoints")) or []
    idx = CHECKPOINT_ORDER.index(checkpoint) if checkpoint in CHECKPOINT_ORDER else None
    if idx is None or idx >= len(cps):
        return {}
    cp = cps[idx] or {}
    consults = cp.get("consults") or {}
    return {
        "name": cp.get("name"),
        "consulter": cp.get("consulter"),
        "catalogs": consults.get("catalogs") or [],
        "decision_frameworks": consults.get("decision-frameworks") or [],
        "constitution_articles": cp.get("constitution-articles") or [],
    }


def open_log_items(log_text: str) -> list:
    """Return PROJECT-LOG entry titles that are still open (not promoted to an ADR).

    An entry is a '### ...' heading. An entry whose body (up to the next heading)
    contains a '-> Promoted to ADR' note is considered closed and excluded.
    """
    lines = (log_text or "").splitlines()
    entries = []
    cur = None
    body = []
    for ln in lines:
        m = _RE_LOG_ENTRY.match(ln)
        if m:
            if cur is not None:
                entries.append((cur, "\n".join(body)))
            cur = m.group(1).strip()
            body = []
        elif cur is not None:
            body.append(ln)
    if cur is not None:
        entries.append((cur, "\n".join(body)))
    out = []
    for title, b in entries:
        if _RE_PROMOTED.search(b):
            continue
        if title.lower().startswith("yyyy-mm-dd"):  # template placeholder, not a real entry
            continue
        out.append(title)
    return out


def compose(north_star_text: str, slice_dict: dict, open_items: list) -> str:
    """Pure. Assemble the ordered context block: north-star, then slice, then open items."""
    parts = []
    parts.append("===== NORTH STAR (why this project exists - read first) =====")
    parts.append((north_star_text or "(no north-star file found)").strip())
    parts.append("")
    cp = slice_dict.get("name") or "(unknown checkpoint)"
    parts.append("===== WORKING SET (manifest slice for {0}) =====".format(cp))
    if slice_dict.get("consulter"):
        parts.append("primary consulter: {0}".format(slice_dict["consulter"]))
    parts.append("catalogs: " + (", ".join(slice_dict.get("catalogs") or []) or "(none)"))
    parts.append("decision frameworks: " + (", ".join(slice_dict.get("decision_frameworks") or []) or "(none)"))
    parts.append("constitution articles: " + (", ".join(slice_dict.get("constitution_articles") or []) or "(none)"))
    parts.append("")
    parts.append("===== OPEN CROSS-CUTTING ITEMS (PROJECT-LOG, not yet resolved) =====")
    if open_items:
        for t in open_items:
            parts.append("- {0}".format(t))
    else:
        parts.append("(none open)")
    return "\n".join(parts) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Deterministic context composition. Advisory; never blocks.")
    p.add_argument("--checkpoint", required=True, help="canonical checkpoint C1..C4")
    p.add_argument("--north-star", default="NORTH-STAR.md")
    p.add_argument("--manifest", default="project-manifest.yaml")
    p.add_argument("--log", default="PROJECT-LOG.md")
    p.add_argument("--out", default="-", help="output path, or - for stdout")
    args = p.parse_args(argv)

    try:
        import yaml
    except ImportError:
        sys.stderr.write("pyyaml required: run via `uv run --with pyyaml python3 ...`\n")
        return 0

    ns = Path(args.north_star)
    ns_text = ns.read_text(encoding="utf-8", errors="replace") if ns.exists() else ""
    mf = Path(args.manifest)
    manifest = yaml.safe_load(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    lg = Path(args.log)
    log_text = lg.read_text(encoding="utf-8", errors="replace") if lg.exists() else ""

    block = compose(ns_text, slice_for_checkpoint(manifest, args.checkpoint), open_log_items(log_text))
    if args.out == "-":
        sys.stdout.write(block)
    else:
        Path(args.out).write_text(block, encoding="utf-8")
        sys.stdout.write("wrote {0}\n".format(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
