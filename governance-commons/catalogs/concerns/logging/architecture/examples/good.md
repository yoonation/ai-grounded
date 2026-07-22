<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.architecture logging architecture ADR (good patterns)

The substrate-recommended location for the consumer's ADR is
`/docs/decisions/ADR-XXX-logging-architecture.md`. The example
below shows the structure of a well-authored ADR that
satisfies logging.architecture.

## Pattern A: Filled-in ADR for a single-cloud SaaS application

```markdown
# ADR-012: Logging Architecture

## Status

Accepted (2026-04-10)

## Context

Acme Health Platform is a single-tenant SaaS hosted on AWS.
Daily log volume: ~20GB across 18 microservices. The
application processes Protected Health Information (PHI)
and is subject to HIPAA (with a BAA from AWS), SOC 2
Type II annually, and our customers' periodic security
questionnaires. Engineering is 12 people; we do not have a
dedicated platform engineering team.

We had been writing logs to local disk and rotating them
weekly. The Security Operations Center was unable to perform
cross-service investigation; our last audit flagged the
absence of centralized aggregation.

## Decision Drivers

- **D1 Cloud footprint:** Single-cloud (AWS), unlikely to
  change in the next 24 months.
- **D2 Existing observability:** We use Datadog for metrics
  and APM; engineers know its query language.
- **D3 Regulatory regime:** HIPAA BAA required from the
  aggregator; SOC 2 audit-log retention 12 months minimum;
  PCI scope is out (no card data handled directly).
- **D4 Operational maturity:** Engineering team of 12, no
  dedicated platform engineers. We need a managed service.
- **D5 Scale and retention profile:** 20GB/day; expected
  growth to 50GB/day in 18 months. Audit retention 13
  months; application retention 90 days; debug 14 days.
- **D6 Application architecture:** EKS-based microservices
  with Fluent Bit DaemonSet sidecar already deployed for
  metrics shipping.
- **D7 Budget:** $4k/month budget for aggregator services
  approved.

**Application-specific driver D8:** Annual customer
penetration tests include a logging-coverage check; absence
of incident-response query capability has been flagged in
two consecutive years.

## Considered Options

### Option 1: AWS CloudWatch Logs Insights (cloud-native managed)

Pros:
- Tightest AWS IAM integration; we use IRSA already.
- HIPAA-eligible service under our BAA.
- Cost predictable at our volume (~$1500/mo projected).
- Object-lock on archived audit-stream export to S3
  provides integrity.

Cons:
- Query language differs from Datadog; engineers need to
  learn CloudWatch Logs Insights syntax.
- Cross-service join requires explicit field structuring;
  no built-in trace correlation UI.

### Option 2: Datadog Logs (commercial SaaS)

Pros:
- Engineers already know Datadog; APM-Log correlation
  is automatic.
- HIPAA-eligible.
- Cross-service join via trace_id is built-in.

Cons:
- Ingestion cost projection ($3200/mo at current volume)
  exceeds budget at the projected 50GB/day growth point.
- Data residency: logs leave AWS to Datadog's infrastructure.

### Option 3: Self-hosted Loki on EKS (open-source)

Pros:
- Lowest direct cost; infrastructure-only spend.
- LogQL is approachable for engineers familiar with
  PromQL.

Cons:
- Operational burden of running Loki at this scale
  exceeds our platform-engineering capacity (D4).
- Self-managed integrity requires explicit configuration.

## Decision Outcome

We adopt **Option 2: Datadog Logs** as the aggregator,
**Fluent Bit DaemonSet** as the transport (continuing the
existing deployment), **operational 14 days / application
90 days / audit 13 months** as retention bands, and
**Datadog Logs Indexed pipelines + S3 export with
object-lock** as the integrity model for audit streams.

Substrate-alignment statement: The substrate-preferred
option for our context (D1 single-cloud, D4 limited platform
maturity) is Option 1 (cloud-native managed). We chose
Option 2 because D2 (existing Datadog familiarity) and D8
(APM-Log correlation reduces incident-response time
demonstrated in last quarter's GameDay) outweighed the
substrate preference. Cost (D7) is within budget at current
volume; at 50GB/day we will revisit at the substrate-
recommended annual cadence.

## Consequences

- **Operational ownership:** Security Operations team owns
  the Datadog aggregator configuration. Platform team owns
  the Fluent Bit DaemonSet. Engineering team owns the
  application-side logging libraries.
- **Cost profile:** Projected $2800/mo at current volume.
  At 50GB/day projected ~$4500/mo; budget revisit required
  before reaching that volume. Cost-monitoring alert at
  $3500/mo trigger.
- **Compliance posture:** HIPAA BAA in place with Datadog;
  SOC 2 audit-log retention satisfied via Datadog 13-month
  retention plus S3 object-lock archival; data residency
  documented for customer SQs.
- **Risks accepted:** Data egress from AWS to Datadog
  carries a transmission cost; vendor lock-in to Datadog
  query language; cost-growth sensitivity.
- **Migration cost if revisited:** Two-week engineering
  effort to switch aggregators, dominated by query template
  rewriting.

## Pros and Cons of Options

(See "Considered Options" above for per-option pros/cons.)

## References

- Substrate rule logging.architecture
- Decision framework: decision-frameworks/logging-architecture.madr.md
- Datadog HIPAA Compliance: https://docs.datadoghq.com/data_security/
- AWS BAA: in our compliance records

## Decision-review schedule

- Annual review at the start of each calendar year
- Trigger events that prompt early review:
  - AWS account expansion to a new region
  - Log volume exceeding 40GB/day (cost-trigger threshold)
  - New regulatory regime applicable to our customer base
- Next scheduled review: 2027-01-15
- Review ownership: VP Engineering and CISO jointly
```

Why this satisfies logging.architecture: every required section is
present and substantive. Drivers are application-specific,
not generic. Considered options have genuine pros and cons.
The substrate-alignment statement explains the deviation
from the substrate-preferred option with reasoning tied to
the consumer's drivers. Consequences are operational, not
aspirational. The review schedule is specific.

## Pattern B: ADR for a multi-cloud platform

The substrate-original example above covers a SaaS-on-AWS
case. A multi-cloud case follows the same structure but
typically lands on Option 2 (self-hosted) or Option 3
(commercial SaaS) for the portability driver. The
substrate-alignment statement in a multi-cloud ADR justifies
the choice against the substrate's preference for
cloud-native managed in single-cloud contexts.

## Cross-reference

- Anti-patterns: examples/logging/architecture-anti-pattern.md
- Substrate rule: logging.architecture
- Decision framework: decision-frameworks/logging-architecture.madr.md
- Review checklist: checklist.md
