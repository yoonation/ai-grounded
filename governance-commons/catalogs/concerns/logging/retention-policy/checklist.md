---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.logging.retention-policy-retention-policy"
title: "logging.retention-policy review checklist: log retention policy"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code or infrastructure changes affecting log retention configuration"
  - "New log streams added to production"
  - "Changes to compliance regime affecting retention requirements"
  - "Substrate-recommended quarterly retention policy review"
---

# logging.retention-policy review checklist: log retention policy

## How to use this binding

Reviewers answer every question below when reviewing pull
requests that match the review triggers, or during the periodic
self-assessment. Unanswered items block merge or escalate as
findings in the self-assessment.

## Review questions

### 1. Does a written retention policy exist?

A retention policy must be a written artifact, not tribal
knowledge, because regulators require visible reasoning and
audit teams need a reference for verification.

What good looks like: a retention policy document
(SECURITY.md, an ADR, a runbook, a wiki page) that lists log
streams in scope, retention bands, and disposition; the document
is accessible to engineering, security, and audit teams; the
document is reviewed and dated.

What needs follow-up: retention is configured but not
documented; documentation exists but is older than 12 months
and clearly out of date; documentation references aggregator
defaults rather than a deliberate decision.

### 2. Are log streams categorized into retention bands?

Not all log streams need the same retention. Operational debug
logs (high volume, marginal forensic value beyond the immediate
window) warrant short bands. Security and audit logs warrant
long bands with integrity protection.

What good looks like: streams are categorized into substrate-
recommended bands (operational, application, audit); each
stream's category is documented; the categorization is reviewed
when new streams are added.

What needs follow-up: all streams retained for the same
duration regardless of value; debug streams retained beyond
operational need (cost and disclosure exposure); audit streams
retained for the same short duration as debug (compliance gap).

### 3. Are retention durations matched to compliance and forensic needs?

The substrate-recommended starting bands (consumers tune by
regulatory regime and threat model):

- Operational debug and trace: 7 to 30 days
- Application logs: 60 to 180 days
- Authentication, authorization, administrative-action audit:
  12 months minimum (PCI DSS Requirement 10.5.1), longer per
  HIPAA, SOX, or organization-specific requirement

What good looks like: per-band retention is documented with
the driver (compliance regime, threat model, operational
window); retention durations are within or stricter than the
substrate-recommended starting bands; rationale documents any
deviation.

What needs follow-up: retention shorter than compliance
minimums (audit finding risk); retention significantly longer
than driver without rationale (cost, disclosure exposure);
"default" retention with no documented driver.

### 4. Is the configured retention verifiable against the documented policy?

Configuration drift is the recurring failure mode. A policy
documented in writing but not implemented in the aggregator
produces audit failures.

What good looks like: per-stream retention is configured at
the aggregator (CloudWatch Logs retention, Datadog log
retention rules, Splunk index retention, Elastic ILM, GCP
Cloud Logging buckets); a periodic check (substrate-
recommended quarterly) compares configured retention to
documented policy; drift is treated as a finding.

What needs follow-up: configuration deviates from policy with
no record of why; policy and configuration are checked manually
once per year (drift accumulates between checks); some streams
have no explicit retention configuration and inherit aggregator
defaults.

### 5. Is end-of-retention disposition explicit?

What happens to log records when the retention window expires
is part of the policy, not an afterthought.

What good looks like: the policy specifies disposition for
each band (deletion, archival to cold storage, hand-off to a
records system); legal hold procedures override retention
when applicable; deletion produces an audit trail confirming
records were removed.

What needs follow-up: deletion happens silently with no
audit trail; archival is mentioned but not verified;
disposition is "the aggregator handles it" without inspection
of what that means.

### 6. Are cost implications of retention reviewed?

Retention is a cost lever as well as a compliance lever. Cost
review keeps retention honest.

What good looks like: per-band retention cost is monitored;
trends are reviewed (substrate-recommended quarterly); cost
spikes trigger review of whether the underlying logs are
necessary or could be sampled.

What needs follow-up: log retention costs grow without
oversight; cost surprises drive ad-hoc retention cuts that
break compliance; high-volume debug streams retained at audit
durations because the categorization is wrong.

### 7. Are non-production environments excluded from production retention?

Production retention requirements (cost, compliance) should
not bleed into development or staging environments.

What good looks like: dev and staging log streams have shorter
retention (substrate-recommended 7 days); production-only
retention applies only to production streams; aggregator
boundaries enforce the separation.

What needs follow-up: all environments share the production
retention; dev and staging logs are retained for compliance
durations (cost waste); production retention rules omit
production streams because they were created in a non-default
aggregator bucket.

### 8. Has the policy been reviewed within the substrate-recommended cadence?

What good looks like: the policy is reviewed at least
annually (substrate-recommended); the most recent review is
documented with the reviewer's name and date; review confirms
both the policy is current and configuration matches.

What needs follow-up: policy has not been reviewed since
authoring; review happens but is not documented; review
documents the policy is current but does not verify
configuration matches.

## Reviewer attestation

```
logging.retention-policy review checklist: complete
- Written policy: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Stream categorization: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Retention durations: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Configuration verifiability: PASS / FOLLOW-UP / EXEMPT-with-rationale
- End-of-retention disposition: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cost review: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Non-production separation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Review cadence: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: logging.retention-policy in catalogs/concerns/logging.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/logging/retention-policy-good.md
- Anti-patterns: examples/logging/retention-policy-anti-pattern.md
