---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.logging.redaction-redaction"
title: "logging.redaction review checklist: sensitive-data redaction strategy"
substrate-rule: "logging.redaction"
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
  - "New code paths introducing fields that may carry application-specific sensitive data"
  - "New log streams added"
  - "Changes to the data classification taxonomy"
  - "Substrate-recommended quarterly redaction policy review"
---

# logging.redaction review checklist: sensitive-data redaction strategy

## How to use this binding

Reviewers answer every question below when reviewing pull
requests that match the review triggers, or during the periodic
review. Unanswered items block merge or escalate as findings.

## Review questions

### 1. Does a redaction policy exist that goes beyond the substrate-recognized vocabulary?

logging.no-sensitive-data-in-logs catches generic sensitive vocabulary (password,
ssn, credit_card, etc.). L2-003 covers application-specific
sensitive fields whose names do not match the substrate-
recognized vocabulary.

What good looks like: the policy lists application-specific
sensitive fields (e.g., negotiated_rate for a B2B app,
diagnosis_code for a healthcare app, internal_score for a
financial app); the policy is reviewed when the application's
data classification evolves.

What needs follow-up: the policy relies entirely on substrate-
recognized vocabulary (application-specific fields are
implicitly assumed safe); the policy lists no application-
specific fields despite the application clearly handling
sensitive data; the policy was authored once at project start
and never revisited.

### 2. Is each sensitive field classified into a substrate-recognized handling?

Substrate-recognized handlings:
- Allow-listed inclusion (explicit fields permitted in logs)
- Redaction-on-emission (replaced with [REDACTED] or similar)
- Hashing for join (replaced with a salted hash for cross-
  record correlation without disclosure)
- Exclusion (the field is not logged at all)

What good looks like: each sensitive field has a documented
handling; the handling is appropriate (e.g., a join key gets
hashing, not exclusion, so cross-record analysis still works);
the rationale is documented.

What needs follow-up: handlings are not assigned per field;
the policy says "redact everything sensitive" without per-field
specificity; allow-list is implicit (everything not listed as
sensitive is logged); deny-list is the only mechanism (new
fields default to logged).

### 3. Is the strategy enforced at the call site?

Pipeline-side enforcement is defense in depth, not the
primary line. Call-site enforcement is the substrate's
preferred primary mechanism.

What good looks like: sensitive values are wrapped in
redaction types at the type-system level (Password type whose
__repr__ returns "[REDACTED]"); the redaction wrapper is used
in function signatures; logger plugins reject or transform
sensitive fields based on field name patterns.

What needs follow-up: call-site enforcement relies on
developer discipline only (no type-system or plugin support);
some code paths use the wrappers and others bypass them; the
wrapper is bypassed by ad-hoc serializers (model.to_dict())
that lose the type information.

### 4. Is the strategy enforced at the pipeline as defense in depth?

Aggregator-side scrubbing catches disclosures that evaded the
call site.

What good looks like: the aggregator has scrubbing rules
configured for known sensitive patterns (credit-card regex,
PEM headers, application-specific field patterns); findings
trigger alerts to security review; pipeline scrubbing is
verified in test ingestion (a test record carrying a known
pattern arrives scrubbed in the aggregator).

What needs follow-up: pipeline-side enforcement is asserted
but not configured; configuration exists but is not verified;
scrubbing rules are out of date relative to the policy.

### 5. Does the strategy favor allow-list over deny-list?

Deny-list approaches treat new fields as logged by default and
require remembering to add them to the deny list. Allow-list
treats new fields as not-logged until reviewed.

What good looks like: the policy is allow-list framed; new
fields require explicit approval before they reach logs;
emergent fields (added late in development) are caught by the
allow-list discipline.

What needs follow-up: the policy is deny-list framed; new
fields silently log unless someone remembers to add them;
multi-team applications have inconsistent lists.

### 6. Is hashing-for-join configured with proper salt scope?

A logging-pipeline-specific salt is the substrate-recommended
scope: the hash is stable within the pipeline (so cross-record
correlation works) but not portable outside (so leaked logs
cannot be re-identified against external data).

What good looks like: the salt is logging-pipeline-scoped;
the salt is not exposed in logs or in cross-system contexts;
salt rotation procedure exists for compromise scenarios.

What needs follow-up: the salt is application-scoped (used in
other contexts where rainbow-table attacks become feasible);
the salt is exposed in source or configuration; no salt
rotation procedure exists.

### 7. Are debug and emergency paths handled?

Debug logging and emergency dump paths frequently bypass
redaction because the developer needs to see the data. The
policy addresses these explicitly.

What good looks like: debug paths still apply redaction (the
developer sees [REDACTED], not the raw value); emergency
dumps are routed to an access-controlled location separate
from regular logs; the procedure for accessing un-redacted
data exists, is approved-gated, and is audited.

What needs follow-up: debug paths bypass redaction silently;
emergency dumps are in the same retention store as regular
logs with the same broad access; un-redacted access has no
approval gate.

### 8. Is the policy reviewed when data classification evolves?

Applications add new data fields over time; the redaction
policy must keep pace.

What good looks like: the policy is reviewed when a new data
classification (new tenant types, new regulatory regime, new
data domain) is added; the review is documented; the review
catches fields added since the last review.

What needs follow-up: the policy is reviewed on a fixed
calendar (annual) regardless of application changes; reviews
happen but new fields slip through without classification;
new fields are added with no policy update.

## Reviewer attestation

```
logging.redaction review checklist: complete
- Policy beyond substrate vocabulary: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Per-field handling: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Call-site enforcement: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Pipeline enforcement: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Allow-list framing: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Hashing salt scope: PASS / FOLLOW-UP / NA
- Debug and emergency paths: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Periodic review: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: logging.redaction in catalogs/concerns/logging.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/logging/redaction-good.md
- Anti-patterns: examples/logging/redaction-anti-pattern.md
- Related: secrets-management secrets-management.no-secrets-in-logs (no secrets in logs subset)
