---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.input-validation.deserialization-safe-loaders-deserialization-safe-loaders"
title: "input-validation.deserialization-safe-loaders test template: deserialization safe loaders"
substrate-rule: "input-validation.deserialization-safe-loaders"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# input-validation.deserialization-safe-loaders test template: deserialization safe loaders

## How to use this binding

This binding describes test scenarios for safe-loader behavior
on structured data the application loads (configuration files,
ML model artifacts, registry data). The tests verify that
unsafe loaders are not used and that load-time failures produce
fail-closed behavior.

## Scenario 1: Malformed YAML configuration causes startup failure

**Preconditions**
- A configuration file exists at the application's expected
  load path
- The file is modified to contain malformed YAML (unbalanced
  brackets, invalid indentation)

**Action**
- Start the application

**Expected**
- The application fails to start with a structured error
  identifying the file and the parse failure
- No process continues with default or partial configuration
- An audit log entry records the startup failure

## Scenario 2: Unknown configuration field rejected

**Preconditions**
- A configuration file with a typo in a field name (e.g.,
  "loglevel" instead of "log_level")

**Action**
- Start the application

**Expected**
- The application rejects the configuration with a structured
  error identifying the unknown field
- The application does not continue with default values for
  the misspelled field

## Scenario 3: Configuration version mismatch rejected

**Preconditions**
- The configuration schema expects version "2.0"
- A configuration file declares version "1.0"

**Action**
- Start the application

**Expected**
- The application rejects the configuration or triggers a
  documented migration step
- The behavior matches the documented version-compatibility
  policy

## Scenario 4: ML model with mismatched hash rejected

**Preconditions**
- The application loads an ML model from a known location
- The expected model hash is documented (in code or
  configuration)
- A test model file with a different hash is placed at the
  load location

**Action**
- Trigger model loading (startup or first request requiring
  the model)

**Expected**
- The application rejects the model load with a structured
  error identifying the hash mismatch
- No model inference runs with the unverified model
- The hash-mismatch event is logged

## Scenario 5: PyTorch weights_only loading enforced

**Preconditions**
- The application uses torch.load to load PyTorch checkpoints
- The PyTorch version supports weights_only (1.13+)

**Action**
- Inspect the torch.load invocation in the application code

**Expected**
- torch.load is invoked with weights_only=True
- A test that supplies a malicious checkpoint (containing
  pickle code that would execute on load) is rejected by
  the weights_only=True flag

## Scenario 6: YAML safe_load used at all load sites

**Preconditions**
- The application loads YAML at one or more locations

**Action**
- Static inspection of YAML load call sites (or grep / Semgrep
  rule)

**Expected**
- Every YAML load call site uses yaml.safe_load (or an
  equivalent safe loader)
- No yaml.load without SafeLoader exists anywhere in the
  application's source paths
- The input-validation.no-unsafe-deserialization mechanical detection rule produces no
  findings for the application

## Scenario 7: XXE external entity expansion rejected (if XML is used)

**Preconditions**
- The application loads XML at some point (configuration,
  external data, file upload)
- A malicious XML file with an external entity reference is
  constructed

**Action**
- Load the XML file (test fixture)

**Expected**
- The XML parser does not expand external entities
- The malicious entity reference is either rejected or treated
  as literal text
- No file-disclosure or DoS occurs from the entity expansion

## Scenario 8: Load failure halts dependent operations

**Preconditions**
- A configuration value is required for a feature
- The configuration loads but the required value is missing
  or invalid

**Action**
- Trigger the feature that requires the value

**Expected**
- The feature fails closed: the operation is rejected with a
  structured error identifying the missing or invalid value
- The application does not silently fall through to a default
  behavior that may have security implications
