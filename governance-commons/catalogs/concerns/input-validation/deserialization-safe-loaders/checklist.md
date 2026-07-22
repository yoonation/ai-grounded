---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.deserialization-safe-loaders-deserialization-safe-loaders"
title: "input-validation.deserialization-safe-loaders review checklist: deserialization safe loaders"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add or modify configuration file loading"
  - "Code changes that integrate ML model loading or other structured-data ingestion"
  - "Code changes that touch deserialization at cross-trust-boundary interfaces"
  - "Periodic input-validation self-assessment"
---

# input-validation.deserialization-safe-loaders review checklist: deserialization safe loaders

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block
merge.

This checklist extends input-validation.no-unsafe-deserialization's mechanical detection of
unsafe deserialization calls into the design-pattern layer: data
loaded from disk, network, or external source is treated as
cross-boundary even when the file is "local," and safe-loader +
schema-validation discipline is applied uniformly. Configuration
files and ML model artifacts are the most common patterns in
this category.

## Review questions

### 1. Safe loader selection: are YAML and JSON files loaded with safe parsers?

Confirm that YAML files use yaml.safe_load (Python) or
equivalents; JSON files are parsed with schema-validation. The
unsafe variants (yaml.load without SafeLoader, JSON parsers that
allow code-execution callbacks) do not appear at load call sites.

What good looks like: every YAML load call site uses safe_load;
JSON load call sites pair with schema validation against a
declared schema; the application's startup configuration loading
follows the same pattern as request-time loading.

What needs follow-up: yaml.load is used at any call site; JSON
loading produces raw dicts that downstream code accesses without
schema validation; configuration loading and request loading use
inconsistent patterns.

### 2. Configuration version: is the version field validated at load?

Confirm that configuration files include an explicit version
field and that the loader validates version compatibility before
accepting the data. A configuration file with an unknown version
is rejected; a configuration file with a version requiring
migration triggers migration before use.

What good looks like: the configuration schema includes a version
field with permitted values; loading rejects files outside the
permitted set; migration steps are explicit and reviewed.

What needs follow-up: configuration files have no version field;
version mismatches produce silent acceptance with default values
that may not match the file's intent; the application does not
distinguish configuration schema generations.

### 3. ML model provenance: are model artifacts loaded from trusted sources?

Confirm that ML model files loaded by the application are paired
with provenance signals: a known source URL, a verified hash, a
format-specific safety control (ONNX model checks, safetensors
format which prohibits code execution). PyTorch torch.load and
Keras load_model are particular substrate concerns because they
use pickle internally.

What good looks like: model loading is restricted to a closed set
of model registries; model files are hash-verified against a
pinned hash list; safetensors format is used where available;
torch.load is invoked with weights_only=True (available in
PyTorch 1.13+).

What needs follow-up: model files are loaded from arbitrary
sources (a user-supplied URL); model files are not hash-verified;
torch.load is invoked with default weights_only=False on models
of uncertain provenance.

### 4. Fail-closed behavior: do load errors prevent startup or operation?

Confirm that load failures result in fail-closed behavior: the
application refuses to start (or refuses to perform the operation)
rather than continuing with partial or default configuration.
Silent fallback to defaults masks misconfigurations that may
have security implications.

What good looks like: configuration loading errors halt startup
with a structured error message identifying the file and the
specific failure; ML model loading errors halt the request that
required the model with a structured error response.

What needs follow-up: configuration loading errors log a warning
and continue with default values; missing configuration files
are silently treated as empty; ML model loading errors fall
through to a default behavior that may not match the operational
intent.

### 5. Schema validation: are loaded values validated against schemas?

Confirm that loaded structured data (configuration, model
metadata, registry artifacts) is validated against a declared
schema after deserialization, the same way request bodies are
validated per input-validation.schema-validation-at-boundary. The schema rejects unexpected fields
and out-of-range values.

What good looks like: configuration schemas are declared
(Pydantic models, JSON Schema documents, equivalent in the
application's language); loaded data is validated immediately
after deserialization; unknown fields trigger a documented
behavior (reject or strip).

What needs follow-up: loaded data is treated as a raw dict and
accessed by key without validation; configuration changes that
introduce typos are not caught at load time; unexpected fields
are silently accepted.

### 6. Cross-format coverage: does the policy cover all loaded formats?

Confirm that the same safe-loader + schema-validation discipline
applies to all data formats the application loads: YAML, JSON,
TOML, INI, XML, Protocol Buffers, Avro. XML in particular
requires explicit XXE protection (disable external entity
resolution) and is a frequent gap.

What good looks like: a documented list of permitted load
formats; each format has a substrate-recommended safe loader
configured (XML with external entity resolution disabled);
unsupported formats are explicitly rejected.

What needs follow-up: format coverage is partial; XML loading
does not disable external entities; some formats use safe
loaders while others do not.

### 7. Testing: are load failures tested?

Confirm that the application's test suite includes specific
cases for load-time failures: malformed YAML or JSON files,
unknown configuration fields, version mismatches, ML model
hash mismatches.

What good looks like: a dedicated configuration-loading test
module exercises positive and negative cases; new configuration
fields are added to the test module when introduced; ML model
loading errors have integration test coverage.

What needs follow-up: load-time failures are not tested; the
application's behavior on malformed input is undefined; load
failures are first observed in production.

## Output

Each question receives GOOD, NEEDS FOLLOW-UP, or NOT APPLICABLE
per the standard checklist output convention.
