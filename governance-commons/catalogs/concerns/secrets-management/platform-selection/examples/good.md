<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.platform-selection platform selection (good patterns)

Substrate-original good-pattern examples for secrets-management.platform-selection.

The L3-001 examples are excerpts from well-formed ADRs that
satisfy the substrate's review checklist. Real consumer ADRs
will be longer and more application-specific; these excerpts
illustrate the qualities the substrate looks for.

## Good ADR excerpt A: Single-cloud Kubernetes application

```markdown
# ADR-007: Secrets Management Platform Selection

Status: Accepted
Date: 2026-04-12
Deciders: platform-team, security-architect

## Context

This service runs on EKS in us-east-1 and us-west-2. We
have approximately 18 production secrets across database
credentials, third-party API keys, and JWT signing keys.
Workload identity via IRSA is established for all
services. Our compliance scope is SOC 2 Type 2; we do not
process PCI or HIPAA data in this service.

Operational maturity: we have a 4-person platform team
with experience running EKS but no current Vault
expertise. We have AWS-native expertise and existing
investment in CloudTrail, KMS, and IAM.

## Decision Drivers

D1 (cloud platform): single-cloud AWS.
D2 (identity infrastructure): IRSA established.
D3 (regulatory): SOC 2 Type 2; no HIPAA/PCI.
D4 (operational maturity): AWS-native skills; no Vault.
D5 (multi-region): yes (us-east-1 + us-west-2 active-active).
D6 (architecture): Kubernetes.
D7 (budget): low operational overhead preferred.

## Considered Options

We considered the substrate's Options 1, 2, 3, and 4.
Option 5 (deployment-platform) was excluded immediately
as substrate-discouraged for production.

[Option 1, 2, 3, 4 analysis adapted from the substrate's
framework with our specific values...]

## Decision Outcome

Option 4 (Kubernetes-native with AWS Secrets Manager
backend via external-secrets operator).

Reasoning: D6 (Kubernetes) pushes toward Option 4. D2
(IRSA established) makes AWS Secrets Manager the natural
backend. D4 (no Vault expertise) excludes Option 2. D5
(multi-region) is straightforward with AWS Secrets
Manager replication.

## Substrate Alignment

This choice aligns with the substrate's preferred order
(Option 4 first for Kubernetes applications, Option 1
backend choice given single-cloud AWS). No deviation.

## Consequences

Positive: workload-identity-based access works
naturally; secrets-management.runtime-retrieval retrieval pattern is straight-
forward; secrets-management.encryption-at-rest encryption-at-rest via AWS KMS
is platform-managed; SOC 2 audit benefits from
CloudTrail integration.

Negative: vendor lock-in to AWS for secret storage;
external-secrets operator is an additional component to
operate; per-secret cost grows linearly.

Follow-up work: ADR-008 will address KMS key strategy
(per-environment KEKs vs shared); operator deployment
manifest pending; runbook for KMS key rotation pending.

## Decision Review Schedule

Annual review (2027-04-12) or earlier on: cloud
platform change, significant regulatory regime change,
substrate version increment past 0.5.0.
```

Why this satisfies secrets-management.platform-selection: the ADR addresses
every substrate-required element from the review
checklist. Context is application-specific. Drivers are
enumerated with the application's values. Options
considered span the applicable substrate options. The
decision references the drivers. Substrate alignment is
explicit. Consequences are honest. Review schedule is
concrete.

## Good ADR excerpt B: Multi-cloud application with deviation

```markdown
# ADR-002: Secrets Management Platform Selection

Status: Accepted
Date: 2026-03-08
Deciders: platform-team, ciso

## Context

This product is deployed in AWS (primary) and GCP
(analytics overflow). We have 60 production secrets
across both clouds. Compliance scope includes HIPAA
(US healthcare).

Operational maturity: 8-person platform team with
established Vault expertise from prior work; we
currently operate a Vault cluster for an adjacent
product line.

## Decision Drivers

D1 (cloud platform): multi-cloud AWS + GCP.
D2 (identity): IRSA in AWS, workload identity federation
in GCP, both established.
D3 (regulatory): HIPAA; requires audit trail.
D4 (operational maturity): Vault expertise present.
D5 (multi-region): yes within AWS.
D6 (architecture): mixed (some Kubernetes, some Lambda,
some Cloud Functions).
D7 (budget): operational efficiency through consolidation
preferred.

## Decision Outcome

Option 2 (HashiCorp Vault self-managed) used as the
unified platform across both clouds.

## Substrate Alignment

The substrate-preferred Option 1 for single-cloud or
Option 4 for Kubernetes does not fit because:
1. The multi-cloud requirement (D1) does not match
   Option 1's cloud-native pattern.
2. Option 4 fits some workloads but not the Lambda and
   Cloud Functions surfaces.

The substrate's Option 2 is preferred for multi-cloud
with operational maturity (D4), which describes our
context.

This is a substrate-aligned choice; no deviation from
the substrate's preferred order for THIS context.

## Consequences

Positive: unified audit trail across clouds; dynamic
secrets engine reduces standing credentials; transit
engine consolidates application crypto needs.

Negative: Vault cluster operational burden (clustering,
unsealing, upgrade, backup); HSM not in initial scope
which limits FIPS-140-2 Level 3 posture (HIPAA
acceptable at lower levels).

Follow-up work: ADR-003 will document Vault unseal
strategy (auto-unseal via AWS KMS); ADR-004 will
document HIPAA evidence collection.

## Decision Review Schedule

Annual (2027-03-08) or on: significant cloud footprint
change, regulatory regime expansion, HSM requirement
emerges.
```

Why this satisfies secrets-management.platform-selection: the multi-cloud
context creates tension that the ADR addresses
explicitly. The "Option 1 doesn't fit because" reasoning
is concrete. The team's operational maturity (D4) is
substantively addressed, not assumed. Negative
consequences include the operational burden honestly.

## Good ADR excerpt C: Substrate deviation justified

```markdown
# ADR-001: Secrets Management Platform Selection

Status: Accepted
Date: 2026-05-01
Deciders: platform-team

## Context

This is a small SaaS application; team of 3; running
on AWS only; about 6 production secrets.

[drivers section...]

## Decision Outcome

Option 1 (AWS Secrets Manager directly) without an
operator pattern.

## Substrate Alignment

The substrate's Option 4 (Kubernetes-native with operator)
is preferred for Kubernetes applications. Our workloads
include Kubernetes (one service) and Lambda (most
services). The operator pattern would only benefit the
Kubernetes workload; for the Lambda workloads, direct
AWS Secrets Manager retrieval via SDK is simpler.

This is a deviation from the substrate's preferred order
(Option 4 first for projects with Kubernetes content).
The deviation is justified by:
1. Most services are Lambda, not Kubernetes.
2. The single Kubernetes service does not warrant the
   operator overhead at our scale.
3. The team's capacity is low; Option 1 is operationally
   simpler.

We will revisit this if the Kubernetes footprint grows.

## Consequences

[as appropriate...]
```

Why this satisfies secrets-management.platform-selection: deviation is
explicit, reasoning is concrete, and the future trigger
for revisit is named. Substrate alignment statement is
honest about the deviation rather than retroactively
fitting the substrate's preferred option to a choice
that was actually different.

## Cross-reference

- Anti-patterns: examples/secrets-management/platform-selection-anti-pattern.md
- Substrate rule: secrets-management.platform-selection
- Decision framework: decision-frameworks/secrets-management-platform.madr.md
- Review checklist: checklist.md
