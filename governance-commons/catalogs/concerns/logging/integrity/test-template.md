---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.logging.integrity-integrity"
title: "logging.integrity test template: log integrity controls"
substrate-rule: "logging.integrity"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.3.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# logging.integrity test template: log integrity controls

## How to use this binding

Integrity tests verify that the chosen mechanism is configured
and functional. Substrate-recommended cadence: quarterly
verification exercise documented in the operational runbook.
Some scenarios require attempted destructive operations and
should run in a staging-equivalent environment, not against
production audit logs.

## Scenario 1: Attempted deletion is blocked on protected streams

**Preconditions**
- A security-relevant log stream with documented integrity
  protection (append-only, object-lock, or equivalent)
- Test credentials with the highest privilege the consumer
  retains for this aggregator

**Action**
- Attempt to delete a record (or a record batch) in the
  protected stream

**Expected**
- The deletion is blocked by the aggregator
- An audit event records the attempt
- The data remains queryable after the failed deletion

## Scenario 2: Attempted modification is blocked

**Preconditions**
- A protected log stream with a known record
- Test credentials with administrative access

**Action**
- Attempt to modify the record's content (e.g., overwrite a
  field value, alter the timestamp)

**Expected**
- The modification is blocked
- An audit event records the attempt
- The record's content is unchanged

## Scenario 3: Hash chain head matches external publication (hash-chain mechanism)

**Preconditions**
- The integrity mechanism is a hash chain with external head
  publication
- A recent batch of records has been ingested and chained

**Action**
- Read the current chain head from the aggregator
- Read the most recent published chain head from the external
  attestation service
- Compare

**Expected**
- The aggregator's head matches the externally published head
  for the publication cadence
- A history of past heads is preserved and matches across both
  sources

## Scenario 4: SIEM access is restricted to non-application-admin roles

**Preconditions**
- The integrity mechanism is SIEM-based with administrative
  isolation
- An application admin account exists and is distinct from
  the SIEM admin account

**Action**
- Using application admin credentials, attempt to access SIEM
  retention configuration
- Using application admin credentials, attempt to delete or
  modify SIEM records

**Expected**
- Application admin cannot access SIEM retention configuration
- Application admin cannot delete or modify SIEM records
- The attempts produce audit events visible to the SIEM team

## Scenario 5: Signed records survive aggregator compromise

**Preconditions**
- The integrity mechanism includes per-record signing
- A test record is produced and signed by the trusted shipper

**Action**
- Modify the record at the aggregator (bypass the immutability
  configuration via an authorized maintenance window)
- Re-verify the record's signature

**Expected**
- The signature verification fails on the modified record
- A monitoring alert fires on the verification failure
- The signed-record trail allows reconstruction of the
  pre-modification content

## Scenario 6: Configuration drift on immutability flag is detected

**Preconditions**
- Aggregator is configured with immutability enabled
- The configuration is managed by IaC (Terraform, Pulumi)

**Action**
- Disable immutability via console (simulating drift)
- Run the drift-detection job

**Expected**
- The drift job reports the immutability flag is now disabled
- The IaC reconciliation re-enables immutability
- A finding is filed for the unauthorized change

## Scenario 7: Audit log of integrity-configuration changes is itself protected

**Preconditions**
- The aggregator emits audit events for integrity-configuration
  changes
- The audit log resides in a separately access-controlled
  store

**Action**
- Attempt to modify an audit event in the integrity-configuration
  audit log
- Attempt to access the audit log with application admin
  credentials

**Expected**
- The modification is blocked
- The application admin does not have read access (or has read
  but not write, per the consumer's policy)
- The audit log of the audit log is itself preserved

## Scenario 8: End-to-end integrity holds across shipping hops

**Preconditions**
- Logs travel through multiple hops (application → shipper →
  aggregator → archival)
- Each hop has integrity protection documented

**Action**
- Inject a test record at the application
- At each hop, verify the integrity protection is active
- Confirm the test record arrives at archival unchanged

**Expected**
- Each hop's integrity protection is active and verified
- The test record's signature or hash matches end-to-end
- No hop introduces a tamper window

## Test attestation

```
logging.integrity test suite: PASSING
- Scenario 1 (deletion blocked): PASS
- Scenario 2 (modification blocked): PASS
- Scenario 3 (hash chain head matches): PASS / NA
- Scenario 4 (SIEM access restricted): PASS / NA
- Scenario 5 (signed records survive modification): PASS / NA
- Scenario 6 (drift detected): PASS
- Scenario 7 (audit-log audit-log preserved): PASS
- Scenario 8 (end-to-end integrity): PASS
```

## Cross-reference

- Substrate rule: logging.integrity
- Review checklist: checklist.md
- Good examples: examples/logging/integrity-good.md
