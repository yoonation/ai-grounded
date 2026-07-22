#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Construct-time brief generator: the writer's slice of the substrate.

C1 persists the feature's concern selection at
specs/NNN-feature/feature-concerns.yaml. Until now that selection routed
REVIEWERS only; the main session wrote code against the constitution slice
alone and met the substrate's rules for the first time as C3 findings. This
tool closes that gap on the prevention side: it reads the selection
(scope.selected plus scope.locked; excluded is ignored) and emits a compact
brief so violations are not written in the first place rather than caught
later by the review wave. concerns/* catalogs are expanded to their rules
(the writer acts on these directly); threats/*, compliance/*, and
design-patterns/* catalogs, which the selector also places in scope, are
named as surfaces the reviewers model rather than expanded, since attack
patterns are not coding rules.

Brief shape, per concern: mechanical (L1) rules first (the directly
writable-against class), then semantic (L2), then judgmental (L3) as names
only. Each rule line is the rule's one-line name with its severity; rules
with co-located examples get a pointer so the writer can lazily pull
good/anti-pattern material for the surface being implemented (pointers, not
copies; the rule folders stay the single source).

The brief is derived output: regenerate rather than hand-edit. It is
committed with the feature (like reviews/) so the audit trail records what
the writer was shown. A selected concern that resolves to no catalog on disk
is a hard error, the phantom-name failure class fails loudly.

Usage:
    python3 tooling/construct-brief/generate.py specs/NNN-feature [--text]
    (writes specs/NNN-feature/construct-brief.md unless --text)

Exit codes: 0 written/printed; 1 input error (missing feature dir,
feature-concerns.yaml absent or unreadable, unknown concern).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("construct-brief: pyyaml required (uv run --with pyyaml ...)", file=sys.stderr)
    raise

LAYER_ORDER = {"mechanical": 0, "semantic": 1, "judgmental": 2}
LAYER_LABEL = {
    "mechanical": "Mechanical (L1): write to these directly; SAST and reviewers will check them",
    "semantic": "Semantic (L2): design-level; reviewers verify with checklists",
    "judgmental": "Judgmental (L3): named for awareness; decided at review, not at the keyboard",
}


# Catalog families the concern-selector can legitimately place in scope.selected.
# concerns/* are directory catalogs of per-rule folders the writer acts on directly;
# threats/*, compliance/*, and design-patterns/* are single-file catalogs the
# reviewers reason about, surfaced by name only so the writer sees the surface
# without the brief expanding attack patterns as if they were coding rules.
def classify_ref(catalog_ref: str) -> tuple[str, str]:
    """Return (family, name) for a selected catalog ref. A bare id (no prefix)
    defaults to the concerns family for backward compatibility with the schema's
    documented bare-id form."""
    ref = catalog_ref.strip()
    for family in ("concerns", "threats", "compliance", "design-patterns"):
        if ref.startswith(family + "/"):
            return family, ref.split("/", 1)[1]
    return "concerns", ref


def load_selection(feature_dir: Path) -> list[str]:
    fc = feature_dir / "feature-concerns.yaml"
    if not fc.is_file():
        raise FileNotFoundError(
            f"{fc} not found; run the C1 concern selection before generating the brief")
    data = yaml.safe_load(fc.read_text(encoding="utf-8"))
    scope = (data or {}).get("scope") or {}
    refs = []
    for key in ("selected", "locked"):
        for entry in scope.get(key) or []:
            ref = entry.get("catalog") if isinstance(entry, dict) else entry
            if isinstance(ref, str) and ref.strip():
                refs.append(classify_ref(ref))
    # deterministic, de-duplicated, order-independent of the yaml
    return sorted(set(refs))


def load_catalog_name(path: Path) -> str:
    """Human-readable name of a single-file catalog (threats/compliance/
    design-patterns), from metadata.catalog_name, falling back to the stem."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return (data.get("metadata") or {}).get("catalog_name") or path.stem
    except (OSError, yaml.YAMLError):
        return path.stem


def load_rules(concern_path: Path) -> list[dict]:
    rules = []
    for rule_yaml in sorted(concern_path.glob("*/rule.yaml")):
        r = yaml.safe_load(rule_yaml.read_text(encoding="utf-8")) or {}
        rules.append({
            "id": r.get("id", rule_yaml.parent.name),
            "name": " ".join(str(r.get("name", "")).split()),
            "layer": r.get("layer", "judgmental"),
            "severity": r.get("severity", ""),
            "has_examples": (rule_yaml.parent / "examples").is_dir(),
            "rel": rule_yaml.parent,
        })
    rules.sort(key=lambda r: (LAYER_ORDER.get(r["layer"], 9), r["id"]))
    return rules


def render(feature_dir: Path, repo_root: Path) -> str:
    refs = load_selection(feature_dir)
    concerns_root = repo_root / "governance-commons" / "catalogs" / "concerns"
    lines = [
        "<!-- SPDX-License-Identifier: Apache-2.0 -->",
        "<!-- Copyright 2026 Myoung Hong -->",
        "<!--",
        "  DERIVED OUTPUT of tooling/construct-brief/generate.py from this feature's",
        "  feature-concerns.yaml and the substrate rule catalogs. Regenerate rather",
        "  than hand-edit:",
        f"      python3 tooling/construct-brief/generate.py {feature_dir.as_posix()}",
        "-->",
        "",
        f"# Construct-time brief: {feature_dir.name}",
        "",
        "Write to these rules; do not meet them for the first time as review",
        "findings. Mechanical rules are directly checkable and non-negotiable at",
        "the keyboard. Pull a rule's co-located examples/ when implementing the",
        "surface it governs.",
        "",
    ]
    if not refs:
        lines.append("_No catalogs selected for this feature (scope.selected and scope.locked are empty)._")
        return "\n".join(lines) + "\n"

    concern_refs = [name for fam, name in refs if fam == "concerns"]
    other_refs = [(fam, name) for fam, name in refs if fam != "concerns"]

    catalogs_root = repo_root / "governance-commons" / "catalogs"
    for name in concern_refs:
        cdir = concerns_root / name
        if not cdir.is_dir():
            raise FileNotFoundError(
                f"selected concern {name!r} resolves to no catalog at {cdir}; "
                f"fix feature-concerns.yaml (phantom names fail loudly)")
        rules = load_rules(cdir)
        lines.append(f"## concerns/{name}")
        lines.append("")
        current_layer = None
        for r in rules:
            if r["layer"] != current_layer:
                if current_layer is not None:
                    lines.append("")
                current_layer = r["layer"]
                lines.append(f"**{LAYER_LABEL.get(current_layer, current_layer)}**")
                lines.append("")
            if current_layer == "judgmental":
                lines.append(f"- `{r['id']}`")
            else:
                sev = f" [{r['severity']}]" if r["severity"] else ""
                ex = ""
                if r["has_examples"]:
                    ex = f" (examples: `{(r['rel'] / 'examples').relative_to(repo_root).as_posix()}/`)"
                lines.append(f"- `{r['id']}`{sev}: {r['name']}{ex}")
        lines.append("")

    if other_refs:
        lines.append("## Threat and compliance surfaces (modeled by reviewers, not expanded here)")
        lines.append("")
        lines.append("These catalogs are reasoned about by the threat-modeler and "
                     "security-reviewer at C1/C2/C3, not written to rule-by-rule. "
                     "Write defensively against these families; the brief names them "
                     "so the surface is visible without miscasting attack patterns as "
                     "coding rules.")
        lines.append("")
        for fam, name in other_refs:
            suffixes = [".yaml", ".yml"]
            fpath = next((catalogs_root / fam / (name + s) for s in suffixes
                          if (catalogs_root / fam / (name + s)).is_file()), None)
            if fpath is None:
                raise FileNotFoundError(
                    f"selected {fam} catalog {name!r} resolves to no file under "
                    f"{catalogs_root / fam}; fix feature-concerns.yaml "
                    f"(phantom names fail loudly)")
            lines.append(f"- `{fam}/{name}`: {load_catalog_name(fpath)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Generate the writer's construct-time substrate brief.")
    p.add_argument("feature_dir", help="specs/NNN-feature directory")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--text", action="store_true", help="print to stdout instead of writing the file")
    args = p.parse_args(argv)
    feature_dir = Path(args.feature_dir)
    repo_root = Path(args.repo_root)
    try:
        out = render(feature_dir, repo_root)
    except (FileNotFoundError, OSError, yaml.YAMLError) as exc:
        print(f"construct-brief: {exc}", file=sys.stderr)
        return 1
    if args.text:
        sys.stdout.write(out)
    else:
        target = feature_dir / "construct-brief.md"
        target.write_text(out, encoding="utf-8")
        print(f"construct-brief: wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
