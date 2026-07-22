---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.dependency-management.update-cadence-update-cadence"
title: "dependency-management.update-cadence test template: dependency update cadence"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# dependency-management.update-cadence test template: dependency update cadence

## How to use this binding

These tests are CI checks that surface staleness rather than
pass-fail acceptance tests. They run on a schedule (substrate-
recommended weekly) and produce a report that feeds the
quarterly self-assessment under secrets-management.rotation-policy review checklist.

## Scenario 1: Direct-dependency freshness measurement

**Preconditions**
- A registry-query tool is available (npm outdated, pip list
  --outdated, cargo outdated, go list -u -m all, or equivalent)

**Action**
- Run the freshness query against the project's lockfile
- For each direct dependency, compare the installed version
  to the latest published version
- Compute the gap in days

**Expected**
- A report is produced listing each direct dependency, its
  installed version, the latest version, and the day-count gap
- No direct dependency has a gap exceeding the documented
  staleness budget (substrate-recommended 90 days)
- Dependencies exceeding the budget surface as findings

## Scenario 2: Update bot is configured and active

**Preconditions**
- The project documents which update bot is in use
  (Dependabot, Renovate, custom)

**Action**
- Verify the bot's configuration file is present in the repo
- Query the bot's recent activity (PRs opened in the last 4
  weeks)

**Expected**
- The configuration file is present and not commented out
- Recent PR activity exists (the bot has opened at least one
  PR in the last 4 weeks for an active project)
- The bot's schedule matches the documented cadence

## Scenario 3: Update PR throughput is healthy

**Preconditions**
- Update PR history available via the repository host's API

**Action**
- Query the last 90 days of update bot PRs
- Compute: opened, merged, closed-without-merge, time-to-merge

**Expected**
- The opened-to-merged ratio is healthy (substrate-recommended
  at least 70 percent of opened PRs result in merge for patch
  and minor updates)
- Time-to-merge for patch updates is within the documented SLA
  (substrate-recommended ceiling 7 days)
- Closed-without-merge PRs have documented rationale (test
  failure, intentional defer)

## Scenario 4: Major-version backlog is bounded

**Preconditions**
- Update bot opens major-version PRs and the queue is queryable

**Action**
- List open major-version PRs and their age

**Expected**
- No major-version PR is open longer than 90 days without an
  associated ADR or upgrade plan
- The pattern of "indefinite defer" does not appear

## Scenario 5: Security-flagged updates have priority SLA evidence

**Preconditions**
- dependency-management.vulnerable-dependencies produces security findings; the project has an
  SLA per the production-grade-baseline profile

**Action**
- For each security-flagged finding in the last 90 days,
  compute time from advisory publication to merged remediation

**Expected**
- High and critical advisories were addressed within the SLA
  (immediate for critical; substrate-recommended within 7
  days for high)
- Medium advisories were addressed within 30 days or have
  active exemptions
- Pattern of slipped SLAs surfaces in the report

## Scenario 6: Maintainer-abandonment scan

**Preconditions**
- Registry metadata accessible per ecosystem

**Action**
- For each direct dependency, query the registry for the
  publish date of the latest release
- Identify dependencies with no release in 18+ months

**Expected**
- A list of potentially-abandoned dependencies is produced
- For each, a triage decision exists (continue using with
  vendoring backup, replace with alternative, accept risk
  with documented rationale)

## Scenario 7: Cadence drift detection

**Preconditions**
- The documented cadence is committed to the repository

**Action**
- Compare the documented cadence against actual recent
  practice (PR throughput, scheduled scan frequency)

**Expected**
- The documented cadence matches actual practice within a
  reasonable margin
- Drift triggers an issue for review and update of the
  documentation

## Scenario 8: SBOM freshness

**Preconditions**
- The project generates an SBOM as part of the build

**Action**
- Inspect the most recent SBOM artifact
- Verify it was generated within the documented build cadence

**Expected**
- The latest SBOM is current with the latest build
- Old SBOMs are retained per the consumer's policy (typical:
  per-release for the release lifetime)

## Test attestation (used in quarterly self-assessment)

```
dependency-management.update-cadence staleness scan: COMPLETED
Date: YYYY-MM-DD
- Direct dependency freshness: PASS / FINDINGS
- Update bot active: PASS / FINDINGS
- Update PR throughput: PASS / FINDINGS
- Major-version backlog: PASS / FINDINGS
- Security SLA evidence: PASS / FINDINGS
- Maintainer abandonment scan: PASS / FINDINGS
- Cadence drift: PASS / FINDINGS
- SBOM freshness: PASS / FINDINGS
Findings count: N
Remediation owner: <name>
Next scan: <date>
```

## Cross-reference

- Substrate rule: dependency-management.update-cadence
- Review checklist: checklist.md
- Good examples: examples/dependency-management/update-cadence-good.md
