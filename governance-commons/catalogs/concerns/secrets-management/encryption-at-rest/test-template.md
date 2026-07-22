---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.secrets-management.encryption-at-rest-encryption-at-rest"
title: "secrets-management.encryption-at-rest test template: secret material encrypted at rest"
substrate-rule: "secrets-management.encryption-at-rest"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# secrets-management.encryption-at-rest test template: secret material encrypted at rest

## How to use this binding

These tests verify the encryption-at-rest properties of the
secrets platform storage. They mix infrastructure-as-code
assertions (Terraform/OpenTofu plan inspection, cloud API
verification) with platform-state queries.

## Scenario 1: Secret storage backend reports encryption enabled

**Preconditions**
- The secrets platform is deployed
- The infrastructure-as-code (or equivalent) declares
  encryption at rest

**Action**
- Query the platform's configuration API for the storage
  encryption status

**Expected**
- The query confirms encryption at rest is enabled
- The encryption key reference matches the IaC declaration
- The configuration is not in an "encryption pending" or
  partial state

## Scenario 2: Encryption key is held in a separate KMS

**Preconditions**
- The platform is configured to use a KMS-held key for
  encryption

**Action**
- Verify the KMS resource exists and is in a different
  trust boundary from the secret data store
- Verify the KMS access policy is distinct from the data-
  store access policy

**Expected**
- The KMS key is in a separate account, project, or vault
  appropriate to the platform
- The principals with KMS decrypt are not the principals
  with data-store read

## Scenario 3: Envelope encryption produces distinct DEKs

**Preconditions**
- The platform uses envelope encryption (DEK per secret
  or per data block, wrapped by a KEK in KMS)

**Action**
- Inspect the storage of two distinct secrets
- Compare their DEKs

**Expected**
- Each secret has a distinct DEK
- DEKs are themselves stored encrypted (not in plaintext)
- The KEK can decrypt either DEK; without KEK access,
  neither DEK is recoverable

## Scenario 4: Direct data-store read produces ciphertext, not plaintext

**Preconditions**
- A secret with a known plaintext value exists
- The test has read access to the raw storage layer (this is
  test-only; production should not grant this)

**Action**
- Read the raw storage entry for the secret
- Inspect the bytes

**Expected**
- The raw bytes are ciphertext, not the plaintext secret value
- A search for the plaintext value across the raw storage
  returns no hits

## Scenario 5: KEK rotation produces re-encrypted DEKs

**Preconditions**
- An envelope-encrypted secret exists
- KEK rotation is initiated at the KMS

**Action**
- Trigger KEK rotation
- Wait for the platform's re-encrypt job to run

**Expected**
- The secret remains readable through the platform's normal
  API
- The DEK is now wrapped by the new KEK
- The old KEK can be deactivated without breaking secret
  reads

## Scenario 6: KMS unavailability produces fail-closed behavior

**Preconditions**
- A secret exists; KMS is reachable

**Action**
- Simulate KMS unavailability (network partition or KMS
  policy change blocking access)
- Attempt to read a secret that requires KMS decryption

**Expected**
- The read fails; the application cannot return a stale
  plaintext "just in case"
- The platform's audit log records the failure
- KMS recovery restores read functionality

## Scenario 7: Backup is encrypted

**Preconditions**
- The secrets platform supports backup; backup is configured

**Action**
- Initiate a backup
- Inspect the backup artifact

**Expected**
- The backup is encrypted
- The backup's encryption key is distinct from the platform's
  data-encryption key (or is the same KMS-held KEK with
  appropriate audit trail)
- Restoration from the backup requires the encryption key

## Scenario 8: Cross-region replication preserves encryption properties

**Preconditions**
- The platform replicates secret data across regions
- Each region has KMS keys in that region's KMS

**Action**
- Inspect a secret's storage representation in the primary
  region
- Inspect the replicated representation in the secondary
  region

**Expected**
- Both representations are ciphertext
- The secondary region's representation can be decrypted by
  the secondary region's KMS (not dependent on cross-region
  KMS access)
- Failover does not break secret reads

## Test attestation

```
secrets-management.encryption-at-rest test suite: PASSING
- Scenario 1 (encryption enabled at backend): PASS
- Scenario 2 (KMS separate from data store): PASS
- Scenario 3 (envelope encryption with distinct DEKs): PASS
- Scenario 4 (raw read produces ciphertext): PASS
- Scenario 5 (KEK rotation re-encrypts DEKs): PASS
- Scenario 6 (KMS unavailability fail-closed): PASS
- Scenario 7 (backup encrypted): PASS
- Scenario 8 (cross-region replication encrypted): PASS
```

## Cross-reference

- Substrate rule: secrets-management.encryption-at-rest
- Review checklist: checklist.md
- Good examples: examples/secrets-management/encryption-at-rest-good.md
