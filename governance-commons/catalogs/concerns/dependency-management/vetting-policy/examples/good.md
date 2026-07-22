<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.vetting-policy vetting policy (good patterns)

Substrate-original good-pattern examples for dependency-management.vetting-policy.

The L3-001 examples are excerpts from well-formed ADRs that
satisfy the substrate's review checklist. Real consumer
ADRs will be longer; these excerpts illustrate the
qualities the substrate looks for.

## Good ADR excerpt A: Criteria-based gate for a production SaaS

```markdown
# ADR-004: Dependency Vetting Policy

Status: Accepted
Date: 2026-04-22
Deciders: platform-team, security-architect

## Context

Production SaaS. Ecosystems: npm (frontend),
pip (backend), Docker (images). 47 direct dependencies
across ecosystems. SOC 2 Type 2 in scope. 6-person
engineering team; no dedicated supply-chain reviewer.

## Decision Drivers

D1 (license posture): permissive only (MIT, Apache-2.0,
BSD, ISC, MPL-2.0); copyleft requires explicit
exemption.
D2 (operational capacity): low; no dedicated reviewer.
D3 (regulatory): SOC 2 Type 2.
D4 (transitive footprint): high acceptance; npm
transitive graph approaches 400.
D5 (ecosystem maturity): npm has highest incident rate;
pip mature; Docker base images well-vetted.
D6 (build-time cost): cannot tolerate multi-day intake
delays.
D7 (team size): 6 engineers.

## Decision Outcome

Option 2 (criteria-based gate).

## Concrete Criteria

A direct dependency may be added if it meets ALL of:
1. License is in the allow-list above.
2. OpenSSF Scorecard >= 6.0 (verified via
   `scorecard --repo=<URL>`).
3. Last release within 12 months OR maintained
   replacement identified.
4. No open critical CVEs without patch path.
5. Maintainer count >= 2 (per npm registry or
   GitHub contributors).
6. Transitive footprint <= 100 packages (npm) or 30
   (pip); over the threshold requires review.

Dependencies meeting all criteria auto-approve via
Renovate. Failing any criterion: PR requires review
by platform-team or security-architect.

## Intake Process

Reviewer: platform-team rota (one named reviewer per
week).
SLA: 5 business days for review.
Escalation: security-architect on review backlog or
SLA breach.

## Substrate Alignment

Substrate-preferred Option 2 for production projects.
No deviation.

## Consequences

Positive: most updates auto-approve; reviewer time
focuses on novel introductions; criteria are
falsifiable.

Negative: criteria definition is work; criteria must be
maintained; transitive footprint ceiling will require
exception handling for legitimate large-graph
dependencies.

Follow-up: tooling automation to check Scorecard in CI;
exemption-file format documented; quarterly review of
auto-approval rate.

## Decision Review Schedule

Annual (2027-04-22) or on: major incident, SOC 2
finding, substrate version increment past 0.5.0.
```

Why this satisfies dependency-management.vetting-policy: criteria are concrete
and falsifiable (Scorecard >= 6.0, not "good
maintenance"); intake process is named with SLA;
substrate alignment is explicit; consequences include
honest negatives.

## Good ADR excerpt B: Strict allowlist for regulated context

```markdown
# ADR-001: Dependency Vetting Policy

Status: Accepted
Date: 2026-03-01
Deciders: ciso, compliance-lead

## Context

Healthcare data processor; HIPAA + HITRUST scope. 14
direct dependencies. Compliance posture requires
documented vetting evidence per dependency.

## Decision Drivers

D1 (license): allow-list of 6 specific licenses.
D2 (operational capacity): dedicated supply-chain
reviewer (0.5 FTE).
D3 (regulatory): HIPAA + HITRUST.
D4 (transitive footprint): minimal (current ~40 total
including transitives).
D5 (ecosystem maturity): pip and Go only.
D6 (build cost): can tolerate days of intake delay.
D7 (team size): 12 engineers but only the supply-chain
reviewer adds dependencies.

## Decision Outcome

Option 1 (strict allowlist).

## Allowlist

Maintained at /security/dependency-allowlist.yaml.
Each entry includes:
- package name and version range
- rationale
- responsible engineer
- review date
- next review date

## Intake Process

New dependency requests filed as JIRA tickets. Reviewer
investigates Scorecard, advisory history, license,
maintainer health. Decision committed to allowlist with
evidence attached. SLA: 10 business days.

## Substrate Alignment

Substrate-acceptable Option 1 for regulated contexts
with operational capacity. Our context fits; no
deviation.

## Consequences

Positive: maximally auditable; HITRUST evidence is
the allowlist file; reviewer judgment captured in
intake tickets.

Negative: high operational cost; engineer frustration
on slow intake (mitigated by SLA + escalation);
reviewer single point of failure (mitigated by
backup reviewer named in inventory).

## Decision Review Schedule

Annual (2027-03-01) or on: regulatory change, team
capacity change, substrate version increment past
0.5.0.
```

Why this satisfies dependency-management.vetting-policy: strict allowlist
appropriate to regulated context; intake is named with
SLA; the allowlist itself is the audit evidence;
negative consequences honestly acknowledged.

## Good ADR excerpt C: Lightweight gate for small team

```markdown
# ADR-003: Dependency Vetting Policy

Status: Accepted
Date: 2026-04-10
Deciders: founder, lead-engineer

## Context

Early-stage product; 2 engineers; pre-revenue. Mostly
npm + Docker. No regulatory scope. Cannot afford
formal vetting process at this scale.

## Decision Drivers

D1 (license): permissive only; copyleft excluded.
D2 (operational capacity): minimal; both engineers
review every PR.
D3 (regulatory): none.
D4 (transitive footprint): tolerant.
D5 (ecosystem maturity): npm.
D6 (build cost): low tolerance.
D7 (team size): 2.

## Decision Outcome

Option 3 (lightweight gate).

## Intake Process

New direct dependencies surfaced in PR description.
Both engineers review with informal criteria:
- Is this dependency widely used? (>10K weekly
  downloads or 5K stars indicator)
- Does it have recent commits?
- Does the README make sense?
- Is the license permissive?

Decisions captured in PR comments. The PR comment IS
the vetting record at this scale.

## SLA

Both engineers review PRs same-day during business
hours; weekend PRs reviewed Monday.

## Substrate Alignment

Substrate-acceptable Option 3 for small teams without
regulatory scope. Our context fits.

We acknowledge this option will not satisfy compliance
review at later stage. The trigger for upgrading to
Option 2 (criteria-based) is: revenue >= [threshold],
team growth past 5 engineers, or compliance audit
requirement.

## Consequences

Positive: zero overhead beyond normal PR review;
captures both engineers' judgment.

Negative: not auditable; reviewer consistency depends
on the two engineers; future migration to a stricter
option will require backfilling vetting records for
existing dependencies.

## Decision Review Schedule

Quarterly (next: 2026-07-10) or on: team growth past
5 engineers, revenue milestone, first paying customer.
```

Why this satisfies dependency-management.vetting-policy: appropriate to scale;
trigger conditions for upgrading the policy are
named; "the PR comment IS the vetting record" is
explicit rather than implicit; future migration cost
acknowledged.

## Cross-reference

- Anti-patterns: examples/dependency-management/vetting-policy-anti-pattern.md
- Substrate rule: dependency-management.vetting-policy
- Decision framework: decision-frameworks/dependency-vetting-policy.madr.md
- Review checklist: checklist.md
