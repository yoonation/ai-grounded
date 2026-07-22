<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.slo-policy SLO and error budget policy (good patterns)

Substrate-original good-pattern example for observability.slo-policy:
a complete consumer ADR adapting the substrate framework.

## Example consumer ADR

```markdown
---
# Consumer ADR: ADR-014 payments-api SLO and Error Budget Policy
status: accepted
date: 2026-05-15
authors: [@myoung, @product-owner-name]
substrate-framework: decision-frameworks/observability-slo-policy.madr.md
substrate-version: 0.3.0
---

# ADR-014: payments-api SLO and Error Budget Policy

## Status

Accepted (2026-05-15). Next review 2027-05-15.

## Context

payments-api is a top-tier customer-facing service. The
service handles HTTP POST requests for payment authorization,
capture, and refund operations. Customer-visible failure
modes include: failed payment attempts (5xx responses, 4xx
responses misclassified by the service); slow payment
attempts (p99 latency above 2 seconds is operationally
defined as "user-felt slow"). External SLA commits to 99.9
percent monthly availability in the standard customer
contract.

## Decision drivers

Following the substrate framework drivers:

- **D1 Customer commitments:** SLA in customer contract
  commits to 99.9 percent monthly availability of the
  payments-api endpoints.
- **D2 Customer experience signals:** request success ratio
  (failed payments are user-visible) and p99 latency
  (users abandon checkout above 2 seconds, validated by
  product analytics 2026-04).
- **D3 Operational maturity:** the team has been on-call
  for payments-api for 18 months; incident response is
  practiced; instrumentation is mature.
- **D4 Service criticality tier:** payments-api is in the
  consumer's tier-0 catalog (highest criticality).
- **D5 Architectural dependency depth:** payments-api
  depends on payments-database (tier-0) and three external
  payment processors (tier-1 external commitments at 99.95
  percent per processor). Composite availability ceiling
  is approximately 99.95 percent x 0.999 (database) =
  approximately 99.85 percent against any single processor;
  the multi-processor failover architecture lifts the
  composite ceiling to about 99.95 percent.
- **D6 Cost of reliability investment:** the next 9 of
  availability (from 99.9 to 99.99) would require a multi-
  region active-active payments-database; estimated annual
  cost $1.2M; rejected for the current cycle.
- **D7 Alerting cadence requirements:** burn-rate alerting
  with substrate-recommended 1-hour and 6-hour windows.

## Considered options (summary; full analysis in substrate framework)

SLI selection: A1 (request success ratio) and A2 (latency
p99). Substrate-preferred composite for synchronous services.

SLO target shape: B2 (commitment-driven). External SLA
commits to 99.9 percent monthly; internal SLO matches.

Measurement window: C1 (rolling 28-day). Substrate-
preferred default; matches multi-window burn-rate alerting.

Error budget computation: D1 (simple ratio). The composite
SLI is straightforward; weighting (D2) is rejected for this
cycle.

Burndown response: E2 (tiered escalation) plus E3 (product
owner engaged).

## Decision outcome

**SLI 1 - availability:** request success ratio for
payments-api HTTP POST endpoints, computed as

  sum(rate(api_requests_total{service="payments-api",status!~"5..|429|408"}[5m]))
  /
  sum(rate(api_requests_total{service="payments-api"}[5m]))

Excluded statuses: 5xx (server errors), 429 (rate limit;
counted toward client-side dispute), 408 (timeout; counted
toward latency SLI not availability).

**SLI 2 - latency:** p99 latency for payments-api HTTP POST
endpoints, computed as

  histogram_quantile(0.99,
    sum by (le) (rate(api_request_duration_seconds_bucket{service="payments-api"}[5m]))
  )

**SLO target 1 - availability:** 99.9 percent of requests
succeed over a rolling 28-day window. Error budget:
0.1 percent of total requests.

**SLO target 2 - latency:** p99 latency below 2 seconds
sustained over 5-minute windows. Latency violations count
against the latency budget.

**Error budget computation:** simple ratio. Budget consumed
= (failed requests + latency-violating requests) / total
requests over the 28-day rolling window. Latency violations
are computed as 5-minute windows where p99 exceeds 2 seconds.

**Burndown response policy:**

| Budget remaining | Window elapsed | Action |
|------------------|----------------|--------|
| > 75%           | any            | Normal feature work pace |
| 50% to 75%      | > 25%          | Slow feature deploys; double-coverage on any database migration |
| 25% to 50%      | > 50%          | Pause non-customer-facing feature work; prioritize reliability |
| < 25%           | any            | Pause all feature deploys; engage incident-response review |
| 0%              | any            | Escalate to leadership; SLO renegotiation or extraordinary remediation |

Product owner is engaged at the 50 percent threshold;
product owner has authority to invoke the next tier if
business judgment supports it.

## Substrate alignment

This ADR adapts decision-frameworks/observability-slo-policy.madr.md
at substrate version 0.3.0. The chosen options align with
substrate-preferred defaults for a synchronous request-
driven tier-0 service. The next 9 of availability is
rejected for cost (D6); the rejection is documented for
future review.

## Consequences

- **Instrumentation:** observability.no-sensitive-data-in-telemetry, observability.trace-context-propagation, observability.metric-naming-convention,
  observability.semantic-convention-coverage, observability.cardinality-discipline are all in scope and enforced for
  the SLI-driving metrics.
- **Alerting:** the observability.alerting-discipline burn-rate alerts reference
  this ADR. See alerts/payments-api.slo.yml for the
  Prometheus configuration.
- **Dashboard:** the observability.dashboard-discipline SLI dashboard (payments-api
  SLI) references this ADR; the SLI panels reflect the
  computations above.
- **Team operations:** the burndown response policy is
  authoritative; feature work allocation follows the table
  above.

## References

- decision-frameworks/observability-slo-policy.madr.md
- /docs/architecture/payments-api-overview.md
- /docs/decisions/ADR-007-payments-multi-processor-failover.md (architecture context)
- Customer contract template, Section 8.2 (availability SLA)

## Decision review schedule

- **2027-05-15:** annual review (mandatory).
- **Triggered:** new external payment processor; significant
  customer commitment change; significant budget burndown
  event (substantially below the budget at any threshold
  for two consecutive months).
- **Quarterly light-touch:** confirm SLI computation and
  alerting still match the ADR; next light-touch 2026-08-15.
```

Why this satisfies observability.slo-policy: every substrate-required
section is present and substantive; SLI choices reflect
customer experience (validated by product analytics);
numeric targets are explicit; the measurement window matches
the alerting configuration; budget computation is formula-
precise; burndown response has graduated thresholds with
documented actions; the ADR cross-references the substrate
framework, the operational ADRs, and the customer contract;
review cadence is documented.

## Substrate reference observations

- The ADR is operationally meaningful because the burndown
  response is actually invoked when thresholds are crossed.
  The substrate cannot enforce this through the catalog; the
  test of meaningfulness is whether the team has invoked
  the policy in retrospective review of past quarters.
- Product owner engagement (Option E3 in the substrate
  framework) appears in the ADR because the consumer's
  organizational context supports it. Consumers without
  product-owner authority over the SLO mechanism may
  document the equivalent decision-maker.
- The "next 9 rejected for cost" documentation is substrate-
  recommended discipline: rejecting a higher target should
  be a documented decision, not an absence.

## Cross-reference

- Substrate rule: observability.slo-policy in catalogs/concerns/observability.oscal.yaml
- Decision framework: decision-frameworks/observability-slo-policy.madr.md
- Review checklist: checklist.md
- Anti-pattern examples: examples/observability/slo-policy-anti-pattern.md
- Related: observability.alerting-discipline (burn-rate alerting); observability.dashboard-discipline (SLI dashboard); OBS-L1, observability.semantic-convention-coverage, observability.cardinality-discipline (instrumentation supplying SLI data)
