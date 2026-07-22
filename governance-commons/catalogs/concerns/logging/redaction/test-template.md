---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.logging.redaction-redaction"
title: "logging.redaction test template: sensitive-data redaction strategy"
substrate-rule: "logging.redaction"
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

# logging.redaction test template: sensitive-data redaction strategy

## How to use this binding

Redaction tests verify both call-site enforcement (the type
system or logger plugin redacts at emission) and pipeline-side
enforcement (the aggregator scrubs any disclosure that evaded
the call site). Tests run in unit and integration suites.

## Scenario 1: Type-system redaction wrapper produces redacted output at call site

**Preconditions**
- A redaction wrapper type exists (e.g., Password, SensitiveValue)
- A test object holds a redaction-wrapped sensitive value

**Action**
- Log the test object via the application's standard logger
- Capture the serialized log record

**Expected**
- The record's serialized field for the sensitive value contains
  the redaction marker ([REDACTED] or similar), not the raw value
- str(), repr(), and JSON serialization all produce the marker
- The marker survives nested data structures (dicts containing
  the wrapped value, lists of wrapped values)

## Scenario 2: Application-specific sensitive field is redacted at the call site

**Preconditions**
- The redaction policy lists an application-specific sensitive
  field (e.g., negotiated_rate, diagnosis_code, internal_score)
- The logger plugin or wrapper recognizes the field name

**Action**
- Log a record with the application-specific sensitive field as
  a value
- Capture the serialized log record

**Expected**
- The application-specific sensitive value is redacted in the
  serialized output
- Other non-sensitive fields in the same record are unchanged
- The redaction is consistent across all code paths that log
  the field

## Scenario 3: Pipeline-side scrubbing catches a call-site-evading disclosure

**Preconditions**
- Aggregator-side scrubbing is configured for known patterns
  (credit-card regex, PEM headers, JWT structure, application-
  specific patterns)
- A test record is constructed to bypass call-site redaction
  (e.g., a credit card number embedded in a generic message
  field)

**Action**
- Ingest the test record through the normal application path
- Query the aggregator for the record after ingestion

**Expected**
- The record arrives at the aggregator with the sensitive
  pattern scrubbed (replaced by a marker or redacted-fields
  notation)
- A finding is emitted to security review noting that call-site
  redaction was bypassed
- The pre-scrubbing buffer (if any) has a documented retention
  bound

## Scenario 4: Allow-list discipline rejects a new sensitive field by default

**Preconditions**
- The redaction policy is allow-list framed
- A new code path adds a new field name not in the allow list

**Action**
- Attempt to log a record containing the new field
- Capture the serialized log record

**Expected**
- The new field is excluded from the log output (or replaced
  with [REDACTED-UNCLASSIFIED-FIELD] depending on the logger
  plugin behavior)
- A warning is emitted indicating an unclassified field was
  encountered
- The warning surfaces in CI or pre-production gates so the
  field is classified before reaching production

## Scenario 5: Hashing for join produces stable hashes within pipeline

**Preconditions**
- A field is configured for hash-for-join handling
- The pipeline-scoped salt is set

**Action**
- Log multiple records containing the same value of the hashed
  field
- Compare the hashed values across records

**Expected**
- Identical input values produce identical hash output within
  the pipeline (join works)
- The hash output is not the raw value (disclosure prevented)
- Cross-pipeline export of the hash output does not enable
  re-identification (the salt prevents rainbow-table attacks)

## Scenario 6: Salt rotation preserves cross-record join for new records only

**Preconditions**
- A salt rotation procedure exists
- Pre-rotation records exist with old-salt hashes

**Action**
- Execute the salt rotation
- Log a new record with the same input value
- Compare new-record hash to old-record hash

**Expected**
- The new-record hash differs from the old-record hash (the
  rotation produced a salt change)
- Old records remain queryable with old hashes
- The pipeline's join logic accommodates the rotation epoch

## Scenario 7: Debug path applies redaction

**Preconditions**
- The application has a debug logging path
- A debug log call is made with a sensitive value

**Action**
- Trigger the debug path in a test environment
- Capture the debug log output

**Expected**
- The debug output applies redaction (the developer sees the
  marker, not the raw value)
- An out-of-band un-redacted access procedure exists, is
  approval-gated, and is audited
- Emergency dumps are routed to access-controlled storage
  separate from regular logs

## Scenario 8: Exception logging does not include sensitive data

**Preconditions**
- A code path that may raise exceptions with sensitive data in
  the exception body (e.g., an assertion comparing user input)

**Action**
- Trigger the exception in a test environment
- Capture the exception log

**Expected**
- The exception type is logged
- The exception message is a sanitized summary, not the raw
  str representation
- No sensitive data appears in the captured log

## Test attestation

```
logging.redaction test suite: PASSING
- Scenario 1 (type-system redaction at call site): PASS
- Scenario 2 (application-specific field redacted): PASS
- Scenario 3 (pipeline catches call-site evasion): PASS
- Scenario 4 (allow-list rejects new field by default): PASS
- Scenario 5 (hashing produces stable join): PASS / NA
- Scenario 6 (salt rotation preserves new joins): PASS / NA
- Scenario 7 (debug path applies redaction): PASS
- Scenario 8 (exception logging sanitized): PASS
```

## Cross-reference

- Substrate rule: logging.redaction
- Review checklist: checklist.md
- Good examples: examples/logging/redaction-good.md
