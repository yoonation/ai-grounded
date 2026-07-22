---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.monitoring-alerting.on-call-rotation-coverage-on-call-rotation-coverage"
title: "monitoring-alerting.on-call-rotation-coverage review checklist: on-call rotation covers every hour with a defined handoff"
substrate-rule: "monitoring-alerting.on-call-rotation-coverage"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.7.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-03"
last-modified: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M5 close consolidation (2026-06-04); cooling-off honored, authoring landed on a prior calendar day in the concern's M5 authoring session and attestation lands in a discrete close commit on 2026-06-04."
ai-assistance: "AI drafted from substrate-author intent at M5 Session 5 authoring (2026-06-03). Substrate-author review required for stable promotion at M5 close."
review-triggers:
  - "An on-call rotation is established or changed"
  - "A responder joins or leaves the rotation"
  - "A holiday or coverage period needs ownership"
  - "A post-incident review finds a page that fell into an uncovered window"
---

# monitoring-alerting.on-call-rotation-coverage review checklist: on-call rotation covers every hour with a defined handoff

## How to use this binding

The most carefully built routing and escalation chain still terminates at a
human, and if no human is on the other end the chain is decorative. This rule
is review-only and has no test template because its subject is a human rotation
and an operational policy that no application-source test settles. This review
confirms the rotation covers every hour and hands off cleanly. Reviewers answer
the questions below for changes matching the triggers.

## Review questions

### 1. Does the rotation cover every hour with no gap?

What good looks like: a documented rotation covers every hour of the period the
service is operated, including nights, weekends, and holidays, with no unowned
window.

What needs follow-up: a rotation that looks complete but leaves a holiday or a
departed engineer's slot unowned, so a page falling into that window reaches no
one.

### 2. Is there a defined handoff?

What good looks like: a handoff procedure where the outgoing responder hands
active context to the incoming one and coverage does not lapse at the boundary.

What needs follow-up: no defined handoff, so an outgoing responder stops
watching before the incoming one is ready and pages are missed at the seam.

### 3. Do the escalation targets match the rotation?

What good looks like: the escalation targets monitoring-alerting.routing-and-escalation routes pages to name
the people or teams actually on the current rotation.

What needs follow-up: escalation targets that point at a stale rotation, so a
page escalates to someone no longer on call.

## When to escalate to L3

Escalate to monitoring-alerting.alerting-strategy when the on-call model itself is the policy decision.
This rule confirms the human coverage the routing and escalation mechanics
(monitoring-alerting.routing-and-escalation) depend on; it cross-references those mechanics rather than
restating them. There is no test template: the rotation is an organizational
artifact, so the review of the schedule and policy is the conformance check.
