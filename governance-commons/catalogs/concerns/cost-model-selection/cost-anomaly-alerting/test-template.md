---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.cost-model-selection.cost-anomaly-alerting-cost-anomaly-alerting"
title: "cost-model-selection.cost-anomaly-alerting test template: cost anomaly alerting configured"
substrate-rule: "cost-model-selection.cost-anomaly-alerting"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-21"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# cost-model-selection.cost-anomaly-alerting test template: cost anomaly alerting configured

## How to use this binding

Cost anomaly alerting tests exercise the consumer's alerting
configuration via synthetic cost variance (driving a test
workload to consume above its threshold for a controlled window)
and verify the alert fires, routes, and produces the documented
response. Tests also exercise the routing without firing the
alert (a synthetic drill that confirms the on-call path works).

Substrate-recommended cadence: quarterly synthetic drill of the
alert routing; annual real-fire test (where a workload is
intentionally over-driven against a sandboxed budget to confirm
the alert fires); spot-check after any routing change or
threshold change.

## Scenario 1: Per-service budget is configured and reflects the ADR

**Preconditions**
- A service has a documented cost SLO in the cost-model-selection.cost-model-selection-policy ADR
  (the ADR specifies the monthly budget target)
- The alerting platform (AWS Cost Anomaly Detection plus AWS
  Budgets, Azure Cost Management alerts, GCP Budget alerts,
  third-party FinOps platform, OpenCost-derived Prometheus
  alerts) is configured for the service

**Action**
- Query the alerting configuration for the service's budget
- Compare the configured budget value against the ADR's
  documented SLO target
- Compare the configured threshold structure against the
  substrate-recommended multi-window burn-rate pattern

**Expected**
- The configured budget matches the ADR's documented target
  (within the substrate-recommended variance for rounding)
- Multi-window thresholds are configured (1-day burn-rate and
  7-day burn-rate at minimum)
- The thresholds normalize the monthly budget appropriately
  for each window
- Configured budgets exist for every service the ADR
  documents

## Scenario 2: Burn-rate alert fires on synthetic variance

**Preconditions**
- A non-production sandbox environment exists where synthetic
  cost can be driven without affecting production budgets
- A test workload can be driven to consume above the sandbox
  budget's burn-rate threshold for the substrate-recommended
  trigger window
- The alerting platform's test routing is configured to a test
  endpoint (not the production on-call rotation)

**Action**
- Drive the test workload to consume at the rate that triggers
  the 1-day burn-rate threshold
- Wait for the alerting platform's evaluation cycle
- Verify the alert fires at the expected trigger point

**Expected**
- The alert fires within the alerting platform's documented
  evaluation latency (substrate-recommended: alert visible
  within hours of trigger, not days)
- The alert payload contains the substrate-recommended fields:
  service name, budget threshold, actual burn rate, time
  window, link to the cost-model ADR, link to the runbook
- The alert routing delivers to the test endpoint (the
  routing has not silently been redirected)

## Scenario 3: Alert routes to the service-owning team

**Preconditions**
- A service has an assigned owning team with on-call rotation
- The alerting configuration routes to the team's substrate-
  recommended routing target (on-call rotation, paging service,
  or substrate-equivalent)
- A synthetic-drill mode is supported by the alerting platform
  (a test message that exercises routing without invoking the
  full burn-down response)

**Action**
- Trigger the synthetic drill against the service's alerting
  configuration
- Verify the drill message arrives at the on-call rotation
- Verify acknowledgment routing back to the alerting platform
  works
- Verify escalation routing fires if the drill is not
  acknowledged within the substrate-recommended window

**Expected**
- The drill message arrives at the on-call rotation
- The on-call rotation can acknowledge the drill, and the
  acknowledgment is recorded
- Escalation fires if the drill is not acknowledged (the
  escalation chain has not silently been retired)
- The drill exercises only routing, not the full response
  policy (the consumer's production workload is not affected)

## Scenario 4: Burndown response is documented and exercisable

**Preconditions**
- The cost-model-selection.cost-model-selection-policy ADR documents the over-budget response policy
- The policy specifies concrete actions at named burndown
  thresholds (e.g., 50 percent budget remaining, 25 percent, 10
  percent, 0 percent)
- The team has a runbook implementing the response policy

**Action**
- For each documented burndown threshold, walk through the
  documented response with the service-owning team
- Verify each response action is operationally meaningful
  (the team knows how to execute, has the authority to
  execute, and has the tooling required)
- Run a synthetic drill of one or two responses (the workload-
  level mitigations are typically safe to drill; the service-
  level rate limiting may require sandbox)

**Expected**
- Every documented threshold maps to an executable response
- The team can demonstrate execution of at least one response
  in a drill
- The response policy is current (no stale references to
  retired processes, tools, or roles)
- The response policy invokes the substrate-recommended
  cross-references (the cost-model-selection.cost-model-selection-policy ADR cross-references
  observability.slo-policy SLO policy where the trade-off applies)

## Scenario 5: Threshold values produce signal not noise

**Preconditions**
- The service has historical spend data for at least 90 days
- The consumer's spend baseline is computable from the
  pipeline (the cost-model-selection.cost-emission-pipeline pipeline outputs the historical
  distribution)
- The alerting platform has fired against the threshold (in
  production) or can simulate firing against historical data

**Action**
- Simulate the alert configuration against the historical
  spend distribution
- Count the number of historical days the alert would have
  fired (false positives if the day was normal variance; true
  positives if the day was a real anomaly)
- Compute the signal-to-noise ratio against the documented
  anomaly events in the historical period

**Expected**
- The alert fires on documented anomaly events (the substrate-
  recommended signal capture)
- The alert does not fire on normal variance days (the
  substrate-recommended noise rejection)
- Threshold tuning produces a substrate-recommended ratio
  (the substrate does not prescribe a specific ratio; the
  reviewer compares against the consumer's prior-year ratio
  to confirm thresholds have not drifted into noise)

## Scenario 6: Per-tenant alerts fire on tenant variance

**Preconditions**
- A multi-tenant service has cost-model-selection.cost-emission-pipeline per-tenant attribution
- Per-tenant cost anomaly alerts are configured
- A test tenant can be driven to consume above the tenant
  threshold without affecting production tenants

**Action**
- Drive the test tenant's consumption above the per-tenant
  budget threshold
- Verify the per-tenant alert fires (separate from the
  per-service alert; the per-service alert may not fire if
  the service total is within budget)
- Verify the alert routes to the tenant-management function
  (or whichever consumer function the routing documents)

**Expected**
- Per-tenant alerts fire independently of per-service alerts
- Per-tenant alert routing targets the substrate-recommended
  function (customer-success or tenant-management for tenant-
  facing response; service-owning team for workload-shaping
  response)
- The per-tenant alert produces actionable signal (the
  tenant can be identified; the consumer's runbook documents
  the per-tenant response)
