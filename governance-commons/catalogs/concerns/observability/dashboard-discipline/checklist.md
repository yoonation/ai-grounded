---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.observability.dashboard-discipline-dashboard-discipline"
title: "observability.dashboard-discipline review checklist: dashboard discipline"
substrate-rule: "observability.dashboard-discipline"
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
  - "New dashboard authoring"
  - "Significant service architecture change"
  - "Substrate-recommended quarterly dashboard sweep"
  - "Post-incident review identifying dashboard navigation friction"
---

# observability.dashboard-discipline review checklist: dashboard discipline

## How to use this binding

Reviewers answer every question below when reviewing pull
requests adding or modifying dashboards, or during the
periodic dashboard sweep. Unanswered items block merge or
escalate as findings in the self-assessment.

The reviewer opens the dashboard in the consumer's
visualization tool and answers from the rendered view rather
than the dashboard JSON alone; layout and visual readability
are part of the review.

## Review questions

### 1. Does the dashboard declare its methodology?

A dashboard's methodology (RED, USE, Four Golden Signals)
tells operators how to read it. Without a declared
methodology, operators must reverse-engineer the layout.

What good looks like: the dashboard title or top-of-dashboard
text identifies the methodology applied (e.g., "Service X RED
Dashboard"); the methodology is appropriate to the service
type (RED or Four Golden Signals for request-driven; USE for
resource-constrained; both for composite); the consumer's
dashboard catalog documents the methodology choice.

What needs follow-up: dashboard has no methodology declaration;
methodology is mixed without composition (panels follow no
identifiable organization); methodology declared does not
match the visible layout.

### 2. Are the methodology's required signals present and labeled?

Each methodology specifies a signal set. The signal set must
appear on the dashboard, in panels labeled by the
methodology's vocabulary.

What good looks like for RED: rate (request rate per second),
errors (error rate as count or ratio), duration (latency
percentiles); each appears in a labeled panel; the labels use
the methodology's vocabulary ("Rate" not "Throughput" if RED
was declared).

What good looks like for USE: utilization (resource use
fraction), saturation (work queued waiting on the resource),
errors (resource errors); each appears for the resources the
service depends on (CPU, memory, I/O, connection pool, queue
depth).

What good looks like for Four Golden Signals: latency,
traffic, errors, saturation; each appears in a labeled
panel.

What needs follow-up: required signal missing (RED without
duration; USE without saturation); signals present but
unlabeled or labeled with non-methodology vocabulary; multiple
panels for the same signal without explanation (which is the
authoritative view).

### 3. Are SLI panels separated from operational panels?

SLI panels answer "is the service meeting its SLO?" Operational
panels answer "what is the service doing now?" Mixing the
audiences degrades both.

What good looks like: the consumer has a separate SLI
dashboard pinned at the top of the navigation; the SLI
dashboard shows current burn rate against the observability.slo-policy SLO,
budget remaining, and historical trend; the operational
dashboards (RED, USE, etc.) cross-link to the SLI dashboard
but do not duplicate SLI panels.

What needs follow-up: SLI panels are mixed with operational
panels on the same dashboard; SLI panels are buried among
many operational panels (executives cannot find them under
pressure); no SLI dashboard exists (observability.slo-policy cross-violation
surfaces here); the SLI dashboard exists but is not pinned or
not in a discoverable location.

### 4. Is panel count appropriate for incident-response scanning?

Operators scan dashboards under pressure. Too many panels
slows scanning; too few hides relevant signals.

What good looks like: the dashboard fits on a representative
screen size (substrate-recommended target: visible at typical
laptop and external monitor sizes without horizontal scroll;
substrate-recommended ceiling: roughly 20 panels per
dashboard); information density is high without crowding;
panels that answer separate questions are on separate
dashboards cross-linked from a parent dashboard.

What needs follow-up: dashboard requires scrolling to see
the methodology's full signal set; dashboard exceeds 30
panels (operators cannot effectively scan it); dashboard is
sparse to the point of hiding information operators need.

### 5. Are panels organized into rows or sections by signal?

A dashboard's spatial organization is part of its readability.
Operators expect related signals to cluster.

What good looks like: panels are organized into rows or
sections corresponding to the methodology's signal categories
(RED: a rate row, an errors row, a duration row; USE: a
utilization section, a saturation section, an errors section);
rows are labeled with the signal category.

What needs follow-up: panels are placed in arbitrary order;
related signals (different latency percentiles, different
error categories) are separated rather than grouped; row
labels are missing or generic.

### 6. Do panels use consistent time ranges and refresh rates?

Inconsistent panel time ranges produce misleading comparisons.
A dashboard where some panels show the last 5 minutes and
others the last hour produces confused operators.

What good looks like: dashboards use a single time range
across panels (the dashboard-level range, not per-panel
override); refresh rate is set to a substrate-recommended
cadence (live for incident-response dashboards; longer for
analytical dashboards); per-panel time range overrides exist
only for specific comparative purposes and are labeled.

What needs follow-up: panels use mixed time ranges without
documentation; refresh rate is set incorrectly (live refresh
on a long-running analytical dashboard wastes backend query
load); time range mismatches cause panels to disagree on
what "now" means.

### 7. Are panels linked to source-of-truth queries and to relevant alerts?

A dashboard panel that fires an alert should link to the
alert; an alert that pages on a panel's data should link to
the panel.

What good looks like: SLI panels link to the SLO documentation
(observability.slo-policy ADR); rate, errors, and duration panels link to
the observability.alerting-discipline alerts that fire on the underlying data; alert
runbooks link back to the dashboard panel where the responder
can see live data; the cross-references survive dashboard
renames (the substrate-recommended pattern is stable panel
URLs).

What needs follow-up: panels do not link to alerts; alerts do
not link to panels; cross-references break when dashboards
are renamed; the consumer has no shared convention for cross-
linking.

### 8. Has the dashboard been reviewed in the substrate-recommended sweep cadence?

Dashboards age. The service evolves; the dashboard's
relevance to the current service architecture must be
verified periodically.

What good looks like: each dashboard was reviewed in the
past quarter against the questions above; the review
documents the reviewer and outcome; the sweep catches
dashboards to retire, to amend, or to migrate to a methodology
that better fits the current service architecture.

What needs follow-up: dashboards have not been reviewed since
authoring; the sweep happens but is not documented; the
review surfaces dashboards that no longer match the service
they were authored for.

## Reviewer attestation

```
observability.dashboard-discipline review checklist: complete
- Methodology declared: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Required signals present: PASS / FOLLOW-UP / EXEMPT-with-rationale
- SLI separation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Panel count appropriate: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Spatial organization: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Consistent time and refresh: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cross-references intact: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Reviewed in sweep cadence: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: observability.dashboard-discipline in catalogs/concerns/observability.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/observability/dashboard-discipline-good.md
- Anti-patterns: examples/observability/dashboard-discipline-anti-pattern.md
- Related: observability.slo-policy (anchors SLI panel content); observability.alerting-discipline (anchors alert-to-panel cross-links)
