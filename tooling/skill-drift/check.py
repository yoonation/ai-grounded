#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Skill-drift checker: rendered SKILL.md files must match their canonical
extension command sources.

The framework's rendered skills under .claude/skills/ are derived output of
the command files under .specify/extensions/<ext>/commands/. Hand-editing a
rendered skill is the named anti-pattern: the edit is silently lost on the
next render and the canon stops being canon. This tool compares each
extension command/skill pair on the body after the first markdown heading
(frontmatter, provenance header, and the injected User Input block all sit
above the first heading), normalized for the renderer's three documented
in-body transforms: em/en dashes become hyphens, __SPECKIT_COMMAND_X__
placeholders become the rendered /speckit-x command name, and trailing
whitespace is stripped. Any transform beyond those three surfaces as drift,
which is the correct failure mode: a new upstream render behavior gets
reviewed and added here deliberately instead of passing silently.

Preset-owned command pairs (speckit.specify/clarify/plan/implement) are NOT
covered here: their render includes version-dependent content transforms
({ARGS} substitution, template-path rewriting), so a textual diff would be
brittle. Bootstrap's marker checks cover those four.

Advisory by itself (exit 0) unless --strict; the 45-skill-drift gate owns
strictness. Run:
    python3 tooling/skill-drift/check.py --repo-root . --text
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_H1 = re.compile(r"^# ", re.M)
_PLACEHOLDER = re.compile(r"__SPECKIT_COMMAND_([A-Z0-9_]+)__")
_SKILL_COMMAND = re.compile(r"(?<![\w-])[$/]?(speckit-[a-z0-9-]+)")
_CODEX_AGENT = re.compile(r"the `([a-z][a-z-]+)` Codex agent")


def normalize(text: str) -> str:
    """Apply the renderer's documented in-body transforms so canon and render
    compare equal when only those transforms differ."""
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = _PLACEHOLDER.sub(
        lambda m: "speckit-" + m.group(1).lower().replace("_", "-"), text)
    text = _SKILL_COMMAND.sub(lambda m: m.group(1), text)
    text = _CODEX_AGENT.sub(lambda m: "@" + m.group(1), text)
    return text


def body_after_first_heading(text: str) -> str | None:
    """Content from the first markdown H1 to the end, trailing space stripped.
    None when the file has no H1 (nothing comparable)."""
    m = _H1.search(text)
    if not m:
        return None
    return normalize(text[m.start():]).rstrip()


def skill_dir_for(command_file: Path) -> str:
    """speckit.workflow.post-impl.md -> speckit-workflow-post-impl"""
    return command_file.name[: -len(".md")].replace(".", "-")


def discover_pairs(repo_root: Path):
    """Every extension command file paired with Claude and Codex renders."""
    pairs = []
    ext_root = repo_root / ".specify" / "extensions"
    if not ext_root.is_dir():
        return pairs
    for cmd in sorted(ext_root.glob("*/commands/*.md")):
        for target in (".claude/skills", ".agents/skills"):
            skill = repo_root / target / skill_dir_for(cmd) / "SKILL.md"
            pairs.append((cmd, skill))
    return pairs


def compare_pair(cmd: Path, skill: Path) -> dict:
    rel_cmd, rel_skill = str(cmd), str(skill)
    if not skill.exists():
        return {"command": rel_cmd, "skill": rel_skill, "status": "missing-skill"}
    cb = body_after_first_heading(cmd.read_text(encoding="utf-8", errors="replace"))
    sb = body_after_first_heading(skill.read_text(encoding="utf-8", errors="replace"))
    if cb is None or sb is None:
        return {"command": rel_cmd, "skill": rel_skill, "status": "no-heading"}
    if cb == sb:
        return {"command": rel_cmd, "skill": rel_skill, "status": "parity"}
    first = next((i + 1 for i, (a, b) in enumerate(
        zip(cb.splitlines(), sb.splitlines())) if a != b),
        min(len(cb.splitlines()), len(sb.splitlines())) + 1)
    return {"command": rel_cmd, "skill": rel_skill, "status": "drift",
            "first_divergent_body_line": first}


def build_report(repo_root: Path) -> dict:
    results = [compare_pair(c, s) for c, s in discover_pairs(repo_root)]
    bad = [r for r in results if r["status"] != "parity"]
    return {"checked": len(results), "results": results,
            "drifted": bad, "passes": not bad}


def render(report) -> str:
    lines = [f"skill-drift: {report['checked']} extension pair(s) checked; "
             f"passes: {report['passes']}"]
    for r in report["drifted"]:
        if r["status"] == "missing-skill":
            lines.append(f"  MISSING: {r['command']} has no rendered skill at {r['skill']}")
        elif r["status"] == "no-heading":
            lines.append(f"  UNCOMPARABLE: {r['command']} or {r['skill']} has no markdown heading")
        else:
            lines.append(f"  DRIFT: {r['skill']} diverges from canon {r['command']}"
                         f" (first divergent body line {r['first_divergent_body_line']})")
    if report["drifted"]:
        lines.append("  Rendered skills are derived output: edit the extension command"
                     " (canon), then sync the skill; never hand-edit the render.")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Rendered-skill drift checker. Advisory unless --strict.")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args(argv)
    report = build_report(Path(args.repo_root))
    sys.stdout.write(render(report) if args.text else json.dumps(report, indent=2) + "\n")
    return 1 if (args.strict and not report["passes"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
