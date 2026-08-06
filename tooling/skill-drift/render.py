#!/usr/bin/env python3
"""Render framework extension commands as Codex native skills."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PLACEHOLDER = re.compile(r"__SPECKIT_COMMAND_([A-Z0-9_]+)__")
DESCRIPTION = re.compile(r'^description:\s*["\']?(.*?)["\']?\s*$', re.M)
AGENT_MENTION = re.compile(r"@([a-z][a-z-]+)")


def skill_dir_for(command_file: Path) -> str:
    return command_file.name[: -len(".md")].replace(".", "-")


def command_name(token: str) -> str:
    return "speckit-" + token.lower().replace("_", "-")


def parse_body(source: str) -> tuple[str, str]:
    body = source
    if body.startswith("---\n"):
        _, frontmatter, body = body.split("---\n", 2)
    else:
        frontmatter = ""
    description = DESCRIPTION.search(frontmatter)
    return (description.group(1) if description else "AI Grounded extension command", body.lstrip())


def codex_body(source: str) -> tuple[str, str]:
    description, body = parse_body(source)
    body = PLACEHOLDER.sub(lambda match: "$" + command_name(match.group(1)), body)
    body = re.sub(r"(?<![$\w])-?/(speckit-[a-z0-9-]+)", r"$\1", body)
    body = AGENT_MENTION.sub(lambda match: f"the `{match.group(1)}` Codex agent", body)
    return description, body


def render(command_file: Path) -> str:
    description, body = codex_body(command_file.read_text(encoding="utf-8"))
    name = skill_dir_for(command_file)
    isolation = ""
    if command_file.parent.parent.name == "workflow":
        isolation = '''## Codex reviewer isolation

Before spawning a review wave, inspect the parent session's active sandbox and
permission override. If it supersedes a child role's `read-only` default, state
the warning prominently in the saved dispatch artifact, then continue with the
review as advisory isolation. The main session remains the only writer of
artifacts and `events.jsonl`.

'''
    return f'''---
name: "{name}"
description: "{description}"
argument-hint: "Optional: feature directory path (defaults to active feature)"
compatibility: "Requires AI Grounded and local Codex"
metadata:
  author: "ai-grounded-framework"
  source: "{command_file.parent.parent.name}:commands/{command_file.name}"
user-invocable: true
disable-model-invocation: false
---

## User Input

```text
$ARGUMENTS
```

{isolation}
{body}'''


def command_files(root: Path):
    return sorted((root / ".specify" / "extensions").glob("*/commands/*.md"))


def output_path(root: Path, command_file: Path) -> Path:
    return root / ".agents" / "skills" / skill_dir_for(command_file) / "SKILL.md"


def write(root: Path) -> None:
    for command_file in command_files(root):
        output = output_path(root, command_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render(command_file), encoding="utf-8")


def check(root: Path) -> list[Path]:
    return [output_path(root, command) for command in command_files(root)
            if not output_path(root, command).exists()
            or output_path(root, command).read_text(encoding="utf-8") != render(command)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    drifted = check(root)
    if args.check:
        for path in drifted:
            print(f"DRIFT: {path.relative_to(root)}")
        return 1 if drifted else 0
    write(root)
    print(f"codex-skill-render: rendered {len(command_files(root))} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
