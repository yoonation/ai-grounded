---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.supply-chain.attestation-and-sbom-retention-attestation-and-sbom-retention"
title: "supply-chain.attestation-and-sbom-retention review checklist: attestation and SBOM retention with audit trail"
substrate-rule: "supply-chain.attestation-and-sbom-retention"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Pull requests modifying retention policy or storage configuration"
  - "Pull requests modifying access controls on retention store"
  - "Periodic substrate-recommended quarterly retention audit"
  - "Post-incident review verifying retention served incident response"
---

# supply-chain.attestation-and-sbom-retention review checklist: attestation and SBOM retention with audit trail

## How to use this binding

Reviewers answer every question below at policy changes or during
the periodic audit. Findings block storage configuration changes
or surface remediation issues.

This checklist verifies that the consumer's incident-response
capability is supported by the retention discipline: given a
deployed artifact's digest or version, the consumer can retrieve
the associated attestations and SBOM within minutes.

## Review questions

### 1. Retention window: does the window match the consumer's profile?

Confirm the retention window matches the consumer's substrate-
recommended profile target:
- Production-grade-baseline: three years (matches typical
  regulatory minima)
- Stricter profiles (financial-services, healthcare, government):
  seven years (aligns with industry-typical regulatory horizons)
- Looser profile (greenfield-startup): one year

Consumer deviation from the substrate-recommended default is
substrate-accepted with documented rationale in the supply-chain.supply-chain-integrity-strategy
ADR.

### 2. Retention scope: are all substrate-recognized attestation types covered?

Confirm the retention store contains, per production release:
- SLSA provenance attestation (per supply-chain.slsa-provenance-verification)
- Signature artifacts and signing certificate (per supply-chain.signature-verification)
- SBOM in CycloneDX or SPDX format (per supply-chain.sbom-presence-and-validity)
- Substrate-recommended additional attestations (vuln-scan
  results, license-clearance attestations) if required by
  consumer's supply-chain.supply-chain-integrity-strategy ADR

Missing artifact types for recent releases are findings.

### 3. Storage surface: is the storage substrate-recommended or substrate-accepted?

Confirm the primary storage surface:
- OCI registry referrers-attached attestations for container-
  based releases (substrate-recommended)
- GitHub release assets for GitHub-released artifacts
- Dependency-Track for substrate-recommended-retention consumers
- Substrate-accepted equivalent with documented rationale

### 4. Audit-trail integrity: is the store append-only or write-once-read-many?

Confirm:
- Sigstore Rekor's transparency log is referenced for attestation
  immutability (substrate-default model)
- Self-hosted retention stores satisfy append-only or WORM
  property (substrate-accepted alternatives: object-storage
  versioning, immutability locks)
- Write access to the retention store is restricted to substrate-
  acceptable automation principals (CI/CD publishing on release;
  cross-references authorization.least-privilege-role-design least-privilege role design)

### 5. Read access logging: are access events logged per logging.integrity integrity?

Confirm:
- Read access events to the retention store record subject-
  identity, query pattern, and timestamp
- Access logs are themselves retained per logging.retention-policy retention
  policy
- Access logs have tamper-evident storage per logging.integrity integrity

### 6. Retrieval-time test: can the consumer retrieve a deployed artifact's attestations within minutes?

Confirm:
- Substrate-recommended retrieval test executed in the audit
  window: given a randomly-selected deployed artifact's digest,
  the auditor can retrieve the associated SLSA provenance,
  signature, and SBOM within five minutes
- Test results retained per this rule's retention policy
- Failed retrieval (artifact deployed but attestation
  unavailable) is a finding

### 7. Attestation-deployment consistency: do retained attestations match deployed artifact digests?

Confirm:
- Spot-check several recent releases: deployed artifact digest
  matches the digest in the retained SLSA provenance attestation
- Spot-check several recent releases: deployed artifact digest
  matches the digest in the retained signature
- Deployed artifact's SBOM components match the artifact's
  actual component composition (sampled verification)

Mismatches are findings; substantial mismatches are incident-
candidate signals.

### 8. Exemption activity: are recorded exemptions current and tracked?

Confirm:
- Exemption files (from supply-chain.slsa-provenance-verification and supply-chain.signature-verification) are
  reviewed; exemptions past their transition-end-date are
  escalated
- Substrate-recommended quarterly review of exemption activity

## Findings disposition

Critical findings (missing retention for in-policy releases;
non-append-only storage; failed retrieval-time test; deployed-vs-
retained digest mismatch) block continued release activity until
remediated. Non-critical findings (exemption activity drift,
incomplete cross-references) escalate to engineering management
with substrate-recommended two-week resolution.
