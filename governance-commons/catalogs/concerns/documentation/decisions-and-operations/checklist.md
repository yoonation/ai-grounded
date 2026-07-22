---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.documentation.decisions-and-operations-decisions-and-operations"
title: "documentation.decisions-and-operations review checklist: decisions and operational knowledge"
substrate-rule: "documentation.decisions-and-operations"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-05"
last-modified: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 4 authoring (2026-06-05). Substrate-author review required for stable promotion at M6 close."
review-triggers:
  - "An architecturally significant decision"
  - "A consumer-visible release"
  - "Substrate-recommended periodic review of setup and runbook documentation"
---

# documentation.decisions-and-operations review checklist: decisions and operational knowledge

## How to use this binding

Reviewers confirm that the knowledge a team needs to operate and evolve the
system is written down and findable, not held only in individuals. The aim
is resilience to any one person's absence.

## Review questions

### 1. Are architecturally significant decisions recorded?

What good looks like: significant decisions (per the strategy ADR's
definition) have decision records capturing the context, the choice, and the
consequences.

What needs follow-up: a major decision was made in a chat thread or a
meeting and never written down; the reasoning is lost.

### 2. Are consumer-visible changes captured in a changelog?

What good looks like: each consumer-visible release has a changelog entry a
reader can use to understand what changed.

What needs follow-up: releases ship with no record of what changed, so
consumers and future maintainers reconstruct it from commits.

### 3. Does a setup or onboarding document exist and work?

What good looks like: a new engineer can bring the system up from the
documented setup guide without tribal knowledge.

What needs follow-up: setup lives in one person's memory; onboarding depends
on pairing with them.

### 4. Is there a runbook for the on-call surface?

What good looks like: the system's on-call surface has a runbook covering
known failure responses, and it is current.

What needs follow-up: an incident response depends on whoever happens to
know; there is no runbook, or it is stale.

### 5. Is the recorded knowledge discoverable?

What good looks like: decisions, changelog, setup, and runbooks live where a
reader will find them, linked from an obvious entry point.

What needs follow-up: the records exist but are scattered and effectively
unfindable.
