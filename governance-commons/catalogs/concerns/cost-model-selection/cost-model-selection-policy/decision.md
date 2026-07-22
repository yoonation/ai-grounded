---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: cost-model-selection.cost-model-selection-policy
title: "Cost Model Selection and Over-Budget Response Policy"
lifecycle-status: stable
commons-version: "0.4.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-21"
entered-status-at: "2026-05-22"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
ai-assistance: "AI drafted from substrate-author intent following the observability-slo-policy.madr.md precedent; fifth decision framework authored in the substrate; exercises the established MADR pattern for the cost-model-selection concern. SPDX header placed as YAML comments inside frontmatter per Section 10 settled decision 15. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft."
authoritative-sources:
  - "https://www.finops.org/framework/principles/"
  - "https://www.finops.org/framework/capabilities/"
  - "https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html"
  - "https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/"
  - "https://cloud.google.com/architecture/framework/cost-optimization"
  - "https://www.opencost.io/"
  - "https://sre.google/workbook/error-budget-policy/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.observability-slo-policy
---

# Cost Model Selection and Over-Budget Response Policy

This decision framework provides the substrate's analysis of cost
model selection options. Consumers reference this framework when
authoring their own ADR documenting their service's cost commitments
and over-budget response policy. The substrate-recommended location
for the consumer's ADR is `/docs/decisions/ADR-XXX-cost-model-
selection-policy.md`.

The framework is referenced by substrate rule cost-model-selection.cost-model-selection-policy, which
requires services to have an explicit, documented cost model before
exiting their initial production soak period. Consumers satisfy
cost-model-selection.cost-model-selection-policy by authoring an ADR that adapts the analysis in this
framework to their service context.

This framework deliberately parallels the observability-slo-policy
framework in structure and approach. The two concerns are siblings:
reliability has an SLO and an error budget; cost has a cost SLO and
a budget; both have an over-budget response policy. Where the
consumer's service has both kinds of budget, the cost-model ADR
cross-references the SLO-policy ADR at the cost-vs-reliability
trade-off boundary.

## Context

Cost-model selection is a service-level concern with five interlocking
decisions: cost SLI choice (which cost dimensions reflect the
consumer's economic interest), cost SLO target (the numeric cost
commitment), budget computation method (how the consumer's pipeline
calculates the SLO denominator and numerator), over-budget response
policy (what the team does when the budget is consumed), and the
cost-vs-reliability trade-off rationale (the consumer's position on
trade-offs where cost and reliability investments compete). Each
decision affects the others. Choosing the cost SLI without
considering the cost-model-selection.cost-emission-pipeline pipeline's attribution capability forces
re-engineering of the pipeline or undermines the SLI's
reproducibility; choosing the SLO target without instrumentation
discipline produces a target that is not actually computable;
choosing the over-budget response without product-owner alignment
produces a policy that is invoked but not respected.

The substrate-recommended pattern is to make all five decisions
together as a single architectural choice, document the decision in
an ADR before the service exits its initial production soak period,
and revisit annually or on triggers (significant architecture
change, business model shift, substantial budget-burndown event).

The choice has implications across every COST-L1 and COST-L2 rule.
Cost-attribution tagging (cost-model-selection.cost-attribution-tags) supplies the attribution the
budget computation depends on. Workload resource limits (cost-model-selection.workload-resource-limits)
bound the runtime cost per the SLO's per-workload allocation.
Pipeline discipline (cost-model-selection.cost-emission-pipeline) produces the SLO computation.
Anomaly alerting (cost-model-selection.cost-anomaly-alerting) fires against the SLO's per-service
budget. Dashboard discipline (where it exists in the consumer's
observability stack) renders the cost SLO panel set the team and
stakeholders consume.

Common substrate failure modes:

- Teams adopt aspirational cost targets that never materially affect
  team behavior. The target is a number in a dashboard rather than
  a decision input; the over-budget response is not invoked even
  when the budget is exhausted.
- Teams choose cost SLIs that reflect operator convenience (raw
  monthly spend; provider-defined cost categories) rather than the
  consumer's economic interest (cost per active user; cost per
  transaction; cost per tenant). The cost target passes while the
  business is unsustainable.
- Teams set cost SLO targets borrowed from peer services without
  examining the unit economics and business commitments that
  justified those targets in the original context.
- Teams treat the over-budget response as a soft signal. Feature
  work continues at the same pace regardless of burndown; the
  response policy is invoked only in retrospect during post-incident
  review.
- Teams document a cost-vs-reliability trade-off in the abstract
  but improvise the actual decision at trade-off points. The ADR
  is silent on the substrate-recognized boundaries (an additional
  9 of availability; a fault-injection program; a multi-region
  active-active topology) where the trade-off most often arises.

The substrate provides analysis of each viable option but does not
prescribe a single answer. Consumers select based on their context.
The substrate requires the choice to be documented and reasoned; it
does not require consumers to choose the substrate-preferred option
for their context.

## Decision Drivers

The substrate identifies the following drivers that should inform
the cost-model selection. Consumers may add service-specific drivers
but should address each substrate driver in their ADR.

- **D1. Business model and unit economics.** Whether the consumer's
  business model is unit-economics-driven (cost per active user
  matters; cost per transaction matters), volume-driven (absolute
  spend matters at scale), tier-driven (different cost targets for
  different service tiers), or platform-investment-driven (cost is
  managed at the platform level rather than per-service). The
  business model determines which cost SLI options are substantively
  meaningful.

- **D2. Reliability commitments and the cost-vs-reliability boundary.**
  The reliability commitments the service has made (via the observability.slo-policy
  SLO policy) determine the floor of acceptable reliability
  investment cost. Where the reliability commitment is tight,
  reliability investments are non-negotiable and the cost model
  budgets around them. Where the reliability commitment is loose,
  reliability investments compete with cost target at the trade-off
  boundary the cost-model ADR documents.

- **D3. Operational maturity and pipeline discipline.** Whether the
  team can sustain the cost-model-selection.cost-emission-pipeline pipeline discipline that the
  budget computation depends on. Tight cost targets require
  reproducible computation; reproducible computation requires
  cost-model-selection.cost-attribution-tags tag coverage at near-100 percent and a pipeline
  reconciling within the substrate-recommended variance threshold.
  Teams without these capabilities produce cost targets that are
  not auditably met.

- **D4. Multi-tenant constraints.** Where the service is multi-
  tenant, the cost-model ADR must address per-tenant attribution
  (cost-model-selection.cost-emission-pipeline), per-tenant cost variance alerting (cost-model-selection.cost-anomaly-alerting),
  and the consumer's response to a single tenant whose usage drives
  the service into budget burndown. Multi-tenant cost-model decisions
  also constrain the pricing model the consumer's business uses.

- **D5. Vendor contract structure.** Whether the consumer's primary
  cost drivers are cloud-billed (on-demand or reserved pricing
  applies; the cloud provider's billing system is authoritative) or
  vendor-contracted (annual commitments, reseller relationships,
  per-seat licensing, professional services). Vendor-contracted
  cost has different cadence (monthly amortization rather than
  daily billing), different attribution challenges (a single
  invoice line item often does not attribute cleanly to a
  service), and different over-budget response (contract changes
  require lead time the on-demand model does not).

- **D6. Growth phase and cost forecasting cadence.** Whether the
  service is in steady-state (cost targets emphasize variance from
  baseline) or growth phase (cost targets emphasize unit-economics
  trajectory). Growth-phase services often warrant a year-over-year
  growth target as the substrate-recommended cost SLO; steady-state
  services warrant absolute budget targets. The cost forecasting
  cadence the consumer's business uses (annual budget cycle;
  quarterly planning; rolling forecast) constrains the cost SLO's
  measurement window.

- **D7. Cost-anomaly tolerance and burn-rate alerting cadence.**
  The window choice for cost SLO measurement interacts with the
  cost-model-selection.cost-anomaly-alerting burn-rate alerting configuration. A monthly absolute
  budget pairs with the substrate-recommended 1-day and 7-day
  burn-rate windows; a quarterly target requires custom alerting
  math. The two must be designed together.

## Considered Options

The substrate-recognized options span cost SLI selection patterns,
cost SLO target shapes, budget computation methods, and over-budget
response policies. The cost-vs-reliability trade-off rationale is
not an option-space (it is a position the consumer takes) but is
addressed in the Decision Outcome section as part of the substrate-
recommended composite.

### Cost SLI selection options

#### Option A1: Absolute monthly cost per service

**Substrate preference:** Substrate-preferred for steady-state
services in a mature consumer organization where service-level
budgets align with the consumer's annual budget cycle.

**Applicable when:** The service has a stable cost profile; the
business model treats monthly spend per service as the operative
financial line item; the consumer's budgeting cadence is monthly
or quarterly absolute amounts.

**Pros:**
- Simple to communicate and audit
- Aligns with most consumer budgeting cadences
- Cleanly maps to provider billing system invoices
- Pairs cleanly with burn-rate alerting against monthly totals

**Cons:**
- Does not capture unit-economics variance: a service that doubles
  cost because it doubled traffic passes a per-unit target while
  failing an absolute target
- Cannot detect a single tenant or workload driving the spend out
  of band if the service total stays within budget
- Insensitive to growth-phase trajectory: a growth service whose
  cost grows linearly with users may show an alert-triggering
  pattern that is actually healthy growth

#### Option A2: Cost per customer or active user

**Substrate preference:** Substrate-preferred for SaaS providers
and consumer services where unit-economics determine business
sustainability.

**Applicable when:** The consumer's business model is per-user
revenue; the consumer can compute a denominator (active users in
the prior month; paying customers in the prior month) that is
auditable; the cost-per-user dimension is the substrate-recognized
signal the team optimizes for.

**Pros:**
- Aligns with unit-economics business reasoning
- Captures growth-phase trajectory correctly (a service whose
  cost-per-user holds steady at growing volume passes the target;
  a service whose cost-per-user grows is signaling diseconomy)
- Provides a tool for product-side trade-offs (a new feature with
  significant cost-per-user impact is explicitly visible)
- Cross-references with the consumer's revenue-per-user model

**Cons:**
- Requires a reliable denominator (the consumer's "active user"
  definition must be auditable; multi-month definitions get
  complicated)
- Sensitive to denominator-definition changes: redefining "active
  user" produces apparent cost movement that does not reflect
  real change
- Does not capture absolute spend: a service with healthy
  cost-per-user can still exceed an annual absolute budget at
  high enough volume

#### Option A3: Cost per transaction or per business-meaningful operation

**Substrate preference:** Substrate-preferred for transactional
services and platform services that bill internal customers by
operation count.

**Applicable when:** The service has a discrete, business-meaningful
transaction type (a payment; an API call at a billable tier; a
rendered analytical query); the transaction count is computable
from instrumentation; the cost-per-transaction dimension is the
substrate-recognized signal the team optimizes for.

**Pros:**
- Captures the cost of the service's primary operation
- Pairs with pricing decisions (the consumer's transaction-priced
  product has visible margin)
- Provides a tool for transaction-level optimization (a code change
  that doubles transaction cost is visible in the SLI)
- Combines with A1 or A2 to capture multiple dimensions

**Cons:**
- Defines "transaction" requires care (some operations are
  meta-operations like health checks that should not count; some
  operations are billed-tier and should count differently from
  free-tier)
- Cost per transaction does not capture fixed-cost overhead (an
  idle service still incurs cost; per-transaction targets fail
  to constrain idle cost)
- Sensitive to transaction-definition changes the same way A2 is
  sensitive to user-definition changes

#### Option A4: Cost per tenant for multi-tenant services

**Substrate preference:** Substrate-preferred for multi-tenant
SaaS and platform services where per-tenant cost determines
pricing and contract structure.

**Applicable when:** The service is multi-tenant; per-tenant
attribution (cost-model-selection.cost-emission-pipeline sub-rule) is implemented; the consumer's
business model has per-tenant cost relevance (per-seat pricing;
tier-based pricing; capacity-based contracts).

**Pros:**
- Captures multi-tenant cost variance per tenant
- Pairs with the consumer's pricing model
- Detects a single tenant driving the service's spend out of band
- Tier-by-tier targets enable substrate-recommended differentiated
  cost discipline

**Cons:**
- Depends on per-tenant attribution discipline (cost-model-selection.cost-emission-pipeline) being
  in place
- Multi-tenant services with high shared-cost overhead have
  per-tenant attribution that is structurally noisy
- Tenant definitions may be unstable (a new sub-account model;
  consolidations and splits) and produce apparent cost movement
  that does not reflect real change

### Cost SLO target shape options

#### Option B1: Absolute monthly budget

**Substrate preference:** Substrate-preferred default for
steady-state services and for organizations whose budgeting
process is monthly absolute amounts.

**Applicable when:** The consumer's business is in steady-state;
the consumer's annual budget cycle commits absolute amounts; the
service's cost profile is stable enough that an absolute target
is meaningful.

**Pros:**
- Simple to communicate
- Aligns with most organizations' budgeting cadence
- Pairs cleanly with burn-rate alerting

**Cons:**
- Does not capture unit-economics variance
- Hard to apply to growth-phase services
- Can encourage seasonal over-provisioning to stay under target
  rather than right-sizing for variable load

#### Option B2: Unit-economics target

**Substrate preference:** Substrate-preferred for services where
the consumer's business is unit-economics driven.

**Applicable when:** The consumer's revenue model is per-user,
per-transaction, or per-tenant; the unit denominator is computable;
the consumer's product-margin analysis depends on the unit-economics
view.

**Pros:**
- Captures business sustainability beyond absolute amounts
- Aligns with product-margin analysis
- Captures growth-phase trajectory

**Cons:**
- Requires reliable denominator data
- Sensitive to denominator-definition changes
- Does not bound absolute spend

#### Option B3: Tiered by service criticality

**Substrate preference:** Substrate-recommended for consumer
organizations with explicit service criticality tiers in their
service catalog.

**Applicable when:** The consumer's service catalog assigns
criticality tiers; the cost targets reflect the tier (tier-0
services warrant tighter cost discipline because their reliability
investments cost more; tier-2 internal services warrant looser
cost discipline because their reliability investments are cheaper).

**Pros:**
- Reflects the consumer's existing service-tiering discipline
- Encourages substrate-recommended differentiated cost discipline
- Pairs with the observability.slo-policy SLO policy tiering

**Cons:**
- Requires the consumer's service catalog to have meaningful
  tiering
- Tier-by-tier targets can lead to fragmented cost reporting
  (the same cost rolls up differently by tier than by service)

### Budget computation method options

#### Option D1: Provider-billing-export-driven

**Substrate preference:** Substrate-preferred default for services
where the primary cloud provider is the dominant cost source.

**Applicable when:** The consumer's spend is primarily through one
or two cloud providers; the providers' billing exports (AWS CUR,
Azure Cost Management, GCP Billing export to BigQuery) cover the
substrate-recommended attribution granularity.

**Pros:**
- Authoritative against the provider invoice (reconciliation is
  cleanest)
- Daily cadence supports the substrate-recommended burn-rate
  alerting
- Pairs with provider-native anomaly detection (AWS Cost Anomaly
  Detection, Azure Cost Management anomaly detection, GCP Billing
  budgets and alerts)

**Cons:**
- Single-source: vendor invoices outside the cloud provider must
  be merged in separately
- Provider billing-export latency means the budget view is one
  day behind real time (acceptable for the substrate-recommended
  burn-rate cadence)
- Cost data schema can change at provider's discretion (the
  consumer's pipeline must absorb schema changes)

#### Option D2: Pipeline-derived with reseller adjustment

**Substrate preference:** Substrate-recommended for consumers in
reseller or partner relationships, multi-cloud arrangements, or
vendor-contracted spend that does not pass through cloud billing.

**Applicable when:** A significant fraction of the consumer's spend
arrives via reseller invoices, vendor contracts, or multi-cloud
aggregation; the consumer operates a centralized cost lake that
ingests multiple sources and applies a unified attribution.

**Pros:**
- Covers spend outside the cloud provider's billing system
- Single authoritative view for the consumer's organization
- Allows consumer-specific allocation rules (cross-business-unit
  splits; chargeback to internal teams)

**Cons:**
- Pipeline operates as the consumer's authoritative source rather
  than the provider invoice (reconciliation discipline is critical;
  pipeline failures produce silent gaps)
- More engineering investment than D1; requires substantive
  cost-model-selection.cost-emission-pipeline pipeline implementation
- The pipeline's allocation rules become a substrate-author
  reviewed artifact

### Over-budget response policy options

#### Option E1: Workload-level mitigation first

**Substrate preference:** Substrate-preferred default for over-
budget response. The first move is to constrain runaway workloads
before escalating.

**Applicable when:** The over-budget signal is workload-correlated
(the cost-model-selection.cost-anomaly-alerting alert identifies the workload or workloads
driving the variance); the team has authority to constrain the
workload (downscaling, rate limiting at the workload boundary,
emergency limit reduction).

**Pros:**
- Fastest response to the substrate-recognized common over-budget
  cause (runaway workload, misconfiguration)
- Limits the variance window before escalation
- Does not invoke product-side trade-offs unless workload-level
  response is insufficient

**Cons:**
- Workload-level mitigation can degrade user experience (the
  trade-off into reliability or feature performance must be
  documented)
- Requires the team to have authority to mitigate without
  product-owner sign-off (or the policy must document the fast-
  path approval mechanism)

#### Option E2: Service-level rate limiting

**Substrate preference:** Substrate-recommended addition to E1
where the workload-level mitigation is insufficient or the
service's traffic is the cost driver rather than a misconfiguration.

**Applicable when:** The service has rate-limiting infrastructure
(API gateway, request throttling, queue depth limits); rate
limiting is operationally meaningful (customer experience absorbs
the rate limit better than service degradation or revenue loss).

**Pros:**
- Bounds cost at the service traffic boundary
- Preserves quality of service for traffic within the rate limit
- Pairs with the consumer's rate-limiting infrastructure

**Cons:**
- Customer impact: rate-limited customers see throttled responses
- Requires substantive infrastructure investment if not already
  in place
- May breach customer SLAs depending on contract terms

#### Option E3: Escalation to product owner for trade-off renegotiation

**Substrate preference:** Substrate-recommended as the layered
response on top of E1 and E2 for services with engaged product
ownership.

**Applicable when:** The over-budget signal persists after E1 and
E2 responses, or the variance source is feature-driven rather
than incident-driven (a new feature is generating cost the budget
did not anticipate); the product owner is empowered to renegotiate
scope.

**Pros:**
- Brings the customer commitment owner into the cost conversation
- Lets product-side trade-offs (which features can be deferred to
  restore budget) be made explicitly rather than by engineering
  unilaterally
- Cross-references with the observability.slo-policy error-budget burndown
  response pattern

**Cons:**
- Requires product-owner alignment with the cost-model mechanism
- Uninformed product owners may invoke their authority to override
  the cost signal
- Slower than E1 and E2; not appropriate as the first response

#### Option E4: Accepted variance with documented rationale

**Substrate preference:** Substrate-recommended for one-time
documented variance events; substrate-recommended-against as a
recurring response.

**Applicable when:** The over-budget event has a documented
external cause (vendor price increase that exceeded forecast;
unexpected growth event for a growth-phase service); the consumer
has accepted the variance via the product-owner escalation; the
acceptance is documented in the ADR's review history.

**Pros:**
- Avoids forced action where the variance is reasoned-and-accepted
- Documents the consumer's position for future audit

**Cons:**
- Recurring acceptance erodes the cost-model mechanism
- The substrate-recommended pattern is to amend the budget rather
  than repeatedly accept variance against the prior budget

## Decision Outcome

The substrate-recommended position for a typical request-driven
service in a mature consumer organization:

- **Cost SLI:** Composite of absolute monthly cost (Option A1) and
  unit-economics target (Option A2 for SaaS providers; Option A3
  for transactional services; Option A4 for multi-tenant services).
  Both signals together capture business sustainability that either
  alone misses.
- **Cost SLO target shape:** Absolute monthly budget (Option B1)
  with unit-economics target (Option B2) as the substrate-
  recommended composite; tiered by service tier (Option B3) where
  the consumer has tiering.
- **Budget computation:** Provider-billing-export-driven (Option D1)
  for cloud-primary consumers; pipeline-derived with reseller
  adjustment (Option D2) for consumers with significant vendor-
  contracted spend.
- **Over-budget response:** Workload-level mitigation first
  (Option E1), service-level rate limiting (Option E2) as the
  second tier, product-owner escalation (Option E3) layered on
  top for persistent burn, accepted variance (Option E4) only for
  documented one-time external events.
- **Cost-vs-reliability trade-off rationale:** documented at the
  substrate-recognized boundaries (an additional 9 of availability
  rejected on cost grounds with the cost calculation explicit; a
  fault-injection program budgeted as a discrete line item; a
  multi-region active-active topology evaluated and accepted or
  rejected with the trade-off documented).

This is the substrate's default recommendation. Consumers should
treat it as a starting point and tailor based on the drivers above.

## Substrate Alignment

The decisions in this framework intersect every other cost-model-
selection rule:

- cost-model-selection.cost-attribution-tags (cost-attribution tags present) governs the
  attribution dimensions the budget computation references;
  tag-floor extension (consumer-specific tags) follows the cost
  SLI choice.
- cost-model-selection.workload-resource-limits (workload resource limits set) bounds the runtime
  cost per the SLO's per-workload allocation; right-sizing the
  limits (the cost-model-selection.cost-emission-pipeline review concern) follows the budget
  target.
- cost-model-selection.cost-emission-pipeline (cost-emission pipeline discipline) produces the
  budget computation; the window choice in this framework
  determines the pipeline's required output cadence.
- cost-model-selection.cost-anomaly-alerting (cost anomaly alerting configured) implements
  burn-rate alerting against the cost SLO; the over-budget
  response policy in this framework determines the alert's
  burndown response.

The cost-model ADR also cross-references the observability.slo-policy SLO policy
ADR at the cost-vs-reliability trade-off boundary. Where the
service has both kinds of budget (reliability error budget and
cost budget), the two ADRs together document the consumer's
position on trade-offs. The substrate's discipline is that both
ADRs exist for services that need both kinds of budget; the
substrate does not collapse them.

A consumer ADR satisfying cost-model-selection.cost-model-selection-policy references both this framework
and the consumer's specific positions on each section above.

## Consequences

The decisions made under this framework cascade as follows:

- **For attribution discipline:** the cost SLI choice determines
  which tag dimensions and which per-tenant labels the pipeline
  must support. Underestimating tag-discipline investment is a
  recurring failure mode; the substrate recommends treating tag
  governance as a first-class cost of the cost-model commitment.
- **For workload configuration:** the cost SLO target combined
  with workload resource limits (cost-model-selection.workload-resource-limits) determines the
  service's runtime cost ceiling. Underestimating limit-discipline
  investment produces workloads that drive cost above the SLO
  even when the IaC layer passes.
- **For team operations:** the over-budget response policy
  determines what happens to the team's work allocation when the
  budget is burned. The policy is binding on the engineering team
  and on the product organization; ADR authoring should involve
  both. The cross-reference to observability.slo-policy error budget policy is
  expected where both exist.
- **For executive reporting:** the cost SLO target and measurement
  window choice determines what the team reports outward. Aligning
  the ADR with the consumer's existing financial reporting cadence
  (monthly close; quarterly business review) reduces friction.
- **For pricing decisions (where the consumer prices a product):**
  the cost-per-unit SLI choice (A2, A3, or A4) feeds the consumer's
  pricing analysis. A cost target that exceeds the consumer's
  pricing margin signals either pricing renegotiation or cost
  reduction; the cost-model ADR is the substrate-recognized place
  to surface this.

## References

- FinOps Foundation Framework: Principles, Capabilities, and
  Personas (substrate-author references; not reproduced)
- AWS Well-Architected Framework Cost Optimization Pillar
- Azure Well-Architected Framework Cost Optimization Pillar
- Google Cloud Architecture Framework Cost Optimization Pillar
- OpenCost project documentation (CNCF Sandbox; substrate-recommended
  for Kubernetes per-workload and per-tenant cost attribution)
- Google SRE Workbook: Error Budget Policy chapter (the reliability-
  budget analog the cost-budget policy parallels; copyrighted;
  substrate references concept without reproducing text)
- MADR (Markdown Any Decision Records) format
- Related substrate framework: observability-slo-policy.madr.md
  (the SLO policy and error budget framework this cost-model
  framework parallels)

## Decision Review Schedule

The substrate-recommended cadence for reviewing the consumer's ADR
derived from this framework:

- **Annual:** full review of cost SLI choice, cost SLO target,
  budget computation method, over-budget response policy, and
  cost-vs-reliability trade-off rationale. The annual review
  reconfirms each choice against current drivers (the consumer's
  business model has not shifted; the unit economics still apply;
  the vendor contract structure is unchanged).
- **Triggered:** significant architecture change affecting cost
  characteristics; major business model shift affecting unit
  economics (price change, tenancy model change, vendor contract
  renegotiation); substantial budget-burndown event requiring
  policy invocation; substantial growth in volume that invalidates
  the prior cost forecast; substrate-recommended observability.slo-policy SLO
  review producing reliability commitments that change the cost-
  vs-reliability boundary.
- **Quarterly light-touch:** confirm the cost SLI computation is
  still producing meaningful data; confirm the alerting
  configuration still matches the budget computation; confirm the
  over-budget response policy is still authoritative (the team
  has invoked it, or has not had cause to invoke it, as
  appropriate).

This framework itself is reviewed by the substrate-author on the
substrate's MADR review cadence; framework version increments
propagate to consumer ADRs on the consumer's next annual review.
