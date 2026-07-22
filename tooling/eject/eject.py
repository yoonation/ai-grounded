#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
eject.py - export a consumer's application as a standalone tree, stripped of
the governance framework.

Never mutates the consumer repo. The export is a repeatable build into an
output directory (default dist/standalone under the consumer, which the
consumer's own .gitignore keeps out of version control), so a fresh
standalone cut can be produced after every framework or application change.

What ships: application files (paths the template does not own) plus
scaffold files the consumer filled, minus the manifest's eject.exclude
globs. What is stripped: everything classified framework or substrate in
the template's sync-manifest.yaml, plus the excludes.

Verification, in order, all mandatory unless skipped by flag:
  1. reference scan  no exported file may mention a framework path
     (governance-commons, .specify, presets/, tooling/, .githooks,
     .claude/) except files matching eject.allow-references
  2. marker scan     no exported file may carry a template-managed marker
  3. proof gate      prints (or with --run-proof executes) the standalone
     proof: pnpm install --frozen-lockfile, build, typecheck, unit tests
     inside the exported tree; the eject is not done until that passes

Exit codes: 0 export clean, 2 verification findings (export left in place
for inspection).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent.parent / "sync"))
from sync import Manifest, load_manifest, walk  # noqa: E402

REFERENCE_RE = re.compile(
    r"governance-commons|\.specify/|(?<![A-Za-z0-9_-])presets/|(?<![A-Za-z0-9_-])tooling/|\.githooks|\.claude/"
)
MARKER = "managed by ai-grounded"


def guard_out_dir(out: Path, consumer: Path, template: Path) -> None:
    """Refuse to rmtree a dangerous target. export() deletes `out` wholesale, so an
    out that resolves to the filesystem root, the caller's home, the consumer repo,
    the template repo, or the current directory would wipe real files on a typo
    (eject --out . or a mistyped path). Those targets are refused outright.
    """
    out_r = out.resolve()
    forbidden = {
        Path(out_r.anchor).resolve(),
        Path.home().resolve(),
        Path.cwd().resolve(),
        consumer.resolve(),
        template.resolve(),
    }
    if out_r in forbidden:
        sys.stderr.write(
            "eject: refusing to export into {0}; it resolves to a protected "
            "location (filesystem root, home, the consumer repo, the template "
            "repo, or the current directory), and the export would delete it. "
            "Choose a dedicated output directory such as dist/standalone.\n".format(out_r)
        )
        raise SystemExit(2)


def export(consumer: Path, manifest: Manifest, out: Path) -> list:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shipped = []
    for rel in walk(consumer):
        cls = manifest.class_of(rel)
        if cls in ("framework", "substrate") and (rel_in_template_scope(rel, manifest)):
            continue
        if Manifest._match(rel, manifest.eject_exclude):
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(consumer / rel, dst)
        shipped.append(rel)
    return shipped


def rel_in_template_scope(rel: str, manifest: Manifest) -> bool:
    """True when the path is one the template plausibly owns: substrate or
    scaffold globs, explicit framework globs, or the wholly template-owned
    directory roots. Application files (src/, tests/, bin/, ...) return
    False even though class_of defaults them to framework."""
    if Manifest._match(rel, manifest.substrate):
        return True
    if Manifest._match(rel, manifest.scaffold):
        return True
    if manifest.framework_glob_hit(rel):
        return True
    template_roots = ("tooling/", ".githooks/", "presets/", ".specify/", ".claude/",
                      ".github/")
    template_root_files = {"AGENTS.md", "CONTRIBUTING.md", "FUTURE.md", "LICENSE",
                           "NOTICE", "Makefile", "PREREQUISITES.md", "SETUP.md",
                           "NORTH-STAR.md", "renovate.json", "sync-manifest.yaml"}
    if rel in template_root_files:
        return True
    return any(rel.startswith(r) for r in template_roots)


def scan_references(out: Path, allow) -> list:
    hits = []
    for rel in walk(out):
        if Manifest._match(rel, allow):
            continue
        p = out / rel
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if REFERENCE_RE.search(line):
                hits.append(f"{rel}:{n}: {line.strip()[:120]}")
    return hits


def scan_markers(out: Path) -> list:
    hits = []
    for rel in walk(out):
        try:
            if MARKER in (out / rel).read_text(encoding="utf-8", errors="ignore"):
                hits.append(rel)
        except OSError:
            continue
    return hits


PROOF = [
    ["pnpm", "install", "--frozen-lockfile"],
    ["pnpm", "run", "build"],
    ["pnpm", "run", "typecheck"],
    ["pnpm", "run", "test:unit"],
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Export the application as a standalone tree.")
    ap.add_argument("--template", required=True, help="Path to the template repo (manifest source).")
    ap.add_argument("--consumer", default=".", help="Consumer repo to export (default: cwd).")
    ap.add_argument("--out", default=None, help="Output directory (default: <consumer>/dist/standalone).")
    ap.add_argument("--run-proof", action="store_true",
                    help="Execute the pnpm proof gate inside the export (default: print the commands).")
    ap.add_argument("--skip-scans", action="store_true", help="Skip reference and marker scans.")
    args = ap.parse_args(argv)

    template = Path(args.template).expanduser().resolve()
    consumer = Path(args.consumer).expanduser().resolve()
    out = Path(args.out).expanduser().resolve() if args.out else consumer / "dist" / "standalone"
    manifest = load_manifest(template)

    guard_out_dir(out, consumer, template)
    shipped = export(consumer, manifest, out)
    print(f"eject: exported {len(shipped)} files to {out}")

    findings = 0
    if not args.skip_scans:
        refs = scan_references(out, manifest.eject_allow_refs)
        for h in refs:
            print(f"  [reference] {h}")
        marks = scan_markers(out)
        for h in marks:
            print(f"  [marker] {h}")
        findings = len(refs) + len(marks)
        print(f"eject scans: references={len(refs)} markers={len(marks)}")

    print("eject proof gate (run inside the export):")
    for cmd in PROOF:
        print("  " + " ".join(cmd))
    if args.run_proof:
        for cmd in PROOF:
            r = subprocess.run(cmd, cwd=str(out))
            if r.returncode != 0:
                print(f"eject: proof gate failed at: {' '.join(cmd)}")
                return 2
        print("eject: proof gate passed")

    return 2 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
