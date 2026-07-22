<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-anomaly-alerting cost anomaly alerting (good patterns)

Substrate-original good-pattern example for cost-model-selection.cost-anomaly-alerting. This
illustrates substrate-recommended burn-rate alerting against
per-service cost budgets, routing to service-owning teams, and
exercised burndown response.

## Per-service alert configuration

```yaml
# alerting-rules.yaml (consumer-operated alerting configuration)
apiVersion: cost-alerting/v1
kind: AlertConfiguration
metadata:
  name: payments-api-cost-anomaly
  service: payments-api
  cost-model-adr: docs/decisions/ADR-014-payments-api-cost-model.md

spec:
  budget:
    monthly-amount-usd: 25000
    source: cost-model-adr
    derivation: >
      Per ADR-014, payments-api cost SLO is $25,000 monthly
      absolute target. Unit-economics target: cost per
      transaction under $0.0024 at expected volume.

  burn-rate-alerts:
    # 1-day window: catches short-burst anomalies
    - name: payments-api-cost-1d-burn-rate
      window: 1d
      threshold-multiplier: 3.0
      threshold-rationale: >
        At 3x baseline daily spend for 1 day, the service is on
        track to consume 3 days' budget in 1 day. The substrate-
        recommended multiplier mirrors observability.alerting-discipline burn-rate
        alerting for reliability SLOs.
      severity: high
      routing:
        primary: team-payments-oncall
        escalation:
          - after: 30m
            to: team-payments-manager
          - after: 2h
            to: finops-team

    # 7-day window: catches sustained burn
    - name: payments-api-cost-7d-burn-rate
      window: 7d
      threshold-multiplier: 1.5
      threshold-rationale: >
        At 1.5x baseline weekly spend for 7 days, the service is
        on track to exceed its monthly budget by 50 percent.
        Substrate-recommended sustained-burn multiplier.
      severity: medium
      routing:
        primary: team-payments-oncall
        escalation:
          - after: 4h
            to: team-payments-manager
          - after: 1d
            to: finops-team

  per-tenant-alerts:
    # Per-tenant variant for multi-tenant workloads
    - name: payments-api-tenant-cost-1d-burn-rate
      window: 1d
      threshold-multiplier: 5.0
      threshold-rationale: >
        At 5x baseline tenant spend, the tenant is consuming
        disproportionately. Substrate-recommended for catching
        a single noisy tenant.
      severity: medium
      routing:
        primary: customer-success-payments
        escalation:
          - after: 1h
            to: team-payments-oncall
        rationale: >
          Per-tenant variances are tenant-facing in the first
          instance; escalate to the workload team if the
          tenant-management function cannot resolve.

  pipeline-source:
    name: cost-lake
    view: per-service-attributed-spend
    rationale: >
      Alerting subscribes to the same pipeline output that
      drives chargeback and the cost-model ADR's budget
      computation. Single source of truth.
```

Why this is good: every element of the substrate-recommended
pattern is present: per-service budgets tied to the ADR, multi-
window burn-rate thresholds (1-day and 7-day), explicit
rationale for each threshold, routing to the service-owning
team with escalation, per-tenant alerting for multi-tenant
services, single pipeline source.

## Alert payload (sample firing)

```
Alert fired: payments-api-cost-1d-burn-rate
Time: 2026-05-21 14:32 UTC
Window: 1d
Threshold: 3.0x baseline ($833/day; threshold $2,500/day)
Actual: $3,200/day for last 1d window (3.84x baseline)
Severity: high
Routing: team-payments-oncall (Mike B., on-call)

Cost trajectory:
  Baseline daily (90-day average): $833
  Last 1d:                         $3,200
  Last 7d total:                   $8,940 (1.5x baseline weekly)
  MTD:                             $22,400
  Monthly budget:                  $25,000
  Projected month-end at 1d rate:  $99,200 (3.97x budget)

Top contributors (last 1d):
  payments-processor Lambda:  +$1,800 (vs baseline +$200)
  payments-database RDS:      +$1,200 (vs baseline +$580)
  payments-events Kinesis:      +$200 (vs baseline +$53)

ADR reference: docs/decisions/ADR-014-payments-api-cost-model.md
Runbook: runbooks/payments-api/cost-burndown-response.md
```

Why this is good: the alert payload is actionable. The on-call
engineer sees the trajectory, the top contributors, and a
direct link to the burndown response runbook. The payload
identifies the workload (payments-processor Lambda) most likely
to be the variance source.

## Burndown response runbook (sample)

```markdown
# Runbook: payments-api cost burndown response

When fired: cost-model-selection.cost-anomaly-alerting burn-rate alert on payments-api

## Threshold-based response (per ADR-014 over-budget policy)

### At 50 percent budget remaining (projected; first alert)

1. **Investigate the top contributor.** From the alert payload,
   identify the workload driving the variance.
2. **Apply workload-level mitigation if applicable** (E1 in
   ADR-014). Examples:
   - Lambda misconfiguration: revert the deploy that introduced
     the variance
   - Database query pattern change: identify the slow query and
     either roll back or tune
   - Event volume spike: confirm upstream traffic is legitimate;
     if not, throttle upstream
3. **Acknowledge the alert** and link to the investigation
   ticket.

### At 25 percent budget remaining (projected; second alert)

4. **Apply service-level rate limiting if applicable** (E2 in
   ADR-014). The payments-api API gateway has a rate limiter
   configured per tenant tier; engage the substrate-recommended
   tier-1 rate limit.

### At 10 percent budget remaining (projected; third alert)

5. **Escalate to product owner for trade-off renegotiation** (E3
   in ADR-014). The product owner has authority to:
   - Pause non-essential feature work that drives cost
   - Negotiate scope with the customer commitments owner
   - Accept the variance with documented rationale (E4 in
     ADR-014) and amend the budget

### At budget exceeded

6. **Run the burndown after-action review.** Update ADR-014 if
   the burndown reveals a structural mismatch between the
   budget and the workload's actual cost shape.
```

Why this is good: the response is concrete and tied to the
ADR's documented thresholds. Each step is operationally
meaningful. Escalation chain is clear.

## Drill log (sample)

```
Quarterly drill: 2026-04-15
Drill type: synthetic routing exercise
Drill steward: @myoung

Steps executed:
1. Trigger synthetic 1d-burn-rate alert via test mode
2. Verify alert arrives at team-payments-oncall (Slack page)
3. On-call Mike B. acknowledges the alert
4. Verify acknowledgment recorded in alerting platform
5. Do not acknowledge a second synthetic alert; verify
   escalation to team-payments-manager after 30 minutes
6. Manager Sarah acknowledges; verify escalation chain stops

Results:
- All routing worked end-to-end
- Acknowledgment recording: works
- Escalation timing: 30 minutes within +/- 2 minutes (within
  substrate-recommended tolerance)
- Slack channel for alert receipt: correctly configured
- Post-drill cleanup: synthetic alerts cleared

Findings:
- None. Alerting works as documented.

Next drill: 2026-07-15 (quarterly)
```

Why this is good: routing is exercised quarterly with a
documented drill. The drill produces evidence the substrate's
L2 review can verify. The next drill is scheduled.

## What the L2 review confirms

Reviewers checking this consumer's alerting against the COST-
L2-002 review checklist confirm:

- Per-service budgets documented and tied to ADR-014: yes
- Burn-rate pattern (multi-window): yes (1-day and 7-day)
- Alerts route to service-owning team: yes (team-payments-
  oncall with documented escalation)
- Burndown response policy documented and operationally
  meaningful: yes (the runbook implements ADR-014's documented
  thresholds with concrete actions)
- Threshold values produce signal, not noise: yes (the
  thresholds reflect a 3x daily / 1.5x weekly multiplier with
  documented rationale)
- Alert has fired and been actioned in the past quarter: yes
  (synthetic drill 2026-04-15; real fire 2026-03-22 around
  a Lambda misconfiguration; both have action records)
- Per-tenant alerts for multi-tenant services: yes (per-tenant
  variant configured with routing to customer-success)

The substrate's review passes. The alerting produces forward-
looking cost control.
