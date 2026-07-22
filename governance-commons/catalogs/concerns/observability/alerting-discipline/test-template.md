---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.observability.alerting-discipline-alerting-discipline"
title: "observability.alerting-discipline test template: alerting discipline"
substrate-rule: "observability.alerting-discipline"
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

# observability.alerting-discipline test template: alerting discipline

## How to use this binding

Alerting discipline tests exercise the alert rule structure
itself (does every rule carry the substrate-required labels
and annotations?) and the alert rule behavior (does the rule
fire correctly given known input data?). The first form is a
static check against alert rule definitions; the second is a
load test with a controlled metrics fixture. Substrate-
recommended cadence: CI on every alert rule change; quarterly
simulation against representative incident scenarios.

## Scenario 1: Every alert rule carries the required structural elements

**Preconditions**
- All consumer-authored alert rules are accessible in their
  source format (Prometheus rule files, Alertmanager
  configuration, vendor-equivalent YAML or JSON)

**Action**
- Parse the alert rule files
- For each rule, check the presence of required fields

**Expected**
- Every alert rule has a severity label from the consumer's
  bounded vocabulary
- Every alert rule has a runbook_url annotation
- Every alert rule has a summary annotation
- Every alert rule has a description or equivalent (vendor-
  specific) detail annotation
- Rules missing any required field fail the test

## Scenario 2: Runbook URLs resolve to live documents

**Preconditions**
- Alert rule runbook_url annotations have been collected
- Network access to the consumer's runbook hosting (wiki,
  documentation site, etc.)

**Action**
- For each unique runbook_url, issue a HEAD or GET request
- Check the response status

**Expected**
- All runbook URLs return 2xx responses
- 404s, 5xx, or auth-walled URLs fail the test
- The test produces a report identifying the affected alert
  rules

## Scenario 3: Alert fires correctly on synthetic input

**Preconditions**
- A test metrics backend or in-process metric registry
- A fixture that drives the metrics the alert rule queries
- The alert rule loaded into a test Alertmanager (or vendor
  equivalent) configured with the consumer's routing

**Action**
- Drive the fixture metrics to produce the alert condition
- Wait for the alert evaluation interval
- Inspect the resulting alert notification

**Expected**
- The alert fires within the expected evaluation window
- The notification carries the expected severity, summary,
  description, and runbook_url
- The notification is routed to the expected destination
  (paging system, ticket system, log only) per the consumer's
  routing rules

## Scenario 4: Inhibition rule suppresses cascading alerts

**Preconditions**
- Two related alerts where one represents a root cause and
  the other represents a downstream symptom
- An Alertmanager inhibition rule configured to suppress the
  symptom when the root cause is firing
- Fixture metrics that can independently trigger each alert

**Action**
- Drive fixtures to fire both alerts simultaneously
- Inspect the resulting notifications

**Expected**
- Only the root-cause alert produces a notification
- The symptom alert is suppressed by inhibition
- The test produces a record of the inhibition state for
  audit

## Scenario 5: Burn-rate alert fires at the documented threshold

**Preconditions**
- Service has an SLO documented (observability.slo-policy)
- Multi-window burn-rate alerts are configured
  (substrate-recommended: 1-hour and 6-hour windows)
- A fixture that can drive error rates to produce specific
  burn rates

**Action**
- Drive the fixture to produce a burn rate at the alerting
  threshold for each configured window
- Verify the alert fires at the expected sensitivity

**Expected**
- The 1-hour fast-burn alert fires when the 1-hour burn rate
  exceeds the substrate-recommended threshold (substrate-
  recommended starting threshold: 14.4 burn rate at 1 hour)
- The 6-hour slow-burn alert fires when the 6-hour burn rate
  exceeds the configured threshold
- The combined notification routes to the expected severity
  tier
- False-positive burn rates (transient spikes within
  acceptable bounds) do not fire the alert

## Scenario 6: Chronically-noisy alert triggers self-assessment

**Preconditions**
- Alert firing history for the past quarter is queryable
- A threshold defining "chronically noisy" is documented
  (substrate-recommended starting threshold: more than 5
  silenced firings in the past month)

**Action**
- Query the alert firing history
- Identify alerts that exceed the noise threshold

**Expected**
- Chronically-noisy alerts are surfaced in a report
- The report becomes input to the observability.alerting-discipline quarterly sweep
- The substrate-recommended remediation (disable with
  documented rationale) is tracked per surfaced alert

## Scenario 7: Negative test: alert rule with no severity fails the structural check

**Preconditions**
- A test fixture alert rule deliberately omits the severity
  label

**Action**
- Run the structural check (Scenario 1) on the fixture

**Expected**
- The check fails on the missing severity label
- The failure message identifies the rule and the source
  location
- The test catches the case before the rule merges to the
  production alert configuration

## Cross-reference

- Substrate rule: observability.alerting-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Good examples: examples/observability/alerting-discipline-good.md
- Anti-patterns: examples/observability/alerting-discipline-anti-pattern.md
- Related: observability.slo-policy (anchors burn-rate alerting via SLO documentation)
