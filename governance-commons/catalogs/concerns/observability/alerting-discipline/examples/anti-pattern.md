<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.alerting-discipline alerting discipline (anti-patterns)

Substrate-original anti-pattern examples for observability.alerting-discipline.

## Anti-pattern A: Alert with no severity, no runbook, no summary (Prometheus)

```yaml
- alert: HighErrorRate
  expr: rate(errors[5m]) > 10
  for: 5m
```

Why this violates observability.alerting-discipline: severity label missing
(responder cannot triage urgency); runbook_url annotation
missing (responder has no documented remediation steps);
summary annotation missing (notification body will be the
alertname alone, indistinguishable from any other
HighErrorRate alert in the consumer's environment); the
expression depends on an undefined metric name "errors".

Remediation: see the good-pattern PaymentsApiHighErrorRate
rule for the complete structural form.

## Anti-pattern B: Severity inflation (everything paged as critical)

```yaml
- alert: DiskUsageHigh
  expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.20
  labels:
    severity: critical

- alert: CertificateExpiringIn30Days
  expr: cert_expiry_seconds < 86400 * 30
  labels:
    severity: critical

- alert: PaymentsApiDown
  expr: up{service="payments-api"} == 0
  labels:
    severity: critical
```

Why this violates observability.alerting-discipline: disk usage at 80 percent and a
certificate expiring in 30 days are not equivalent to a
service being down. Labeling all three as critical paginates
indiscriminately; on-call responders develop alert fatigue
and start ignoring critical-tagged alerts. The vocabulary
collapses to a single tier.

Remediation: tier severity by paging urgency. Disk usage at
80 percent becomes a ticket-tier alert (warning) with a 7-
day investigation window; certificate expiring in 30 days
becomes a ticket-tier alert with an automated renewal ticket;
service-down stays critical with immediate paging.

## Anti-pattern C: Runbook URL points to a 404

```yaml
- alert: PaymentsApiHighErrorRate
  expr: ...
  annotations:
    runbook_url: "https://wiki.internal.example/runbooks/payments-api-error-rate"
```

The URL was authored a year ago; the wiki page was migrated
to a new platform and the redirect was not maintained.

Why this violates observability.alerting-discipline: the runbook annotation exists
but is operationally useless. The responder following the
URL during an incident wastes time finding the new location.
Worse, the existence of the annotation creates a false
sense that the alert is operationally documented.

Remediation: the substrate-recommended Scenario 2 test in
the observability.alerting-discipline test template (runbook URLs resolve to live
documents) catches this in CI. The quarterly sweep is the
backstop.

## Anti-pattern D: Cause-based alerting that misses composition failures

```yaml
- alert: PaymentsApiDatabaseConnectionPoolHigh
  expr: db_connection_pool_used / db_connection_pool_max > 0.80
  labels:
    severity: warning
```

Why this violates observability.alerting-discipline: the alert fires on the database
connection pool, which is a single cause. The service has
many other failure modes (downstream API slow, internal queue
saturated, GC pressure) that produce the same customer-felt
outcome (slow or failed payments) without firing this alert.
Operators rely on the alert as a proxy for service health
and miss incidents that bypass the connection pool.

Remediation: alert on the customer-felt symptom (latency
above threshold, error rate above threshold) which fires
regardless of root cause. The cause-based metric (connection
pool usage) remains on the dashboard for diagnosis but does
not page.

## Anti-pattern E: Cascade firing without inhibition

A single database outage triggers ten alerts at once
(database-down, payments-api-errors, orders-api-errors,
fulfillment-api-errors, notification-api-errors, plus the
five derived burn-rate alerts on each service). All ten
page; the responder receives ten notifications, switches
context across ten dashboards, and takes longer to identify
the root cause than if they had received one notification.

Why this violates observability.alerting-discipline: the alerting system surfaces
symptoms without dedup. The cascade exists because no
inhibition rules suppress dependent alerts when the upstream
root-cause alert fires.

Remediation: configure Alertmanager inhibition rules (or
vendor equivalent) so the root-cause alert suppresses the
dependent symptom alerts. The good-pattern Pattern C
example shows the substrate-recommended configuration.

## Anti-pattern F: Threshold alerting on raw error rate when SLO exists

```yaml
- alert: PaymentsApiErrorRateAbove1Percent
  expr: |
    rate(api_requests_total{status=~"5.."}[5m])
    /
    rate(api_requests_total[5m]) > 0.01
  for: 5m
```

Why this violates observability.alerting-discipline: the alert fires whenever the
5-minute error rate exceeds 1 percent. At low traffic
(overnight, weekend), a small number of errors produce a
high rate without representing a sustained problem. At high
traffic, the same rate represents a significantly larger
customer impact. The alert tunes for one traffic regime and
misbehaves in others.

Remediation: use burn-rate alerting against a documented
SLO (good-pattern Pattern B). The burn-rate normalizes by
traffic volume, providing consistent sensitivity across
regimes.

## Anti-pattern G: Chronically ignored alert

The same alert has fired 47 times in the past quarter; the
on-call responders have silenced it each time without
acting; the alert continues to page because no one has done
the work to retire it.

Why this violates observability.alerting-discipline: the alert is operationally
noise. It contributes to alert fatigue; responders develop
the habit of silencing alerts without investigation, which
generalizes to alerts that should be acted on.

Remediation: the quarterly sweep (good-pattern Pattern E)
catches this and retires the alert with a documented
rationale. The substrate-recommended escalation: if more
than three rules per quarter require this kind of retire-
or-amend treatment, the consumer holds a meta-review on
the alert authoring process.

## Cross-reference

- Substrate rule: observability.alerting-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Good-pattern examples: examples/observability/alerting-discipline-good.md
