<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.strategy-adr strategy ADR (good pattern)

Substrate-original good-pattern example for feature-flags.strategy-adr. A recorded ADR decides
every required sub-decision and draws the configuration-management and
secrets-management boundaries rather than restating them.

## Excerpt: a feature-flags strategy ADR

```markdown
# ADR-021: Feature-flags strategy

Status: Accepted   Owner: platform-team   Review: annual

- Management approach: OpenFeature SDK with a single provider; server-side
  evaluation only.
- Taxonomy: release, experiment, operational kill-switch, permission. Per-type
  lifecycle and expiry defined; release flags expire in 90 days.
- Fail-static convention: every flag defaults to its safe path; permission and
  kill-switch flags fail closed.
- Context schema: targetingKey plus a fixed allow-list of non-secret
  attributes; no secrets, PII minimized to targeting inputs.
- Rollout: provider targeting with deterministic bucketing on a stable key.
- Kill-switch inventory: maintained in flags.yaml, exercised in game-days.
- Boundaries: static config and its validation owned by
  configuration-management; secret values owned by secrets-management.
```

Each sub-decision is stated and resolved, the boundaries are referenced rather
than absorbed, and the record names an owner and a cadence.
