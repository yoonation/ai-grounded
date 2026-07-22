---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: logging.architecture
title: "..."
lifecycle-status: stable
commons-version: "0.4.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-20"
entered-status-at: "2026-05-22"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
ai-assistance: "AI drafted from substrate-author intent following the secrets-management-platform.madr.md precedent; third decision framework authored in the substrate; exercises the established MADR pattern for the logging concern. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft."
authoritative-sources:
  - "https://csrc.nist.gov/publications/detail/sp/800-92/final"
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x20-V11-BusLogic.md"
  - "https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/"
  - "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"
  - "https://opentelemetry.io/docs/specs/otel/logs/"
  - "https://docs-prv.pcisecuritystandards.org/PCI%20DSS/Standard/PCI-DSS-v4_0_1.pdf"
  - "https://adr.github.io/madr/"
---

# Logging Architecture Selection

This decision framework provides the substrate's analysis of
logging architecture options. Consumers reference this framework
when authoring their own ADR documenting their application's
logging architecture. The substrate-recommended location for
the consumer's ADR is
`/docs/decisions/ADR-XXX-logging-architecture.md`.

The framework is referenced by substrate rule logging.architecture,
which requires applications to have an explicit, documented
logging architecture decision before non-trivial log streams
enter production. Consumers satisfy logging.architecture by authoring an
ADR that adapts the analysis in this framework to their
application context.

## Context

Logging architecture is a platform-level concern with four
interlocking decisions: aggregator selection (where logs land),
transport (how they get there), retention bands (how long they
stay), and integrity model (how they are protected from
tampering). Each decision affects the others. Choosing the
aggregator after the transport is built forces re-engineering;
choosing retention without the integrity model produces
compliance gaps; choosing the integrity model without the
aggregator constrains aggregator selection significantly.

The substrate-recommended pattern is to make all four
decisions together as a single architectural choice, document
the decision in an ADR before the first non-trivial log stream
enters production, and revisit annually or on triggers (new
cloud platform, new regulatory regime, significant scale
change).

The choice has implications across every subsequent LOG-L2
rule. Retention bands (logging.retention-policy) depend on aggregator
capability and cost profile. Integrity (logging.integrity) depends on
aggregator features and the transport's in-flight protection.
Redaction (logging.redaction) is enforced both at the call site (the
application's logger library) and at the pipeline (the
aggregator's content scanning). Aggregation readiness
(logging.aggregation) is satisfied by the aggregator's search, time-
range, and cross-service-join capabilities.

Common substrate failure modes:

- Teams default to whatever the cloud provider's documentation
  first surfaces, treating the default as a deliberate choice.
  The default may be good or bad for the application's context;
  the failure is not making the choice deliberately.
- Teams adopt the cheapest aggregator without examining
  integrity, search, or cross-service join capability. The
  cost lever is real but it is one driver among several.
- Teams adopt an aggregator that satisfies operational needs
  but does not satisfy regulatory needs (e.g., a SaaS
  aggregator without the data residency the consumer's
  regulator requires). The mismatch surfaces during the first
  audit.
- Teams treat retention as the aggregator's default, then
  discover during a compliance audit that the default is
  shorter than the required retention.

The substrate provides analysis of each viable architectural
choice but does not prescribe a single answer. Consumers
select based on their context. The substrate requires the
choice to be documented and reasoned; it does not require
consumers to choose the substrate-preferred option for their
context.

## Decision Drivers

The substrate identifies the following drivers that should
inform the logging architecture choice. Consumers may add
application-specific drivers but should address each substrate
driver in their ADR.

- **D1. Cloud platform footprint.** Single-cloud, multi-cloud,
  hybrid, or on-premises. Cloud-native aggregators (CloudWatch
  Logs Insights, Cloud Logging, Azure Monitor) have tightest
  integration with the respective cloud's IAM and ingestion
  agents but create cross-cloud friction. Cloud-agnostic
  aggregators (Datadog, Splunk, Elastic, Loki) trade
  integration depth for portability.

- **D2. Existing observability infrastructure.** Whether the
  consumer already runs a SIEM, an Elastic cluster, or a
  commercial observability platform. Adopting an aggregator
  that integrates with existing infrastructure has lower
  operational cost than adopting a parallel system. Where the
  consumer has none, the choice is open.

- **D3. Regulatory regime.** PCI DSS, HIPAA, FedRAMP, FIPS-140
  compliance modes, financial services data residency,
  government cloud requirements (AWS GovCloud, Azure
  Government, GCP Assured Workloads), and EU data residency
  (GDPR) all constrain which aggregators are usable in which
  configurations. The consumer's regulatory context narrows
  the option set materially.

- **D4. Operational maturity.** Self-managed Elastic or Loki
  clusters require operational effort: index management,
  upgrade discipline, capacity planning, retention
  management. Teams without dedicated platform engineering
  capacity often find managed cloud-native or commercial SaaS
  aggregators more sustainable. The honest assessment of
  operational maturity is a substrate-required driver because
  underweight produces predictable failure modes.

- **D5. Scale and retention profile.** Log volume per day,
  query rate, and retention duration drive aggregator cost in
  fundamentally different ways. Cloud-native aggregators
  charge by ingestion plus per-query cost; commercial SaaS
  charges by retention plus query volume; self-managed costs
  scale with infrastructure capacity. The consumer's profile
  determines which cost model is favorable.

- **D6. Application architecture.** Container-orchestrated
  workloads (Kubernetes) benefit from sidecar-based shippers
  (Fluent Bit, Vector) or cluster-level log collectors.
  Serverless workloads (Lambda, Cloud Functions) emit logs
  directly to the cloud-native aggregator. VM workloads accept
  agent-based shipping. The architecture constrains the
  transport choice.

- **D7. Budget and cost model.** Logging costs are typically
  in the top operational cost categories; the chosen
  architecture should produce a predictable cost profile that
  matches the consumer's budget. Cost surprises drive ad-hoc
  retention cuts that break compliance.

## Considered Options

The substrate-recognized options span cloud-native managed,
self-hosted open-source, commercial SaaS, and hybrid
configurations.

### Option 1: Cloud-native managed (CloudWatch Logs Insights, Cloud Logging, Azure Monitor)

**Substrate preference:** Substrate-preferred for single-cloud
applications.

**Applicable when:** Application runs in one cloud and is
likely to remain so; the team has limited operational capacity
for platform infrastructure; the regulatory regime is
satisfied by the cloud provider's compliance certifications.

**Pros:**
- Tightest IAM integration; workload identity for log shipping
  binds directly to aggregator access
- Built-in retention configuration with compliance retention
  modes (e.g., AWS S3 object-lock with governance retention,
  GCP Cloud Logging bucket retention)
- Managed service: capacity, upgrades, redundancy handled by
  the provider
- Tight integration with rest of cloud-native stack (CloudWatch
  alarms, Cloud Monitoring, Azure Monitor metrics)
- Cost transparent for typical workloads (ingestion plus
  retention)

**Cons:**
- Cross-cloud portability is limited; logs in CloudWatch are
  not portable to GCP without re-shipping
- Vendor lock-in: query languages differ across the three
  major clouds (CloudWatch Logs Insights, Cloud Logging
  query, KQL)
- Cross-service join across multiple cloud accounts requires
  aggregator-specific configuration
- Cost can be unpredictable for high-volume workloads with
  ad-hoc query patterns

### Option 2: Self-hosted open-source (Elastic, OpenSearch, Loki)

**Substrate preference:** Substrate-preferred for multi-cloud
deployments where operational maturity supports it; for cost-
sensitive high-volume workloads.

**Applicable when:** Application is multi-cloud, hybrid, or
on-premises; the consumer has dedicated platform engineering
capacity to operate the cluster; advanced query capability is
needed; cost predictability at scale matters.

**Pros:**
- Cloud-agnostic; one aggregator serves all environments
- Operational control: the team owns retention, integrity,
  and access without vendor dependency
- Cost scales with infrastructure capacity, predictable per
  unit volume
- Strong query languages (Elasticsearch DSL, LogQL)
- Mature integrations (Beats, Fluent Bit, OpenTelemetry)
- Custom retention bands and integrity mechanisms
  configurable

**Cons:**
- Operational burden: clustering, upgrade, backup, capacity
  planning
- Self-managed integrity requires explicit configuration; not
  free as it is with cloud-managed object-lock
- Cross-cluster federation for multi-region requires platform
  effort
- License complications: Elastic License (Elasticsearch),
  Apache-2.0 (OpenSearch), Apache-2.0 (Loki). The Elastic vs.
  OpenSearch split affects vendor choice.

### Option 3: Commercial SaaS (Datadog, Splunk Cloud, New Relic, Sumo Logic)

**Substrate preference:** Substrate-acceptable; common
pragmatic choice for organizations with budget but limited
operational capacity.

**Applicable when:** The consumer has the budget; operational
capacity is limited; cross-cloud portability is required;
the SaaS provider's compliance posture matches the consumer's
regulatory regime.

**Pros:**
- Multi-cloud and hybrid support out of the box
- Managed service with strong query and visualization tooling
- Strong commercial support
- Pre-built integrations across most production tools
- Compliance certifications (SOC 2, HIPAA BAAs, PCI DSS)
  often satisfy enterprise regulatory needs

**Cons:**
- Cost scales aggressively with volume; high-volume workloads
  can exceed budget
- Data residency depends on the provider's regional offerings;
  not all regions or compliance regimes are supported
- Vendor lock-in: query languages, dashboard formats are
  vendor-specific
- Third-party data handling: consumer log content reaches the
  vendor's infrastructure; data classification and contractual
  protections matter

### Option 4: Hybrid (cloud-native primary plus cross-cloud aggregator for federation)

**Substrate preference:** Substrate-acceptable; common pragmatic
compromise.

**Applicable when:** Application primarily lives in one cloud
but has cross-cloud or on-premises components; the consumer
wants to limit cross-cloud infrastructure to the cases that
genuinely require it.

**Pros:**
- Combines simplicity of cloud-native within the primary cloud
  with cross-cloud portability for components that need it
- Reduces operational footprint compared to a fully self-hosted
  multi-cloud deployment
- Allows incremental adoption: start cloud-native, add the
  cross-cloud aggregator when cross-cloud needs emerge

**Cons:**
- Two aggregators to operate and learn
- Cross-aggregator query is operationally painful; correlation
  between systems requires extra effort
- Cost of both systems; query patterns may shift unpredictably
- Cross-aggregator integrity model is harder to attest

### Option 5: Sidecar-shipped versus agent-shipped versus cloud-direct (transport sub-decision)

The transport choice is partially independent of aggregator.
Substrate-acceptable transports:

- **Sidecar shippers (Fluent Bit, Vector as sidecar):**
  Container-orchestrated workloads. Sub-minute latency, per-
  container configuration, isolation from the application
  container. Substrate-preferred for Kubernetes.
- **Node-level agents (Fluent Bit, Vector as DaemonSet, cloud-
  native agents):** Container workloads with shared node
  configuration. Lower resource overhead, slightly less
  isolation.
- **In-process libraries (logback appenders, log4net targets,
  language-native HTTP loggers):** Direct ingestion from
  application code. Lower latency, tight coupling, can produce
  application slowdown under aggregator backpressure.
- **Cloud-direct (Lambda console logs, Cloud Run logs):**
  Serverless workloads emit directly to the cloud-native
  aggregator. Minimal configuration; transport is the
  platform's responsibility.

### Option 6: No deliberate logging architecture (substrate-discouraged)

The substrate names this option only to document its
rejection. Teams that defer the decision until "we get
around to it" produce three reliable outcomes: implicit
adoption of cloud-provider defaults (which may or may not fit
the regulatory regime), retention drift (logs accumulate
beyond cost-effective windows), and operational gaps surface
during the first incident or audit.

**Substrate position:** Not a valid option for production
applications with non-trivial log volume.

## Decision Outcome

The consumer's ADR documents the chosen option for each of
four components: aggregator, transport, retention bands, and
integrity model. The decision outcome connects the chosen
option to the consumer's drivers.

Example outcome statements:

- "We adopt CloudWatch Logs Insights as the aggregator
  (Option 1), Fluent Bit sidecar as the transport (Option 5
  sidecar-shipped), operational 14 days / application
  90 days / audit 13 months as retention bands (logging.retention-policy),
  and CloudWatch Logs retention plus S3 object-lock on the
  audit-stream export as the integrity model (logging.integrity).
  We chose Option 1 because D1 (single-cloud AWS) and D4
  (team has limited platform-engineering capacity) dominated;
  D3 (PCI DSS) is satisfied by AWS attestations and the
  object-lock configuration."

- "We adopt self-hosted Elastic (Option 2) with Vector
  shipper (Option 5 sidecar), tiered retention via ILM
  (operational 7 days / application 120 days / audit
  7 years), and per-record signing via the Vector signing
  transform as the integrity model. We chose Option 2
  because D5 (multi-petabyte volume) and D7 (commercial
  SaaS cost projection exceeded budget by 4x) dominated; the
  platform team's existing Elastic operational maturity
  satisfies D4."

## Consequences

Documenting the consequences of the chosen architecture is
required. Substrate-recommended consequences to document:

- **Operational ownership:** which team owns the aggregator
  configuration, the shipping pipeline, the retention policy
  reviews, and the integrity verification exercises.
- **Cost profile:** projected ingestion volume, retention
  cost, query cost; the cost-review cadence and trigger for
  rebudgeting.
- **Compliance posture:** which regulator-facing
  certifications the chosen architecture satisfies and which
  require additional controls.
- **Risks accepted:** known limitations of the chosen
  architecture; the consumer's acceptance of those
  limitations.
- **Migration cost if revisited:** the effort required to
  switch aggregators or transports if a future driver
  changes; the substrate-recommended posture is to make this
  cost visible so future migration decisions are informed.

## Documentation Required

The consumer's ADR satisfies logging.architecture by addressing each
section the substrate's template specifies:

- Status (proposed, accepted, deprecated, superseded)
- Context and problem statement (application-specific)
- Decision drivers (the substrate's seven plus any
  application-specific)
- Considered options (at least two non-trivial alternatives
  evaluated)
- Decision outcome (aggregator, transport, retention bands,
  integrity model named)
- Substrate-alignment statement (which substrate-preferred
  option applies to the consumer's context, and where the
  consumer's choice differs and why)
- Consequences (operational, cost, compliance, risks,
  migration cost)
- Pros and cons of each option
- References (this framework, the substrate rule, the
  authoritative sources)
- Decision-review schedule (cadence and trigger events)

## More Information

The substrate's logging architecture position is
operationalized across LOG-L1 and LOG-L2 rules:

- logging.structured-format structured format: the chosen aggregator must
  consume structured records
- logging.correlation-ids correlation IDs: the chosen transport must
  preserve trace context
- logging.retention-policy retention policy: the chosen aggregator must
  support per-stream retention configuration
- logging.integrity integrity: the chosen aggregator must support
  the chosen integrity mechanism
- logging.redaction redaction: the chosen aggregator must support
  pipeline-side scrubbing
- logging.aggregation aggregation: the chosen aggregator must satisfy
  the substrate's search, time-range, and cross-service-join
  capability requirements

Consumers whose ADR conflicts with any of these rules
document the conflict explicitly and adopt mitigations.
