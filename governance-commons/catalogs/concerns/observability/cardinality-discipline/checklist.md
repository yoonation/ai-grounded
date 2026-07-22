---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.observability.cardinality-discipline-cardinality-discipline"
title: "observability.cardinality-discipline review checklist: cardinality discipline"
substrate-rule: "observability.cardinality-discipline"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-21"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New metric registration in code review"
  - "Service launch into production"
  - "Cardinality alert from metrics backend"
  - "Substrate-recommended quarterly cardinality audit"
---

# observability.cardinality-discipline review checklist: cardinality discipline

## How to use this binding

Reviewers answer every question below when reviewing pull
requests matching the review triggers, or during the periodic
self-assessment. Unanswered items block merge or escalate as
findings in the self-assessment.

Substrate-author note recorded 2026-05-21: observability.cardinality-discipline is the
explicit L1 promotion candidate. The substrate-author has
stated that real-project usage at L2 will inform whether the
rule's mechanical pattern is stable enough to promote to L1.
Reviewers performing this checklist contribute to that
evaluation: cases where the review surfaces a violation the
substrate's L1 vocabulary would have caught, and cases where
the review surfaces a violation that depends on application-
specific context, both inform the L1 promotion decision.

## Review questions

### 1. Does each metric's label set use the substrate-recognized bounded vocabulary?

The substrate-recognized bounded vocabularies are: tenant_id
(business-unit count bound), region (deployment region list),
environment (production, staging, development), service
version, endpoint template (the routed path pattern), HTTP
status code, error class.

What good looks like: every label key in the metric's
registration is drawn from the substrate vocabulary or from
a consumer-documented bounded vocabulary; the registration
call site or accompanying comment lists the label vocabularies.

What needs follow-up: label keys include vocabulary outside
both substrate and consumer-documented lists; label set was
chosen ad-hoc without explicit cardinality consideration; the
metric registration site has no comment documenting the
intended bounded vocabularies.

### 2. Are unbounded vocabularies excluded from label values?

The substrate-recognized unbounded vocabularies are: user_id,
customer email, session identifier, request identifier, raw
URL with substituted parameters, arbitrary user input, free-
form error messages, full timestamps.

What good looks like: no label receives values from unbounded
sources; questions that seem to require per-identity labels
are instead answered through traces (per-request identity in
span attributes) or through logs (structured fields with
retention-based cost discipline); the metric's documentation
notes how per-identity questions are answered without
unbounded labels.

What needs follow-up: a label takes values from a user input
field directly; a label encodes a session identifier or
request identifier; the metric is the only data source for a
per-identity question (the consumer's tooling has no other way
to ask "what happened for user X?").

### 3. Are consumer-documented bounded vocabularies actually bounded?

A vocabulary documented as bounded but unbounded in practice
defeats the discipline. Reviewers verify the bound.

What good looks like: each consumer-documented vocabulary has
an explicit cardinality bound (tenant_id bounded at "up to
1000 tenants in the business roadmap"; region bounded at "5
regions in the deployment topology"); the bound is sourced
from a non-metric data point (the business roadmap, the
deployment topology); the bound is reviewed when the source
data changes.

What needs follow-up: documented bound is significantly
exceeded in production; bound is described qualitatively
("a few hundred") without a numeric ceiling; bound has not
been reviewed for over a year.

### 4. Does the metric registration carry vocabulary documentation?

Future maintainers of the service need to understand the
cardinality decisions without inferring them from production
behavior. Documentation at the registration site is the
substrate-recommended pattern.

What good looks like: each metric registration carries a
comment listing the bounded vocabulary for each label key
(or a reference to a vocabulary doc); new label additions
update the documentation; documentation is reviewed when the
metric is renamed or restructured.

What needs follow-up: registration has no documentation;
documentation exists in a separate document the maintainer
must find first; documentation is stale relative to the
current label set.

### 5. Have backend cardinality reports been reviewed?

Production telemetry is the integration test for cardinality
discipline. Backend cardinality reports are the verification.

What good looks like: the consumer has a periodic
(substrate-recommended monthly for active services) review of
the metrics backend's cardinality report; the report compares
actual series counts to the consumer's expected counts; the
review documents corrective actions for any divergence.

What needs follow-up: cardinality reports are not reviewed;
reports show series counts substantially above expected with
no follow-up; the backend has flagged cardinality cost
concerns that the consumer has not investigated.

### 6. Are emergency cardinality cuts (metric_relabel drops) documented?

Where cardinality has exceeded acceptable bounds in
production, pipeline-level drops are a stabilization step.
The drop is documented so the source-side remediation lands.

What good looks like: pipeline drops are temporary stabilization
with a documented timeline for source-side fix; each drop
references the source code location to remediate; the drop is
removed when the source-side fix lands.

What needs follow-up: pipeline drops have been in place for
multiple quarters with no source-side fix; drops accumulate
without documentation; the source-side fix is deferred
indefinitely because the pipeline drop "is working."

### 7. Has cardinality been considered in the service's SLO instrumentation?

SLI computation depends on specific metrics. Cardinality
discipline in the SLI-driving metrics is load-bearing for
observability.slo-policy (SLO policy).

What good looks like: SLI-driving metrics use the bounded
vocabulary explicitly (e.g., availability SLI labeled by
tenant_id and endpoint, not by user_id); the SLI computation
is verified to be stable as cardinality grows within the
documented bounds.

What needs follow-up: SLI computation depends on a metric with
unbounded labels; SLI dashboards have degraded query
performance correlated with cardinality growth; the SLI is
intermittently unavailable when cardinality spikes.

### 8. Is the cardinality discipline consistent across services?

Cross-service consistency matters because operators query
across services. A vocabulary discipline that varies per
service produces cross-service queries that fail silently.

What good looks like: the consumer's service catalog has a
shared bounded-vocabulary doc; new services adopt the shared
vocabulary; deviations are documented and reviewed.

What needs follow-up: each service has its own vocabulary;
cross-service queries return surprising results because
identical label keys have different meanings per service; the
consumer has no shared vocabulary doc.

## Reviewer attestation

```
observability.cardinality-discipline review checklist: complete
- Bounded vocabulary per metric: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Unbounded exclusion: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Bounds verifiable: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Registration documentation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Backend reports reviewed: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Emergency cuts documented: PASS / FOLLOW-UP / EXEMPT-with-rationale
- SLI cardinality stable: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cross-service consistency: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## L1-promotion contribution log

Substrate-author note recorded 2026-05-21: this checklist's
findings contribute to the substrate's L1 promotion evaluation
for observability.cardinality-discipline. Reviewers using this checklist may record
patterns observed for substrate feedback:

- Cases where a violation matched the substrate vocabulary
  exactly (would have been caught by a candidate L1 Semgrep
  rule)
- Cases where a violation depended on application-specific
  context (would NOT have been caught by a generic L1 rule)
- False-positive cases where the substrate vocabulary would
  have flagged an acceptable usage

Patterns recorded contribute to the substrate-author's
decision on L1 promotion timing.

## Cross-reference

- Substrate rule: observability.cardinality-discipline in catalogs/concerns/observability.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/observability/cardinality-discipline-good.md
- Anti-patterns: examples/observability/cardinality-discipline-anti-pattern.md
