---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.supply-chain.signed-commit-and-protected-branch-signed-commit-and-protected-branch"
title: "supply-chain.signed-commit-and-protected-branch test template: signed-commit and protected-branch policy"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# supply-chain.signed-commit-and-protected-branch test template: signed-commit and protected-branch policy

## How to use this binding

This binding describes verification of signed-commit and
protected-branch policy on the consumer's release-bearing
branches. The verification consumes the hosting-provider's
substrate-recognized API surface (GitHub REST API, GitLab REST
API, Bitbucket REST API, substrate-acceptable equivalents).

## Scenario 1: protected-branch policy is in effect

**Preconditions**
- Repository hosts at a substrate-recognized provider with API
  access available to the verification step
- Substrate-recommended automation principal has read access to
  branch-protection settings

**Verification**
- The verification step queries the hosting provider's API for
  branch-protection settings on substrate-recognized release-
  bearing branches (main, release-*, configured patterns)
- The settings include: pull-request review required (minimum
  one reviewer distinct from author; stricter profile two);
  status-checks required including substrate L1 enforcement;
  push restriction excluding non-automation principals

**Substrate-recommended assertion shape**
- Assert: for each release-bearing branch, branch-protection is
  configured with substrate-recommended settings
- Assert: settings match the supply-chain.supply-chain-integrity-strategy ADR's documented
  policy

## Scenario 2: signed-commit verification active on recent release-branch commits

**Preconditions**
- Substrate-recommended verification-history window
  (substrate-default: most recent 50 commits on release branches)

**Verification**
- The verification step queries the hosting provider's commit-
  verification API for each commit in the window
- All commits show verified signature status

**Substrate-recommended assertion shape**
- Assert: in the most recent 50 release-branch commits, 100%
  show verified signature status
- Substrate-recommended: failure threshold below 100% blocks the
  audit; substrate-accepted exception for the substrate-
  acknowledged transition period during signing-scheme migration

## Scenario 3: release tags signature-verified

**Preconditions**
- Substrate-recommended release-tag history window (substrate-
  default: most recent 10 release tags)

**Verification**
- The verification step queries tag-signature status for each
  release tag in the window
- All tags show verified signature status

**Substrate-recommended assertion shape**
- Assert: in the most recent 10 release tags, 100% show verified
  signature status

## Scenario 4: administrator-bypass discipline

**Preconditions**
- Substrate-recommended audit-trail surface available (GitHub
  audit log, GitLab audit events, substrate-acceptable
  equivalent)

**Verification**
- The verification step queries the audit-trail for branch-
  protection bypass events in the substrate-recommended window
  (default: past 90 days)
- For each bypass event: substrate-acceptable bypass justification
  is recorded in the substrate-recommended bypass-log
  (substrate-default: `docs/bypass-log.md`)

**Substrate-recommended assertion shape**
- Assert: every audit-trail bypass event has a corresponding
  bypass-log entry with substrate-acceptable justification

## Scenario 5: service-account discipline

**Preconditions**
- Service-account credentials authorized for release-branch
  writes are inventoried

**Verification**
- The verification step inspects the consumer's service-account
  inventory (substrate-recommended path:
  `docs/service-accounts.md` or substrate-acceptable equivalent)
- Service accounts use OIDC-bound short-lived credentials
  (substrate-preferred) or substrate-acceptable rotated long-
  lived credentials

**Substrate-recommended assertion shape**
- Assert: service-account inventory exists; substrate-rejected
  patterns (personal access tokens for automation; unrotated
  long-lived service credentials) are absent

## Out of scope for this test template

- Reviewer-decision quality on protected pull requests is not a
  mechanical check
- Hosting-provider security (the substrate-trusted base for
  branch-protection enforcement) is upstream territory
