<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.vetting-policy vetting policy (anti-patterns)

Substrate-original anti-pattern examples for dependency-management.vetting-policy.
These patterns illustrate ADR violations and should NOT be used.

## Anti-pattern A: No ADR exists

```text
# Project state: 80+ direct dependencies across 3
# ecosystems. No documented vetting policy. Dependency
# additions happen via PR with whatever review the
# reviewer feels like applying at the time.
```

Why this violates dependency-management.vetting-policy: the substrate's L3 rule
requires an explicit, documented vetting policy. Absence
of an ADR is the most common violation. Without the
ADR, every reviewer applies their own implicit
criteria, and the team has no shared decision
framework.

## Anti-pattern B: Vague criteria

```markdown
# ADR-004: Dependency Vetting

We will only accept dependencies that are:
- Well maintained
- Popular
- Have good security
```

Why this violates dependency-management.vetting-policy: "well maintained",
"popular", and "good security" are not falsifiable
criteria. Two reviewers will disagree on whether a
dependency meets them. Substrate-recommended pattern:
concrete thresholds (Scorecard >= 6.0, last release
within 12 months, no open critical CVEs).

## Anti-pattern C: No intake SLA

```markdown
# Intake Process

New dependencies are reviewed by the platform team.
```

Why this violates dependency-management.vetting-policy (operational property):
no SLA means review can take any duration. Engineers
under deadline pressure will bypass the process.
Substrate-recommended pattern: named SLA (5 business
days, 10 business days, etc.) with named escalation
path.

## Anti-pattern D: Substrate framework copy-pasted verbatim

```markdown
# ADR-004: Dependency Vetting Policy

[entire content is the substrate's
dependency-vetting-policy.madr.md framework copied
without adaptation to the project's context]
```

Why this violates dependency-management.vetting-policy: the framework is the
substrate's analysis; the ADR should be the consumer's
adapted analysis with the project's specific drivers,
chosen option, and concrete criteria. Substrate text
without adaptation does not document a decision; it
documents the framework.

## Anti-pattern E: No review schedule

```markdown
# ADR-004: Dependency Vetting Policy

[Decision Review Schedule section omitted entirely]
```

Why this violates dependency-management.vetting-policy: vetting policies decay
as the ecosystem and project change. Without a review
schedule, the ADR becomes a historical artifact that
does not reflect current practice. Substrate-recommended
pattern: annual review with named triggers for earlier
revisit (major incident, regulatory change, team
growth, substrate version increment).

## Anti-pattern F: Consequences are positive-only

```markdown
# Consequences

Positive: dependencies are vetted. Supply-chain risk
is reduced. Audit trail exists. Compliance posture
improved.
```

Why this violates dependency-management.vetting-policy (in spirit): every
vetting policy has negative consequences (operational
overhead, intake friction, reviewer burden, false
rejects of legitimate dependencies). An ADR that
acknowledges only positives has not done the analysis.
Reviewers should ask for the hard parts: what does this
policy COST?

## Anti-pattern G: Follow-up work unowned

```markdown
# Follow-up Work

- Tooling will be built to automate criteria checks
- The allowlist will be created
- Training will be provided to engineers
- A dashboard will be created
```

Why this violates dependency-management.vetting-policy (operational property):
passive voice without ownership produces no action.
"Will be built" without a named owner and a deadline
is wishful thinking. Substrate-recommended pattern:
follow-up items each have an owner and a target date,
tracked in the team's normal work system.

## Anti-pattern H: Criteria do not connect to drivers

```markdown
# Decision Drivers

D1: We want strong supply-chain assurance.
D2: We have many dependencies.
D3: We have a small team.

# Concrete Criteria

A direct dependency may be added if:
1. The team lead approves it.
```

Why this violates dependency-management.vetting-policy: the drivers point to
needing automation and falsifiable criteria (because
of D2: many dependencies and D3: small team); the
chosen criterion (team lead approval) does not address
either driver. Either the drivers are wrong or the
criteria are wrong. Substrate-recommended pattern: the
criteria are traceable to the drivers they address.

## Cross-reference

- Good patterns: examples/dependency-management/vetting-policy-good.md
- Substrate rule: dependency-management.vetting-policy
- Decision framework: decision-frameworks/dependency-vetting-policy.madr.md
- Review checklist: checklist.md
