---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.supply-chain.build-environment-isolation-build-environment-isolation"
title: "supply-chain.build-environment-isolation review checklist: build environment isolation and reproducibility"
substrate-rule: "supply-chain.build-environment-isolation"
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
  - "Pull requests modifying CI build configuration"
  - "Pull requests modifying build runner platform or image"
  - "Pull requests modifying build-stage network policy"
  - "Periodic substrate-recommended quarterly build-environment audit"
  - "Reproducibility-verification cadence per profile"
---

# supply-chain.build-environment-isolation review checklist: build environment isolation and reproducibility

## How to use this binding

Reviewers answer every question below for the consumer's
production build environment. Findings block CI configuration
merge or surface remediation issues.

This checklist verifies the L2 structural posture; supply-chain.no-remote-execution-in-build
(no remote execution) catches the syntactic surface, this rule
catches the structural surface.

## Review questions

### 1. Runner ephemerality: are build runners ephemeral?

Confirm:
- Hosted-runner case: substrate-default GitHub-hosted, GitLab
  SaaS, or substrate-acceptable equivalent. Runners are
  ephemeral by platform default.
- Self-hosted runner case: container-per-job isolation, no host
  filesystem persistence, no cross-job state. Self-hosted runner
  configuration documents the isolation guarantees.

Persistent self-hosted runners are substrate-rejected for
production builds.

### 2. SLSA Build Level: does the build platform match supply-chain.supply-chain-integrity-strategy ADR target?

Confirm the build platform aligns with the SLSA Build Level
target documented in the supply-chain.supply-chain-integrity-strategy ADR:
- Production-grade-baseline: minimum Build L2 (build platform
  generates provenance, not the producer claiming the platform
  did)
- Stricter profiles (financial-services, healthcare,
  government): minimum Build L3 (hardened, hermetic, isolated)
- Looser profile (greenfield-startup): minimum Build L1 with
  substrate-required documented migration plan to L2 within
  six months

Mismatch between ADR target and operational reality is a finding.

### 3. Network policy during build: is the policy substrate-accepted?

Confirm the consumer's build-stage network policy:
- Fully hermetic (no external network access; all dependencies
  pre-fetched and digest-pinned) is substrate-preferred for
  stricter profiles
- Substrate-acceptable controlled network (access restricted to
  substrate-allowed upstream endpoints with documented allow-
  list) is substrate-accepted for production-grade-baseline
- Open-network builds are substrate-rejected for production
  paths

Network policy is operationalized via container network policy,
namespace isolation, or CI-platform-native controls.

### 4. Substrate-recognized dependencies in the build image: are they pinned and verified?

Confirm the build image's toolchain dependencies (compilers,
interpreters, package managers, build tools) are pinned by
digest per supply-chain.digest-pinned-artifacts and verified per supply-chain.signature-verification. Build
image base is itself digest-pinned to an attested upstream
image.

### 5. Reproducibility verification: is the cadence being met?

Confirm:
- Reproducibility verification is configured (substrate-
  recommended tooling: diffoscope for byte-level artifact
  comparison)
- Cadence matches the consumer's profile target
  (production-grade-baseline: semi-annual; stricter profiles:
  every release)
- Most recent verification result is within the cadence window
- Non-reproducible artifacts are tracked with substrate-
  acceptable rationale (near-reproducibility with documented
  drift sources) or as findings

### 6. Build-time secrets discipline: are secrets injected via substrate-accepted channels?

Confirm:
- Secrets used at build time (signing keys, registry credentials,
  dependency-fetch credentials) are injected via substrate-
  accepted channels (OIDC-bound short-lived credentials,
  CI-platform secrets store with substrate-acceptable access
  controls)
- No secrets in build environment variables visible in build
  logs
- Cross-references SECRETS-* catalog for secret-management
  discipline at build time

### 7. Build provenance generation: is provenance generated by the build platform?

Confirm the build platform generates SLSA provenance (the
producer does not claim the platform did). Substrate-recommended
patterns: slsa-github-generator for GitHub Actions builds;
substrate-acceptable equivalents for other platforms.

### 8. Substrate cross-references: are the L1 mechanical rules in effect?

Confirm:
- supply-chain.no-remote-execution-in-build (no remote execution) detection is active in CI
- supply-chain.digest-pinned-artifacts (digest pinning) detection is active for build-
  image references
- supply-chain.slsa-provenance-verification and supply-chain.signature-verification verification steps are in the
  deployment gate

## Findings disposition

Critical findings (persistent self-hosted runners in production;
SLSA Build Level below ADR target; open-network build policy)
block CI configuration merge until remediated. Non-critical
findings (dated reproducibility result, missing cross-reference
to supply-chain.supply-chain-integrity-strategy ADR) escalate to engineering management with
substrate-recommended two-week resolution.
