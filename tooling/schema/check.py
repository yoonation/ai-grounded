#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
check.py - the schema-enforcement gate.

The framework ships JSON Schemas for its structured artifacts
(.specify/schemas/project-manifest.schema.json, feature-concerns.schema.json) and
instructs agents to emit conforming output, but nothing verifies that the actual
instances conform. The schema is a declaration; whether the instance matches it
was never checked. That is the framework's own declared-vs-actual failure class
turned on itself: a malformed project-manifest.yaml or feature-concerns.yaml
silently breaks the downstream tools that read it (the dial, the quality gate's
language read, the concern selector), with no signal at commit time.

This wires the validators the framework already owns into the loop. For each
recognized instance among the files it is given (or, with no files, every instance
it can find), it validates the instance against its schema and reports conformance.

Scope: project-manifest.yaml and specs/*/feature-concerns.yaml. events.jsonl is
deliberately excluded: its schema is permissive by design (additionalProperties
true for cross-tool events), so validating it catches little. The manifest's
consumer sections are validated against the consumer schema here; the substrate
`manifest:` block is the substrate's concern.

Report-only by default (exit 0); --strict exits 1 on a nonconforming instance.
Graceful no-op when the validator (jsonschema) or the YAML parser (PyYAML) is not
installed, so an unconfigured clone is never broken by this gate. The CLI is run
under uv with both: `uv run --with jsonschema --with pyyaml python3 ...`.

The pure core (which files are instances; the report verdict given a validator) is
stdlib-only and unit-testable without jsonschema or PyYAML; the validator and YAML
parser are imported lazily so the module imports for testing without them.

Usage:
    uv run --with jsonschema --with pyyaml python3 tooling/schema/check.py [FILE ...] --repo-root . [--strict] [--text]

Exit: 0 when advisory (default), all instances conform, or the validator is
unavailable; 1 only with --strict and a nonconforming instance.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MANIFEST_SCHEMA = ".specify/schemas/project-manifest.schema.json"
FEATURE_CONCERNS_SCHEMA = ".specify/schemas/feature-concerns.schema.json"


def pair_for(rel_path: str):
    """Map an instance path to its schema path, or None if not a recognized instance."""
    name = Path(rel_path).name
    if rel_path == "project-manifest.yaml" or name == "project-manifest.yaml":
        return MANIFEST_SCHEMA
    if name == "feature-concerns.yaml":
        return FEATURE_CONCERNS_SCHEMA
    return None


def recognized_instances(repo_root: Path, files=None):
    """
    Pure-ish. The (instance, schema) pairs to validate. If `files` is given, keep
    only those that are recognized instances; otherwise discover the manifest and
    every specs/*/feature-concerns.yaml on disk.
    """
    pairs = []
    if files:
        for f in files:
            schema = pair_for(f)
            if schema:
                pairs.append((f, schema))
    else:
        if (repo_root / "project-manifest.yaml").exists():
            pairs.append(("project-manifest.yaml", MANIFEST_SCHEMA))
        specs = repo_root / "specs"
        if specs.exists():
            for fc in sorted(specs.glob("*/feature-concerns.yaml")):
                pairs.append((str(fc.relative_to(repo_root)), FEATURE_CONCERNS_SCHEMA))
    # de-dup, stable order
    seen, out = set(), []
    for p in pairs:
        if p[0] not in seen:
            seen.add(p[0])
            out.append(p)
    return out


def build_report(pairs, validate_fn) -> dict:
    """
    Pure given validate_fn(instance_path, schema_path) -> (status, detail) where
    status is 'pass' | 'fail' | 'unavailable' | 'missing'. 'unavailable' (no
    validator/parser) and 'missing' (schema absent) never count as failures.
    """
    checked = []
    failures = []
    unavailable = False
    for instance, schema in pairs:
        status, detail = validate_fn(instance, schema)
        checked.append({"instance": instance, "schema": schema, "status": status})
        if status == "fail":
            failures.append({"instance": instance, "detail": detail})
        if status == "unavailable":
            unavailable = True
    return {
        "checked": checked,
        "failures": failures,
        "unavailable": unavailable,
        "passes": not failures,
    }


def validate_instance(instance_path, schema_path, repo_root: Path):
    """I/O + validation. Returns (status, detail)."""
    try:
        import yaml
        import jsonschema
    except ImportError:
        return ("unavailable", "jsonschema/pyyaml not installed")
    sp = repo_root / schema_path
    ip = repo_root / instance_path
    if not sp.exists():
        return ("missing", f"schema not found: {schema_path}")
    if not ip.exists():
        return ("missing", f"instance not found: {instance_path}")
    try:
        schema = json.loads(sp.read_text(encoding="utf-8"))
        instance = yaml.safe_load(ip.read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError) as exc:
        return ("fail", f"could not parse: {exc}")
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if not errors:
        return ("pass", "")
    parts = []
    for e in errors:
        loc = "/".join(str(x) for x in e.path) or "(root)"
        parts.append(f"{e.message} at {loc}")
    return ("fail", "; ".join(parts))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Schema-enforcement gate. Advisory unless --strict.")
    p.add_argument("files", nargs="*", help="Staged files to consider (default: discover all instances)")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)

    repo_root = Path(args.repo_root)
    pairs = recognized_instances(repo_root, args.files or None)
    report = build_report(pairs, lambda i, s: validate_instance(i, s, repo_root))

    if args.text:
        if not pairs:
            sys.stdout.write("schema: no manifest or feature-concerns instances to validate.\n")
        elif report["unavailable"]:
            sys.stdout.write("schema: validator unavailable; run under 'uv run --with jsonschema --with pyyaml'.\n")
        else:
            lines = [f"passes: {report['passes']}"]
            for c in report["checked"]:
                lines.append(f"  {c['status']:11} {c['instance']}")
            for f in report["failures"]:
                lines.append(f"  --- {f['instance']} ---")
                lines.append(f"  {f['detail']}")
            sys.stdout.write("\n".join(lines) + "\n")
    else:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")

    if args.strict and not report["passes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
