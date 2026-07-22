---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.feature-flags.staged-rollout-and-context-staged-rollout-and-context"
title: "feature-flags.staged-rollout-and-context review checklist: staged rollout and evaluation-context hygiene"
substrate-rule: "feature-flags.staged-rollout-and-context"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.8.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-06-04"
last-modified: "2026-06-04"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M6 close consolidation (2026-06-06); cooling-off honored, authoring landed on a prior calendar day in the concern's M6 authoring session and attestation lands in a discrete close commit on 2026-06-06."
ai-assistance: "AI drafted from substrate-author intent at M6 Session 2 authoring (2026-06-04). Substrate-author review required for stable promotion at M6 close."
review-triggers:
  - "Introduction of a flag intended for gradual rollout"
  - "A change to the evaluation-context schema or a new targeting dimension"
  - "Review of a flag that carries user or request attributes"
  - "A major flag-SDK or provider change"
---

# feature-flags.staged-rollout-and-context review checklist: staged rollout and evaluation-context hygiene

## How to use this binding

Reviewers answer every question below when reviewing a flag intended for
gradual rollout and the construction of its evaluation context. The
purpose is to confirm the flag delivers what a flag system is for: bounded,
reversible exposure and stable, safe targeting. The reviewer reads the
flag's targeting configuration, the evaluation-context construction site,
and the rollout plan before answering. feature-flags.fail-static-default (fail-static default) is
assumed to hold.

## Review questions

### 1. Is the rollout staged through the provider's targeting, not hardcoded?

A flag flipped fully on in one step, or varied by per-environment
hardcoding, carries a deploy's blast radius without a deploy's review.

What good looks like: the rollout uses the provider's targeting (a
percentage, a ring, or a named cohort), advances in stages, and is
reversible to the safe default in one provider action.

What needs follow-up: the flag is enabled globally at once; rollout state
is hardcoded per environment so it cannot be rolled back centrally.

### 2. Is bucketing deterministic from a stable targeting key?

What good looks like: a given subject is assigned a stable bucket from a
durable targeting key (a user or account identifier, or a deliberately
chosen stable key), so the subject's experience does not flicker across
requests within a stage.

What needs follow-up: bucketing keys on a per-request random value, a
timestamp, or a value that changes within a session, so the same subject
sees the new and old paths inconsistently.

### 3. Does the evaluation context carry only the attributes targeting needs?

What good looks like: the context carries the stable targeting key and the
minimal attributes the targeting rules use; it does not carry a full user
record or attributes no rule consumes.

What needs follow-up: the context is a dumping ground of user fields; it
carries data no targeting rule uses.

### 4. Is the evaluation context free of secrets and minimized for personal data?

Flag context often flows to a third-party provider and into its logs, so
anything in it is exposed there.

What good looks like: no secret (token, key, password) appears in context;
secret handling is deferred to secrets-management. Personal data is
minimized to a stable identifier and the necessary targeting attributes,
consistent with the privacy concern.

What needs follow-up: a session token, API key, or email and full profile
are placed into context for convenience.

## Escalation to L3

If the review finds the rollout approach, the targeting-key choice, or the
context schema is being decided ad hoc per flag rather than against a
written standard, that is a strategy question for the feature-flags.strategy-adr ADR, not
a per-flag fix. Escalate.
