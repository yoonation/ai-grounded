---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.dependency-management.provenance-provenance"
title: "dependency-management.provenance review checklist: direct dependency provenance verification"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add a new direct dependency"
  - "Code changes that change the source registry for an existing dependency"
  - "Code changes that modify package-manager configuration (registry URLs, scope mappings)"
  - "Periodic dependency audit (substrate-recommended quarterly)"
---

# dependency-management.provenance review checklist: direct dependency provenance verification

## How to use this binding

Reviewers answer every question below when reviewing PRs that
add a new direct dependency or change a dependency source. The
questions evaluate provenance for the specific dependency being
introduced or changed.

## Review questions

### 1. Source registry: is the dependency obtained from a substrate-recognized registry?

What good looks like: dependency is from a substrate-recognized
public registry (registry.npmjs.org, pypi.org, proxy.golang.org,
crates.io, rubygems.org, repo.maven.apache.org, packagist.org,
hex.pm, nuget.org) or from a private registry listed in the
consumer's profile.

What needs follow-up: dependency is from an arbitrary git URL
or tarball URL; dependency is from a personal fork rather than
the canonical project; dependency comes from a CDN or mirror
that is not listed in the trusted-registry set.

### 2. Lockfile entry: does the lockfile pin the exact version and integrity hash?

The substrate's L1 rule requires a lockfile per ecosystem. The
L2 provenance question is whether the lockfile entry for this
specific dependency is complete.

What good looks like: lockfile entry includes the exact
resolved version, the source URL, and the integrity hash; the
hash matches what the registry publishes; install verifies the
hash.

What needs follow-up: lockfile entry has no integrity hash;
lockfile entry was added without running the strict install
that verifies the hash; the entry's resolved-from URL points
somewhere other than the trusted registry.

### 3. Strongest available provenance: is it verified?

Different ecosystems offer different provenance signals. The
review asks whether the consumer is using the strongest signal
available.

What good looks like: npm provenance (Sigstore-backed)
verified for packages that publish it; PyPI digital
attestations checked where PEP 740 attestations are available;
PGP signatures verified for Maven Central artifacts; in-toto
attestations checked where they exist.

What needs follow-up: the dependency publishes provenance
attestations but the consumer's CI does not verify them; only
hash-based integrity is checked when stronger signals are
available; signatures are checked but the keys are not pinned
to expected signers.

### 4. Maintainer health: is the project actively maintained?

A dependency that has not had a release in 24 months may be
abandoned. Abandonment is not the same as compromise but it
increases supply-chain risk.

What good looks like: latest release within the last 12 months;
active commits or issue responses; OpenSSF Scorecard score
within the consumer's acceptable range; alternative dependencies
considered if maintenance is weak.

What needs follow-up: latest release older than 24 months
without explicit "feature complete, stable" status; project
archived on its source-code host; primary maintainer has
publicly announced reduced involvement.

### 5. Transitive footprint: what does this dependency drag in?

Direct dependencies pull transitive dependencies. The review
considers the size and shape of the transitive footprint.

What good looks like: transitive dependency count is
proportional to the value delivered (a small utility should
not pull in 200 transitive dependencies); the transitive set
does not include known-problematic packages; the consumer's
overall transitive count is bounded.

What needs follow-up: tiny dependency pulls a large transitive
graph (a known-bad pattern: left-pad-style micro-utilities);
transitive set includes deprecated or abandoned packages;
transitive count violates a consumer-side ceiling.

### 6. Dependency confusion: is the resolution path unambiguous?

For projects that use both public and private registries, the
resolution path must prevent accidental substitution.

What good looks like: scoped packages (npm @org/package) with
explicit registry mapping; pip index URLs explicit and ordered;
NuGet feed configuration prefers private over public for known
namespaces; private artifacts are not also published to the
public registry namespace.

What needs follow-up: no scoping; multiple registries configured
without preference; private package names that could be claimed
on the public registry; public-private namespace overlap with
no mitigation.

### 7. License compatibility: does the dependency's license fit the consumer's policy?

The dependency's license matters for redistribution. The review
confirms compatibility with the consumer's licensing posture.

What good looks like: the license is on the consumer's
allow-list; the license is one of MIT, Apache-2.0, BSD, MPL-2.0
for permissive use; copyleft licenses (GPL, AGPL) are evaluated
against the consumer's redistribution model.

What needs follow-up: license is unknown or unspecified in the
dependency's metadata; license is on the consumer's deny-list;
license is permissive but the consumer's vetting policy (per
dependency-management.vetting-policy) requires additional review for the category.

### 8. Vendor-introduced supply-chain concerns

Some dependencies have a track record of supply-chain incidents
(event-stream, ua-parser-js, colors.js, faker.js, xz-utils).
The review considers whether this dependency's history flags
caution.

What good looks like: dependency has no known compromise
history; if there is one, the consumer's response was timely
and the dependency is now under a vetted maintainer.

What needs follow-up: dependency was compromised within the
past 24 months and the consumer has not reviewed whether the
compromise is fully remediated; the current maintainer
transferred ownership recently without clear public reasoning.

## Reviewer attestation

```
dependency-management.provenance review checklist: complete
- Source registry: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Lockfile entry: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Strongest available provenance: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Maintainer health: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Transitive footprint: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Dependency confusion mitigation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- License compatibility: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Supply-chain history: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

## Cross-reference

- Substrate rule: dependency-management.provenance in catalogs/concerns/dependency-management.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/dependency-management/provenance-good.md
- Anti-patterns: examples/dependency-management/provenance-anti-pattern.md
- Related: dependency-management.vetting-policy vetting policy that establishes consumer-side criteria
