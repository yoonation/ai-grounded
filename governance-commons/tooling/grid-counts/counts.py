#!/usr/bin/env python3
"""Deterministic count tool and drift check for docs/MASTER-GRID.md section 4.

MASTER-GRID's "what exists today" counts were hand-authored and drifted from the
substrate. This tool recomputes every count directly from the filesystem, using
the same paths the assembler validator uses, and either emits the section-4 block
(default) or checks the committed MASTER-GRID against the computed truth
(--check). Run it whenever the substrate grows so the index cannot silently drift
again; the 90-master-grid-counts pre-commit gate runs --check automatically.

Rule layers map to grid levels: mechanical -> L1, semantic -> L2, judgmental -> L3.

Modes:
  (default)        emit the regenerated section-4 block on stdout
  --check          compare MASTER-GRID's counts to computed truth, report drift
  --check --strict exit non-zero if MASTER-GRID has drifted

Exit codes:
  0  emit succeeded, or --check found no drift (or drift without --strict)
  1  internal inconsistency (per-concern sums do not reconcile), or
     --check --strict found drift, or MASTER-GRID could not be parsed
"""
import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # governance-commons/
CONCERNS = ROOT / "catalogs" / "concerns"
PROFILES = ROOT / "profiles"
THREATS = ROOT / "catalogs" / "threats"
MAPPINGS = ROOT / "mappings"
DESIGNPATTERNS = ROOT / "catalogs" / "design-patterns"
MASTER_GRID = ROOT / "docs" / "MASTER-GRID.md"


def rule_layer(rule_path):
    for line in rule_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("layer:"):
            return line.split(":", 1)[1].strip()
    return None


def compute():
    per_concern = collections.defaultdict(lambda: collections.Counter())
    for concern_yaml in sorted(CONCERNS.glob("*/concern.yaml")):
        per_concern[concern_yaml.parent.name]  # ensure 0-rule concerns appear
    for rule in sorted(CONCERNS.glob("*/*/rule.yaml")):
        per_concern[rule.relative_to(CONCERNS).parts[0]][rule_layer(rule)] += 1

    tot = collections.Counter()
    for c in per_concern.values():
        tot.update(c)

    return {
        "per_concern": per_concern,
        "n_concerns": len(per_concern),
        "n_rules": sum(sum(c.values()) for c in per_concern.values()),
        "l1": tot["mechanical"],
        "l2": tot["semantic"],
        "l3": tot["judgmental"],
        "n_profiles": len(list(PROFILES.glob("*.oscal.yaml"))),
        "n_threats": len(list(THREATS.glob("*.yaml"))),
        "n_mappings": len(list(MAPPINGS.glob("*.oscal.yaml"))),
        "n_patterns": len(list(DESIGNPATTERNS.glob("*.yaml"))),
        "n_test_templates": len(list(CONCERNS.glob("*/*/test-template*.md"))),
        "n_decisions": len(list(ROOT.rglob("decision.md"))) + len(list(ROOT.rglob("*.madr.md"))),
    }


def self_consistent(d):
    """The per-concern sums must reconcile to the layer totals and rule count.
    A failure here is a tool bug, not doc drift."""
    pc = d["per_concern"]
    return (
        d["l1"] + d["l2"] + d["l3"] == d["n_rules"]
        and sum(c["mechanical"] for c in pc.values()) == d["l1"]
        and sum(c["semantic"] for c in pc.values()) == d["l2"]
        and sum(c["judgmental"] for c in pc.values()) == d["l3"]
    )


def render_section4(d):
    out = ["Substrate-wide totals (regenerate with tooling/grid-counts/counts.py):", ""]
    out.append(f"- {d['n_concerns']} concern catalogs (stable).")
    out.append(f"- L1 machine-decidable: {d['l1']} mechanical rules, each naming a")
    out.append("  capability gate the toolchain resolves to an OSS tool.")
    out.append(f"- L2 review-decidable: {d['l2']} review checklists plus {d['n_test_templates']} test templates.")
    out.append(f"- L3 decision-with-recorded-rationale: {d['l3']} MADR decision frameworks")
    out.append("  homed in concerns.")
    out.append(f"- {d['n_threats']} threat spines, {d['n_profiles']} profiles, {d['n_mappings']} threat/compliance mappings.")
    out.append(f"- {d['n_patterns']} design-pattern catalogs.")
    out.append(f"- {d['n_decisions']} decision-framework files total (concern-homed L3 plus any top-level frameworks).")
    out.append("")
    out.append("Per-concern shape (L1 / L2 / L3 primary-home counts):")
    out.append("")
    out.append("| Concern | L1 | L2 | L3 |")
    out.append("|---|---|---|---|")
    for c in sorted(d["per_concern"]):
        t = d["per_concern"][c]
        out.append(f"| {c} | {t['mechanical']} | {t['semantic']} | {t['judgmental']} |")
    out.append(f"| TOTAL | {d['l1']} | {d['l2']} | {d['l3']} |")
    return "\n".join(out) + "\n"


def check_against_grid(d, grid_path):
    """Return a list of drift findings comparing MASTER-GRID to computed truth.
    An empty list means the index matches the substrate."""
    findings = []
    try:
        text = grid_path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"cannot read {grid_path}: {e}"]
    flat = re.sub(r"\s+", " ", text)  # collapse wraps for scalar phrases

    def scalar(label, pattern, expected):
        m = re.search(pattern, flat)
        if not m:
            findings.append(f"{label}: expected phrasing not found in MASTER-GRID (cannot verify {expected})")
        elif int(m.group(1)) != expected:
            findings.append(f"{label}: MASTER-GRID says {m.group(1)}, actual {expected}")

    scalar("L1 mechanical", r"(\d+) mechanical rules", d["l1"])
    scalar("L2 checklists", r"(\d+) review checklists", d["l2"])
    scalar("test templates", r"(\d+) test templates", d["n_test_templates"])
    scalar("L3 frameworks", r"(\d+) MADR decision frameworks", d["l3"])
    scalar("threat spines", r"(\d+) threat spines", d["n_threats"])
    scalar("profiles", r"(\d+) profiles", d["n_profiles"])
    scalar("mappings", r"(\d+) threat/ ?compliance mappings", d["n_mappings"])
    scalar("design-pattern catalogs", r"(\d+) design-pattern catalogs", d["n_patterns"])
    scalar("concern catalogs", r"(\d+) concern catalogs", d["n_concerns"])

    # column-sum reference "(62 / 131 / 33)"
    m = re.search(r"\((\d+) / (\d+) / (\d+)\)", flat)
    if not m:
        findings.append("column-sum reference (L1 / L2 / L3) not found in MASTER-GRID")
    elif tuple(int(m.group(i)) for i in (1, 2, 3)) != (d["l1"], d["l2"], d["l3"]):
        findings.append(f"column-sum reference: MASTER-GRID says {m.group(0)}, actual ({d['l1']} / {d['l2']} / {d['l3']})")

    # per-concern table rows
    row = re.compile(r"^\|\s*([a-z][a-z0-9-]*)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", re.M)
    seen = set()
    for m in row.finditer(text):
        concern, l1, l2, l3 = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        if concern not in d["per_concern"]:
            findings.append(f"table row '{concern}': concern not found in substrate")
            continue
        seen.add(concern)
        t = d["per_concern"][concern]
        actual = (t["mechanical"], t["semantic"], t["judgmental"])
        if (l1, l2, l3) != actual:
            findings.append(f"table row '{concern}': MASTER-GRID {l1}/{l2}/{l3}, actual {actual[0]}/{actual[1]}/{actual[2]}")
    missing = set(d["per_concern"]) - seen
    for c in sorted(missing):
        findings.append(f"table row '{c}': present in substrate but missing from MASTER-GRID table")

    return findings


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Deterministic MASTER-GRID counts. Default emits the section-4 "
                    "block; --check compares the committed doc to computed truth "
                    "(advisory unless --strict).")
    p.add_argument("--check", action="store_true", help="compare MASTER-GRID to computed counts")
    p.add_argument("--strict", action="store_true", help="with --check, exit non-zero on drift")
    p.add_argument("--master-grid", default=str(MASTER_GRID), help="path to MASTER-GRID.md")
    args = p.parse_args(argv)

    d = compute()

    if not self_consistent(d):
        sys.stderr.write(
            f"INCONSISTENT: layers {d['l1']}+{d['l2']}+{d['l3']} do not reconcile to "
            f"{d['n_rules']} rules; this is a tool bug, not doc drift.\n")
        return 1

    if args.check:
        findings = check_against_grid(d, Path(args.master_grid))
        if not findings:
            sys.stdout.write("master-grid-counts: MASTER-GRID matches the substrate.\n")
            return 0
        sys.stdout.write("master-grid-counts: DRIFT between MASTER-GRID and the substrate:\n")
        for f in findings:
            sys.stdout.write(f"  - {f}\n")
        sys.stdout.write("  regenerate section 4 with: tooling/grid-counts/counts.py\n")
        return 1 if args.strict else 0

    sys.stdout.write(render_section4(d))
    sys.stderr.write(f"\nOK: {d['n_rules']} rules reconcile ({d['l1']} + {d['l2']} + {d['l3']}).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
