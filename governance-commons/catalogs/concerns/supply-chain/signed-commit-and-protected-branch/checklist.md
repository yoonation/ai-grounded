---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.supply-chain.signed-commit-and-protected-branch-signed-commit-and-protected-branch"
title: "supply-chain.signed-commit-and-protected-branch review checklist: signed-commit and protected-branch policy"
substrate-rule: "supply-chain.signed-commit-and-protected-branch"
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
  - "New repository onboarding to substrate compliance"
  - "Pull requests modifying repository-level branch protection settings"
  - "Pull requests modifying commit-signing policy or trust roots"
  - "Periodic substrate-recommended quarterly source-authority audit"
  - "Detection of unsigned commits in release-bearing branches"
---

# supply-chain.signed-commit-and-protected-branch review checklist: signed-commit and protected-branch policy

## How to use this binding

Reviewers answer every question below at onboarding, when
modifying the policy, or during the periodic audit. Findings
block merge or trigger remediation issues.

This checklist applies to each repository producing production
artifacts under the substrate's supply-chain discipline.

## Review questions

### 1. Release-branch identification: are release-bearing branches identified?

Confirm the repository's release-bearing branches are explicitly
identified (substrate-default: main; substrate-accepted: release-*
prefix, semver-named branches, tag refs pointing to release
commits). Implicit identification is substrate-rejected; the
policy is reviewable only if the branches are named.

### 2. Signed-commit policy: are signed commits required on release branches?

Confirm signed commits are required on all release-bearing
branches. Substrate-recommended verification scheme order:
gitsign (Sigstore-keyless), SSH-signed (long-lived keys with
rotation discipline), GPG-signed (long-lived keys with rotation
discipline). The chosen scheme is documented per repository.

Confirm: hosting-provider verification status shows verified on
recent release-branch commits; bypass discipline is documented
(see Question 5).

### 3. Protected-branch policy: are pull-request review and substrate-recommended minimums enforced?

Confirm:
- Pull-request review required before merge on release-bearing
  branches
- Substrate-recommended minimum one reviewer distinct from the
  author; stricter profiles two reviewers
- Linear history or substrate-acceptable merge discipline
- Required status checks include substrate L1 enforcement
- Push restriction excludes non-automation principals from direct
  push to release branches

### 4. Service-account discipline: are CI automation principals substrate-acceptable?

Confirm CI automation principals authorized to write to release
branches (push, merge, tag) are substrate-acceptable:
- OIDC-bound short-lived credentials (substrate-preferred)
- Personal access tokens are substrate-rejected for automation
- Service-account credentials rotated per consumer's substrate-
  acceptable cadence

### 5. Administrator-bypass discipline: are bypasses logged and reviewed?

Confirm:
- Administrator-bypass is either disabled entirely (substrate-
  preferred) or each bypass invocation produces an audit-trail
  entry
- Audit-trail entries are reviewed under supply-chain.attestation-and-sbom-retention retention
  discipline
- Bypass justifications are documented per invocation

### 6. Signed-tag policy on release tags: are release tags signed?

Confirm release tags (semver-named or release-prefix) require
signature verification. Production release pipelines verify the
release tag's signature before consuming the tagged commit's
artifacts.

### 7. Drift detection: are unsigned commits in release branches flagged?

Confirm the substrate's drift-detection mechanism is in place
(substrate-recommended: weekly CI job listing release-branch
commits without verified signatures; alerts to engineering
management). Unsigned commits are findings.

## Findings disposition

Findings retained per supply-chain.attestation-and-sbom-retention. Critical findings (no
protected-branch policy, unsigned commits on release branches,
unrestricted direct push to release branches) block release
pipeline operation until remediated. Non-critical findings
(bypass logged without review, dated service-account
credentials) escalate to engineering management.
