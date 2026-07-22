---
description: Code style and formatting standards
globs: ["**/*.py", "**/*.tf", "**/*.sh", "**/*.yaml", "**/*.json"]
---

# Code Style

## General
- Prefer readability over cleverness
- Use descriptive names — no single-letter variables except loop counters
- Keep functions under 50 lines — extract if longer
- One concept per function (single responsibility)
- Use early returns to reduce nesting
- Add the license header at file creation: every source and doc file begins
  with an `SPDX-License-Identifier: Apache-2.0` line and a copyright line, in
  the file's comment syntax. Verbatim third-party or standard texts (`LICENSE`,
  `NOTICE`, `DCO`, `CODE_OF_CONDUCT.md`, `THIRD-PARTY-LICENSES/`) are the
  exception and keep their upstream text.

## Python
- Type hints on all function signatures
- Docstrings on public functions (Google style)
- f-strings over .format() or %
- Use pathlib over os.path
- Use uv for dependency management

## Terraform (HCL)
- Run terraform fmt before committing
- Variables must have description and type
- Use validation blocks on variables where possible
- Group resource arguments: required first, optional second, tags last

## Shell
- Start every script with a shebang (`#!/usr/bin/env bash`, or `#!/bin/sh` for POSIX-portable hooks)
- Use set -euo pipefail for strict mode
- Quote all variable expansions: "$VAR" not $VAR
- Use functions for any logic repeated more than once

## YAML
- 2-space indentation
- No trailing whitespace
- Use anchors and aliases to avoid repetition
