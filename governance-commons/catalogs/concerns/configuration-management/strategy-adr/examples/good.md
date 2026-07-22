<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.strategy-adr strategy ADR (good pattern)

Substrate-original good-pattern example for configuration-management.strategy-adr. A recorded ADR
decides every required sub-decision and draws the secrets and feature-flags
boundaries.

## Excerpt: a configuration-management strategy ADR

```markdown
# ADR-014: Configuration-management strategy

Status: Accepted   Owner: platform-team   Review: annual

- Source model: base config file for structured defaults + environment
  variables for deploy-varying values.
- Precedence: defaults < base file < env-specific file < env vars < overrides.
- Validation: startup gate (configuration-management.startup-validation), run in every environment.
- Parity: shared required-keys.yaml enforced in CI.
- Secrets boundary: references only; handling owned by secrets-management.
- Static vs dynamic: static by default; runtime-changeable toggles are
  feature-flags (deferred to the feature-flags concern).
- Change control: configuration PRs reviewed proportionate to blast radius.
```

Each decision is stated and resolved; the boundaries are drawn rather than
blurred; the record has an owner and a cadence.
