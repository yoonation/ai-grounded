<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Security Policy

## Reporting a vulnerability

Please report suspected security vulnerabilities **privately**. Do not open a
public issue for a suspected vulnerability.

- Use GitHub's private vulnerability reporting: open the repository's
  **Security** tab and choose **Report a vulnerability**.
- Include a description, reproduction steps, the affected files or components,
  and the impact you observed.

Expect an acknowledgement within a few days and a decision after triage.
Coordinated disclosure is appreciated: please allow a reasonable window for a
fix to ship before any public disclosure.

## Scope

AI Grounded is a development template and governance substrate. The most
relevant security surfaces are:

- The pre-commit gate chain and hooks under `.githooks/` and `.claude/hooks/`.
- The Python tooling under `tooling/`.
- The Cedar policies and threat/compliance catalogs under `governance-commons/`.

Example credentials under `governance-commons/**/examples/` are intentional,
non-functional demonstration data and are **not** vulnerabilities.

## Supported versions

The latest release on `main` is supported. This is a community-maintained
project provided under Apache-2.0 with no warranty; see `LICENSE`.
