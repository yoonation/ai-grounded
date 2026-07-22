---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.data-classification.encryption-per-class-encryption-per-class"
title: "data-classification.encryption-per-class review checklist: encryption at rest and in transit per class"
substrate-rule: "data-classification.encryption-per-class"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "A new classified data store or transport path is introduced"
  - "A change to a store's encryption configuration"
  - "A data element's class is raised so a stronger encryption standard applies"
---

# data-classification.encryption-per-class review checklist: encryption at rest and in transit per class

## How to use this binding

Encryption decouples the confidentiality of classified data from the security
of the medium that holds or carries it. This review confirms the per-class
encryption standard is defined and in force. This rule owns the per-class
requirement; the cryptographic mechanism and key management are owned by the
security concerns, and provision-time enforcement of at-rest encryption is
owned by infrastructure-misconfiguration.

## Review questions

### 1. Is at-rest encryption enabled for stores holding the higher classes?

What good looks like: stores holding confidential or restricted data have
at-rest encryption enabled, with keys managed per policy (a managed KMS or
equivalent, not a hardcoded key).

What needs follow-up: a confidential or restricted store with encryption
disabled, or one encrypted with a key managed outside policy.

### 2. Does classified data cross only encrypted transport?

What good looks like: classified data crosses TLS for external paths and
encrypted transport for internal paths per its class; plaintext connections
to classified stores are rejected.

What needs follow-up: a classified path that permits a plaintext connection,
or an internal hop that carries restricted data in the clear.

### 3. Is the per-class encryption standard recorded and enforced at provision time?

What good looks like: the policy records which classes require which
encryption standard, and the at-rest setting is enforced when the store is
provisioned (cross-referencing infrastructure-misconfiguration).

What needs follow-up: encryption applied ad hoc per store with no recorded
per-class standard, or an at-rest setting that can be provisioned off.

## When to escalate to L3

Escalate to data-classification.data-classification-policy when the per-class encryption standard or the key
management approach is a policy decision to record: which classes require
which strength, and where keys live.
