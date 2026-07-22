<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.infrastructure-security-baseline infrastructure security baseline (good patterns)

Substrate-original good-pattern example for infrastructure-misconfiguration.infrastructure-security-baseline. The L3
rule is satisfied by a consumer-authored ADR adapted from the
substrate's paired MADR at
`governance-commons/decision-frameworks/infrastructure-security-baseline.madr.md`.
This file shows an exemplary consumer ADR.

## Consumer ADR: ADR-007 Infrastructure Security Baseline

```markdown
# ADR-007: Infrastructure Security Baseline and Enforcement Model

* Status: Accepted
* Date: 2026-04-14
* Authors: Maya O. (platform engineering), Devon P. (security)
* Reviewers: CTO Office, Security Architecture Council
* Substrate reference: governance-commons v0.7.0;
  infrastructure-misconfiguration.infrastructure-security-baseline and infrastructure-security-baseline MADR
* Next review: 2027-04-14 (annual) or on regulatory change

## Context

We operate a single-cloud (AWS), multi-account (six accounts:
mgmt, audit, prod, staging, dev, ephemeral-ci) topology. We
handle PCI cardholder data in the production account and SOC 2
Type II-attested customer data across all accounts. Team size
is 22 engineers including 3 platform-engineering and 2 security
substrate-authors.

## Sub-Decision 1: Baseline Benchmark

**Choice:** CIS AWS Foundations Benchmark v3.0.0 plus PCI DSS
v4.0 overlay for the production account.

**Rationale:** PCI DSS applies to the production account scope.
CIS provides the IaC-prescriptive baseline; PCI DSS overlay
adds the cardholder-data-specific controls. Mapped to NIST SP
800-53 Moderate via OSCAL catalog for SOC 2 evidence
collection.

## Sub-Decision 2: Enforcement Model

**Choice:** Option C hybrid preventive plus detective.

Preventive layer (in pipeline):
- Checkov as PR gate for substrate L1 rules
- OPA Conftest for substrate L2 patterns expressible as policy
- Sentinel policies via HCP Terraform for production workspace
  apply-gate (terraform destroy, IAM PassRole on production)

Detective layer:
- AWS Config rules for CIS Foundations conformance pack
- AWS Security Hub aggregating Config findings across accounts
- AWS Access Analyzer for unused IAM permissions
- Wiz for cross-substrate posture and runtime visibility

**Rationale:** We are PCI-scoped, large enough to maintain
self-hosted policy library, and benefit from the defense in
depth.

## Sub-Decision 3: Exception Governance

**Choice:** Substrate-preferred discipline.

- Approval authority: Security Architecture Council for
  exceptions on IAM and network; CTO Office for cross-account
  trust exceptions; Platform Engineering Lead for non-security
  operational exceptions.
- Registry: GitHub Issues in repo `org/security-exceptions`
  with required fields (resource ARN, finding ID, justification,
  expiration date, remediation plan).
- Expiration: 90 days default; renewable once with re-
  justification; expiration enforced via scheduled job.
- Review cadence: quarterly review of open exceptions.

## Sub-Decision 4: Drift Detection

**Choice:** Hourly for production account; daily for staging
and dev; weekly for ephemeral-ci.

**Implementation:** GitHub Actions scheduled workflows per
account; alerts route to PagerDuty for production drift,
Slack for non-production drift.

## Cross-references

This ADR operationalizes the substrate-curated L1 and L2 rules
in `governance-commons/catalogs/concerns/infrastructure-misconfiguration.oscal.yaml`.
The L1 and L2 rules apply in addition to this baseline. Where
the substrate is silent, this ADR defers to CIS AWS Foundations
v3.0.0 plus the PCI DSS overlay.

## Consequences

- Recurring cost: ~$8K/month for Wiz; ~6 engineering days/month
  for policy library maintenance.
- PR-cycle latency: 2-3 minutes added per IaC PR for policy
  evaluation.
- Cross-cloud portability: low (AWS-specific); accepted because
  multi-cloud is not on the 18-month roadmap.
- Exception accumulation: tracked via the registry; quarterly
  review prevents silent erosion.
- Drift latency: ≤1 hour for production; ≤24 hours for staging.

## Decision drivers (substrate D1-D6 mapping)

| Driver | Value                              |
|--------|------------------------------------|
| D1     | Industry-regulated (PCI DSS, SOC 2) |
| D2     | Multi-account, single-cloud         |
| D3     | 5 platform/security substrate-authors |
| D4     | Hybrid preferred per D1 + D3        |
| D5     | Substrate-preferred discipline       |
| D6     | Production hourly, non-prod daily   |
```

## Why this ADR satisfies infrastructure-misconfiguration.infrastructure-security-baseline

The L3 review checklist verifies:
1. **Presence:** ADR exists at the consumer's documented ADR
   location (`docs/decisions/ADR-007-infra-security-baseline.md`).
2. **Currency:** the next-review date (2027-04-14) is in the
   future; the ADR was authored before substantive scale-up.
3. **Conformance:** the ADR's chosen Option C is implemented:
   Checkov + OPA + Sentinel preventive layer exists in CI; AWS
   Config + Security Hub + Wiz detective layer is deployed;
   exception registry is populated; drift workflows run at the
   stated cadence.

## Cross-references

- Substrate rule infrastructure-misconfiguration.infrastructure-security-baseline
- Substrate MADR
  `governance-commons/decision-frameworks/infrastructure-security-baseline.madr.md`
- The substrate's L1 and L2 rules in the parent catalog
