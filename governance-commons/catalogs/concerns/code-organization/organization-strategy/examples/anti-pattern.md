<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.organization-strategy organization strategy (anti-pattern)

Substrate-original illustration. There is no documented strategy. Folders
are named by technical kind, with no rule about what may depend on what,
so structure accretes by accident and the L2 rules have nothing to check
against.

## Repository layout with no recorded decision

```
src/
    controllers/      # all HTTP controllers, every feature mixed
    services/         # all services, every feature mixed
    models/           # all ORM models
    utils/            # grab-bag (see code-organization.module-boundary-cohesion anti-pattern)
```

```
# No /docs/decisions/ADR-*-code-organization-strategy.md exists.
# No import-linter / ArchUnit / dependency-cruiser contract exists.
# A "service" freely imports a "controller"; a "model" imports a
# "service"; dependencies point in every direction.
```

Why this is a finding: package-by-layer scatters each feature across
controllers, services, and models, maximizing change-coupling; no
dependency rule means there is no intended direction for code-organization.dependency-direction-layering
to enforce; and the absent ADR means code-organization.organization-strategy is unsatisfied. Each
contributor organizes by personal habit and newcomers cannot predict
where anything lives.

Remediation: author the strategy ADR (retrospectively documenting the
effective structure if one exists), choose a target organization (the
good-pattern modular-monolith-by-domain, for instance), encode the
dependency rule as an enforced contract to stop further drift, and
converge incrementally rather than in one high-risk reorganization.
