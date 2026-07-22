---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.key-management-design-key-management-design"
title: "infrastructure-misconfiguration.key-management-design review checklist: key-management design"
substrate-rule: "infrastructure-misconfiguration.key-management-design"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 1 (2026-05-31). Substrate-author review required for stable promotion."
review-triggers:
  - "New customer-managed key (CMK) declaration"
  - "Key-policy modification that broadens scope or adds principals"
  - "Key rotation policy change or disablement"
  - "Multi-region or multi-account key replication declaration"
  - "Change of data-classification tier requiring key-management uplift"
  - "Annual key-management posture review per substrate-recommended cadence"
---

# infrastructure-misconfiguration.key-management-design review checklist: key-management design

## How to use this binding

Reviewers answer every question below when reviewing IaC-declared
key-management resources (AWS KMS keys + aliases + grants, Azure
Key Vault keys, GCP Cloud KMS key rings + keys, Kubernetes SealedSecrets
or external-secrets KMS references). infrastructure-misconfiguration.data-resource-encryption-at-rest verifies encryption is
declared; this L2 review verifies the key-management posture *behind*
the encryption is deliberate.

A consumer may legitimately operate at a tier where provider-managed
keys (AWS SSE-S3, GCS provider-default, Azure Storage default) are
sufficient. This checklist's first question determines the tier; the
remaining questions apply only when CMK is in use.

## Review questions

### 1. Is the key-management tier appropriate to the data-classification?

- Has the consumer's data-classification scheme been applied to the
  resources this PR encrypts (relates to infrastructure-misconfiguration.governance-tagging and the
  forthcoming data-classification concern)?
- Does the resource's classification require CMK per the consumer's
  documented matrix, or is provider-managed encryption sufficient?
- Where CMK is required, does the IaC declaration use a CMK rather
  than the provider-default key? (infrastructure-misconfiguration.data-resource-encryption-at-rest catches absence; this
  question catches a CMK requirement met with a provider-default
  key.)

### 2. Are key policies scoped?

For each KMS key declared:

- Is the key policy's root-account grant (AWS `kms:*` to
  arn:aws:iam::ACCT:root) present and intentional? Removing root
  grant is a known foot-gun (key recovery becomes impossible);
  consumers retaining root grant document the recovery path.
- Are non-root principals scoped (specific role ARNs or specific
  service principals, not `*`)?
- Are key-administrator and key-user roles separated (two distinct
  IAM roles in the key policy: one to manage the key, another to
  use it cryptographically)?
- For grants on top of the key policy, are the grant operations and
  constraints scoped per the grantee's actual usage?

### 3. Is rotation configured?

- Is `enable_key_rotation` set to `true` for AWS KMS symmetric keys?
- For Azure Key Vault, is the key's rotation policy configured with
  an interval the consumer's regulatory regime requires?
- For GCP Cloud KMS, is `rotation_period` set per consumer policy?
- For asymmetric keys, is the rotation policy documented (since
  automatic rotation is not always available; consumer-side
  rotation procedures may apply)?

### 4. Are keys scoped per workload, per region, per environment?

- Is a single key shared across multiple workloads, or does each
  workload have its own key?
- For multi-region resources, are keys regional (the substrate-
  recommended pattern) rather than multi-region replicas (which
  trade convenience for blast-radius)?
- Are production and non-production environments using distinct
  keys?
- Where keys are shared (a single key encrypting all S3 buckets in
  an account), is the shared scope justified by operational
  simplicity and bounded by complementary controls (the bucket
  policy restricts access; the key policy restricts use)?

### 5. Is the key's downstream usage auditable?

- Is the key's use logged via CloudTrail data events (AWS) or the
  equivalent Azure / GCP audit-log configuration (relates to
  infrastructure-misconfiguration.audit-and-flow-logging-enabled)?
- For high-sensitivity keys, is dual control (split-knowledge,
  N-of-M approval) configured where the consumer's regulatory
  regime requires it?

### 6. Is the key's lifecycle protected?

- Is deletion protected (AWS KMS pending-deletion window set to
  the substrate-recommended 30 days minimum; Azure Key Vault
  purge protection enabled; GCP Cloud KMS keys protected from
  destruction by IAM policy)?
- For keys whose loss would render encrypted data unrecoverable,
  is the recovery procedure documented and tested?

### 7. Has cross-tooling KMS coverage been reviewed?

- Have the IaC scanner suite's KMS-related findings (Checkov
  CKV_AWS_7 KMS rotation, CKV_AWS_33 KMS key policy, CKV_AZURE_42
  Key Vault purge protection, etc) been triaged?
- Where the L1 mechanical layer flags an apparent issue resolved
  intentionally at L2 (e.g. shared key for a documented reason),
  is the L1 suppression accompanied by a comment referencing this
  checklist's review record?

## Findings disposition

PASS / PASS with note / REWORK / EXCEPTION, per the infrastructure-misconfiguration.least-privilege-iac-iam
disposition section. Key-management exceptions persist longer than
most other exceptions (changing a key is operationally expensive),
so the substrate-recommended exception review cadence for infrastructure-misconfiguration.key-management-design
is annual with documented re-evaluation triggers (regulatory change,
data-classification change, breach event).

## Cross-references

- infrastructure-misconfiguration.data-resource-encryption-at-rest (mechanical encryption-at-rest declaration that this
  L2 review's key-management posture sits behind)
- SECRETS-L1-* and SECRETS-L2-* (secrets management concern; KMS
  is one mechanism for secret encryption-at-rest)
- The forthcoming `data-classification` concern: data-classification
  drives the key-management tier requirement
- NIST SP 800-53 SC-12 (cryptographic key establishment and
  management), SC-13 (cryptographic protection), SC-28 (protection
  of information at rest)
- NIST SP 800-57 Part 1 (recommendation for key management)
