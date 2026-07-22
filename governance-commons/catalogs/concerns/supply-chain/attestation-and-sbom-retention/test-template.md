---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.supply-chain.attestation-and-sbom-retention-attestation-and-sbom-retention"
title: "supply-chain.attestation-and-sbom-retention test template: attestation and SBOM retention with audit trail"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# supply-chain.attestation-and-sbom-retention test template: attestation and SBOM retention with audit trail

## How to use this binding

This binding describes verification that attestations and SBOMs are
retained per the consumer's profile-selected retention window, that
the retention store supports the consumer's incident-response query
pattern, and that the audit-trail integrity matches logging.integrity.

The template is framework-agnostic. Consumers implement the
retention-store query mechanism appropriate to their substrate-
recommended retention surface (OCI registry referrers API,
Dependency-Track API, Sigstore Rekor query, substrate-acceptable
equivalent).

## Scenario 1: retention scope covers each substrate-required artifact type

**Preconditions**
- Substrate-recommended retention surface is operational (OCI
  registry referrers, Dependency-Track, GitHub release assets,
  or substrate-acceptable equivalent)
- Consumer profile selected (production-grade-baseline by default)
- Sample list of recent production releases available

**Verification**
- For each sampled production release in the past 90 days, the
  retention store contains: SLSA provenance attestation
  (predicate type `https://slsa.dev/provenance/v1`), signature
  bundle (Sigstore or substrate-acceptable equivalent), SBOM in
  CycloneDX 1.6 JSON or SPDX 2.3 JSON
- For consumers on stricter profiles: additional substrate-
  required attestations per the supply-chain.supply-chain-integrity-strategy ADR (vuln-scan
  attestation, license-clearance attestation) are also present

**Substrate-recommended assertion shape**
- Assert: for each sampled release digest, query the retention
  surface and confirm the substrate-required artifact set is
  retrievable
- Assert: artifact-type completeness is 100% for the sampled
  window; substrate-recommended threshold below 100% blocks the
  audit

## Scenario 2: retention window matches profile target

**Preconditions**
- Retention store is operational and contains historical artifacts
- supply-chain.supply-chain-integrity-strategy ADR documents the consumer's retention window

**Verification**
- The verification step queries the retention surface for the
  oldest retained artifact
- The oldest retained artifact's age is greater than or equal to
  the profile-target retention window:
  - production-grade-baseline: at least three years (1095 days)
  - stricter profiles: at least seven years (2555 days)
  - looser profile: at least one year (365 days)
- Substrate-accepted alternative for consumers younger than the
  retention window: confirm retention discipline has been active
  since the consumer's earliest production release (every
  production release since inception is retained)

**Substrate-recommended assertion shape**
- Assert: retention-store oldest-artifact age >= profile target
  OR consumer-since-inception assertion holds

## Scenario 3: retrieval time meets the substrate-recommended incident-response threshold

**Preconditions**
- Retention store is operational
- Verification step has authenticated read access

**Verification**
- The verification step selects three randomly-chosen deployed
  artifact digests from the past 90 days
- For each digest, the step issues a retrieval query for the
  associated SLSA provenance, signature, and SBOM
- Each retrieval completes within five minutes (substrate-
  recommended threshold; stricter profiles tighter)

**Substrate-recommended assertion shape**
- Assert: for each sampled digest, all three artifact-type
  retrievals complete within five minutes
- Substrate-recommended: retrieval-time measurement retained in
  the audit record per this rule's retention policy

## Scenario 4: attestation-deployed-artifact consistency

**Preconditions**
- Retention store contains attestations for recent releases
- Deployed-artifact digest is observable at deployment surface
  (production cluster manifests, deployment audit log,
  substrate-acceptable equivalent)

**Verification**
- The verification step selects three recent production
  deployments
- For each deployment, the step compares the deployed artifact's
  digest against the digest declared in the retained SLSA
  provenance attestation and signature
- Mismatches surface as findings; substantial mismatches
  (multiple deployments diverging from attested digests) are
  incident-candidate signals

**Substrate-recommended assertion shape**
- Assert: for each sampled deployment, deployed digest equals
  attested digest equals signed digest

## Scenario 5: audit-trail integrity per logging.integrity

**Preconditions**
- Retention store's access log is operational and queryable
- Cross-reference logging.integrity tamper-evident-log integrity rule

**Verification**
- The verification step queries the retention store's access log
- Read access events record subject-identity, query pattern,
  and timestamp
- Write access is restricted to substrate-acceptable automation
  principals (CI/CD publishing on release); no unexpected
  identities appear in the write-access log
- Append-only or WORM property holds: prior log entries are not
  modifiable after write

**Substrate-recommended assertion shape**
- Assert: access-log records contain substrate-required fields
- Assert: write-access subject-identities are in the substrate-
  acceptable automation-principal allow-list
- Assert: append-only or WORM property is enforced by the
  underlying storage (object-versioning enabled, immutability
  lock active, or Sigstore Rekor transparency-log entry
  immutability holds)

## Out of scope for this test template

- SBOM accuracy (does the SBOM accurately enumerate the
  components in the artifact) is L2 reviewer territory and
  surfaced via supply-chain.attestation-and-sbom-retention review checklist sampled
  verification; the mechanical gate confirms retention, not
  accuracy
- Attestation validity beyond the substrate-required predicate-
  type and digest match is supply-chain.slsa-provenance-verification verification territory;
  this rule covers retention, not re-verification at retrieval
  time
- Retention-store vendor security posture (the trust assumption
  beneath the underlying object-storage or Rekor service) is
  outside this rule's scope; the supply-chain.supply-chain-integrity-strategy ADR documents
  the substrate-acceptable vendor-trust assumptions
