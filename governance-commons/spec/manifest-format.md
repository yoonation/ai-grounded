<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Manifest Format

This document specifies the format used for consumer manifests. A
manifest is a consumer-side artifact that binds substrate content
to consumer workflow: it declares the commons version the consumer
integrates against, the profile that determines selections, and the
checkpoints in the consumer's workflow at which substrate
consultation occurs.

The format is referenced by Charter Article VI (consultation
evidence) and Charter Article VII (compatibility with consumers).
Mechanical validation lives in `../schemas/manifest.schema.json`.

This format is published by the substrate; manifest files
themselves live consumer-side, not in the substrate. The substrate
ships the format spec and schema. Consumers author manifests in
their own repositories per their own discipline.

## Why a manifest

The substrate's value depends on actual consultation occurring at
the right points in consumer workflows. A consumer could in
principle hard-code substrate consultation into agent prompts,
workflow scripts, or runtime middleware. The manifest provides a
declarative, audit-friendly alternative:

- **Declarative**: the manifest states what should be consulted
  where; substrate tooling and consumer workflows read the same
  source of truth.
- **Audit-friendly**: when a finding is raised or absent, the
  manifest records what was supposed to happen, so audit can
  detect missing consultation.
- **Update-friendly**: substrate evolution (new rules, new
  catalogs, new mappings) can be picked up by updating the
  manifest, without rewriting workflow integrations.
- **Profile-explicit**: the consumer's chosen profile is named in
  one place, not scattered across agent prompts.

Manifests are optional. Consumers may integrate the substrate
without manifests; they still satisfy the consultation evidence
contract by other means. The manifest mechanism is a convenience.

## File format and serialization

Manifests are serialized as YAML. The conventional filename and
location is consumer-defined; the substrate recommends:

```
<consumer-repo>/governance-manifest.yaml
```

Some consumers prefer placement inside a configuration directory:

```
<consumer-repo>/.governance/manifest.yaml
<consumer-repo>/config/governance-manifest.yaml
```

The substrate does not prescribe location. The manifest's location
is part of the consumer's repository conventions.

## Top-level document structure

A manifest has the following top-level shape:

```yaml
manifest:
  schema-version: 0.1.0
  consumer:
    identifier: <consumer-defined identifier>
    type: <consumer architecture type>
    contact: <optional contact information>
  substrate:
    commons-version: <pinned commons version>
    profile: <selected profile identifier>
    profile-version: <pinned profile version, optional>
  workflow:
    checkpoints: <list of consultation checkpoints>
  evidence:
    medium: <audit medium type>
    location: <consumer-defined location reference>
    integrity: <integrity mechanism descriptor>
  provenance:
    author: <human identity>
    authored: <ISO 8601 date>
    last-modified: <ISO 8601 date>
    ai-assistance: <description per Charter Article II Section 2.2>
```

Top-level keys are described in the sections below.

## `schema-version`

The manifest format version this manifest conforms to. Required.
The substrate maintains backward compatibility for manifest format
within a major version per Charter Article VIII Section 7.5.

Current value: `0.1.0` matches commons VERSION.

## `consumer` block

Identifies the consumer using the substrate.

- **identifier** (required): a stable identifier for the consumer.
  Recommended pattern: `<organization-namespace>.<project-name>`,
  e.g., `acme-corp.payment-service`. The substrate does not assign
  consumer identifiers; consumers define their own.
- **type** (required): the consumer's architectural category.
  Permitted values:
  - `build-time-framework`: AI-assisted spec-driven development
    framework (writes code based on substrate-consulted findings)
  - `runtime-enforcement`: production runtime that consults
    substrate at policy decision points
  - `standalone-catalog-consumer`: uses substrate as reference
    without AI consultation
  - `hybrid`: combinations of the above
- **contact** (optional): email, repository URL, or other reference
  for substrate maintainer outreach.

Example:

```yaml
consumer:
  identifier: acme-corp.payment-service
  type: build-time-framework
  contact: platform-engineering@acme-corp.example
```

## `substrate` block

Identifies the substrate version and profile this manifest binds
to.

- **commons-version** (required): the commons version this
  manifest integrates against, per Charter Article VII Section 7.3.
  Consumers pin to a specific version (semantic versioning string)
  or a version range constraint (e.g., `^0.1.0` for minor-version
  compatibility). Implicit dependencies are not permitted.
- **profile** (required): the active profile identifier. Either a
  substrate-shipped profile (e.g., `production-grade-baseline`,
  `financial-services`) or a consumer-side profile identifier per
  `extension-contract.md` Section "Custom profile authoring
  procedures".
- **profile-version** (optional): pinned profile version when
  precise reproducibility matters. If omitted, the manifest accepts
  the profile at its current commons-version.

Example:

```yaml
substrate:
  commons-version: 0.1.0
  profile: production-grade-baseline
  profile-version: 0.1.0
```

## `workflow.checkpoints` block

The core of the manifest. Each checkpoint declares a point in the
consumer's workflow at which substrate consultation occurs and what
should be consulted.

Each checkpoint has the following shape:

```yaml
- name: <checkpoint identifier>
  trigger: <when this checkpoint fires>
  consulter: <which consumer principal performs consultation>
  consults:
    catalogs: <list of catalog identifiers>
    rules: <optional; specific rule identifiers when scope is finer-grained>
    mappings: <optional; mapping identifiers to consult>
    decision-frameworks: <optional; decision framework identifiers>
  required-findings: <how findings are handled>
  blocking: <boolean; whether findings block workflow progress>
```

### Checkpoint fields

- **name** (required): a consumer-defined identifier for the
  checkpoint. Used in audit events to reference which checkpoint
  produced an event.
- **trigger** (required): describes when the checkpoint fires.
  This is a consumer-specific reference (a Git hook name, a
  workflow stage identifier, a runtime event name, a CI/CD step).
  The substrate makes no assumptions about trigger semantics; the
  trigger is a label the consumer understands.
- **consulter** (required): identifier of the consumer principal
  (AI agent, runtime service, automated tool, human role) that
  performs consultation at this checkpoint.
- **consults** (required): what substrate content is consulted.
  At least one of `catalogs`, `rules`, `mappings`, or `decision-
  frameworks` must be non-empty.
  - `catalogs`: full catalog identifiers (e.g., `concerns/
    authentication`); consulter examines all rules in the catalog
  - `rules`: specific rule identifiers when only a subset of a
    catalog is relevant
  - `mappings`: mapping identifiers when cross-taxonomy
    traceability is needed
  - `decision-frameworks`: framework identifiers when Layer 3
    decisions are anticipated at this checkpoint
- **required-findings** (optional): how findings are handled.
  Permitted values: `report-only`, `record-only`, `report-and-
  block`, `record-and-block`. Default: `report-and-block`.
- **blocking** (optional): convenience boolean. True if findings
  block workflow progress. False if findings are advisory only.
  Default depends on `required-findings`; explicit override
  permitted.

### Example checkpoints

For a build-time AI coding framework, typical checkpoints:

```yaml
workflow:
  checkpoints:
    - name: post-spec-drafting
      trigger: spec-completion
      consulter: threat-modeling-agent
      consults:
        catalogs:
          - threats/owasp-llm-top10
          - threats/owasp-agentic-asi
          - threats/stride
          - concerns/authentication
        decision-frameworks:
          - auth-strategy
      blocking: true

    - name: pre-implementation
      trigger: plan-completion
      consulter: implementation-planning-agent
      consults:
        catalogs:
          - concerns/code-organization
          - concerns/error-handling
          - concerns/logging
          - concerns/testing-strategy
      blocking: false

    - name: post-implementation
      trigger: code-completion
      consulter: code-review-agent
      consults:
        catalogs:
          - concerns/authentication
          - concerns/authorization
          - concerns/input-validation
          - concerns/error-handling
          - concerns/logging
        rules:
          - performance-database.performance-database.no-query-in-loop
          - performance-database.performance-database.bounded-result-sets
      required-findings: report-and-block
      blocking: true
```

For a runtime enforcement consumer, typical checkpoints:

```yaml
workflow:
  checkpoints:
    - name: request-inception
      trigger: incoming-request
      consulter: policy-decision-point
      consults:
        catalogs:
          - concerns/authentication
          - concerns/authorization
      blocking: true

    - name: ai-model-invocation
      trigger: llm-call
      consulter: model-gateway
      consults:
        catalogs:
          - threats/owasp-llm-top10
          - concerns/cost-model-selection
          - concerns/responsible-ai
      blocking: true
```

## `evidence` block

Declares the audit medium where consultation evidence is recorded
per Charter Article VI.

- **medium** (required): the storage form of consultation evidence.
  Permitted values: `jsonl-append-only`, `opentelemetry-spans`,
  `immutable-database`, `cloud-audit-log`, `signed-git-history`,
  `custom`. When `custom`, additional fields describe the medium.
- **location** (required): a consumer-defined reference to where
  the medium is hosted. May be a file path, a database connection
  identifier (without credentials), an OpenTelemetry collector
  endpoint, or an opaque identifier the consumer's tooling
  resolves.
- **integrity** (required): the integrity mechanism. Permitted
  values include `append-only-filesystem`, `write-once-storage`,
  `cryptographic-signatures`, `hash-chain`, `signed-commits`,
  `trusted-timestamping`, `third-party-audit-service`, `custom`.

Example:

```yaml
evidence:
  medium: jsonl-append-only
  location: .governance/events/
  integrity: signed-commits
```

The evidence block is the manifest's declaration of how the
consumer satisfies the consultation evidence contract. The
substrate's tooling for evidence verification uses this block to
locate and validate evidence per `consultation-evidence.md`.

## `provenance` block

Per Charter Article II Section 2.2, applied to consumer-side
manifest authoring. The substrate cannot enforce provenance on
consumer artifacts but recommends it.

- **author** (recommended): identity of the human who authored
  the manifest
- **authored** (recommended): ISO 8601 date
- **last-modified** (recommended): ISO 8601 date of most recent
  modification
- **ai-assistance** (recommended): description of any AI
  assistance per Charter Article II Section 2.2

Example:

```yaml
provenance:
  author: jane.smith@acme-corp.example
  authored: 2026-05-17
  last-modified: 2026-05-18
  ai-assistance: AI proposed initial checkpoint structure; human
                 reviewed, modified, and approved.
```

## Custom extensions

Consumers may add additional top-level keys to the manifest under
the namespace prefix `x-` to avoid collision with future substrate-
defined keys. Substrate tooling ignores `x-` extensions.

Example:

```yaml
manifest:
  schema-version: 0.1.0
  # standard substrate-defined keys here
  x-acme-corp:
    custom-routing: high-availability
    internal-ticketing-system: jira
```

The `x-` namespace is permanent; the substrate commits never to
define `x-` keys.

## Multi-environment manifests

Consumers with multiple environments (development, staging,
production) may either:

- Maintain separate manifest files per environment
- Use a single manifest with environment-specific overrides

The substrate recommends separate files because environment
boundaries are typically Git-isolated anyway. Single-file overrides
are not specified in the current format; consumers needing this
pattern may propose it for a future format version.

## Manifest references and inheritance

The current format does not support manifest inheritance (one
manifest extending another). Consumers needing inheritance:

- Use YAML's native anchor/alias mechanism for in-file reuse
- Use a templating layer (Helm, Kustomize, Jinja) outside the
  manifest format
- Propose inheritance for a future format version

The format is intentionally simple at this stage. Complexity is
added when it solves real consumer problems.

## Validation

Substrate tooling validates manifests against
`../schemas/manifest.schema.json`. The schema enforces:

- Required top-level keys present
- Field values within allowed enumerations
- `consults` blocks reference valid catalog/rule/mapping/framework
  identifiers (when the substrate version is reachable)
- Provenance fields well-formed

Mechanical validation does not check whether the consumer's
workflow actually fires the declared triggers. That requires
runtime observation, addressed by audit verification per
`consultation-evidence.md`.

## What the format does not specify

- **The format does not specify workflow tooling.** Consumers
  invoke substrate consultation via whatever workflow mechanism
  they use (Git hooks, CI/CD pipelines, AI agent frameworks,
  runtime middleware). The manifest declares what should happen;
  the workflow tooling makes it happen.
- **The format does not specify consultation timing.** A trigger
  may fire synchronously (blocking the workflow) or asynchronously
  (recording the event without blocking). The `blocking` field
  expresses intent; the runtime behavior is consumer's choice.
- **The format does not specify finding routing.** Where findings
  go after being raised (issue tracker, alert system, dashboard)
  is consumer-defined.
- **The format does not specify consumer-side artifact versions.**
  Consumer-side artifacts (custom catalogs, custom profiles)
  referenced by the manifest are versioned by the consumer per
  their own discipline.

## Versioning

This format specification is versioned with the commons. Changes
follow Charter Article VIII versioning discipline.

Current specification version: **0.1.0** (matches commons VERSION)

Breaking changes:

- Adding a new required top-level key
- Removing a top-level key
- Changing the meaning of an existing field
- Removing permitted values from an enumeration

Non-breaking changes:

- Adding optional top-level keys (under `governance-commons:`
  namespace or unprefixed; consumer extensions live under `x-`)
- Adding optional fields within existing blocks
- Adding permitted values to enumerations
- Clarifying field documentation

## Cross-references

- `../CHARTER.md` Article VI (consultation evidence; manifest
  declares what evidence is recorded)
- `../CHARTER.md` Article VII (compatibility; manifest is consumer
  obligation interface)
- `../spec/consultation-evidence.md` (audit obligations the
  evidence block expresses)
- `../spec/extension-contract.md` (consumer-side profile authoring
  the manifest references)
- `../spec/catalog-format.md` (catalog and rule identifier formats
  the manifest references)
- `../schemas/manifest.schema.json` (mechanical validation)
- `../catalogs/` (substrate catalogs the manifest binds to)
- `../profiles/` (substrate profiles the manifest selects)
