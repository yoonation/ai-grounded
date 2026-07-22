---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: secrets-management.platform-selection
title: "Secrets Management Platform Selection"
lifecycle-status: stable
commons-version: "0.4.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-20"
entered-status-at: "2026-05-22"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
ai-assistance: "AI drafted from substrate-author intent following auth-strategy.madr.md precedent; second decision framework authored in the substrate; exercises the established MADR pattern for a different concern domain. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft."
authoritative-sources:
  - "https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final"
  - "https://owasp.org/www-project-secrets-management/"
  - "https://developer.hashicorp.com/vault/docs"
  - "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html"
  - "https://cloud.google.com/secret-manager/docs"
  - "https://learn.microsoft.com/en-us/azure/key-vault/general/overview"
  - "https://adr.github.io/madr/"
---

# Secrets Management Platform Selection

This decision framework provides the substrate's analysis of
secrets management platform options. Consumers reference this
framework when authoring their own ADR documenting their
application's platform choice. The substrate-recommended
location for the consumer's ADR is
`/docs/decisions/ADR-XXX-secrets-management-platform.md`.

The framework is referenced by substrate rule secrets-management.platform-selection,
which requires applications to have an explicit, documented
platform choice before any secret-handling code is introduced.
Consumers satisfy secrets-management.platform-selection by authoring an ADR that
adapts the analysis in this framework to their application
context.

## Context

Secrets management is a platform-level concern, not an
application-level concern. The application interacts with
whichever platform the consumer selects; the platform
determines how rotation, access control, encryption at rest,
audit, and recovery work. Choosing the platform after secrets
exist forces a migration; choosing it before is the substrate-
recommended path.

The choice has implications across every subsequent SECRETS-
L2 rule. The application's L2-001 runtime retrieval pattern
depends on the platform's client API. The L2-002 rotation
cadence depends on the platform's rotation capabilities. The
L2-003 least-privilege access depends on the platform's
policy model. The L2-004 encryption at rest depends on the
platform's KMS integration. A platform choice that fits the
context produces L2 compliance with comparatively little
effort; a poor fit makes L2 compliance disproportionately
expensive.

Common substrate failure mode: teams default to environment
variables populated by deployment templates, treating the
deployment system as an implicit secrets platform. This
defers the platform choice rather than making it. The
environment-variable-as-platform pattern fails at L2-001
(no audit trail of retrieval), at L2-002 (rotation requires
redeploy), at L2-003 (no per-secret policy granularity), and
at L2-004 (deployment-tool storage is not separately
encrypted with KMS-held keys). The framework forces the
platform choice to be explicit.

The substrate provides analysis of each viable option but
does not prescribe a single choice. Consumers select based
on their context. The substrate requires the choice to be
documented and reasoned; it does not require consumers to
choose the substrate-preferred option.

## Decision Drivers

The substrate identifies the following drivers that should
inform the platform choice. Consumers may add application-
specific drivers but should address each substrate driver in
their ADR.

- **D1. Cloud platform footprint.** Single-cloud, multi-
  cloud, hybrid, or on-premises. Cloud-native platforms
  (AWS Secrets Manager, GCP Secret Manager, Azure Key
  Vault) have tightest integration with the respective
  cloud's IAM and KMS but create cross-cloud friction.
  Platform-agnostic options (HashiCorp Vault) trade
  integration depth for portability.

- **D2. Existing identity infrastructure.** Workload-
  identity systems (AWS IRSA and IAM Roles for EC2, GCP
  workload identity federation, Azure managed identities,
  Kubernetes service accounts with projected tokens) make
  cloud-native secrets platforms easier to adopt because
  the identity binding is already established. Independent
  identity infrastructure (custom certificate authority,
  bespoke PKI) shifts the trade-off toward platforms that
  can authenticate against the existing infrastructure.

- **D3. Regulatory regime.** PCI DSS, HIPAA, FedRAMP, FIPS-
  140 compliance modes, financial services data residency,
  and government cloud requirements (AWS GovCloud, Azure
  Government, GCP Assured Workloads) constrain which
  platforms are usable in which configurations. The
  consumer's regulatory context narrows the option set.

- **D4. Operational maturity.** Self-managed HashiCorp
  Vault offers significant capability but requires
  operational effort: clustering, unsealing, backup,
  upgrade, monitoring. Teams without dedicated platform
  engineering capacity often find managed cloud-native
  platforms more sustainable. The honest assessment of
  operational maturity is a substrate-required driver
  because the underweight of this driver produces
  predictable failure modes.

- **D5. Multi-region requirements.** Replication,
  failover, and disaster recovery shape the platform
  choice. Cloud-native platforms replicate per cloud-
  native conventions. Vault offers performance and
  disaster-recovery replication with operational cost.
  Single-region deployments simplify the choice.

- **D6. Application architecture.** Container-orchestrated
  workloads (Kubernetes) may benefit from operator
  patterns (external-secrets, secrets-store-csi-driver)
  that abstract the underlying platform. Serverless
  workloads (AWS Lambda, Cloud Functions, Azure Functions)
  may benefit from native integrations that work without
  long-lived processes. Traditional VM workloads may
  prefer agent-based patterns.

- **D7. Budget and cost model.** Cloud-native platforms
  typically charge per secret per month plus per API
  request. Vault has license cost (Vault Enterprise) or
  significant operational cost (Vault Open Source).
  Cost scales with the secret count and access frequency;
  applications with many high-access secrets may face
  different cost profiles than applications with few low-
  access secrets.

## Considered Options

The substrate-recognized options span a spectrum from
single-cloud managed services to self-managed platforms.

### Option 1: Single-cloud native (AWS Secrets Manager / GCP Secret Manager / Azure Key Vault)

**Substrate preference:** Substrate-preferred for single-
cloud applications.

**Applicable when:** Application runs in one cloud and is
likely to remain so for the foreseeable future; workload
identity is already established in that cloud.

**Pros:**
- Tightest IAM integration; workload identity binds
  directly to platform access
- Tight KMS integration for secrets-management.encryption-at-rest encryption at
  rest
- Managed service: rotation, replication, audit log
  emission, and key lifecycle handled by the provider
- Tight integration with rest of cloud-native stack
  (CloudWatch, Cloud Logging, Azure Monitor)
- Cost transparent (per-secret-per-month plus API call)

**Cons:**
- Cross-cloud portability is limited; secrets must be
  replicated or re-keyed to use in another cloud
- Vendor lock-in: secrets-manager API differs across the
  three major clouds
- Multi-region replication is per cloud's mechanism, not
  abstracted
- Cost per secret can become significant with high secret
  counts

### Option 2: HashiCorp Vault (self-managed)

**Substrate preference:** Substrate-preferred for multi-
cloud and hybrid deployments where operational maturity
supports it.

**Applicable when:** Application is multi-cloud, hybrid, or
on-premises; the consumer has dedicated platform
engineering capacity to operate Vault; advanced features
(dynamic secrets, transit engine, PKI engine) are needed.

**Pros:**
- Cloud-agnostic; one platform serves all environments
- Dynamic secrets engine (database, cloud credentials)
  provides per-session credentials, enabling stronger
  least-privilege patterns (secrets-management.least-privilege-access)
- Mature policy language for secrets-management.least-privilege-access grants
- PKI engine, transit engine, and KMIP support extend
  beyond simple secret storage
- Strong audit logging
- Performance replication and disaster-recovery
  replication for multi-region

**Cons:**
- Operational burden: clustering, unsealing, backup,
  upgrade, monitoring, capacity planning
- Bootstrap chicken-and-egg: Vault needs an unseal
  mechanism; choosing the unseal mechanism is its own
  decision (auto-unseal via cloud KMS is substrate-
  recommended where applicable)
- License cost for Vault Enterprise features (HSM
  integration, MFA support, multi-tenant namespaces)
- Steeper learning curve for both operators and consumers

### Option 3: Hybrid (cloud-native primary plus Vault for cross-cloud)

**Substrate preference:** Substrate-acceptable; common
pragmatic compromise.

**Applicable when:** Application primarily lives in one
cloud but has cross-cloud or on-premises components that
need secrets; the consumer wants to limit Vault's
operational footprint to the cases that genuinely require
it.

**Pros:**
- Combines simplicity of cloud-native with portability of
  Vault for the components that need it
- Reduces Vault operational burden compared to Option 2
- Allows incremental adoption: start cloud-native, add
  Vault when cross-cloud needs emerge

**Cons:**
- Two platforms to learn and operate
- Cross-platform consistency (audit format, rotation
  cadence, access policy patterns) requires consumer-side
  discipline
- Cost of both platforms; complexity multiplied

### Option 4: Kubernetes-native (external-secrets operator with cloud or Vault backend)

**Substrate preference:** Substrate-preferred for
Kubernetes-orchestrated applications.

**Applicable when:** Application runs on Kubernetes; the
team wants to abstract the underlying secrets platform
behind a Kubernetes-native interface.

**Pros:**
- Application code reads from Kubernetes Secret objects
  (familiar pattern); platform team configures the backend
- Switching backends (e.g., AWS Secrets Manager today,
  Vault tomorrow) does not require application code changes
- Operator pattern reconciles secret state continuously
- Mature open-source operators (external-secrets,
  secrets-store-csi-driver)

**Cons:**
- Adds a layer that must be operated and monitored
- Secret values reach Kubernetes Secret objects which are
  base64-encoded, not encrypted unless etcd KMS encryption
  is configured (must combine with EncryptionConfiguration
  to satisfy secrets-management.encryption-at-rest)
- Operator failure modes can produce stale or missing
  secrets in Kubernetes
- Audit trail spans the operator plus the underlying
  platform; correlation requires consumer-side tooling

### Option 5: Deployment-platform secrets (Kubernetes Secret raw, environment variables, deployment templates)

**Substrate preference:** Substrate-DISCOURAGED as the
primary platform choice. Acceptable only for development
and non-production environments where the underlying
platform's L2 properties are not required.

**Applicable when:** Local development, test environments,
genuinely ephemeral non-production workloads where
SECRETS-L2 rules are explicitly out of scope.

**Pros:**
- Zero additional operational burden
- Familiar to developers
- Works in all environments

**Cons:**
- Fails secrets-management.runtime-retrieval (no runtime retrieval; values are
  static in the deployment)
- Fails secrets-management.rotation-policy (rotation requires redeploy)
- Fails secrets-management.least-privilege-access (no per-secret access policy)
- Fails secrets-management.encryption-at-rest (deployment-tool storage typically
  not separately KMS-encrypted)
- No audit trail of which workload accessed which secret
  when
- The substrate's L2 review checklists will flag this
  pattern as non-compliant

## Decision Outcome

The substrate's preferred order of consideration for new
applications:

1. **Option 4 (Kubernetes-native)** for any application
   running on Kubernetes, regardless of underlying cloud
2. **Option 1 (single-cloud native)** for single-cloud
   applications that are not on Kubernetes
3. **Option 2 (Vault)** for multi-cloud, hybrid, or
   advanced-feature requirements where operational
   maturity supports it
4. **Option 3 (hybrid)** when the application's needs
   genuinely span the boundary between Option 1 and
   Option 2
5. **Option 5 (deployment-platform)** never for production;
   acceptable for development and non-production where the
   profile explicitly scopes out the L2 rules

Consumers may choose any option that fits their context.
Choices that deviate from substrate preference for a given
context must be explicitly justified in the consumer's ADR
(see Documentation Required section).

## Pros and Cons of the Options

Detailed analysis is provided per option in the Considered
Options section above. Consumers should adapt this analysis
to their specific application context, adding application-
specific pros and cons that the substrate cannot anticipate.

When the application context aligns clearly with a substrate-
preferred option (e.g., Kubernetes on AWS with mature
external-secrets operator practice clearly fits Option 4),
the consumer's ADR can be relatively short, citing the
substrate analysis and adding application-specific details.
When the application context creates tension (e.g., single-
cloud team operating with significant platform engineering
capacity choosing Vault over Option 1), the ADR must address
the tension explicitly and reason through the trade-off.

## Documentation Required

Consumers using this framework satisfy secrets-management.platform-selection by
producing an ADR in their application that addresses each
of the following. The consumer's ADR location is substrate-
recommended at
`/docs/decisions/ADR-XXX-secrets-management-platform.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: application-specific
  context covering cloud footprint, existing identity
  infrastructure, regulatory regime, operational maturity,
  multi-region requirements, application architecture, and
  budget
- **Decision Drivers**: the substrate's drivers (D1-D7
  above) adapted to the application's specific context,
  plus any application-specific drivers
- **Considered Options**: at least the substrate options
  that are plausibly applicable; consumers may exclude
  options with brief reasoning (e.g., "Option 2 (Vault
  self-managed) excluded: platform team capacity does not
  support Vault operations")
- **Decision Outcome**: the chosen option with reasoning
  that references the decision drivers
- **Substrate Alignment**: explicit statement of whether
  the choice aligns with substrate-preferred options for
  the application context; deviations must be justified
- **Consequences**: positive consequences (which risks are
  managed), negative consequences (operational overhead,
  cost, vendor lock-in), and required follow-up work
  (additional ADRs for unseal mechanism, KMS choice,
  rotation policy)
- **Pros and Cons of Each Option**: option-comparative
  analysis showing why the chosen option was preferred
  over the rejected options
- **References**: secrets-management.platform-selection substrate rule, related
  substrate rules in scope, application-specific
  references (compliance documentation, prior ADRs)
- **Decision Review Schedule**: next scheduled review
  date (substrate-recommended annually) and triggers that
  force earlier review (compliance regime change, major
  architectural shift, vendor incident, substrate version
  increment)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR. Consumers can self-review against the
checklist before submitting their ADR for acceptance.

## More Information

This framework is referenced by:

- **secrets-management.platform-selection** (substrate rule): the rule that
  requires consumers to author a secrets management
  platform ADR
- **secrets-management.runtime-retrieval through secrets-management.encryption-at-rest**: apply to all
  platforms; the choice affects how each rule is satisfied
- the secrets-management mechanical (L1) rules: apply
  regardless of platform; the L1 rules govern the source-
  code surface, not the platform surface

This framework relates to (but is independent of):

- **Cross-concern boundary with authentication**: a single
  shared secrets platform may serve both the authentication
  concern (e.g., session signing keys) and other concerns.
  The platform choice is the same; the audit, rotation, and
  access policies may be configured per-concern within the
  platform.
- **Cross-concern boundary with supply-chain**: the
  secrets platform's own software supply chain (Vault
  binary provenance, cloud SDK provenance) is governed by
  the dependency-management concern.

External references:

- NIST SP 800-57 Part 1 Rev 5 (Recommendation for Key
  Management):
  https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final
- OWASP Secrets Management Cheat Sheet:
  https://owasp.org/www-project-secrets-management/
- HashiCorp Vault documentation:
  https://developer.hashicorp.com/vault/docs
- AWS Secrets Manager User Guide:
  https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- GCP Secret Manager documentation:
  https://cloud.google.com/secret-manager/docs
- Azure Key Vault documentation:
  https://learn.microsoft.com/en-us/azure/key-vault/general/overview
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
