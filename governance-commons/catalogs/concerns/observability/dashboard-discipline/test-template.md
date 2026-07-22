---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.observability.dashboard-discipline-dashboard-discipline"
title: "observability.dashboard-discipline test template: dashboard discipline"
substrate-rule: "observability.dashboard-discipline"
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

# observability.dashboard-discipline test template: dashboard discipline

## How to use this binding

Dashboard discipline tests verify dashboard JSON (Grafana,
Kibana, vendor equivalents) carries the structural elements
the methodology requires. Tests parse the dashboard
definition and assert against the methodology-specific
required panel set. Substrate-recommended cadence: CI on
every dashboard change committed to the consumer's
dashboard-as-code repository; quarterly sweep against the
deployed dashboard inventory.

## Scenario 1: Dashboard declares its methodology

**Preconditions**
- Consumer manages dashboards as code (JSON files in a
  version-controlled location)
- A consumer convention for declaring methodology (substrate-
  recommended: methodology tag on the dashboard, or
  methodology name in the dashboard title prefix)

**Action**
- Parse the dashboard JSON
- Extract the declared methodology

**Expected**
- The methodology is one of RED, USE, Four Golden Signals,
  Composite, or SLI
- Dashboards with no declared methodology fail the test
- Dashboards declaring an unrecognized methodology fail the
  test

## Scenario 2: RED dashboard has the required signal panels

**Preconditions**
- Dashboard is declared RED methodology

**Action**
- Parse the dashboard panels
- Identify panels by their labels or tags

**Expected**
- A panel labeled Rate or Throughput showing request rate
  per second exists
- A panel labeled Errors showing error rate (count or ratio)
  exists
- A panel labeled Duration or Latency showing latency
  percentiles exists
- Panels not in these categories are either decorative or
  belong to a non-RED dashboard

## Scenario 3: USE dashboard has the required signal panels

**Preconditions**
- Dashboard is declared USE methodology

**Action**
- Parse the dashboard panels
- Identify panels by category

**Expected**
- A Utilization section exists with panels for each resource
  the service depends on (CPU, memory, I/O, connection pool,
  queue depth)
- A Saturation section exists with panels showing waiting
  work for each resource
- An Errors section exists with panels for resource errors
- Required resources for the service type are all represented

## Scenario 4: Four Golden Signals dashboard has all four signals

**Preconditions**
- Dashboard is declared Four Golden Signals methodology

**Action**
- Parse the dashboard panels

**Expected**
- A Latency panel exists
- A Traffic panel exists
- An Errors panel exists
- A Saturation panel exists
- The four signals are visible without scrolling on a
  representative screen size

## Scenario 5: SLI dashboard is separate from operational dashboards

**Preconditions**
- Service has an SLO (observability.slo-policy)
- Service has an SLI dashboard

**Action**
- Inventory the consumer's dashboard catalog for the service
- Check the SLI dashboard's location and the operational
  dashboards' content

**Expected**
- An SLI dashboard exists and is pinned (substrate-recommended:
  at the top of the consumer's dashboard navigation for the
  service)
- The SLI dashboard contains SLI panels (current burn rate,
  budget remaining, historical trend per observability.slo-policy SLI
  choices)
- Operational dashboards do NOT contain SLI panels (the
  panels are cross-linked, not duplicated)

## Scenario 6: Dashboard fits within recommended panel count

**Preconditions**
- Dashboard JSON contains panel definitions

**Action**
- Count the panels in the dashboard
- Inspect for rows or sections

**Expected**
- Panel count is at most the substrate-recommended ceiling
  (roughly 20 panels per dashboard); dashboards exceeding the
  ceiling fail the test
- Panels are organized into rows or sections labeled by
  signal category
- Dashboards below the ceiling but with chaotic panel
  arrangement (no rows or sections) fail a layout sub-check

## Scenario 7: Cross-references are intact

**Preconditions**
- Dashboard panels carry links to alerts and (where applicable)
  to ADRs
- Alert rules carry links back to dashboard panels

**Action**
- For each panel-to-alert link, verify the alert exists in
  the alert configuration
- For each alert-to-panel link, verify the panel URL is
  stable (substrate-recommended: the URL contains a panel
  ID that survives dashboard renaming)

**Expected**
- All panel-to-alert links resolve to live alerts
- All alert-to-panel links resolve to live panels
- Broken cross-references fail the test with a report
  identifying the source and target

## Scenario 8: Negative test: dashboard mixing SLI and operational panels fails

**Preconditions**
- A test fixture dashboard with both SLI panels and
  operational panels on the same surface

**Action**
- Run Scenario 5 against the fixture

**Expected**
- The check fails because the SLI dashboard is not separate
- The failure message identifies the mixed panels
- The substrate-recommended remediation (split the dashboard)
  is logged

## Cross-reference

- Substrate rule: observability.dashboard-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Good examples: examples/observability/dashboard-discipline-good.md
- Anti-patterns: examples/observability/dashboard-discipline-anti-pattern.md
- Related: observability.slo-policy (SLI dashboard content); observability.alerting-discipline (alert cross-references)
