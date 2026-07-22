---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.supply-chain.build-environment-isolation-build-environment-isolation"
title: "supply-chain.build-environment-isolation test template: build environment isolation and reproducibility"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# supply-chain.build-environment-isolation test template: build environment isolation and reproducibility

## How to use this binding

This binding describes verification of the consumer's build
environment posture: runner ephemerality, SLSA Build Level
alignment, network policy, and reproducibility verification.

## Scenario 1: build runners are ephemeral

**Preconditions**
- CI build configuration is available to the verification step

**Verification**
- The verification step parses the CI build configuration
- For hosted-runner cases (substrate-default): the configuration
  declares a hosted runner; ephemerality is platform default
- For self-hosted runner cases: the configuration declares
  container-per-job isolation OR an isolated VM-per-job pattern;
  no host filesystem persistence

**Substrate-recommended assertion shape**
- Assert: runner configuration matches substrate-recognized
  ephemeral pattern
- Substrate-rejected: persistent self-hosted runner without
  isolation in production paths

## Scenario 2: SLSA Build Level matches supply-chain.supply-chain-integrity-strategy ADR

**Preconditions**
- supply-chain.supply-chain-integrity-strategy ADR documents the target SLSA Build Level
- Substrate-recognized SLSA Build Level evidence is available
  (e.g., provenance attestation surface from supply-chain.slsa-provenance-verification)

**Verification**
- The verification step inspects the most recent production
  release's SLSA provenance attestation
- The attested build level matches or exceeds the supply-chain.supply-chain-integrity-strategy
  ADR's documented target

**Substrate-recommended assertion shape**
- Assert: attestation's `builder.builderDependencies` or
  substrate-acceptable equivalent indicates the documented
  build platform
- Assert: attested SLSA Build Level >= ADR target

## Scenario 3: network policy during build is substrate-accepted

**Preconditions**
- CI build configuration is parseable

**Verification**
- The verification step parses build-stage network policy
- Configuration matches substrate-accepted pattern: fully
  hermetic (no external network during build), or substrate-
  acceptable controlled-network (allow-list of upstream endpoints)
- Open-network production builds are substrate-rejected

**Substrate-recommended assertion shape**
- Assert: build configuration declares either hermetic mode or a
  documented network allow-list
- Assert: no production build stage has unrestricted network
  access

## Scenario 4: reproducibility verification cadence is being met

**Preconditions**
- Substrate-recommended reproducibility-verification record
  directory (substrate-default:
  `docs/reproducibility-verification/`)

**Verification**
- Records exist within the consumer's profile cadence (every
  release for stricter profiles; semi-annual for
  production-grade-baseline; substrate-acceptable deviation per
  the supply-chain.supply-chain-integrity-strategy ADR)
- Each record documents the verification method (diffoscope or
  substrate-acceptable equivalent), the two artifacts compared,
  and the result (byte-identical, near-reproducible with
  documented drift sources, or non-reproducible)

**Substrate-recommended assertion shape**
- Assert: most-recent reproducibility-verification record is
  within the substrate-recommended cadence window
- Assert: non-reproducible records have substrate-acceptable
  rationale or trigger an incident response

## Scenario 5: build-time secrets discipline

**Preconditions**
- Build configuration is parseable for environment variables
  and secret references

**Verification**
- Build configuration references secrets via substrate-accepted
  channels (OIDC-bound credentials; CI-platform secret stores
  with substrate-acceptable access controls)
- Build logs do not surface secret values (substrate-recommended:
  CI-platform secret masking enabled)

**Substrate-recommended assertion shape**
- Assert: no build-stage environment variable contains a
  substrate-recognizable secret pattern (substrate-defers to
  SECRETS-L1-* for the specific secret-detection patterns)

## Out of scope for this test template

- Subjective build-platform-quality assessment beyond SLSA Build
  Level alignment (e.g., security-engineering depth of the
  build platform) is L2 reviewer territory
- Build-platform-vendor security (the trust assumption beneath
  hosted build platforms) is outside this rule's scope
