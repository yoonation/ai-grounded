---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.supply-chain.dependency-vetting-dependency-vetting"
title: "supply-chain.dependency-vetting review checklist: dependency vetting"
substrate-rule: "supply-chain.dependency-vetting"
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
  - "Pull requests adding a new production dependency to any manifest"
  - "Pull requests upgrading a production dependency across a major-version boundary"
  - "Pull requests substituting one production dependency for another"
  - "Periodic re-vetting at supply-chain.critical-dependency-audit audit cadence"
---

# supply-chain.dependency-vetting review checklist: dependency vetting

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the triggers. Unanswered items block merge. Answers
are recorded in the vetting artifact referenced by the pull
request (substrate-recommended path:
`docs/dependency-vetting/<ecosystem>-<dependency>-<version>.md`).

This checklist pairs with the dependency-management catalog's MADR
(`dependency-vetting-policy.madr.md`) for the policy-level
framework and with supply-chain.supply-chain-integrity-strategy for the consumer's strategy ADR.

## Review questions

### 1. Identity: is the dependency unambiguously identified?

Confirm the vetting artifact records the dependency's canonical
name, ecosystem (npm, PyPI, Maven, OCI registry, etc.), version
pin, and publisher identity. Substrate-recommended fields:
package-name, version, ecosystem, publisher-org, publisher-url.
The version pin is exact (not a range); cross-references dependency-management.pinned-versions
lockfile pinning.

### 2. Substrate-recognized signals: are supply-chain signals recorded?

Confirm the artifact addresses each substrate-recommended signal,
with the recorded value or an explicit "not available" note. The
signals: SBOM availability at upstream releases; SLSA provenance
attestation availability; signing posture (Sigstore, GPG, none);
OpenSSF Best Practices badge status; OpenSSF Scorecard score
(if available); most-recent-release date; maintainer activity
indicator (commits in last 90 days, distinct contributors in
last year). Missing signals are substrate-accepted when explicitly
recorded with "not available" plus a rationale.

### 3. Architectural fit: is the adoption rationale documented?

Confirm the artifact records: what problem the dependency solves;
what in-tree or alternative approaches were considered; why
those were rejected; exit strategy if the dependency is later
deprecated or compromised. Adoption without alternatives review
is substrate-rejected for production dependencies.

### 4. Tier classification: is the criticality tier assigned?

Confirm the artifact assigns a substrate-recommended criticality
tier (tier-1 critical, tier-2 important, tier-3 commodity) per
supply-chain.critical-dependency-audit criteria, with rationale referencing the
supply-chain.critical-dependency-audit classification criteria. The tier determines the
audit cadence per supply-chain.critical-dependency-audit.

### 5. Audit obligations: are ongoing obligations recorded?

Confirm the artifact documents the audit cadence implied by the
assigned tier (tier-1 quarterly, tier-2 semi-annual, tier-3
annual per substrate defaults), the responsible-party identity
for the audit, and the deprecation-trigger criteria.

### 6. License compatibility: is the upstream license compatible with the consumer's distribution model?

Confirm the artifact records the upstream license and any
compatibility analysis against the consumer's product distribution
model. Substrate-recommended: explicit compatibility statement
for restrictive licenses (AGPL, SSPL, BUSL); license-compatibility
review by the consumer's substrate-recommended legal or
compliance owner.

### 7. Approver identity: who signed off on the adoption?

Confirm the artifact records the approver identity, the approval
date, and substrate-accepted-evidence that the approver was
authorized by the consumer's policy to approve dependency
adoption (per authorization.least-privilege-role-design least-privilege role design).

### 8. Cross-reference completeness: are the artifact's substrate cross-references in place?

Confirm the vetting artifact links to: the consumer's supply-chain.supply-chain-integrity-strategy
ADR (supply-chain integrity strategy); the supply-chain.vulnerability-disclosure-response runbook
section that covers this dependency's advisory-response path;
the supply-chain.critical-dependency-audit tier inventory entry for this dependency. Broken
or missing cross-references block merge.

## Findings disposition

Findings from this checklist are recorded in the pull request
review thread and surface to the substrate-recommended dependency-
vetting log per supply-chain.attestation-and-sbom-retention retention discipline. Critical
findings (missing artifact, missing signals, no approver) block
merge; non-critical findings (incomplete cross-references,
outdated tier classification) escalate to engineering management
for resolution within a substrate-recommended two-week window.
