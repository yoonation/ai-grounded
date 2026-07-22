<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: dependency-management.update-cadence update cadence (anti-patterns)

Substrate-original anti-pattern examples for dependency-management.update-cadence.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: No automation, no documented cadence

```text
# Project state: no Renovate, no Dependabot, no
# scheduled review. Dependency updates happen when
# someone notices a problem or when an audit complains.
```

Why this violates dependency-management.update-cadence: cadence in name only.
Without automation or a documented schedule, updates
trail months behind upstream. Substrate-recommended
pattern: install Renovate or Dependabot with a
documented schedule.

## Anti-pattern B: Automation enabled but PRs accumulate

```text
# Dependabot is enabled.
# PR list:
- 87 open dependency PRs
- Oldest: 6 months
- Median age: 11 weeks
- Last merge: 3 weeks ago
```

Why this violates dependency-management.update-cadence (operational property):
automation is necessary but not sufficient. Without a
process to triage and merge the PRs, they pile up.
Substrate-recommended pattern: weekly dependency-review
cadence with named owner; PR backlog monitored.

## Anti-pattern C: "We'll do a big upgrade next quarter"

```text
# Team statement: "We're behind on dependencies; we'll
# allocate a sprint next quarter to catch up."
# Reality: this has been the plan for 6 quarters.
```

Why this violates dependency-management.update-cadence (process property): "big
upgrade later" is the failure mode of "no incremental
upgrade". Each deferral makes the next upgrade larger.
Substrate-recommended pattern: incremental upgrades on
cadence; "big upgrade" exists only for major versions
that genuinely require migration work.

## Anti-pattern D: Major versions never evaluated

```text
# Renovate PR list:
- minor and patch: merged within a week
- major version PRs: closed without action 12 times in
  a row, citing "out of scope"
# Some libraries are 3+ major versions behind upstream.
```

Why this violates dependency-management.update-cadence (in spirit): closing major
updates without evaluation leaves the project on
versions that may lose support. Substrate-recommended
pattern: major updates evaluated within a defined
window (substrate-recommended 30 days); evaluation
produces an explicit accept/defer decision with
rationale.

## Anti-pattern E: No documented cadence policy

```text
# Asked: "What is the dependency update cadence?"
# Answer (varies by team member):
# - "Weekly"
# - "When Dependabot files a PR"
# - "Whenever we have time"
# - "Quarterly"
```

Why this violates dependency-management.update-cadence (documentation property):
without a single source of truth, the cadence is
fictional. Substrate-recommended pattern: documented
cadence per ecosystem in the project's dependency
policy.

## Anti-pattern F: Abandoned dependencies never reviewed

```text
# Dependency "old-helper" has had no upstream commits
# since 2022. Project still depends on it 4 years
# later. No alternative-evaluation, no risk register
# entry, no migration plan.
```

Why this violates dependency-management.update-cadence (sustainability property):
abandoned dependencies are technical debt that
compounds. Substrate-recommended pattern: dependency
inventory flags abandonment indicators (last commit,
last release); flagged dependencies get migration plans.

## Anti-pattern G: Cadence drift unmeasured

```text
# Cadence policy: patches within 7 days.
# Reality: median 21 days.
# No one is measuring; no one knows about the drift.
```

Why this violates dependency-management.update-cadence (measurement property):
a policy without measurement is a policy without
enforcement. Substrate-recommended pattern: cadence
metrics generated in CI or as a periodic report;
quarterly review compares actual to target.

## Anti-pattern H: Security PRs treated as routine

```text
# Vulnerability advisory: CVE-2025-12345 in HTTP
# parsing library, CVSS 9.8.
# Dependabot creates PR labeled "dependencies".
# PR ages 14 days in the standard backlog.
```

Why this violates dependency-management.update-cadence (escalation property):
security PRs should have tighter SLAs than routine
updates. Substrate-recommended pattern: security-flagged
PRs are auto-labeled "priority-high"; named owner; SLA
breach triggers escalation.

## Cross-reference

- Good patterns: examples/dependency-management/update-cadence-good.md
- Substrate rule: dependency-management.update-cadence
- Review checklist: checklist.md
