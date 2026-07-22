<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# construct-brief

Generates the writer's construct-time slice of the substrate:
`specs/NNN-feature/construct-brief.md`, derived from the feature's C1
concern selection (`feature-concerns.yaml`, scope.selected plus
scope.locked) and the substrate catalogs. `concerns/*` catalogs expand
to their rules: mechanical (L1) first with severity and an examples/
pointer, semantic (L2) next, judgmental (L3) as names only. `threats/*`,
`compliance/*`, and `design-patterns/*` catalogs, which the
concern-selector also legitimately places in scope, are named in a
separate surfaces section rather than expanded, because attack patterns
are modeled by the reviewers, not written to rule-by-rule.
Prevention-side counterpart to the
reviewer slicing: the same selection that routes the C2/C3 reviewers
now also briefs the writer, so substrate violations are not written in
the first place rather than caught as review findings.

Invoked by the `/speckit-implement` flow right after constitution
injection. The brief is derived output committed with the feature (the
audit trail records what the writer was shown); regenerate rather than
hand-edit. A selected concern with no catalog on disk fails loudly.

    uv run --with pyyaml --no-project python3 tooling/construct-brief/generate.py specs/NNN-feature
