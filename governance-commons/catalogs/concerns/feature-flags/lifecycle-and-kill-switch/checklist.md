---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.feature-flags.lifecycle-and-kill-switch-lifecycle-and-kill-switch"
title: "feature-flags.lifecycle-and-kill-switch review checklist: flag lifecycle and kill-switch discipline"
substrate-rule: "feature-flags.lifecycle-and-kill-switch"
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
  - "Introduction of any flag (to set type, owner, and end state)"
  - "Completion of a rollout (to trigger retirement)"
  - "Any incident involving a kill switch"
  - "Periodic flag-inventory audit"
---

# feature-flags.lifecycle-and-kill-switch review checklist: flag lifecycle and kill-switch discipline

## How to use this binding

Reviewers answer every question below against the flag inventory, the code,
and the kill-switch documentation. The purpose is to keep flag debt from
accumulating and to ensure operational kill switches work the moment they
are needed. The reviewer reconciles the inventory against the code before
answering, so flags present in one but not the other are surfaced.

## Review questions

### 1. Does a current flag inventory exist, with an owner and a type per flag?

What good looks like: every flag is recorded with an owner and a type
(release, experiment, operational or kill-switch, permission); the
inventory matches the flags actually present in the provider and code.

What needs follow-up: flags exist with no owner or type; the inventory is
stale or absent; flags exist in code but not the inventory or vice versa.

### 2. Do temporary flags carry a retirement trigger, and are past-due flags retired?

What good looks like: release and experiment toggles carry an expiry or a
retirement trigger; once a flag has fully rolled out or been abandoned it
is removed in code and provider, leaving no pinned residue (feature-flags.no-hardcoded-flag).

What needs follow-up: short-lived flags linger indefinitely; a
fully-rolled-out flag is pinned on in code instead of removed; retired
flags still appear in the provider.

### 3. Are long-lived flags documented as such and reviewed, not retired by default?

What good looks like: operational kill switches and permission toggles are
documented as long-lived, with the behavior each governs, and reviewed
periodically rather than removed.

What needs follow-up: a kill switch is treated as stale and slated for
removal; a long-lived flag is undocumented and indistinguishable from
forgotten debt.

### 4. Do operational kill switches work without a deploy, and have they been tested?

A kill switch exists for the moment something is going wrong, so it must
work then.

What good looks like: the switch is reachable and changeable at the
provider with no code change or redeploy; it is documented with the
behavior it controls; a test demonstrates that flipping it changes
behavior.

What needs follow-up: changing the switch requires a redeploy; the switch
has never been tested; the behavior it controls is undocumented.

## Escalation to L3

If the review finds there is no shared taxonomy, no per-type lifecycle
policy, or no kill-switch testing cadence to check a flag against, that is
a strategy question for the feature-flags.strategy-adr ADR, not a per-flag fix. Escalate.
