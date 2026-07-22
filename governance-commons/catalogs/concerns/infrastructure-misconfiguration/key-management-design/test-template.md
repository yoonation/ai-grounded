---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.infrastructure-misconfiguration.key-management-design-key-management-design"
title: "infrastructure-misconfiguration.key-management-design test template: key-management design"
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
framework-agnostic: true
---

# infrastructure-misconfiguration.key-management-design test template: key-management design

## How to use this binding

Key-management tests exercise the key-policy and rotation
posture of IaC-declared KMS resources (AWS KMS keys, Azure Key
Vault keys, GCP Cloud KMS keys). Tests are framework-agnostic:
consumers running policy-evaluation tooling (AWS KMS policy
simulator via IAM Policy Simulator, Azure RBAC checks against
Key Vault, GCP `policy-troubleshooter` for keys) implement the
scenarios using the consumer's tooling.

Substrate-recommended cadence: pre-merge for every PR that
declares or modifies a KMS resource; annual full-suite execution
as part of the infrastructure-misconfiguration.key-management-design review-checklist cadence; on-trigger
re-execution when the data-classification matrix changes.

## Scenario 1: CMK is in use for resources requiring it per classification

**Intent:** Where the consumer's data-classification matrix
requires CMK, the IaC declares a customer-managed key rather
than relying on provider-default keys.

**Test approach:**

1. Enumerate every data-bearing resource and read its
   data-sensitivity tag (per infrastructure-misconfiguration.governance-tagging).
2. Cross-reference the data-sensitivity to the consumer's
   classification-to-key-tier matrix.
3. For each resource requiring CMK, assert the resource's
   encryption attribute references a customer-managed key, not
   a provider-managed default alias (`alias/aws/s3`,
   `alias/aws/ebs`, etc.).

**Pass criterion:** Every resource requiring CMK has a CMK
reference.

## Scenario 2: Key policies scope non-root principals

**Intent:** A KMS key policy that grants `kms:*` to a wildcard
principal or to the root of multiple accounts has effectively
no isolation.

**Test approach:**

1. Enumerate every KMS key's key policy.
2. For each policy statement, assert the Principal is a
   specific role ARN, a specific service principal, or the
   local-account root (the standard recovery grant).
3. Assert no statement grants `kms:*` to a wildcard principal
   without conditions.

**Pass criterion:** Every key policy statement has a bounded
Principal.

## Scenario 3: Key administrator and key user roles are separated

**Intent:** A single principal that can both manage the key
(rotate, disable, schedule deletion) and use the key
(encrypt, decrypt, re-encrypt) has elevated risk; separation of
duties is the substrate-preferred pattern.

**Test approach:**

1. Enumerate every KMS key policy.
2. Identify principals granted key-administrator actions
   (`kms:Create*`, `kms:Disable*`, `kms:EnableKey`,
   `kms:GetKeyPolicy`, `kms:PutKeyPolicy`,
   `kms:ScheduleKeyDeletion`, `kms:Update*`).
3. Identify principals granted key-user actions (`kms:Encrypt`,
   `kms:Decrypt`, `kms:ReEncrypt*`, `kms:GenerateDataKey*`).
4. Assert the two principal sets do not overlap, or that the
   overlap is documented in the consumer's separation-of-duties
   exception list.

**Pass criterion:** Key-administrator and key-user roles are
distinct, or the overlap is documented.

## Scenario 4: Rotation is configured

**Intent:** Symmetric KMS keys support automatic rotation;
asymmetric keys require a documented rotation procedure.

**Test approach:**

1. Enumerate every KMS key.
2. For symmetric keys: assert `enable_key_rotation = true`
   (AWS), `rotation_policy` is configured (Azure), or
   `rotation_period` is set (GCP).
3. For asymmetric keys: assert there is a documented rotation
   procedure linked from the key's tags or the consumer's
   key-inventory documentation.

**Pass criterion:** Every key has rotation configured (automatic
or documented procedural).

## Scenario 5: Keys are scoped per workload, per region, per environment

**Intent:** A single key shared across unrelated workloads
defeats the substrate's blast-radius-containment intent.

**Test approach:**

1. Build a map of key → resources that reference the key.
2. For each key, assert the referenced resources are within a
   single workload boundary (substrate-defined: a single
   service, or a closely-related set of services owned by the
   same team).
3. Assert the same key is not referenced across production
   and non-production environments.

**Pass criterion:** Every key's reference set is within a single
workload and environment.

## Scenario 6: Key deletion is protected

**Intent:** Loss of a key holding the encryption material for
data-bearing resources renders the data unrecoverable. The
substrate's bias is layered protection.

**Test approach:**

1. Enumerate every KMS key.
2. Assert the deletion window is at the substrate's minimum
   (AWS: 30 days; Azure: purge-protection enabled; GCP:
   deletion prevention via IAM policy denying
   `cloudkms.cryptoKeyVersions.destroy`).
3. For keys holding critical encryption material, assert there
   is a documented recovery procedure (separately-stored key
   backup where the consumer's policy permits export, or a
   documented data-loss acceptance posture).

**Pass criterion:** Every key has the substrate's minimum
deletion protection.

## Scenario 7: Key usage is audited

**Intent:** Key use produces an audit trail; the trail is
captured in the substrate's logging surface.

**Test approach:**

1. For AWS, assert CloudTrail data events are enabled for KMS
   for the consumer's keys (per infrastructure-misconfiguration.audit-and-flow-logging-enabled).
2. For Azure, assert Key Vault diagnostic settings emit audit
   logs to the consumer's logging surface.
3. For GCP, assert Cloud KMS data-access audit logs are enabled
   for the consumer's project.

**Pass criterion:** Every key emits audit events to the
consumer's logging surface.

## Outcome

The L2 test suite for infrastructure-misconfiguration.key-management-design succeeds when every scenario
above passes against the IaC's current state. Failures are
treated as PR-blocking findings unless the IaC is on the
consumer's documented exception list per the infrastructure-misconfiguration.key-management-design review-
checklist's exception governance.
