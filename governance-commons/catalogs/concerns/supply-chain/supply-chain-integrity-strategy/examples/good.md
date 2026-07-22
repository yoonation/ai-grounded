<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: supply-chain.supply-chain-integrity-strategy supply-chain integrity strategy ADR

A substrate-consumer ADR adapting the framework MADR.

## ADR

`docs/decisions/ADR-007-supply-chain-integrity-strategy.md`:

```markdown
# ADR-007: Supply-Chain Integrity Strategy

**Status:** accepted
**Date:** 2026-05-23
**Author:** alice@example.com (engineering-manager-platform)
**Reviewer:** bob@example.com (VP Engineering),
              carol@example.com (General Counsel)

## Section 1: Context

We ship a SaaS API and a downloadable Python SDK to enterprise
customers in financial services. Our regulatory exposure:

- **EU CRA:** in-scope. Products shipped into EU customer base
  since 2025; reporting obligations activate 2026-09-11 for us.
- **SOC 2 Type II:** annual audit by our compliance partner.
- **US federal:** out of scope (no federal contracts).
- **HIPAA / PCI DSS:** out of scope (no healthcare or
  card-data handling).

**Threat model summary:** our primary supply-chain concerns are
(1) compromise of an upstream Python package on PyPI affecting
our SDK or API runtime, and (2) compromise of our GitHub Actions
release workflow signing identity.

## Section 2: SLSA Build Level Target

**Decision:** SLSA Build Level 2 for production-grade-baseline;
Build Level 3 for the SDK distribution path (financial-services
customers expect L3 evidence in vendor questionnaires).

**Rationale:** L2 via slsa-github-generator is operationally
proven on our pipeline; L3 for the SDK is achievable with
slsa-github-generator's L3 template at modest additional cost.

## Section 3: Attestation Scope and Predicate-Type Policy

**Decision:**
- API container image: SLSA provenance, signature, CycloneDX SBOM
- SDK Python distribution: SLSA provenance, signature, CycloneDX SBOM,
  vuln-scan attestation
- Third-party tier-1 dependencies (per supply-chain.critical-dependency-audit): SLSA
  provenance required where upstream provides
- Third-party tier-2/3 dependencies: provenance preferred,
  exemptions tracked

**Predicate types required:** `https://slsa.dev/provenance/v1` at
all profile levels; SDK adds `https://in-toto.io/attestation/vulns/v0.1`.

## Section 4: SBOM Cadence, Format, and Storage

**Decision:**
- Cadence: every release
- Format: CycloneDX 1.6 JSON primary; SPDX 2.3 JSON also published
  for downstream customer compatibility
- Storage: OCI referrers (primary) + Dependency-Track (query
  surface) + S3 versioned bucket (archival)

## Section 5: Signing Identity Policy

**Decision:** OIDC-bound keyless signing via Sigstore Fulcio.

**Allowed OIDC issuers:**
- `https://token.actions.githubusercontent.com` (CI automation)
- `https://accounts.google.com` (engineering staff, for emergency
  manual signing)

**Signer-pattern allow-list:**
- Production: `^https://github\.com/example/api/\.github/workflows/release\.yaml@refs/tags/v[0-9]+\.[0-9]+\.[0-9]+$`
- Staging: `^https://github\.com/example/api/\.github/workflows/staging\.yaml@refs/heads/main$`

## Section 6: Transparency Log Selection

**Decision:** Public-good Sigstore Rekor (rekor.sigstore.dev).

**Rationale:** we have no sovereignty or air-gap requirements that
would drive self-hosting; the operational simplicity of public-
good Rekor outweighs the marginal sovereignty value of self-
hosting for our profile.

## Section 7: Retention Horizon

**Decision:** 7 years.

**Rationale:** our financial-services customers' contracts
require 7-year retention of audit trails covering software
they deploy. We extend the substrate-recommended
production-grade-baseline (3 years) to match contract
obligations.

## Section 8: Exemption Discipline

**Decision:**
- Maximum transition window: 6 months for new dependency adoption;
  9 months for legacy-dependency migration
- Approver: engineering manager for the affected team, with
  notification to security team
- Tracking: committed file at `policy/exemptions/supply-chain/`
  in YAML
- Review cadence: quarterly, jointly by security team and
  engineering management

## Section 9: Review Cadence

**Decision:**
- Annual ADR review (next: 2027-05-23)
- Explicit trigger: EU CRA full enforcement activation 2027-12-11
- Profile-transition trigger: if we begin federal sales (would
  add federal regulatory exposure)
- Post-incident trigger: any supply-chain incident triggers ADR
  review within 30 days

## Cross-references

- supply-chain.slsa-provenance-verification binding policy file: `policy/supply-chain/attestation-policy.yaml`
- supply-chain.signature-verification allowed-signers file: `policy/allowed-signers.yaml`
- supply-chain.vulnerability-disclosure-response runbook: `docs/runbooks/vulnerability-disclosure-response.md`
- supply-chain.critical-dependency-audit inventory: `docs/dependency-inventory.md`
- supply-chain.attestation-and-sbom-retention retention policy: `docs/supply-chain/retention-policy.md`
- Framework MADR: `governance-commons/decision-frameworks/supply-chain-integrity-strategy.madr.md`
```

## Key observations

- Each substrate-required sub-decision is addressed with a
  concrete choice and rationale
- Regulatory exposure is documented in Section 1; CRA in-scope
  determination drives Sections 4 (SBOM cadence) and 7 (retention)
- Cross-references resolve to concrete files; the supply-chain.supply-chain-integrity-strategy
  review checklist verifies consistency between the ADR and the
  operational configuration
