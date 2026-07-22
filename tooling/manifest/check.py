#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - manifest reference validator (semantic half to the schema gate).

The schema gate (tooling/schema) proves project-manifest.yaml has the right SHAPE:
catalogs is an array of strings, constitution-articles is an array of strings, and
so on. It cannot prove those strings name things that exist. A checkpoint that
consults `concerns/authentcation` (typo) or cites `Article-VIII` (no such article)
passes the schema and then silently consults nothing or slices no constitution.
This validator closes that semantic gap: for each reference the manifest declares,
it checks the target resolves.

It builds on the shared reference-resolution primitive (tooling/lib/references.py).
References checked, by how cleanly they resolve:

  Framework-internal (clean, no substrate coupling):
    - constitution-articles -> ## Article N in .specify/memory/constitution.md
    - consulter (agent)      -> .claude/agents/<name>.md (or a known tool consulter
                                like opengrep-static-analysis)
    - stack.pins-source      -> a file on disk

  Substrate (best-effort): catalog references (checkpoint consults.catalogs and
    concerns.always/never) resolve against governance-commons/catalogs/ (a concern
    is a dir, a threat/compliance ref is a .yaml file). If that layout is not
    present, catalog references are reported as NOT VALIDATED (a loud skip), never
    silently passed.

Deferred: decision-frameworks and individual rule ids (rule resolution would mean
parsing OSCAL catalog content, deep substrate coupling, low marginal value).

Report-only by default (exit 0); --strict exits 1 on a dangling reference. A loud
skip of catalog validation (substrate layout absent) does not block, since it is
not actionable from here. Graceful no-op when PyYAML is absent.

Usage:
    uv run --with pyyaml python3 tooling/manifest/check.py --repo-root . --text [--strict]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from references import find_dangling  # noqa: E402

KNOWN_TOOL_CONSULTERS = {"opengrep-static-analysis"}  # consulters that are tools, not agents


# ---------------- edge extraction (pure) ----------------


def extract_edges(manifest):
    """Pure. Pull the declared references out of a parsed manifest as
    (source, target, kind) edges. Missing sections are simply no edges."""
    edges = []
    m = (manifest or {}).get("manifest") or {}
    for cp in ((m.get("workflow") or {}).get("checkpoints") or []):
        src = f"checkpoint:{cp.get('name', '?')}"
        consulter = cp.get("consulter")
        if consulter:
            edges.append((src, consulter, "agent"))
        for art in cp.get("constitution-articles", []) or []:
            edges.append((src, art, "article"))
        for cat in ((cp.get("consults") or {}).get("catalogs") or []):
            edges.append((src, cat, "catalog"))
    concerns = (manifest or {}).get("concerns") or {}
    for cat in (concerns.get("always") or []) + (concerns.get("never") or []):
        edges.append(("concerns", cat, "catalog"))
    stack = (manifest or {}).get("stack") or {}
    for f in (stack.get("pins-source") or []):
        edges.append(("stack.pins-source", f, "file"))
    return edges


# ---------------- resolvers (I/O) ----------------


def article_set(repo_root: Path):
    """Article ids the constitution actually defines, normalized to the manifest's
    'Article-N' form. e.g. '## Article V: Security Posture' -> 'Article-V'."""
    path = repo_root / ".specify" / "memory" / "constitution.md"
    out = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^#{1,3}\s+Article\s+([IVXLC]+)\b", line)
            if m:
                out.add(f"Article-{m.group(1)}")
    return out


def catalog_resolver(repo_root: Path):
    """Return a resolver for catalog refs, or None if the substrate catalog layout
    is absent (so the caller surfaces a loud skip instead of false danglers)."""
    base = repo_root / "governance-commons" / "catalogs"
    if not base.is_dir():
        return None

    def resolves(ref: str) -> bool:
        p = base / ref
        return p.is_dir() or (base / f"{ref}.yaml").is_file() or (base / f"{ref}.oscal.yaml").is_file()

    return resolves


def build_resolvers(repo_root: Path):
    arts = article_set(repo_root)
    resolvers = {
        "article": lambda a: a in arts,
        "agent": lambda n: n in KNOWN_TOOL_CONSULTERS or (repo_root / ".claude" / "agents" / f"{n}.md").is_file(),
        "file": lambda f: (repo_root / f).exists(),
    }
    cat = catalog_resolver(repo_root)
    if cat is not None:
        resolvers["catalog"] = cat   # else catalog edges become 'unresolvable' -> loud skip
    return resolvers


# ---------------- verdict + report ----------------


def pin_status(manifest, repo_root: Path) -> dict:
    """Compare the manifest's commons-version pin to governance-commons/VERSION.
    A stale pin is exactly the drift this checker exists to catch; both sides
    absent is a silent skip (nothing to compare)."""
    pin = str(manifest.get("commons-version") or "").strip()
    vfile = repo_root / "governance-commons" / "VERSION"
    version = vfile.read_text(encoding="utf-8").strip() if vfile.exists() else ""
    if not pin or not version:
        return {"pin": pin or None, "version": version or None, "comparable": False,
                "matches": None}
    return {"pin": pin, "version": version, "comparable": True,
            "matches": pin == version}


def build_report(manifest, repo_root: Path) -> dict:
    edges = extract_edges(manifest)
    result = find_dangling(edges, build_resolvers(repo_root))
    dangling = result["dangling"]
    unresolvable = result["unresolvable"]   # catalog refs when the substrate layout is absent
    pin = pin_status(manifest, repo_root)
    pin_stale = pin["comparable"] and not pin["matches"]
    return {
        "checked": len(edges),
        "dangling": dangling,
        "unvalidated": unresolvable,
        "pin": pin,
        "passes": not dangling and not pin_stale,   # a loud skip is not a failure
        "strict_blocks": bool(dangling) or pin_stale,  # unresolvable does not block (unactionable here)
    }


def load_manifest(path: Path):
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def render(report) -> str:
    lines = [f"checked: {report['checked']} reference(s); passes: {report['passes']}"]
    pin = report.get("pin") or {}
    if pin.get("comparable") and not pin.get("matches"):
        lines.append(f"  STALE PIN: commons-version pins '{pin['pin']}' but"
                     f" governance-commons/VERSION is '{pin['version']}';"
                     f" refresh the pin (or cut the release the pin expects)")
    for d in report["dangling"]:
        lines.append(f"  DANGLING: {d['source']} references {d['kind']} '{d['target']}' which does not exist")
    if report["unvalidated"]:
        kinds = sorted({u["kind"] for u in report["unvalidated"]})
        lines.append("")
        lines.append(f"  !! NOT VALIDATED: {len(report['unvalidated'])} {','.join(kinds)} reference(s) !!")
        lines.append("     governance-commons/catalogs/ was not found, so catalog references")
        lines.append("     could not be resolved. This is a loud skip, not a pass, and does not")
        lines.append("     block (the substrate layout is not fixable from here).")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Manifest reference validator. Advisory unless --strict.")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--manifest", default=None)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    repo_root = Path(args.repo_root)
    manifest_path = Path(args.manifest) if args.manifest else repo_root / "project-manifest.yaml"
    manifest = load_manifest(manifest_path)
    if manifest is None:
        sys.stdout.write("manifest: PyYAML not available; run via 'uv run --with pyyaml'.\n")
        return 0
    report = build_report(manifest, repo_root)
    sys.stdout.write(render(report) if args.text else json.dumps(report, indent=2) + "\n")

    if args.strict and report["strict_blocks"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
