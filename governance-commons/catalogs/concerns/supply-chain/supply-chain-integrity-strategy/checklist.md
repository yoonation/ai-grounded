---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.supply-chain.supply-chain-integrity-strategy-supply-chain-integrity-strategy"
title: "supply-chain.supply-chain-integrity-strategy review checklist: supply-chain integrity strategy ADR"
substrate-rule: "supply-chain.supply-chain-integrity-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
  - "Initial ADR adoption (consumer onboarding to substrate compliance)"
  - "Pull requests proposing ADR revisions"
  - "Substrate-recommended annual ADR review"
  - "Regulatory-change reviews (EU CRA full enforcement 2027-12-11; new in-scope regulation)"
  - "Profile transitions (consumer moving between substrate profiles)"
---

# supply-chain.supply-chain-integrity-strategy review checklist: supply-chain integrity strategy ADR

## How to use this binding

Reviewers answer every question below at ADR adoption, revision,
or periodic review. Unanswered or substrate-unacceptable answers
block ADR approval.

This checklist pairs with the
`supply-chain-integrity-strategy.madr.md` MADR decision framework
and with all SUPPLY-L1 and SUPPLY-L2 rules (whose policy
parameters the ADR pins).

## Review questions

### 1. Context: is the consumer's regulatory exposure documented?

Confirm Section 1 (Context) records:
- Product description sufficient for downstream substrate consumers
  to understand scope
- Regulatory exposure: US federal, EU CRA in-scope, HIPAA,
  PCI DSS, sector-specific, or substrate-accepted "none"
- Supply-chain threat-model summary referencing SLSA threats
  overview at minimum; substrate-recommended additional threats
  per consumer industry

### 2. SLSA Build Level target: is the chosen level substrate-accepted?

Confirm Section 2 (SLSA Build Level target) records:
- Chosen level (1, 2, 3, or higher) with rationale
- Substrate-recommended L2 for production-grade-baseline; L3 for
  stricter profiles; L1 with documented transition for greenfield-
  startup
- Deviation from substrate-recommended level requires documented
  rationale (e.g., engineering-investment timing, upstream
  dependency limitations)

### 3. Attestation scope: are the predicate types substrate-defensible?

Confirm Section 3 (Attestation scope) records:
- Which artifacts carry attestations (first-party builds always;
  third-party per substrate-recommended selectivity)
- Which predicate types are required (SLSA provenance at minimum;
  substrate-recommended additional types per stricter-profile
  policy)
- Whether negative attestations (vuln-scan, license-clearance)
  are required

### 4. SBOM cadence, format, and storage: are choices substrate-accepted?

Confirm Section 4 (SBOM cadence/format/storage) records:
- Cadence (every release substrate-required; substrate-accepted
  cadence on patches and dependency-change events)
- Format (CycloneDX 1.6 substrate-default; SPDX 2.3 substrate-
  accepted; both substrate-accepted)
- Storage surface (substrate-recommended primaries per
  supply-chain.attestation-and-sbom-retention)

### 5. Signing identity policy: are allowed signers explicit?

Confirm Section 5 (Signing identity policy) records:
- Allowed OIDC issuers (substrate-default accept list or
  consumer-specific narrowing)
- Signer-pattern allow-list (regex or exact identity claims)
- Signature schemes (Sigstore-keyless substrate-preferred; SSH
  and GPG substrate-accepted with rotation discipline)
- Substrate-recommended explicit per-environment signer allow-
  lists for stricter profiles

### 6. Transparency log selection: is the choice substrate-defensible?

Confirm Section 6 (Transparency log) records:
- Public-good Sigstore Rekor (substrate-default) OR
- Self-hosted Rekor (substrate-accepted with sovereignty rationale)
  OR
- Substrate-accepted equivalent with rationale

### 7. Retention horizon: does the horizon match supply-chain.attestation-and-sbom-retention profile defaults?

Confirm Section 7 (Retention horizon) records the retention window
and matches the consumer's profile expectation or documents
substrate-acceptable deviation rationale. Cross-references
supply-chain.attestation-and-sbom-retention retention discipline.

### 8. Exemption discipline: is the discipline substrate-defensible?

Confirm Section 8 (Exemption discipline) records:
- Criteria for accepting unverified artifacts (during transition,
  upstream lag, substrate-accepted edge cases)
- Maximum transition window per exemption (substrate-recommended
  six months for new dependency adoption)
- Approver identity per exemption (substrate-recommended
  engineering-management or substrate-recommended security-
  owner)
- Tracking mechanism (substrate-recommended committed exemptions
  file under repository's policy/ directory)

### 9. Review cadence: is the cadence substrate-acceptable?

Confirm Section 9 (Review cadence) records:
- Annual review at minimum
- Regulatory-change trigger (substrate-recommended explicit
  attention to EU CRA full-enforcement activation 2027-12-11)
- Profile-transition trigger
- Substrate-incident-response trigger (a post-incident review
  may surface ADR gaps)

### 10. Cross-references: are the L1 and L2 rules' policy parameters consistent with the ADR?

Confirm:
- supply-chain.slsa-provenance-verification binding's attestation-policy-defaults reference
  the ADR-documented SLSA Build Level and predicate types
- supply-chain.signature-verification binding's signer-policy reference matches the
  ADR-documented allowed signers
- supply-chain.sbom-presence-and-validity binding's SBOM format and storage match the ADR
- supply-chain.build-environment-isolation build environment posture matches the ADR's SLSA
  Build Level target
- supply-chain.attestation-and-sbom-retention retention window matches the ADR

Inconsistencies are findings; either the ADR or the operational
configuration is wrong, and the audit identifies which.

## Findings disposition

Critical findings (missing sections, substrate-unacceptable
choices, inconsistencies between ADR and operational
configuration) block ADR approval. Non-critical findings
(stale rationale, incomplete cross-references) generate action
items with substrate-recommended one-month resolution.
