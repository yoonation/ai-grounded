<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-emission-pipeline cost emission pipeline discipline (good patterns)

Substrate-original good-pattern example for cost-model-selection.cost-emission-pipeline. This
illustrates the substrate-recommended cost emission pipeline shape
and the reconciliation discipline that gives the pipeline
operational authority.

## Pipeline architecture overview

```
Provider billing exports          Vendor invoices (outside cloud)
       |                                |
       v                                v
+----------------------+        +-----------------------+
| AWS CUR daily export | <----+ | Reseller monthly      |
| Azure Cost Mgmt      |        | invoices (DataDog,    |
| GCP Billing -> BQ    |        | Snowflake, etc.)      |
+----------------------+        +-----------------------+
       |                                |
       v                                v
+-----------------------------------------------+
| Centralized cost lake (consumer-operated)     |
| - Daily ingestion of provider exports         |
| - Monthly ingestion of vendor invoices        |
| - Allocation rules apply cost-model-selection.cost-attribution-tags tags     |
| - Shared-cost split rules                     |
| - Per-tenant attribution via OpenCost or      |
|   labeled metrics for multi-tenant workloads  |
+-----------------------------------------------+
       |
       v
+----------------------------------+
| Pipeline output views:           |
| - Chargeback ledger              |
| - Per-service cost dashboard     |
| - cost-model-selection.cost-anomaly-alerting alerting feed      |
| - cost-model-selection.cost-model-selection-policy budget computation |
+----------------------------------+
       |
       v
Reconciliation: pipeline total vs provider invoice
         Within 2 percent variance threshold
```

Why this is good: a single authoritative pipeline ingests all
cost data, applies attribution, and feeds every downstream
consumer of cost information. Reconciliation is built in.

## Allocation rule example (substrate-recommended pattern)

```yaml
# allocation-rules.yaml (consumer-operated cost-lake configuration)
version: 1.0
last-modified: 2026-05-21
last-reviewed: 2026-05-21

allocation-rules:
  # Rule 1: services attribute via the substrate-required tag floor
  - id: rule-service-attribution
    description: >
      Spend on resources carrying the substrate-required tags
      attributes to the service named in the service tag, with
      secondary attribution to cost-center and owner.
    match:
      tags-present:
        - cost-center
        - environment
        - service
        - owner
    attribute-to:
      primary: tag:service
      secondary: tag:cost-center
      owner: tag:owner

  # Rule 2: multi-tenant workloads attribute per-tenant via OpenCost
  - id: rule-multitenant-attribution
    description: >
      Kubernetes workloads with a tenant label attribute their
      spend per-tenant via OpenCost-derived per-tenant cost.
    match:
      provider: kubernetes
      labels-present:
        - tenant
    attribute-to:
      primary: opencost.tenant-spend
      secondary: tag:service

  # Rule 3: shared cross-account services split by usage
  - id: rule-cross-account-vpc-endpoints
    description: >
      VPC endpoint fees in the shared-services account split
      across consuming accounts by traffic volume.
    match:
      resource-type: aws_vpc_endpoint
      account: shared-services-account
    attribute-to:
      formula: split-by-traffic-volume
      across: [account-a, account-b, account-c]
    rationale: >
      VPC endpoints are provisioned in a shared account but
      consumed by multiple business-unit accounts; the consumer's
      finance policy splits by measured traffic.

  # Rule 4: untaggable resources allocate to a designated bucket
  - id: rule-untaggable-resources
    description: >
      Resources whose provider does not support tags allocate to
      the platform-engineering cost center.
    match:
      tags-present: []
      resource-types-in-substrate-untaggable-list: true
    attribute-to:
      primary: cost-center:CC-PLATFORM-001
      secondary: service:shared-platform
    rationale: >
      Per the cost-model-selection.cost-attribution-tags layer-boundary-disclosure, a small set
      of provider resource types remain untaggable. The
      consumer's policy attributes these to platform engineering.

  # Rule 5: unmatched spend surfaces as a finding
  - id: rule-unmatched-default
    description: >
      Spend that does not match any prior rule surfaces as
      unattributed; the pipeline raises a finding for
      investigation.
    match: '*'
    attribute-to:
      primary: cost-center:UNATTRIBUTED
    raise-finding: true
    rationale: >
      Unattributed spend is investigable. Each finding produces a
      tag-coverage gap (remediated in IaC) or an allocation-rule
      gap (remediated in this policy).
```

Why this is good: every allocation rule is documented with a
rationale; unmatched spend surfaces as a finding rather than
silently rolling into a generic bucket. The substrate's L2
review can verify the rules against the consumer's tag coverage
and against the provider invoice.

## Multi-tenant attribution example

```yaml
# OpenCost configuration for per-tenant attribution
apiVersion: opencost.io/v1
kind: OpenCostConfig
metadata:
  name: tenant-attribution
spec:
  costAllocation:
    # Pod-level cost split across tenants based on a labeled metric
    customAllocation:
      - name: tenant-attribution
        labels:
          - tenant
        method: weighted-by-metric
        metric: tenant_workload_seconds
        rationale: >
          Each pod logs tenant_workload_seconds via the
          application's instrumented metrics. OpenCost
          attributes the pod's underlying spend across tenants
          by the metric's distribution within the pod's lifetime.
```

Why this is good: the per-tenant attribution method is explicit
and consumes a labeled metric the workload emits. Reviewers can
verify the metric exists, the values are reasonable, and the sum
of per-tenant attribution reconciles to the workload total.

## Reconciliation report (sample)

```
Reconciliation report: 2026-04 (month finalized 2026-05-05)
Reviewer: @myoung
Reviewed: 2026-05-15

Provider invoices:
  AWS:           $124,532.18 (CUR final)
  GCP:             $8,724.91 (BigQuery export final)
  Datadog:        $14,580.00 (monthly invoice received 2026-05-03)
  Snowflake:      $32,118.55 (monthly invoice received 2026-05-04)
  -------------------------------------------------
  Total invoiced: $179,955.64

Pipeline attributed:
  Services (sum of per-service attribution):  $172,408.91
  Shared services:                              $4,891.22
  Untaggable defaults:                          $2,108.45
  Unattributed (raised as findings):              $551.06
  -------------------------------------------------
  Total attributed:                           $179,959.64

Variance:                              +$4.00 (0.002 percent)
Substrate-recommended threshold:        2 percent
Status:                                PASS

Findings:
  - Unattributed $551.06 traces to new aws_glue_job resources
    in account-b that lack the substrate-required tags. PR #4521
    opened to add tags via the dev team's IaC.
  - The cost-lake's ingestion of Datadog invoice arrived on
    2026-05-04 (one day after invoice date); within the
    substrate-recommended on-publication cadence.

Drill-down spot-checks:
  - payments-api service attributed $24,118.55. Drilled down to
    18 underlying resources (3 EKS clusters, 4 RDS instances,
    11 S3 buckets). All reconcile to provider line items.
  - tenant-A on shared-platform-service attributed $1,840.21.
    Drilled down to the OpenCost output and confirmed the
    metric-weighted attribution matches the tenant's measured
    workload-seconds.
```

Why this is good: the reconciliation is documented, the variance
is within threshold, the unattributed finding has an
investigation outcome, and drill-down spot-checks confirm
attribution chain end-to-end. The substrate's L2 review consumes
this report directly.

## What the L2 review confirms

Reviewers checking this consumer's pipeline against the
cost-model-selection.cost-emission-pipeline review checklist confirm:

- Daily ingestion cadence: yes (CUR ingested daily; vendor
  invoices ingested on publication)
- Allocation rules consume cost-model-selection.cost-attribution-tags tags: yes (rule-service-
  attribution and rule-multitenant-attribution exercise the
  full tag floor)
- Per-tenant attribution: yes (OpenCost configured; sum
  reconciles to workload total within threshold)
- Reconciliation: yes (April 2026 reconciled at 0.002 percent
  variance against the threshold)
- Shared-cost rules documented and reviewed: yes (last reviewed
  2026-05-21; rule-cross-account-vpc-endpoints and rule-
  untaggable-resources both documented with rationale)
- Recent variance exercised: yes (April finding investigated;
  PR #4521 opened)
- Feeds anomaly alerting and budget computation: yes (the COST-
  L2-002 alerting subscribes to the same per-service view; the
  cost-model-selection.cost-model-selection-policy ADR's budget computation references the same
  attribution method)

The substrate's review passes. The pipeline is operationally
authoritative.
