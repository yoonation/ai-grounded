---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.dependency-management.update-cadence-update-cadence"
title: "dependency-management.update-cadence review checklist: dependency update cadence"
substrate-rule: "dependency-management.update-cadence"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Periodic project review (substrate-recommended quarterly)"
  - "Code changes that modify Dependabot, Renovate, or other update-bot configuration"
  - "Project onboarding when adopting a new repository into substrate-governed workflow"
  - "Incident review where the incident traces to a stale dependency"
---

# dependency-management.update-cadence review checklist: dependency update cadence

## How to use this binding

This checklist is primarily a periodic review tool, not a per-PR
review. The substrate-recommended cadence for self-assessment is
quarterly. The questions evaluate the project's overall posture
rather than any single dependency change.

## Review questions

### 1. Documented cadence: does the project have a stated cadence?

The cadence should be visible somewhere consumers can find it
(README, ADR, CONTRIBUTING.md).

What good looks like: a documented cadence per dependency
class; documented owner who reviews updates; documented
staleness budget beyond which a dependency is overdue.

What needs follow-up: no documented cadence; cadence is folk
knowledge held by one team member; cadence exists but is
significantly older than the project's current practice.

### 2. Automation present: is there an update bot configured?

Manual cadence does not scale. Automation is the substrate-
recommended path for ongoing freshness.

What good looks like: Dependabot, Renovate, or equivalent
configured; configuration committed to the repository;
configuration runs at the documented cadence (substrate-
recommended at least weekly).

What needs follow-up: no automation; automation was configured
but is disabled; automation runs less than weekly without
documented rationale.

### 3. PR backlog: are update PRs being processed?

Automation that opens PRs that no one merges produces noise
without value.

What good looks like: open update PR count is small and
addressable within a sprint; merged update PRs visible in
recent history; the team has a defined responsibility for
addressing update PRs.

What needs follow-up: dozens of stale update PRs open for
weeks; updates auto-closed with no discussion; updates merged
without test results being reviewed.

### 4. Patch updates: are patch-level updates merged within SLA?

Patch versions are the lowest-risk updates. They should land
quickly.

What good looks like: patch updates for production dependencies
merge within 1 week; security-flagged patches per the L1-002
SLA (substrate-recommended ceiling 30 days for medium and below;
immediate for high and critical).

What needs follow-up: patch updates accumulate for weeks; patch
PRs not differentiated from minor or major PRs for triage
purposes.

### 5. Minor updates: is there a process for evaluating them?

Minor versions may introduce new behavior even if backward-
compatible. The process should evaluate before merging.

What good looks like: minor updates evaluated against
changelogs and breaking-change notices; tests run including
those that might exercise newly-affected behavior; cadence is
substrate-recommended at 30 days for production dependencies.

What needs follow-up: minor updates merged without changelog
review; minor updates merged without running the test suite;
minor updates accumulate for months.

### 6. Major updates: is there a documented review path?

Major versions warrant deliberate evaluation, not auto-merge.

What good looks like: major-version PRs reviewed within 90
days; ADR or upgrade plan authored for significant major
upgrades; staging environment exercises the new major version
before production.

What needs follow-up: major-version PRs ignored indefinitely;
"we will do a big upgrade next quarter" patterns with no
specific schedule; major upgrades happen only during incidents.

### 7. Maintainer-abandonment surface: is anything visibly unmaintained?

Periodic review checks the dependency closure for signals of
abandonment.

What good looks like: review identifies any direct dependency
with no release in 18 months and triages: replace, vendor, or
accept the risk with documented rationale.

What needs follow-up: review never happens; abandoned
dependencies persist for years; abandonment is only noticed
when a CVE drops and there is no upstream fix path.

### 8. Cadence evidence in the repository

Cadence is verifiable by walking commit history. The review
spot-checks that the documented cadence matches reality.

What good looks like: dependency update commits appear at the
documented cadence in git history; the commit messages link
back to bot PRs or ADRs; the cadence has not drifted from the
documented value.

What needs follow-up: history shows long gaps in update
activity; updates concentrated in pre-release pushes rather
than continuous cadence; the documented cadence was changed
recently without explanation.

## Self-assessment attestation

For periodic review, the reviewer records the assessment in
an artifact (issue, ADR, security dashboard):

```
dependency-management.update-cadence quarterly self-assessment: complete
Date: YYYY-MM-DD
Reviewer: <name>
- Documented cadence: PASS / FOLLOW-UP
- Automation present: PASS / FOLLOW-UP
- PR backlog: PASS / FOLLOW-UP
- Patch updates: PASS / FOLLOW-UP
- Minor updates: PASS / FOLLOW-UP
- Major updates: PASS / FOLLOW-UP
- Maintainer abandonment surface: PASS / FOLLOW-UP
- Cadence evidence: PASS / FOLLOW-UP
Findings: <list>
Remediation owners and dates: <list>
```

## Cross-reference

- Substrate rule: dependency-management.update-cadence in catalogs/concerns/dependency-management.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/dependency-management/update-cadence-good.md
- Anti-patterns: examples/dependency-management/update-cadence-anti-pattern.md
- Related: dependency-management.vulnerable-dependencies (vulnerable dependencies) has stricter SLA for security updates
