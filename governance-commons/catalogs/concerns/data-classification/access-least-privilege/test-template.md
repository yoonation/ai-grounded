---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.data-classification.access-least-privilege-access-least-privilege"
title: "data-classification.access-least-privilege test template: need-to-know access and audit per class"
substrate-rule: "data-classification.access-least-privilege"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# data-classification.access-least-privilege test template: need-to-know access and audit per class

## How to use this binding

Access restriction is testable by attempting access as a principal that lacks
the required role and asserting denial, and by asserting access to the higher
classes is recorded. Adapt the principal and resource to the consumer's
authorization model.

## Scenario 1: a principal without the required role is denied

Attempt to read a confidential or restricted resource as a principal that does
not hold the role the policy requires for that class.

Pass criteria: the read is denied. A principal outside the need-to-know set
that can read the resource is the finding.

## Scenario 2: a principal with the required role is permitted

Attempt the same read as a principal that does hold the required role.

Pass criteria: the read is permitted, confirming the restriction is
need-to-know rather than a blanket denial that would break legitimate use.

## Scenario 3: access to a higher class is audited

Perform a read of a confidential or restricted resource and inspect the audit
trail.

Pass criteria: the access is recorded with the principal, the resource, and
the time. A higher-class access that leaves no audit record is the finding.
