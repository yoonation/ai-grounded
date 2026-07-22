---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.logging.retention-policy-retention-policy"
title: "logging.retention-policy test template: retention policy execution"
substrate-rule: "logging.retention-policy"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
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

# logging.retention-policy test template: retention policy execution

## How to use this binding

Retention tests verify that aggregator configuration matches
the documented policy and that the configured retention
actually executes (records expire at the documented boundary).
Substrate-recommended cadence: weekly verification in a
staging-equivalent environment plus quarterly verification in
production.

## Scenario 1: Configured retention matches documented policy

**Preconditions**
- Retention policy document identifies each log stream and band
- Aggregator is configured with per-stream retention

**Action**
- Query the aggregator for each stream's configured retention
- Compare against the documented policy

**Expected**
- For each stream, the configured retention duration equals the
  documented band
- Streams missing from the aggregator are flagged
- Streams configured but absent from the policy are flagged

## Scenario 2: Operational stream record expires at the boundary

**Preconditions**
- An operational log stream with a documented retention (e.g.,
  14 days)
- A test record is ingested with a known identifier

**Action**
- Wait until the record's age exceeds the retention plus a
  small buffer (e.g., retention + 1 day)
- Query the aggregator for the record

**Expected**
- The record is no longer queryable in the hot retention tier
- The aggregator does not return the record in standard
  searches
- The disposition (deletion or archival) matches the policy

## Scenario 3: Audit stream retention exceeds compliance minimum

**Preconditions**
- An audit log stream subject to compliance retention (e.g.,
  PCI DSS 12 months minimum)

**Action**
- Query the aggregator for the audit stream's configured
  retention
- Calculate the days retained

**Expected**
- Configured retention is at least the compliance minimum
- The retention configuration produces a documented audit
  trail (Terraform plan output, IaC state) confirming the
  duration was deliberate

## Scenario 4: Non-production environments have shorter retention

**Preconditions**
- Dev and staging log streams exist with documented shorter
  retention

**Action**
- Query the aggregator for dev and staging stream retention
- Compare against production retention

**Expected**
- Dev and staging retention is shorter than production
- The shorter retention applies to all dev and staging streams,
  not just some
- Misclassified production streams in non-production
  aggregator buckets are flagged

## Scenario 5: End-of-retention disposition produces audit trail

**Preconditions**
- The policy specifies disposition (deletion, archival,
  hand-off)
- Aggregator is configured to perform the disposition

**Action**
- For a record reaching end-of-retention, observe the
  disposition

**Expected**
- The disposition matches the policy
- A disposition audit event is recorded
- Legal hold records, if any apply, are preserved past their
  normal disposition boundary

## Scenario 6: Configuration drift is detected

**Preconditions**
- Documented policy and aggregator configuration are aligned
  at test start

**Action**
- Simulate a drift event: modify a stream's retention via
  out-of-band change (manual console edit, ad-hoc CLI)
- Run the drift-detection job (substrate-recommended quarterly
  or more frequent)

**Expected**
- The drift-detection job reports the configuration change
- A finding is filed
- The IaC reconciliation restores the documented retention

## Scenario 7: New stream onboarding includes retention policy update

**Preconditions**
- A new service is being added to production
- The new service produces a new log stream

**Action**
- Follow the new-service onboarding procedure
- Verify the procedure includes a retention policy update step

**Expected**
- The new stream is added to the retention policy document
- The new stream's aggregator retention is configured per the
  policy
- The new stream is included in the next retention review

## Scenario 8: Inventory of aggregator streams matches policy inventory

**Preconditions**
- The policy enumerates streams by name
- The aggregator has retention configured per stream

**Action**
- List all streams in the aggregator
- Compare against the policy inventory

**Expected**
- Every aggregator stream appears in the policy
- Every policy stream appears in the aggregator
- Discrepancies are flagged as findings

## Test attestation

```
logging.retention-policy test suite: PASSING
- Scenario 1 (configured retention matches policy): PASS
- Scenario 2 (operational record expires at boundary): PASS
- Scenario 3 (audit retention exceeds compliance minimum): PASS
- Scenario 4 (non-production has shorter retention): PASS
- Scenario 5 (disposition produces audit trail): PASS
- Scenario 6 (configuration drift detected): PASS
- Scenario 7 (new stream onboarding includes policy update): PASS
- Scenario 8 (inventories match): PASS
```

## Cross-reference

- Substrate rule: logging.retention-policy
- Review checklist: checklist.md
- Good examples: examples/logging/retention-policy-good.md
