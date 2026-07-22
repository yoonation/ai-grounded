---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: supply-chain.supply-chain-integrity-strategy
title: "Supply-Chain Integrity Strategy"
lifecycle-status: stable
commons-version: "0.5.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-23"
entered-status-at: "2026-05-26"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention. Promoted to stable at M2 close consolidation (Path A precedent) on 2026-05-26 alongside the four other M2 draft MADRs and the five M2 draft catalogs they pair with."
ai-assistance: "AI drafted from substrate-author intent. Pairs with supply-chain.supply-chain-integrity-strategy substrate rule; mirrors the testing-strategy.madr.md and authorization-model-selection.madr.md precedents for L3-as-pre-build-gate. Portfolio-of-decisions structure (eight sub-decisions, not a single option pick). Draft lifecycle per M2 Session 5; promotion to stable deferred to M2 close per Path A precedent."
authoritative-sources:
  - "https://slsa.dev/spec/v1.1/"
  - "https://csrc.nist.gov/pubs/sp/800/218/final"
  - "https://csrc.nist.gov/pubs/sp/800/161/r1/final"
  - "https://www.federalregister.gov/documents/2021/05/17/2021-10460/improving-the-nations-cybersecurity"
  - "https://eur-lex.europa.eu/eli/reg/2024/2847/oj"
  - "https://github.com/in-toto/attestation"
  - "https://www.sigstore.dev/"
  - "https://cyclonedx.org/specification/overview/"
  - "https://spdx.dev/specifications/"
  - "https://owasp.org/www-project-top-10-ci-cd-security-risks/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.dependency-vetting-policy
  - decision-frameworks.secrets-management-platform
  - decision-frameworks.logging-architecture
---

# Supply-Chain Integrity Strategy

This decision framework provides the substrate's analysis of
supply-chain integrity strategy options. Consumers reference this
framework when authoring their own ADR documenting their
application's supply-chain integrity choices (substrate-recommended
location for the consumer's ADR:
`/docs/decisions/ADR-XXX-supply-chain-integrity-strategy.md`).

The framework is referenced by substrate rule supply-chain.supply-chain-integrity-strategy,
which requires applications to have an explicit, documented
supply-chain integrity strategy before substantive build and
release pipeline implementation begins. Consumers satisfy
supply-chain.supply-chain-integrity-strategy by authoring an ADR that adapts the analysis in
this framework to their application context.

Unlike single-option decision frameworks (authorization-model-
selection, auth-strategy), the supply-chain integrity strategy is
a portfolio of eight sub-decisions. The eight sub-decisions
interact: choosing SLSA Build L3 implies hosted-hardened build
platforms which implies a specific OIDC issuer set which implies
a specific allowed-signers policy. The consumer's ADR addresses
each sub-decision and documents the interactions; this framework
provides the substrate's analysis for each.

The framework is non-binding: it surveys options and consequences
without prescribing the consumer's choice beyond the substrate-
preferred default. Where the substrate has a preference, it is
stated; where the choice depends on consumer context, the
framework provides decision drivers rather than recommendations.

## Context

The supply-chain integrity strategy decision determines how the
consumer's build, release, and deployment pipeline anchors trust
in the artifacts that reach production. The decision is structural:
changing the strategy after significant pipeline investment has
been made requires either rewriting build infrastructure or
accepting drift between the documented strategy and the running
pipeline.

The substrate identifies eight sub-decisions that compose the
strategy:

1. SLSA Build Level target
2. Attestation scope and predicate-type policy
3. SBOM cadence, format, and storage
4. Signing identity policy
5. Transparency log selection
6. Retention horizon
7. Exemption discipline
8. Review cadence

Each sub-decision has a substrate-recommended default keyed to
the consumer's profile (production-grade-baseline, stricter-
profiles for financial-services / healthcare / government, looser-
profile for greenfield-startup). The defaults reflect the
substrate's analysis of typical trade-offs; consumer deviation
is substrate-accepted with documented rationale.

The substrate's framing is risk-based: each sub-decision answers
"what level of evidence does the consumer require to trust an
artifact reaching production?" Higher evidence levels increase
engineering investment and operational discipline; they reduce
the consumer's residual risk of supply-chain compromise. The
consumer's ADR documents the chosen evidence levels and the
threat model that motivates them.

The supply-chain integrity strategy interacts with the substrate's
other concerns in specific ways:

- Dependency-management governs upstream-package selection
  (manifest-lockfile pinning, vetting before adoption,
  vulnerability scanning against advisory databases). Supply-
  chain governs artifact provenance, signing, SBOM discipline,
  and build-environment integrity. Both ADRs are typically
  authored together because they share the upstream-trust
  surface.

- Secrets-management governs build-time credential handling. The
  supply-chain.supply-chain-integrity-strategy ADR documents the signing-identity policy; the
  secrets-management.platform-selection ADR documents the credential-management platform
  that provisions the signing-credential surface.

- Logging governs the retention and integrity of audit-trail
  events. supply-chain.attestation-and-sbom-retention (attestation and SBOM retention) cross-
  references logging.integrity (tamper-evident log integrity); the two
  ADRs share the integrity-storage decision.

- Authorization governs which principals can author or modify
  policy artifacts (allowed-signers files, exemption files,
  retention configuration). supply-chain.supply-chain-integrity-strategy's signing-identity
  policy is administered through the consumer's AUTHZ-* policy.

## Regulatory Context

As of 2026-05-23, the substrate-relevant regulatory environment is:

- **EU Cyber Resilience Act (Regulation 2024/2847)** is the active
  enforceable regulatory driver. Reporting obligations activate
  2026-09-11; full enforcement 2027-12-11. The CRA requires
  manufacturers of products with digital elements to maintain
  vulnerability-handling discipline, generate and retain SBOMs,
  and notify ENISA within 24 hours of awareness of actively-
  exploited vulnerabilities. The substrate-recommended supply-chain.supply-chain-integrity-strategy
  ADR addresses CRA in-scope determination in Section 1 (Context)
  and documents the CRA-specific obligations in the runbook
  (cross-references supply-chain.vulnerability-disclosure-response).

- **Executive Order 14028 of May 12, 2021** remains in force as
  foundational US policy generating the SSDF (NIST SP 800-218).
  EO 14306 (June 2025) amended EO 14144 without rescinding
  EO 14028. The substrate references EO 14028 as foundational
  technical-framework anchor.

- **OMB Memorandum M-26-05 (February 2026)** rescinded the
  universal federal mandate for SSDF self-attestation collection
  (M-22-18, M-23-16). Federal agencies now have risk-based
  discretion. NIST SSDF remains a substrate-recommended technical
  framework regardless of federal attestation-collection status.
  Agency-specific obligations remain; consumers with federal
  contracts document agency-specific requirements in their
  supply-chain.vulnerability-disclosure-response runbook.

- **Sector-specific regulations** (HIPAA Security Rule, PCI DSS
  4.0, NERC CIP, sector-specific equivalents) impose supply-chain
  obligations on consumers in regulated industries. The substrate's
  framework is sector-agnostic; consumers in regulated sectors
  layer their sector-specific obligations onto the substrate's
  baseline.

## Decision Drivers

The substrate identifies the following drivers that should inform
the eight sub-decisions. Consumers may add application-specific
drivers but should address each substrate driver in their ADR.

- **D1. Consumer threat model.** What supply-chain compromises
  is the consumer most concerned about? Compromised upstream
  package (SolarWinds-pattern build-system attack); compromised
  build environment (CI/CD platform breach); compromised signing
  credential (key theft); compromised source authority (rogue
  insider, compromised maintainer account); accidental dependency
  drift (lockfile staleness, missing review). The threat model
  ranks the sub-decisions: provenance verification anchors
  origin; signature verification anchors identity; SBOM anchors
  inventory; build-environment isolation anchors the build
  trust assumption.

- **D2. Regulatory exposure.** What regulations is the consumer
  in scope for? EU CRA, US federal contracts, HIPAA, PCI DSS,
  sector-specific. Regulatory exposure raises the floor on
  retention, attestation, and notification requirements; the
  consumer's strategy cannot drop below the regulatory floor.

- **D3. Engineering-investment tolerance.** What engineering
  capacity does the consumer have to invest in the pipeline?
  SLSA Build L1 is the lowest investment; Build L2 requires
  build-platform adoption; Build L3 requires substantial
  security engineering. Stricter signing-identity policies
  require credential-rotation discipline. Retention requires
  storage investment.

- **D4. Upstream-ecosystem reality.** What attestation surface
  does the consumer's primary upstream ecosystem expose? Mature
  ecosystems (npm with provenance, PyPI with Trusted Publishing)
  permit immediate strict attestation; emerging-attestation
  ecosystems (Maven Central, Go modules) require substrate-
  acceptable transition discipline.

- **D5. Consumer's downstream commitments.** What does the
  consumer commit to its own downstream consumers? Commitments
  to publish SLSA provenance, SBOMs, or signed releases set the
  floor on the consumer's own discipline. Consumers shipping
  products with digital elements into the EU market commit to
  CRA-aligned obligations regardless of voluntary posture.

- **D6. Build-platform sovereignty requirements.** Can the
  consumer use public-good infrastructure (Sigstore public
  Rekor, GitHub Actions hosted runners) or are sovereignty,
  air-gap, or data-residency requirements driving self-hosted
  alternatives? Self-hosting raises engineering investment but
  satisfies sovereignty.

- **D7. Incident-response capability.** What is the consumer's
  realistic incident-response capacity? Strict retention and
  attestation discipline pays off only when the consumer can
  query the retained artifacts under incident pressure;
  retention without retrievability does not anchor incident
  response.

- **D8. Transition discipline maturity.** Does the consumer
  have established discipline for time-bounded exemptions, or
  will exemptions accumulate? Looser exemption discipline is
  substrate-accepted at adoption but degrades over time without
  governance.

## Sub-Decision 1: SLSA Build Level Target

### Substrate-preferred default

- **production-grade-baseline:** SLSA Build Level 2
- **stricter-profiles** (financial-services, healthcare,
  government): SLSA Build Level 3
- **looser-profile** (greenfield-startup): SLSA Build Level 1
  with documented six-month transition to Build Level 2

### Considered options

**Option 1.A: SLSA Build Level 1.** The build process is scripted
and generates provenance metadata. The producer claims the build
followed the script. Pros: lowest engineering investment;
substrate-accepted starting point for greenfield projects. Cons:
producer-side claim only; vulnerable to producer compromise.

**Option 1.B: SLSA Build Level 2.** The build platform (not the
producer) generates the provenance attestation. The attestation
is signed by a verifiable build-platform identity. Pros:
defeats producer-side forgery attack; substrate-default for
production-grade-baseline; broad upstream adoption in
GitHub Actions, Google Cloud Build, npm, PyPI. Cons: requires
build-platform adoption; substrate-recognized hosted build
platforms only.

**Option 1.C: SLSA Build Level 3.** The build platform is
hardened against insider tampering, with hermeticity and
isolation guarantees. Pros: defeats compromised-build-platform
attack; substrate-default for stricter profiles. Cons: requires
substantial security-engineering investment; hosted-hardened
platforms are limited.

**Option 1.D: SLSA Build Level 4 (proposed).** Reproducible
builds with two-party review. Pros: highest evidence level.
Cons: substrate-acknowledges this level is not yet stable in
SLSA v1.1; deferred until SLSA v1.2 or later.

### Decision-driver mapping

- D1 (threat model): producer-compromise concern favors L2+;
  build-platform-compromise concern favors L3
- D2 (regulatory): EU CRA does not specify a SLSA level but
  requires equivalent integrity discipline; stricter sectors
  often prescribe L3-equivalent practice
- D3 (engineering investment): L1 lowest; L3 highest
- D4 (upstream reality): consumer-side L2 is substrate-recommended
  regardless of upstream level because the consumer's downstream
  trust depends on consumer-side provenance

## Sub-Decision 2: Attestation Scope and Predicate-Type Policy

### Substrate-preferred default

- **All consumer-built artifacts:** SLSA provenance attestation
  required at all profile levels
- **All container-image artifacts:** SLSA provenance attestation
  required at all profile levels
- **Third-party artifacts:** attestation requirement keyed to
  criticality tier from supply-chain.critical-dependency-audit (tier-1 attestation
  required; tier-2 attestation strongly recommended; tier-3
  attestation substrate-accepted to be transition-window)
- **Predicate-type policy:** `https://slsa.dev/provenance/v1`
  required at all profile levels; stricter profiles add
  `https://in-toto.io/attestation/vulns/v0.1`

### Considered options

**Option 2.A: First-party only.** Require attestation for
consumer-built artifacts; accept third-party attestation gaps.
Pros: focuses investment on what the consumer controls. Cons:
gaps in third-party attestation leave the consumer dependent on
upstream signal quality.

**Option 2.B: First-party plus tier-1.** Require attestation
for consumer-built and tier-1 third-party artifacts. Substrate-
default for production-grade-baseline. Pros: balances investment
and coverage; aligns with criticality-tier discipline. Cons:
tier-2 and tier-3 attestation gaps remain.

**Option 2.C: All production artifacts.** Require attestation
for every production artifact regardless of tier. Substrate-
recommended for stricter profiles. Pros: comprehensive coverage.
Cons: high transition friction; substrate-recognizes upstream
ecosystems where attestation adoption is incomplete.

### Decision-driver mapping

- D1 (threat model): comprehensive coverage favors Option 2.C
- D4 (upstream reality): Option 2.C may be infeasible for
  consumers in ecosystems with incomplete attestation adoption
- D7 (incident response): attestation enables advisory-response
  triage; broader scope enables faster triage

## Sub-Decision 3: SBOM Cadence, Format, and Storage

### Substrate-preferred default

- **Cadence:** every production release
- **Format:** CycloneDX 1.6 JSON (substrate-default); SPDX 2.3
  JSON substrate-accepted; both formats acceptable in dual-format
  workflows
- **Storage:** OCI registry referrers-attached attestations for
  container artifacts; Dependency-Track for substrate-recommended
  multi-project retention surface

### Considered options

**Option 3.A: CycloneDX 1.6 primary.** Substrate-default. Pros:
strongest fit for component-and-vulnerability use cases;
OWASP-stewarded; broad tooling support. Cons: license-and-
provenance use cases are weaker than SPDX.

**Option 3.B: SPDX 2.3 primary.** Substrate-accepted alternative.
Pros: strongest fit for license-and-provenance use cases; Linux
Foundation steward. Cons: weaker than CycloneDX for component-
and-vulnerability workflows that the substrate-default depends
on.

**Option 3.C: Dual format.** Generate both CycloneDX and SPDX
on each release. Pros: maximum compatibility with downstream
consumers. Cons: doubles SBOM generation and validation cost.

**Storage sub-options:**

- 3.S1: OCI referrers-attached (substrate-default for container
  workflows)
- 3.S2: GitHub release assets (substrate-accepted for GitHub-
  released artifacts)
- 3.S3: Dependency-Track or substrate-acceptable retention
  store (substrate-recommended for multi-project consumers)
- 3.S4: Custom blob-storage with substrate-required append-only
  property (substrate-accepted for sovereignty requirements)

### Decision-driver mapping

- D5 (downstream commitments): consumer commitments to publish
  SBOM determine format choice
- D7 (incident response): Dependency-Track-style retention with
  query capability accelerates advisory-response triage

## Sub-Decision 4: Signing Identity Policy

### Substrate-preferred default

- **OIDC-bound keyless signing** (Sigstore Fulcio) for
  consumer-built artifacts at all profile levels
- **Allowed OIDC issuers:** substrate-default accept list
  (GitHub Actions, Google, consumer-defined enterprise IdPs);
  stricter profiles narrow to consumer-vetted issuers only
- **Signer-pattern allow-list:** per-environment patterns
  (production signers distinct from staging signers); stricter
  profiles require per-environment

### Considered options

**Option 4.A: OIDC-bound keyless (Sigstore).** Substrate-default.
Pros: eliminates long-lived signing-key management; short-lived
certificates limit credential window; transparency log anchors
discovery. Cons: dependency on OIDC issuer integrity; requires
Sigstore-compatible CI integration.

**Option 4.B: Long-lived key (GPG or SSH) with rotation.**
Substrate-accepted for consumers with existing key management.
Pros: simpler initial adoption; works in air-gapped contexts
where OIDC is impractical. Cons: long-lived credential
management is substrate-acknowledged-difficult; rotation
discipline determines whether the model works.

**Option 4.C: Enterprise PKI with internal CA.** Substrate-
accepted for consumers with mature PKI. Pros: integrates with
existing certificate-issuance workflows. Cons: shifts trust
anchor to internal CA; requires CA-issuance and revocation
discipline.

### Decision-driver mapping

- D3 (engineering investment): Option 4.A lowest ongoing cost
- D6 (sovereignty): Option 4.B or 4.C may be required for
  air-gap or sovereignty contexts
- D8 (transition discipline): legacy GPG-signed artifacts during
  ecosystem transition substrate-accepted with exemption-handling

## Sub-Decision 5: Transparency Log Selection

### Substrate-preferred default

- **Public-good Sigstore Rekor** for consumers without
  sovereignty constraints (substrate-default)
- **Self-hosted Rekor** for consumers with sovereignty
  requirements (substrate-accepted alternative)

### Considered options

**Option 5.A: Public-good Sigstore Rekor.** Substrate-default.
Pros: zero operational cost to consumer; broad ecosystem
adoption; Sigstore project operates the substrate-trusted
public-good instance. Cons: dependency on Sigstore project's
operational continuity; public visibility of attestation
metadata.

**Option 5.B: Self-hosted Rekor.** Substrate-accepted. Pros:
sovereignty; private attestation visibility; operational
control. Cons: consumer operational cost; consumer must
maintain Rekor instance integrity.

**Option 5.C: Substrate-accepted equivalent transparency log.**
For consumers with existing audit-log infrastructure that
satisfies append-only / WORM properties. Pros: leverages
existing investment. Cons: substrate requires explicit
substrate-acceptable equivalence rationale in the ADR.

### Decision-driver mapping

- D6 (sovereignty): public-good is substrate-default unless
  sovereignty drives self-hosted
- D7 (incident response): both options support the substrate's
  retrieval-time threshold

## Sub-Decision 6: Retention Horizon

### Substrate-preferred default

- **production-grade-baseline:** three years
- **stricter-profiles:** seven years
- **looser-profile:** one year

### Considered options

**Option 6.A: One year.** Substrate-accepted minimum for
greenfield-startup profile. Pros: lowest storage cost; matches
typical short-tail of incident-response queries. Cons: below
typical regulatory retention floors; rules out long-tail
forensics.

**Option 6.B: Three years.** Substrate-default for
production-grade-baseline. Pros: matches typical regulatory
minima; covers most incident-response query patterns. Cons:
may be below stricter-profile regulatory requirements.

**Option 6.C: Seven years.** Substrate-default for stricter
profiles. Pros: aligns with industry-typical regulatory horizons
(financial services, healthcare). Cons: higher storage cost;
substrate-recognizes the tail of incident-response queries
beyond seven years is rare.

**Option 6.D: Indefinite retention.** Substrate-accepted for
consumers with sovereign storage and regulatory requirements
mandating indefinite retention. Pros: maximal forensic capacity.
Cons: highest storage cost; substrate-recommends explicit
data-protection-impact analysis for indefinite retention of
attestation metadata.

### Decision-driver mapping

- D2 (regulatory): regulatory exposure sets the floor
- D3 (engineering investment): storage cost is the primary
  trade-off
- D7 (incident response): retention capacity must match
  retrieval needs

## Sub-Decision 7: Exemption Discipline

### Substrate-preferred default

- **Maximum transition window per exemption:** six months for
  new dependency adoption; nine months for legacy-dependency
  migration; substrate-recommended explicit deadline for each
  exemption
- **Approver identity per exemption:** engineering management
  or substrate-recommended security owner
- **Tracking mechanism:** committed exemptions file under
  `policy/exemptions/supply-chain/` with substrate-recommended
  YAML structure (one entry per exemption with artifact,
  reason, evidence, transition-end-date, approver, planned-
  resolution)
- **Review cadence:** quarterly substrate-recommended

### Considered options

**Option 7.A: Time-bounded exemptions with quarterly review.**
Substrate-default. Pros: forces transition discipline; surfaces
exemption drift at quarterly cadence; substrate-acceptable
default. Cons: requires substrate-recommended quarterly review
ownership.

**Option 7.B: Time-bounded exemptions with continuous monitoring.**
Substrate-accepted for stricter profiles. Pros: surfaces
exemption drift continuously rather than at quarterly cadence.
Cons: higher tooling investment.

**Option 7.C: Untracked exemptions (substrate-rejected).**
Substrate-rejected as a documented strategy; substrate-acknowledges
this is the failure mode that develops without explicit
discipline.

### Decision-driver mapping

- D4 (upstream reality): ecosystems with incomplete attestation
  adoption produce more exemption activity
- D8 (transition discipline): mature consumers handle more
  exemptions without accumulation; immature consumers benefit
  from tighter exemption windows

## Sub-Decision 8: Review Cadence

### Substrate-preferred default

- **Annual ADR review** at minimum
- **Regulatory-change trigger:** EU CRA full-enforcement
  activation 2027-12-11 is substrate-recommended explicit
  trigger; future regulatory changes documented as they emerge
- **Profile-transition trigger:** consumer moving between
  substrate profiles
- **Post-incident trigger:** any post-incident review surfacing
  ADR gaps

### Considered options

**Option 8.A: Annual review.** Substrate-default. Pros:
substrate-acceptable cadence for most consumers; balances
review cost and currency. Cons: regulatory changes between
annual reviews require unscheduled triggers.

**Option 8.B: Semi-annual review.** Substrate-accepted for
consumers in fast-changing regulatory environments. Pros:
higher currency. Cons: higher review cost.

**Option 8.C: Continuous review (event-driven).** Substrate-
accepted for stricter profiles. Pros: maximum currency. Cons:
requires substrate-recommended review-ownership and substrate-
acceptable trigger discipline.

## Substrate Decision Outcome Guidance

The substrate does not prescribe a single decision outcome
across the eight sub-decisions because the consumer's profile,
threat model, regulatory exposure, and engineering investment
tolerance interact in consumer-specific ways. The substrate-
recommended ADR-authoring sequence:

1. Document the consumer's profile and regulatory exposure
   (Sub-Decision Context in ADR Section 1)
2. Document the consumer's threat model (informs Sub-Decision 1
   and Sub-Decision 2)
3. Author Sub-Decisions 1-8 in sequence, addressing each
   substrate-recommended default and either accepting or
   documenting deviation with rationale
4. Document the interaction between sub-decisions (e.g.,
   choosing Build L3 implies hosted-hardened platforms, which
   implies specific OIDC issuers, which implies specific
   allowed-signers)
5. Document the review-cadence trigger plan (Sub-Decision 8)

The substrate-recommended ADR template provides one page per
sub-decision; consumers may compress or expand as their context
requires.

## Consequences

### Positive consequences of substrate-recommended defaults

- **production-grade-baseline** defaults produce a substrate-
  acceptable supply-chain integrity posture at moderate
  engineering investment; suitable for most commercial software
  product workflows
- **stricter-profiles** defaults produce a posture aligned with
  regulated-industry expectations; suitable for financial
  services, healthcare, government workflows
- **looser-profile** defaults produce a transition-discipline
  posture suitable for greenfield startups while committing to
  a substrate-required migration to production-grade-baseline

### Negative consequences and trade-offs

- All profile levels require engineering investment that smaller
  teams may struggle to absorb; substrate-acknowledges the
  greenfield-startup profile is the substrate-recommended
  starting point with a documented migration path
- SLSA Build L3 stricter-profile default requires hosted-hardened
  build platforms; substrate-acknowledges this constrains
  consumers to a small set of platforms
- Public-good Sigstore Rekor substrate-default introduces an
  external-service dependency; consumers with sovereignty
  requirements migrate to self-hosted Rekor with substrate-
  acknowledged operational cost

### Anti-patterns the substrate rejects

- **Strategy without documented sub-decisions.** The consumer
  declares a profile but does not address each sub-decision
  with substrate-acceptable rationale. The substrate-rejects
  this as substrate-incompatible posture.
- **Sub-decisions inconsistent with operational reality.** The
  ADR declares SLSA Build L3 but the operational pipeline runs
  on a non-hardened build platform. The substrate-rejects this;
  supply-chain.supply-chain-integrity-strategy review checklist surfaces the inconsistency.
- **Indefinite exemption discipline.** Exemptions without
  transition-end-date or with deadlines that are routinely
  extended without review. Substrate-rejects; quarterly review
  surfaces accumulation.
- **No regulatory analysis.** The ADR does not address regulatory
  exposure (EU CRA in-scope determination, sector-specific
  obligations). The substrate-rejects; Section 1 of the ADR
  documents regulatory exposure or explicitly records "none"
  with substrate-acceptable rationale.

## References

The authoritative-sources frontmatter lists the substrate's
primary references. Additional substrate-recommended reading
for ADR authors:

- SLSA v1.1 Threats overview: https://slsa.dev/spec/v1.1/threats-overview
- Sigstore documentation: https://docs.sigstore.dev/
- in-toto attestation framework: https://github.com/in-toto/attestation
- OWASP Top 10 CI/CD Security Risks:
  https://owasp.org/www-project-top-10-ci-cd-security-risks/
- OpenSSF Best Practices badge program:
  https://www.bestpractices.dev/
- OpenSSF Scorecard:
  https://github.com/ossf/scorecard
