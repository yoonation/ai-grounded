<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.strategy-adr strategy ADR (anti-pattern)

Substrate-original anti-pattern example for feature-flags.strategy-adr. No strategy is
recorded, so each team improvises; where a document exists it leaves key
sub-decisions open and blurs the configuration and secrets boundaries.

## Excerpt: a non-decision masquerading as a strategy

```markdown
# ADR-021: Feature flags

Status: Draft   Owner: (unassigned)   Review: (none)

- We will use feature flags where helpful.
- Defaults: TBD per flag by whoever adds it.
- Context: pass whatever the targeting needs, including user records and any
  tokens required to look them up.
- Lifecycle: teams should clean up old flags when they get a chance.
- Static vs dynamic and secrets: handled case by case.
```

Why this is flagged: the fail-static convention, taxonomy, lifecycle, and
context schema are all left open; the context guidance invites secrets and full
user records; and the configuration and secrets boundaries are deferred to
nobody. The remediation is to decide each sub-decision, name an owner and a
review cadence, and reference configuration-management and secrets-management
for what they own instead of waving at them.
