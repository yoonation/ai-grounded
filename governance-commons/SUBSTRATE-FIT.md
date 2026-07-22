<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Substrate fit statement

This document states honestly what the Governance Commons substrate is good
for at its current stable release, where it is strong, and where it is still
maturing. It
is the consumer-facing companion to the roadmap: a consumer or reviewer can
read it cold, without the substrate-author present, and know what to expect.

The substrate's first dishonesty risk is overstating coverage. This document
exists to prevent that. Read the L1 enforcement caveat below before wiring
any substrate binding into a blocking CI gate.

## What the substrate is, in one paragraph

Governance Commons is a human-authored, machine-readable, version-controlled
body of engineering governance that AI agents consult when generating or
reviewing code. It ships rules, patterns, bindings, decision frameworks,
profiles, and cross-taxonomy threat mappings. It is description, not
implementation: it does not ship application code, a runtime, or a workflow
engine. Consumers act on its content in their own environments. Full
identity and philosophy live in `spec/identity-model.md` and
`spec/principles.md`; the supreme authority is `CHARTER.md`.

## What the substrate covers

At its current stable release the substrate is content-complete,
ecosystem-complete, and tooling-scaffolded:

- 25 concern catalogs, all stable, spanning authentication, authorization,
  input validation, secrets management, supply chain, logging, observability,
  monitoring and alerting, reliability, error handling, the performance
  concerns, the infrastructure and configuration concerns, data
  classification, privacy, the AI/ML concerns (responsible-ai and
  agentic-systems), and the operational concerns (backup-recovery,
  feature-flags, documentation, code-organization, testing-strategy,
  dependency-management, cost-model-selection).
- 5 profiles, all stable: `production-grade-baseline` (the opinionated
  default) and four industry tilts that inherit from it,
  `financial-services`, `regulated-ai`, `healthcare`, and `fedramp`.
- 5 cross-taxonomy threat mappings to concerns: STRIDE, OWASP LLM Top 10,
  OWASP Agentic ASI, OWASP Agentic Skills Top 10, and MITRE ATLAS.
- A three-layer rule model throughout: L1 mechanical (capability-bound
  bindings resolved through the toolchain), L2 semantic (review checklists
  and test templates), L3 judgmental (MADR decision frameworks).
- A tooling layer under `tooling/`: maintained substrate utilities
  (assemble, toolchain, floor-generator) plus skeletons (profile-resolver,
  mapping-coverage-reporter, tailoring-agent) with thin read-only reference
  scripts.

## Fit by project shape

**Best fit: application backends on mainstream stacks.** Every concern
applies. The STRIDE mapping is strongest here. Lead with the L2 review
checklists, the L3 decision frameworks, and the threat-model traceability
the mappings provide.

**Good fit: AI/ML and agentic systems.** The responsible-ai and
agentic-systems concerns, plus the three-layer threat picture (OWASP LLM Top
10 at the model layer, OWASP Agentic ASI at the orchestration layer, OWASP
Agentic Skills Top 10 at the skill layer), cover this shape. The mappings
carry explicit coverage-gap records where a threat is only partially
addressable by first-party-code rules. Use the `regulated-ai` profile where
the EU AI Act, NIST AI RMF, or ISO/IEC 42001 apply.

**Good fit: infrastructure as code and data pipelines.** The
infrastructure-misconfiguration, configuration-management, backup-recovery,
reliability, data-classification, and privacy concerns cover provisioning
hygiene, recoverability, and the data layer.

**Good fit: regulated industries.** The four industry-tilt profiles raise
severities for the controls their regimes make critical: financial-services
(PCI-DSS, SOX, GLBA, FFIEC), healthcare (HIPAA, HITECH), fedramp (FedRAMP,
NIST SP 800-53, FIPS 199), and regulated-ai (EU AI Act, NIST AI RMF, ISO/IEC
42001). A profile raises emphasis; it does not by itself make a consumer
compliant.

## The L1 enforcement caveat (read this)

The substrate's strong, dependable surface is L2 and L3: the review
checklists and the decision frameworks are fully authored substrate-original
content and apply regardless of any external tool's state.

The L1 mechanical layer is realized. Each mechanical rule names a capability
gate (for example `sast`, `secrets`, `lint`), and the toolchain registry and
selection resolve that gate to a concrete OSS tool. The substrate holds no
per-rule references into an upstream rule registry, so there is nothing to
drift out of date; L1 is as authoritative as L2 and L3.

What this means in practice:

- L1 enforces once the tools are wired. The substrate ships the gate and the
  tool selection, not the tools or their rule sets. The consumer installs the
  selected OSS tools and, for the SAST gate, supplies the maintained community
  rule set (see `spec/enforcement-tooling.md`). This is one-time setup, not an
  ongoing reliability gap.
- Generate the floor rather than wiring tools by hand. `make gc-generate-floor`
  emits a pre-commit config, a CI workflow, and a review checklist wired to the
  registry's pinned tool versions; the consumer runs it in their environment.
- All three layers carry their own weight. L1 mechanical gates, L2 review
  checklists, and L3 decision frameworks are each authoritative; none is an
  advisory or maturing surface.

This caveat is the single most important thing to understand before adopting
the substrate. It is stated here, in the consumer-facing surface, on purpose.

## What the stable release asserts

Stable-release status is a stability and completeness commitment, scoped honestly:

- The schema set, the OSCAL-based catalog format, the profile model
  (including profile-of-a-profile industry tilts), and the lifecycle and
  attestation discipline are stable. Breaking changes to these contracts
  require a major-version bump per Charter Article VIII.
- All 25 concerns and 5 profiles are stable content under Charter Article
  IV: referenceable, and immutable except through the deprecation and
  retirement path (Article VIII Section 8.2 and 8.3, which guarantees a
  consumer at least one major version of deprecation notice).
- The stable release does not assert that the L1 mechanical layer is fully enforceable
  upstream. It asserts that the authored governance content (L2, L3, the
  catalogs, the profiles, the mappings) is complete and stable, and that the
  L1 maturity status is disclosed (this document).

## How to adopt

1. Pick a profile: `production-grade-baseline` for a sensible default, or an
   industry tilt if a regulated regime applies.
2. Resolve it to its effective rules and severities (see
   `tooling/profile-resolver/`).
3. Stand up all three layers: the L1 mechanical gates, the L2 review
   checklists, and the L3 decision frameworks are each authoritative.
4. Wire the L1 tools through the generated enforcement floor
   (`make gc-generate-floor`); for the SAST gate, supply the maintained
   community rule set per `spec/enforcement-tooling.md`.
5. Use the threat mappings for traceability from a recognized threat
   taxonomy to the substrate rules that address it.

## Pointers

- `README.md` (front door and layout)
- `CHARTER.md` (supreme authority; Article VII compatibility, Article VIII
  versioning and lifecycle)
- `spec/identity-model.md` and `spec/principles.md` (identity and philosophy)
- `FUTURE.md` (design debt, including the registry-ID remediation tiers)
- `spec/substrate-scope.md` (the authoritative concern and depth scope)
