<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.organization-strategy organization strategy (good pattern)

Substrate-original illustration of a filled-in consumer ADR that
satisfies code-organization.organization-strategy: it names a style, a boundary policy, an
enforced dependency rule, a home for cross-cutting concerns, and a
topology, and wires the rule into CI.

## /docs/decisions/ADR-014-code-organization-strategy.md (excerpt)

```markdown
# ADR-014: Code-organization strategy

Status: accepted

## Decision
- Architectural style: modular monolith, dependency rule expressed in
  hexagonal terms (domain core free of infrastructure).
- Module-boundary policy: organize by domain bounded context
  (catalog, ordering, billing, identity). New files are placed by the
  context they serve.
- Dependency rule: domain -> nothing volatile; adapters -> domain.
  Enforced by an import-linter layers contract in CI (required check).
- Cross-cutting concerns: logging and error types as domain-owned
  abstractions; their implementations injected at the composition root
  in main.py. Request logging and auth live in HTTP middleware.
- Repository topology: single repository, single deployable, until an
  independent deployment cadence justifies a split.

## Drivers
Team of 6, one deployable, rich ordering/billing rules, fast
infrastructure-free domain tests required. Reviewed annually.
```

```ini
# setup.cfg (the enforced contract that matches the ADR)
[importlinter]
root_package = shop

[importlinter:contract:layers]
name = domain is the inner layer
type = layers
layers =
    shop.web
    shop.application
    shop.domain
```

Why this passes: every required section is present and substantive, the
dependency rule is a checkable direction enforced in CI, and the contract
matches the ADR (code-organization.organization-strategy review questions 1 through 6).
