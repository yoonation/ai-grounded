<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-anomaly-alerting cost anomaly alerting (anti-patterns)

Substrate-original anti-pattern examples for cost-model-selection.cost-anomaly-alerting. Each
shows a common way alerting falls short of substrate discipline
and explains why the violation matters.

## Anti-pattern 1: Account-wide alerts only

```yaml
# alerting-rules.yaml
apiVersion: cost-alerting/v1
kind: AlertConfiguration
metadata:
  name: account-budget-alert

spec:
  budget:
    monthly-amount-usd: 250000
    source: account-total

  threshold-alerts:
    - name: account-budget-80-percent
      trigger: actual-spend >= 80 percent of monthly-amount-usd
      severity: medium
      routing: finance-team-inbox

    - name: account-budget-100-percent
      trigger: actual-spend >= monthly-amount-usd
      severity: high
      routing: finance-team-inbox
```

Why this fails: account-wide alerts route to a team that does not
own any individual service. Triage requires identifying which
service drove the variance (work the alert should have done) and
routing the actual response to the service-owning team. By the
time triage completes, the variance has compounded.

The substrate-recommended pattern is per-service alerting with
account-wide as a safety net. Per-service alerts route to the
team that can act; account-wide alerts catch the residual where
per-service alerting does not exist.

## Anti-pattern 2: Single-threshold not burn-rate

```yaml
spec:
  budget:
    monthly-amount-usd: 25000

  threshold-alerts:
    - name: monthly-budget-alert
      trigger: mtd-spend >= monthly-amount-usd
      severity: high
      routing: team-payments-oncall
```

Why this fails: the alert fires only when MTD spend reaches the
monthly budget. By that point the budget is consumed; response
is too late to bound the variance.

The substrate-recommended pattern is multi-window burn-rate
alerting (1-day and 7-day windows) that fires on trajectory, not
on absolute consumption. The trajectory-based alert fires hours
or days into a variance event, while single-threshold alerts
fire at month-end.

## Anti-pattern 3: Threshold set so high it does not fire

```yaml
spec:
  budget:
    monthly-amount-usd: 25000

  threshold-alerts:
    - name: catastrophic-spend-alert
      trigger: mtd-spend >= 5 * monthly-amount-usd
      severity: critical
      routing: team-payments-oncall
```

Why this fails: the threshold is set so high that only a 5x
budget overrun fires. Routine 1.5x or 2x variances (which are
substantial cost problems) never produce signal. The alert
exists in the configuration but does not exercise.

The substrate-recommended pattern matches threshold sensitivity
to the consumer's spend distribution: a 1.5x weekly multiplier
or a 3x daily multiplier produces signal on real variance, not
only catastrophe.

## Anti-pattern 4: Alert routes to a generic inbox

```yaml
spec:
  threshold-alerts:
    - name: payments-cost-alert
      threshold-multiplier: 3.0
      severity: high
      routing: cost-alerts@example.com
```

Why this fails: cost-alerts@example.com is an email list with no
on-call accountability. Alerts in the list are read when someone
happens to check; no acknowledgment is required; no escalation
fires. The alert is decoration rather than control.

The substrate-recommended pattern is routing through the
consumer's on-call system (PagerDuty, Opsgenie, equivalent) so
cost alerts inherit the same paging, acknowledgment, and
escalation discipline as operational alerts.

## Anti-pattern 5: Burndown response is aspirational

```markdown
# Runbook: cost burndown response

When fired: any cost alert

## Response

If a cost alert fires, the team will assess the situation and
take appropriate action.
```

Why this fails: "assess the situation" and "take appropriate
action" are not actions. The runbook does not specify what to
do at any threshold; the on-call engineer has no operational
guidance.

The substrate-recommended pattern is threshold-keyed response
with concrete actions (workload-level mitigation at threshold A;
service-level rate limiting at threshold B; product-owner
escalation at threshold C). The good-pattern example shows the
shape.

## Anti-pattern 6: Alert has never fired or been drilled

```
Alert configuration: 14 months old
Last fired:           never
Last drilled:         never

Operator: "We have alerts set up but they've never gone off, so
they must be working."
```

Why this fails: an alert that has never fired could be working
correctly (the cost has never crossed the threshold) or broken
(the threshold is unreachable, the routing is misconfigured,
the underlying pipeline does not feed the alert). Without
exercising the alert, the operator cannot distinguish.

The substrate-recommended pattern is quarterly synthetic drill
of routing (the good-pattern example shows the drill log shape)
plus an annual real-fire test where possible (a workload is
intentionally over-driven against a sandboxed budget). At least
one of these exercises must occur in the past quarter for the
substrate's L2 review to pass.

## Anti-pattern 7: Multi-tenant service without per-tenant alerts

```yaml
# Service is multi-tenant; per-tenant attribution exists in the
# pipeline (cost-model-selection.cost-emission-pipeline passes); but the alerting is per-service
# only.

spec:
  service: payments-platform
  budget:
    monthly-amount-usd: 50000
  burn-rate-alerts:
    - name: payments-platform-cost-1d-burn-rate
      threshold-multiplier: 3.0
      # no per-tenant variant
```

Why this fails: a single noisy tenant can drive the service into
budget burndown without crossing the per-service threshold
(because the service total is averaged across many tenants).
The cost-model-selection.cost-emission-pipeline per-tenant attribution is implemented but the
alerting does not consume it.

The substrate-recommended pattern is per-tenant alerts where
per-tenant attribution exists. The good-pattern example shows
the variant.

## Anti-pattern 8: Alerts fire constantly and are filtered out

```
Alert history (last 90 days):
- payments-api-cost-1d-burn-rate: 47 firings
- payments-api-cost-7d-burn-rate: 28 firings

Operator behavior: "We have a Slack filter that mutes those.
They fire all the time."
```

Why this fails: the thresholds produce noise. The team filters
the noise rather than tuning the thresholds. When a real
variance fires, it is filtered with the noise.

The substrate-recommended pattern is to tune thresholds against
the consumer's spend distribution so signal exceeds noise. The
review checklist asks reviewers to compute the signal-to-noise
ratio against historical data; persistent high-firing alerts
are a finding.

The remediation is either to raise the threshold multiplier (if
the consumer's normal variance is wider than the substrate-
recommended default) or to address the underlying cause (if
the workload is intrinsically noisy). The substrate does not
prescribe a specific signal-to-noise ratio; the review
compares against the consumer's prior-year ratio to confirm
thresholds have not drifted into noise.

## Anti-pattern 9: Alerting feeds a different data path than the pipeline

```
Cost-model ADR target:   $25,000 monthly (computed from cost-
                         lake pipeline output)
Chargeback ledger:       Uses cost-lake pipeline
cost-model-selection.cost-anomaly-alerting alerting:    Uses AWS Cost Anomaly Detection
                         direct on CUR; does not consume the
                         cost-lake pipeline

Pipeline says service spent $24,500 this month.
AWS Cost Anomaly Detection says service spent $27,200 this
month.

Difference: $2,700 (rounding, reseller invoices the cost-lake
includes but AWS does not, allocation rules apportioning
cross-account services).

Operator: "The alert fires from AWS; the ADR target compares to
the pipeline. They diverge by a few percent each month."
```

Why this fails: alerting and ADR target operate on different
data paths. Where the two diverge, the team cannot reason about
which is correct. The substrate-recommended pattern is single
pipeline as source of truth (cost-model-selection.cost-emission-pipeline review confirms this)
with alerts subscribing to the same output.

## What the consequences look like in operation

A team with these anti-patterns sees the consequences when
something goes wrong:

- A misconfigured Lambda runs at 10x baseline for two weeks
  before anyone notices (no per-service burn-rate alert)
- A new multi-tenant customer's heavy usage drives the service
  into budget burndown for the entire account (no per-tenant
  alert)
- The team filters cost alerts to clear the noise, missing a
  real variance event (thresholds untuned)
- The post-incident review finds the alert fired but no one
  knew what to do (aspirational runbook)
- The team adds yet another alert that they will also filter
  (the failure mode compounds)

The substrate's discipline is to design alerting so signal
exceeds noise, routing produces action, response is documented
in advance, and the data path is the same as the pipeline that
feeds the cost-model ADR.
