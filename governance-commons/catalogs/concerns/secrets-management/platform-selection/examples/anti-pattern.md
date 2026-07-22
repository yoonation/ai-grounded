<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.platform-selection platform selection (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.platform-selection.
These patterns illustrate ADR violations and should NOT be used.

## Anti-pattern A: No ADR exists

```text
# Project state: 23 secrets in production. Half are in
# Kubernetes Secret objects, half are in environment
# variables populated by Terraform. No documented
# decision was ever made.
```

Why this violates secrets-management.platform-selection: the substrate's L3 rule
requires explicit, documented decisions for foundational
choices. The absence of an ADR is the most common
violation, not poor ADR quality.

## Anti-pattern B: ADR is a single sentence

```markdown
# ADR-007: Secrets

We use AWS Secrets Manager.
```

Why this violates secrets-management.platform-selection: the ADR has no context,
no drivers, no options considered, no consequences, no
review schedule. A future engineer cannot understand why
the choice was made or under what conditions it should be
revisited.

## Anti-pattern C: Decision asserted without reasoning

```markdown
# ADR-007: Secrets Management Platform Selection

Status: Accepted

## Context
We need to manage secrets.

## Decision
We will use HashiCorp Vault.

## Consequences
Vault will handle our secrets.
```

Why this violates secrets-management.platform-selection: the ADR has the right
sections but content is tautological. "We need to manage
secrets, so we will use a secrets manager" is not
reasoning. There are no drivers, no consideration of
alternatives, no acknowledgment of operational burden.

## Anti-pattern D: Substrate framework copy-pasted verbatim

```markdown
# ADR-007: Secrets Management Platform

[entire content is the substrate's secrets-management-
platform.madr.md framework copied without adaptation]
```

Why this violates secrets-management.platform-selection: the framework is the
substrate's analysis; the ADR should be the consumer's
adapted analysis. Substrate text without application-
specific values does not document a decision; it
documents the framework.

## Anti-pattern E: Drivers listed but not connected to outcome

```markdown
# Decision Drivers
D1: Single-cloud AWS
D2: Kubernetes-based
D3: Small team

# Decision Outcome
We chose HashiCorp Vault self-managed.
```

Why this violates secrets-management.platform-selection: the drivers (Kubernetes,
small team) would naturally suggest Option 4 (operator
pattern) and probably exclude Option 2 (Vault self-
managed, which needs operational capacity). The outcome
does not connect to the drivers. Either the drivers are
wrong or the outcome is wrong.

## Anti-pattern F: Deviation from substrate preference unjustified

```markdown
# Substrate Alignment
We chose Option 2. The substrate prefers Option 4 for
our context, but we wanted Option 2.
```

Why this violates secrets-management.platform-selection: deviation requires
substantive reasoning, not preference. The substrate's
preferred option is the default; deviation is legitimate
but must connect to the project's specific context.

## Anti-pattern G: No review schedule

```markdown
# Decision Review Schedule

[section omitted entirely]
```

Why this violates secrets-management.platform-selection: decisions decay. The
ADR should state when it is revisited and what triggers
earlier review. Without a schedule, the ADR becomes a
historical artifact that does not protect against drift.

## Anti-pattern H: Consequences are positive-only

```markdown
# Consequences

Positive: Vault handles secrets management. Audit logs
provided. Encryption at rest configured. Highly scalable.
Industry standard.
```

Why this violates secrets-management.platform-selection (in spirit): no choice
has only positive consequences. Vault has operational
burden, license cost considerations for Enterprise
features, and a learning curve. An ADR that does not
acknowledge negative consequences has not done the
analysis. Reviewers should ask for the hard parts.

## Cross-reference

- Good patterns: examples/secrets-management/platform-selection-good.md
- Substrate rule: secrets-management.platform-selection
- Decision framework: decision-frameworks/secrets-management-platform.madr.md
- Review checklist: checklist.md
