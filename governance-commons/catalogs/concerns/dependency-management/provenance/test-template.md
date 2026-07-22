---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.dependency-management.provenance-provenance"
title: "dependency-management.provenance test template: dependency provenance verification"
substrate-rule: "dependency-management.provenance"
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

# dependency-management.provenance test template: dependency provenance verification

## How to use this binding

Provenance tests run in CI on dependency changes and on a
schedule. They verify both the install-time properties (hash
check, signature check) and the configuration properties
(registry URLs, scope mappings) that prevent dependency
substitution.

## Scenario 1: Lockfile install verifies integrity hashes

**Preconditions**
- The project has a committed lockfile with integrity hashes
- CI runs the strict-install command for the ecosystem

**Action**
- Run the strict install in a clean environment

**Expected**
- The install succeeds
- Every dependency's downloaded artifact hash matches the
  lockfile hash
- The install command does not modify the lockfile

## Scenario 2: Corrupted artifact fails the install

**Preconditions**
- A registry proxy or local cache is configured
- The cache contains a known-corrupted artifact (test-injected
  byte modification) for one dependency

**Action**
- Run the strict install pointing at the corrupted cache

**Expected**
- The install fails on the corrupted dependency
- The error message identifies the hash mismatch
- The build is blocked

## Scenario 3: Signed-package provenance is verified where available

**Preconditions**
- The project includes a direct dependency that publishes
  Sigstore-backed provenance (npm provenance, PyPI digital
  attestation, or equivalent)
- CI is configured to verify provenance for this dependency

**Action**
- Run the install with provenance verification enabled

**Expected**
- The provenance attestation is fetched
- The attestation is verified against Sigstore's transparency
  log
- The attested build pipeline matches expectations (e.g., a
  known GitHub Actions workflow for the upstream project)

## Scenario 4: Missing-provenance regression is caught

**Preconditions**
- The project tracks expected provenance state per dependency
  (a small manifest committed to the repository)
- A dependency previously had provenance; an upgrade has been
  proposed to a version that does NOT have provenance

**Action**
- Run the provenance-verification CI step against the upgrade

**Expected**
- CI surfaces the provenance regression
- The PR is flagged for human review
- The team either defers the upgrade or accepts the
  regression with documented rationale

## Scenario 5: Dependency-confusion attempt is prevented

**Preconditions**
- The project uses a private registry for some packages
- A package name overlaps with a (test-created) public-
  registry namespace squat

**Action**
- Run the strict install with the project's configured
  resolution path

**Expected**
- The private-registry version resolves
- The public-registry version is not pulled
- An audit of the lockfile confirms the source URL points at
  the private registry

## Scenario 6: Untrusted registry URL is rejected

**Preconditions**
- The project's configuration lists the trusted registries
- An attempt is made to install from a registry not on the
  list (e.g., a fork hosted on a personal CDN)

**Action**
- Attempt the install with the untrusted source

**Expected**
- The install fails or surfaces a warning that escalates to
  failure in CI
- The lockfile is not modified to record the untrusted source

## Scenario 7: License metadata is captured

**Preconditions**
- The project has a documented license allow-list
- A direct dependency change is proposed

**Action**
- Run a license-extraction tool (npm-license-checker, pip-
  licenses, cargo-license, go-licenses, or equivalent)
- Compare each dependency's license against the allow-list

**Expected**
- All dependencies' licenses are on the allow-list
- A new dependency with a non-allow-listed license fails CI
- License metadata is captured into the SBOM (if SBOM
  generation is part of the build)

## Scenario 8: SBOM generation reflects current state

**Preconditions**
- The project generates an SBOM (CycloneDX or SPDX format) in
  CI

**Action**
- Generate the SBOM for the current build
- Verify the SBOM's dependency list matches the lockfile

**Expected**
- Every lockfile entry has a corresponding SBOM component
- Components have integrity hash and license metadata
- The SBOM is signed (where SBOM signing is in scope per the
  consumer's profile)

## Test attestation

```
dependency-management.provenance test suite: PASSING
- Scenario 1 (lockfile install verifies hashes): PASS
- Scenario 2 (corrupted artifact fails install): PASS
- Scenario 3 (signed provenance verified): PASS
- Scenario 4 (missing-provenance regression caught): PASS
- Scenario 5 (dependency confusion prevented): PASS
- Scenario 6 (untrusted registry rejected): PASS
- Scenario 7 (license metadata captured): PASS
- Scenario 8 (SBOM generation): PASS
```

## Cross-reference

- Substrate rule: dependency-management.provenance
- Review checklist: checklist.md
- Good examples: examples/dependency-management/provenance-good.md
