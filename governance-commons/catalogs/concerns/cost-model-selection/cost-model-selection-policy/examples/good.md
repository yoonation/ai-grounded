<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-model-selection-policy cost model selection policy (good patterns)

Substrate-original good-pattern example for cost-model-selection.cost-model-selection-policy: a
complete consumer ADR adapting the substrate framework.

## Example consumer ADR

```markdown
---
# Consumer ADR: ADR-014 payments-api Cost Model and Over-Budget Response Policy
status: accepted
date: 2026-05-15
authors: [@myoung, @product-owner-payments]
substrate-framework: decision-frameworks/cost-model-selection-policy.madr.md
substrate-version: 0.3.0
related-adr: docs/decisions/ADR-013-payments-api-slo-policy.md
---

# ADR-014: payments-api Cost Model and Over-Budget Response Policy

## Status

Accepted (2026-05-15). Next review 2027-05-15.

## Context

payments-api is a top-tier customer-facing service. The service
handles HTTP POST requests for payment authorization, capture,
and refund operations across multiple customer tenants on a
per-transaction SaaS pricing model. The consumer's business
model is unit-economics-driven: each customer pays a per-
transaction fee; service margin depends on cost-per-transaction
staying below a documented threshold.

Cost-model-relevant facts:
- 2025 average transaction volume: 4.2M/month
- 2025 average cost: $22,400/month (cost per transaction
  $0.0053)
- 2026 target volume: 10.4M/month at 2x growth
- 2026 unit-economics target: cost per transaction at or below
  $0.0024 (substrate-recommended growth-phase target reflecting
  economies of scale)
- 2026 absolute budget: $25,000/month at expected growth
- Reliability commitment (per ADR-013): 99.9 percent monthly
  request success ratio; p99 latency under 2 seconds

## Decision drivers

Following the substrate framework drivers:

- **D1 Business model and unit economics:** SaaS provider; per-
  transaction pricing model; substrate-preferred cost SLI is
  cost per transaction (A3) combined with absolute monthly
  budget (A1).
- **D2 Reliability commitments and trade-off boundary:** the
  ADR-013 99.9 percent SLO commits the consumer to a specific
  reliability cost. The cost-model ADR documents the trade-
  off: an additional 9 of availability (99.99 percent) would
  require multi-region active-active payments-database at
  approximately $40,000/month additional spend; rejected at
  the current customer commitment level.
- **D3 Operational maturity and pipeline discipline:** the
  team has operated cost-model-selection.cost-emission-pipeline pipeline reconciliation for
  18 months at 1.2 percent variance against threshold;
  pipeline discipline supports tight cost-per-transaction
  tracking.
- **D4 Multi-tenant constraints:** payments-api is multi-
  tenant; per-tenant attribution via OpenCost is in place;
  per-tenant cost variance affects pricing tier sustainability.
- **D5 Vendor contract structure:** primarily AWS-billed; one
  reseller vendor (Stripe) bills monthly outside AWS; the
  cost-lake pipeline ingests both.
- **D6 Growth phase and cost forecasting cadence:** growth
  phase; year-over-year cost trajectory matters; consumer's
  annual budget cycle is quarterly planning with monthly
  variance review.
- **D7 Cost-anomaly tolerance and burn-rate alerting cadence:**
  substrate-recommended 1-day and 7-day burn-rate windows
  configured.

## Considered options (summary; full analysis in substrate framework)

Cost SLI selection: A1 (absolute monthly cost) and A3 (cost per
transaction). Substrate-preferred composite for transactional
services in unit-economics-driven businesses.

Cost SLO target shape: B1 (absolute monthly budget) and B2
(unit-economics target). Both targets together capture business
sustainability that either alone misses.

Budget computation: D1 (provider-billing-export-driven) for the
AWS portion; D2 (pipeline-derived with reseller adjustment) for
the Stripe portion. The cost-lake pipeline merges the two
into a single attributed view.

Over-budget response: E1 (workload-level mitigation first),
E2 (service-level rate limiting at the API gateway tier), E3
(product-owner escalation) layered on top, E4 (accepted
variance) only for documented one-time external events such as
a Stripe price increase.

## Decision outcome

- **Cost SLI:** Composite of absolute monthly cost (A1) and
  cost per transaction (A3). Both signals tracked monthly.
- **Cost SLO targets:**
  - Absolute monthly budget: $25,000 (B1)
  - Cost per transaction: $0.0024 at expected volume (B2)
  - Tiered by service tier: tier-0 customer-facing (B3); the
    payments-api is in tier-0
- **Budget computation:** cost-lake pipeline (D2) ingesting
  both AWS CUR (daily) and Stripe invoice (monthly on
  publication). Allocation rules attribute spend per service
  via the cost-model-selection.cost-attribution-tags tags; per-tenant attribution via OpenCost
  for Kubernetes workloads.
- **Over-budget response policy:**
  - At 50 percent budget remaining (projected): workload-level
    mitigation per E1. The payments-api on-call engineer
    investigates the alert's top-contributor finding and
    applies the substrate-recommended response (revert
    misconfiguring deploy; tune a slow query; throttle
    upstream traffic).
  - At 25 percent budget remaining (projected): service-level
    rate limiting per E2. The API gateway's tier-1 rate limit
    engages, throttling lowest-tier customers first per the
    consumer's pricing policy.
  - At 10 percent budget remaining (projected): product-owner
    escalation per E3. @product-owner-payments has authority
    to pause non-essential feature work, negotiate scope with
    customer commitments owner, or accept variance with
    documented rationale.
  - At budget exceeded: burndown after-action review. ADR
    amendment if budget mismatch is structural.

## Cost-vs-reliability trade-off rationale

The reliability commitments in ADR-013 (99.9 percent monthly
SLO) cost the substrate-recognized 99.9 percent reliability
investment level. The cost-vs-reliability trade-off at the
substrate-recognized boundaries:

- **Additional 9 of availability (99.99 percent):** rejected.
  Multi-region active-active payments-database at approximately
  $40,000/month additional spend exceeds the consumer's
  unit-economics target. The current customer commitment level
  does not justify the investment. Revisit on customer SLA
  upgrade.
- **Fault-injection program:** approved as discrete line item.
  Substrate-recommended for tier-0 services; budgeted at
  $1,800/month for chaos engineering tooling and synthetic
  load.
- **Multi-region active-active topology:** rejected as above.
  Single-region with substrate-recommended cross-AZ HA at
  current spend level.
- **Regulated-region deployment:** N/A; payments-api operates
  in a single regulatory regime.

The reliability error budget (per ADR-013) and the cost budget
operate as paired constraints. Where a substantial budget-
burndown event invokes a trade-off (an additional reliability
investment would consume budget; reducing reliability
investment would free budget but degrade SLO compliance), the
product-owner escalation (E3) is the substrate-recommended
decision point.

## Substrate alignment

The decisions in this ADR align with the substrate framework:
the substrate-recommended composite (A1+A3 SLI, B1+B2+B3 target,
D1+D2 computation, E1+E2+E3 response) maps cleanly to the
consumer's business model. The cost-vs-reliability trade-off
rationale addresses each substrate-recognized boundary; the
cross-reference to ADR-013 is explicit.

Where the consumer's position diverges from the substrate-
preferred default (none in this ADR; the consumer adopted the
substrate-recommended composite directly), divergences would
be documented in this section with rationale.

## Consequences

- **For attribution discipline:** the cost-per-transaction SLI
  requires reliable transaction-count denominator data. The
  payments-api instrumentation emits a transactions_total
  metric (per observability.metric-naming-convention metric naming convention) that the
  pipeline consumes. The consumer's product analytics confirms
  the definition matches the billing transaction.
- **For workload configuration:** the absolute monthly budget
  combined with cost-model-selection.workload-resource-limits resource limits sets the runtime
  cost ceiling. The team's right-sizing review (cost-model-selection.cost-emission-pipeline)
  uses production data to confirm limits are set to 1.5x the
  observed p99 usage; no workload runs unbounded.
- **For team operations:** the over-budget response policy is
  binding. The team's on-call rotation includes cost burndown
  in the on-call expectations document. @product-owner-payments
  is engaged at the E3 escalation tier and has confirmed
  authority to invoke the documented responses.
- **For executive reporting:** the cost SLI is reported monthly
  to the consumer's finance team; year-over-year trajectory is
  reported quarterly. The substrate-recommended cadence aligns
  with the consumer's existing reporting cycle.
- **For pricing decisions:** the cost-per-transaction SLI feeds
  the consumer's pricing analysis. The 2026 target ($0.0024
  per transaction) reflects expected economies of scale at 2x
  volume; the pricing team uses the SLI in tier-pricing
  decisions for new customer contracts.

## References

- Substrate framework: decision-frameworks/cost-model-selection-
  policy.madr.md (version 0.1.0)
- Related ADR: ADR-013 payments-api SLO and Error Budget Policy
- Substrate rules consumed: cost-model-selection.cost-attribution-tags, cost-model-selection.workload-resource-limits,
  cost-model-selection.cost-emission-pipeline, cost-model-selection.cost-anomaly-alerting, observability.slo-policy (via ADR-013)
- FinOps Foundation Framework

## Decision review schedule

- **Annual full review:** 2027-05-15
- **Triggered review on:** significant architecture change;
  customer SLA upgrade affecting reliability commitments;
  Stripe contract renegotiation; substantial budget-burndown
  event requiring E3 escalation; 2x deviation from 2026
  volume forecast either direction
- **Quarterly light-touch:** 2026-08-15, 2026-11-15, 2027-02-15.
  Confirms the SLI computation is producing meaningful data;
  confirms the alerting matches the budget computation;
  confirms the response policy has been authoritative.
```

## Why this ADR is good

Every required section is present and substantively populated.
The cost SLIs (A1+A3) connect to the consumer's business model
(unit-economics SaaS provider). The cost SLO targets are
numerically specific at multiple horizons (monthly absolute,
per-transaction unit, tier-based). The budget computation is
reproducible from the cost-model-selection.cost-emission-pipeline pipeline. The over-budget
response is threshold-keyed with concrete actions referencing
documented runbooks. The cost-vs-reliability trade-off rationale
addresses each substrate-recognized boundary with a concrete
position. The ADR cross-references the related observability.slo-policy SLO
policy ADR.

The substrate's L3 review passes. The cost model is anchoring
decision for the L1 and L2 rules below it.
