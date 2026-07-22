<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-emission-pipeline cost emission pipeline discipline (anti-patterns)

Substrate-original anti-pattern examples for cost-model-selection.cost-emission-pipeline. Each
shows a common way the pipeline rule is violated and explains
why the violation matters.

## Anti-pattern 1: Cost viewed only in provider consoles

```
Operator workflow:
- "What did payments-api cost last month?"
- Operator opens the AWS Cost Explorer console
- Filters by tag: service = payments-api
- Reads the displayed number
- No pipeline; no reconciliation; no allocation rules; no shared-
  cost split; no per-tenant view
```

Why this fails: the consumer has no pipeline. Every cost question
requires a manual console session; results are not stored; the
view is not reconciled against the invoice; multi-tenant
attribution does not exist. The cost-model-selection.cost-anomaly-alerting anomaly alerting
configured against the same console-only view is account-wide
rather than per-service because per-service granularity is not
materialized into an alertable data store.

This is the substrate-recommended-against baseline that COST-
L2-001 specifically addresses. The remediation is to operate a
cost lake: ingest the provider billing exports, apply allocation
rules, produce attributed views.

## Anti-pattern 2: Pipeline exists but does not reconcile

```
Pipeline output: 2026-04 per-service totals
  payments-api:    $24,118.55
  orders-api:      $18,724.91
  catalog-api:     $12,580.00
  shared-platform: $32,118.55
  -------------------------
  Sum:             $87,542.01

AWS invoice: 2026-04 total
  $124,532.18

Variance: $36,990.17 unaccounted (29.7 percent)

Operator response: "The pipeline view is approximate; the
invoice is the authoritative number."
```

Why this fails: the pipeline exists but is not authoritative.
The operator's response abdicates the pipeline's purpose. The
29.7 percent unattributed spend cannot be chargebacked, cannot
be alerted on per-service, cannot be reasoned about by the
cost-model ADR. The pipeline's existence is overhead with no
operational return.

The substrate's discipline is that the pipeline IS authoritative,
within a substrate-recommended variance threshold. Where variance
exceeds the threshold, the cause is investigated and remediated
(tag coverage, allocation rules, shared-cost rules, reseller
invoice timing). The pipeline either reconciles or it is
remediated; "the invoice is authoritative" is not an acceptable
disposition.

## Anti-pattern 3: Multi-tenant workload spend rolled to shared bucket

```yaml
# allocation-rules.yaml (consumer's broken policy)
allocation-rules:
  - id: rule-payments-multitenant
    match:
      service: payments-platform
    attribute-to:
      primary: cost-center:CC-PLATFORM-SHARED
    rationale: >
      payments-platform is multi-tenant. We don't track per-
      tenant cost, so this attributes the whole thing to the
      shared platform cost center.
```

Why this fails: the consumer operates a multi-tenant service
but cannot attribute cost per tenant. The cost-model-selection.cost-model-selection-policy ADR (if
present) cannot reason about per-tenant unit economics. The
cost-model-selection.cost-anomaly-alerting anomaly alerting cannot detect a single tenant
driving the service into burndown. Tier-based pricing decisions
operate from estimate rather than data.

Where the consumer's business model has multi-tenant cost
relevance (SaaS providers; platform-as-service providers;
internal platform teams chargebacking to tenant teams), per-
tenant attribution is operational discipline. The substrate's
L2 review surfaces the absence as a blocking finding.

## Anti-pattern 4: Allocation rules never updated as IaC grows

```yaml
# allocation-rules.yaml (last modified 18 months ago)
version: 1.0
last-modified: 2024-11-21

allocation-rules:
  - id: rule-old-service-attribution
    match:
      tags-present:
        - cost-center
        - environment
        # missing: the team added "service" and "owner" tags
        # 12 months ago, but the allocation rule never updated
    attribute-to:
      primary: tag:cost-center
```

Why this fails: the consumer added new tags to the cost-model-selection.cost-attribution-tags
floor (service, owner) but never updated the allocation rules
to consume them. The pipeline collects the new tags but does
nothing with them; the operational value of the L1 work is not
realized at the L2 layer.

Reviewers verify the allocation rules consume every L1-required
tag. The substrate's L2 review surfaces this as a finding when
discovered.

## Anti-pattern 5: Shared-cost allocation undocumented

```
Operator question: "Why is account-a's chargeback this month
larger than its provisioned resources should justify?"
Pipeline operator: "Some of the shared services get split across
the accounts. I think the formula uses traffic but I'd have to
check the pipeline code."
Account-a operator: "Can I see the formula?"
Pipeline operator: "It's in a Python script. I'll send you the
file."
```

Why this fails: the shared-cost allocation is encoded in
pipeline code rather than in a versioned, reviewed policy
document. The receiving accounts cannot audit the formula; the
substrate-recommended annual review cadence cannot apply
because there is no document to review.

The substrate-recommended pattern is a versioned, declarative
allocation-rules document (the good-pattern example shows the
shape). Code-encoded allocation rules without document
authority are a substrate finding.

## Anti-pattern 6: Pipeline operates on monthly batches only

```
Ingestion cadence: monthly, on the 5th of the following month
(after the provider invoice finalizes)

Operator observation: "We notice cost variances in the monthly
review meeting on the 15th."
```

Why this fails: cost variances are noticed 45 days after their
onset. By the time the team responds, the variance has compounded
across a full month. The cost-model-selection.cost-anomaly-alerting anomaly alerting cannot
fire on intra-month variance because the pipeline does not have
the data.

The substrate's recommended ingestion cadence is daily for the
primary cloud provider; on-publication for vendor invoices. The
substrate's L2 review surfaces monthly-only ingestion as a
finding (the pipeline functions for retrospective reporting but
not for forward-looking control).

## Anti-pattern 7: Variance investigation never produces root cause

```
April 2026 reconciliation:
  Variance: $4,200 unattributed (4.2 percent; over threshold)
  Disposition: "Investigated; could not identify source. Carry
    forward to next month."

May 2026 reconciliation:
  Variance: $5,100 unattributed (5.1 percent; over threshold)
  Disposition: "Same source as April. Carry forward."

June 2026 reconciliation:
  Variance: $7,800 unattributed (7.8 percent; over threshold)
  Disposition: "Same source. Investigating."
```

Why this fails: variance investigation never produces root
cause. The unattributed spend grows month-over-month because
the underlying issue (a tag coverage gap; an allocation rule
gap; a new shared service not yet in the rules) is not
remediated.

The substrate's discipline is that variance investigation
produces either a root cause and a remediation PR or a
documented acceptance (the substrate-recommended path for
irreducible variance). Persistent "carry forward" disposition
is a finding.

## Anti-pattern 8: Multiple cost views without designated authority

```
Operator question: "What's our cost for payments-api?"

Source 1 (chargeback ledger): $24,118.55
Source 2 (alerting platform):  $26,000.00 (based on different
                               cost estimate path)
Source 3 (cost-model ADR):     $22,500    (target from prior
                               year; not actual)
Source 4 (finance team):       $24,532    (their own
                               reconciliation)

Operator: "Which one's right?"
```

Why this fails: the consumer has multiple cost views with no
designated authority. The substrate's discipline is a single
pipeline that feeds every cost-consuming process; divergence
between views is a finding.

The substrate's L2 review confirms the same pipeline feeds
cost-model-selection.cost-anomaly-alerting alerting and cost-model-selection.cost-model-selection-policy budget computation. Where
divergent views exist, the substrate's recommended remediation
is to merge them into a single source of truth (the pipeline)
with documented rationale for any deliberately differentiated
view (e.g., a finance-team cash-basis view that legitimately
differs from the accrual-basis chargeback view).

## What the consequences look like in operation

A consumer with these anti-patterns sees the consequences
across the cost program:

- The chargeback ledger has low operator trust because the
  numbers do not match the invoice
- The cost-anomaly alerts (cost-model-selection.cost-anomaly-alerting) fire account-wide and
  produce alert fatigue
- The cost-model ADR (cost-model-selection.cost-model-selection-policy) targets are not measurable
  against the pipeline
- New service launches inherit no cost discipline because the
  pipeline does not provide service-level views
- Multi-tenant pricing decisions are made from estimate rather
  than data

The substrate's discipline is to enforce L2 review at substrate-
recommended cadence so these anti-patterns are caught before
they compound.
