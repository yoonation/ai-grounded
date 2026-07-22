<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# skill-drift

Deterministic checker that every rendered `.claude/skills/*/SKILL.md` matches
its canonical source under `.specify/extensions/*/commands/`. Compares the
body after the first markdown heading, which is invariant across the render
transforms, so the check is spec-kit-version independent.

Enforced at commit by `.githooks/pre-commit.d/45-skill-drift` (report-only;
`SKILL_DRIFT_STRICT=1` blocks). Preset-owned command pairs (specify, clarify,
plan, implement) are covered by bootstrap's marker checks instead; their
render transforms are content-modifying and version-dependent.

Run directly:

    python3 tooling/skill-drift/check.py --repo-root . --text
