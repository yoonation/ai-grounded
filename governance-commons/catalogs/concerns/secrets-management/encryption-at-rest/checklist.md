---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.secrets-management.encryption-at-rest-encryption-at-rest"
title: "secrets-management.encryption-at-rest review checklist: secret material encrypted at rest with separate key management"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that introduce a new secret storage path"
  - "Code changes that touch the encryption key configuration of an existing secret store"
  - "Infrastructure changes affecting the KMS or HSM"
  - "Periodic security self-assessment of secret storage"
---

# secrets-management.encryption-at-rest review checklist: secret material encrypted at rest with separate key management

## How to use this binding

Reviewers answer every question below when reviewing changes
that affect secret storage, encryption key configuration, or
KMS integration. The questions apply to the secrets platform's
internal storage as well as any application-side storage of
encrypted material.

## Review questions

### 1. Encryption at rest: is the secret store's storage encrypted?

The underlying storage for the secrets platform (filesystem,
object store, database) must encrypt the contents at rest.

What good looks like: the secrets platform's storage backend
is encrypted (Vault with Consul storage uses Consul TLS plus
backend encryption; Vault with integrated storage uses native
encryption; AWS Secrets Manager uses AWS-managed encryption;
Kubernetes secrets via etcd encrypted with a KMS provider).
The encryption is verifiable from the platform's configuration.

What needs follow-up: secrets platform storage is on
unencrypted disk; encryption is enabled but the key is the
platform's default master key not under the consumer's control.

### 2. Key separation: is the encryption key managed separately from the encrypted secret?

The fundamental property: an attacker with access to the
encrypted secret data should not have access to the key that
decrypts it.

What good looks like: encryption key in a KMS or HSM separate
from the secret storage; envelope encryption pattern where the
data-encryption key is itself encrypted by the key-encryption
key held in KMS; the KMS access policy is distinct from the
secret-data access policy.

What needs follow-up: encryption key file lives in the same
directory as the encrypted secret data; encryption key
configured as a static value in the same configuration that
references the encrypted data; key and data backed up to the
same destination.

### 3. Key lifecycle: how is the encryption key rotated?

The data-encryption keys and the key-encryption keys should
both have rotation procedures, even if their cadences differ.

What good looks like: KEK rotated annually or per consumer
policy; DEK rotated on KEK rotation via re-encryption; rotation
is non-disruptive to operations; rotation is automated where
the KMS supports it.

What needs follow-up: encryption keys are static and never
rotated; rotation requires re-encrypting all data with the new
key but the procedure has never been exercised; rotation cadence
is not defined.

### 4. KMS choice: is the KMS appropriate for the secret sensitivity?

The substrate-recognized options span a spectrum.

What good looks like: cloud-provider KMS (AWS KMS, GCP KMS,
Azure Key Vault) for application-tier secrets; HSM (AWS
CloudHSM, GCP Cloud HSM, Azure Dedicated HSM) for high-
sensitivity material like root signing keys or PCI-regulated
keys; the KMS choice matches the consumer's secrets-management.platform-selection ADR
and any relevant compliance requirements.

What needs follow-up: KMS choice not documented; the choice
does not match the sensitivity (e.g., production signing keys
in non-HSM software-only KMS); compliance regimes (PCI, HIPAA,
FIPS-140) have requirements the chosen KMS does not satisfy.

### 5. Region and replication: where does the key live?

Key residence has data-sovereignty and operational availability
implications.

What good looks like: KMS region matches data residency
requirements; multi-region replication is configured per
disaster-recovery requirements; cross-region keys are explicitly
chosen (with the trade-off documented).

What needs follow-up: key region was not chosen deliberately;
single-region key without multi-region failover for a service
with multi-region availability requirements; key in a region
that violates data residency requirements.

### 6. Access path: who can decrypt versus who can use the result?

Decrypt permission on the KMS is a powerful permission. It
should be narrow.

What good looks like: decrypt permission granted to the
secrets platform's service identity, not to the consumer
workloads; consumer workloads access decrypted secrets via the
secrets platform (which audits) rather than via direct KMS
decrypt; KMS access logs flow to security operations.

What needs follow-up: many workloads have direct decrypt
permission on the KMS, bypassing the secrets platform's audit
trail; KMS access logs not enabled; emergency-access policies
on the KMS are overly broad.

### 7. Cryptographic algorithm and parameters: are the choices substrate-acceptable?

Most platforms use sensible defaults; review confirms the
defaults are in use rather than weakened.

What good looks like: AES-256-GCM or equivalent authenticated
encryption; HMAC-SHA-256 or stronger for integrity; key sizes
at the platform's recommended defaults; no legacy or
deprecated algorithms (3DES, RC4, MD5 for HMAC).

What needs follow-up: algorithm or key size weakened from
default for operational reasons that are not documented;
deprecated algorithms still in use; envelope encryption uses an
unauthenticated cipher mode where authenticated is available.

### 8. Backup encryption: are backups of secret data also encrypted?

A backup that is not encrypted is the encrypted-at-rest
property defeated.

What good looks like: backups of the secret store are
encrypted; the backup encryption key is also under KMS control;
backup restoration procedures are tested and verified to
maintain encryption properties.

What needs follow-up: backups exported in plaintext for
"easier restoration"; backup encryption uses the same key as
the secret data itself (no separation); backup retention
policies are unclear, leading to unencrypted historical
exposure.

## Reviewer attestation

```
secrets-management.encryption-at-rest review checklist: complete
- Encryption at rest: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Key separation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Key lifecycle: PASS / FOLLOW-UP / EXEMPT-with-rationale
- KMS choice: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Region and replication: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Access path: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cryptographic algorithm: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Backup encryption: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

## Cross-reference

- Substrate rule: secrets-management.encryption-at-rest in catalogs/concerns/secrets-management.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/secrets-management/encryption-at-rest-good.md
- Anti-patterns: examples/secrets-management/encryption-at-rest-anti-pattern.md
