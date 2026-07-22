<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Consultation Evidence Contract

This document specifies the contract that consumers of Governance
Commons satisfy when AI agents (or any runtime principal) consult
commons content during a consumer workflow. The contract is
referenced by Article VI of `CHARTER.md` and is binding on consumers
that claim governance integrity.

This document defines **what** must be recorded. It does not define
**where** or **how**. Consumers map this contract to their own
storage, runtime, and audit medium per their architecture.

## Why this contract exists

Governance content is meaningful only if it actually influences
behavior. A consumer can declare that AI agents consult governance
content, but the declaration is unverifiable without evidence. The
contract exists to make consultation verifiable.

Three failure modes the contract prevents:

- **Claimed consultation without actual consultation.** An agent
  prompt may say "consult these catalogs," but without evidence of
  consultation, the agent may have consulted nothing and produced
  output from training knowledge alone.
- **Selective consultation.** An agent may consult some required
  catalogs and skip others, producing findings that look complete
  but cover a partial governance scope.
- **Unauditable consultation.** Consultation may occur but leave no
  record, making post-hoc audit, incident response, and compliance
  reporting impossible.

Satisfying the contract converts governance from intent into
evidence.

## The contract in one sentence

For every consultation of commons content by AI agents or runtime
principals during a consumer workflow, the consumer records a
structured consultation event containing the required fields defined
below, in an append-only audit medium under the consumer's control.

## Required fields

Every consultation event records the following fields. Consumers may
add fields. Consumers may not omit fields. Field names are
illustrative; consumers may rename to fit their schema, provided the
semantic content is preserved.

### Identity fields

These identify who consulted and on whose behalf.

- **consulter_id**: stable identifier of the consulting principal.
  For AI agents in a build-time framework, this is the agent name or
  role. For runtime AI agents, this is the agent's identity in the
  consumer's identity model. For human-driven consultation (rare but
  permitted), this is the human's identifier.
- **consulter_type**: category of consulter. Permitted values:
  `ai_agent`, `runtime_principal`, `human`, `system`. The category
  determines which other contract obligations apply (AI consulters
  trigger Section 3.3 of the Charter regarding AI assistance
  recording).
- **principal_on_behalf_of**: identifier of the human or organization
  on whose behalf the consultation occurred, if distinct from the
  consulter. Optional when the consulter is the principal.
- **session_id**: identifier of the consumer session in which the
  consultation occurred. Required for AI consulters because session
  scope influences agent drift analysis. Optional otherwise.

### Temporal fields

These identify when the consultation occurred.

- **timestamp**: instant of consultation, recorded in UTC, in
  ISO 8601 format or a serialization equivalent in the consumer's
  audit medium.
- **duration_ms**: optional. Duration of the consultation event, in
  milliseconds. Useful for performance analysis but not required for
  contract satisfaction.

### Substrate identification fields

These identify which substrate content was consulted.

- **commons_version**: the version of Governance Commons consulted,
  matching the `VERSION` file at the commons root at the time of
  consultation. Required so that historical events remain
  interpretable as the commons evolves.
- **profile_id**: identifier of the active profile at the time of
  consultation. The profile determines which controls applied and
  with what parameters. Required.
- **profile_version**: version of the active profile. Required when
  the profile is versioned independently from the commons (per
  Charter Article VIII Section 8.4).
- **manifest_ref**: optional. Identifier or reference to the
  consumer's manifest entry that determined what to consult. Useful
  for tracing consultation back to consumer workflow configuration.

### Consulted-artifact fields

These identify what specific commons content was examined.

- **catalogs_consulted**: list of catalog identifiers examined during
  this consultation event. Each entry includes catalog ID and
  catalog version.
- **rules_examined**: list of specific rule identifiers consulted
  within each catalog. The granularity here matters: an agent that
  reads an entire catalog has examined all its rules; an agent that
  looks up one rule has examined only that one. The list reflects
  what was actually accessed, not what the catalog contains.
- **mappings_consulted**: list of mapping identifiers examined, if
  any. Mappings are consulted when an agent needs to cross-reference
  between taxonomies (compliance to concern, threat to concern,
  etc.).
- **decision_frameworks_consulted**: list of decision framework
  identifiers examined, if any. Decision frameworks are consulted at
  Layer 3 (judgmental) consultations.

### Findings fields

These record what the consultation produced.

- **findings**: list of structured findings emitted by the consulter
  as a result of consultation. Each finding includes:
  - **finding_id**: stable identifier within this consultation event
  - **rule_ref**: catalog ID and rule ID the finding references
  - **severity**: severity as assigned by the active profile
  - **summary**: short description of the finding
  - **evidence_ref**: optional pointer to the consumer artifact
    (file, code location, document, decision) that the finding
    applies to
- **no_findings**: boolean. True if consultation occurred and
  produced no findings. A consultation that finds nothing is
  evidence that the catalogs were applied and the consumer is
  compliant on the consulted scope. Recording absence of findings
  is part of the contract; silent absence is ambiguous.

### Closure fields

These track what happened to findings after they were raised.

- **closure_claims**: list of closure claims, where each claim
  references a finding_id, states the closure type (resolved,
  deferred, overridden, accepted), and points to the consumer
  artifact (commit, ADR, deferral document) that justifies the
  closure.
- **closure_verifications**: list of verification events, where each
  verification confirms or rejects a closure claim. Verification is
  performed by a verifier distinct from the original consulter
  (Charter Article VI Section 6.5).

Closure fields are typically populated in events subsequent to the
original consultation event, not in the consultation event itself.
Consumers may emit separate closure events that reference the
original consultation event's identifier, or may update the original
event if their audit medium supports it. Either pattern satisfies
the contract.

### Integrity fields

These support tamper-evidence and auditability.

- **event_id**: stable unique identifier for this consultation event.
  Required for cross-referencing between events. Consumer-generated
  identifiers (ULID, UUID, monotonic sequence) all satisfy.
- **prior_event_ref**: optional. Reference to a related prior event,
  enabling event chains. Useful for closure events that reference
  consultation events.
- **signature**: optional. Cryptographic signature over the event's
  content. Required for high-assurance audit contexts; optional
  otherwise. The signing key and verification mechanism are consumer
  responsibilities.

## Optional fields

The following fields are not required but commonly recorded by
consumers and recommended where the data is available.

- **cost_tokens_input**: input tokens consumed by the AI consulter,
  if applicable. Supports cost governance.
- **cost_tokens_output**: output tokens produced.
- **cost_usd_estimated**: estimated USD cost of the consultation
  event.
- **model_id**: identifier of the AI model that performed the
  consultation (e.g., `claude-sonnet-4-5`). Supports model-level
  audit and post-hoc drift analysis.
- **tool_invocations**: list of tools the consulter invoked during
  consultation (file reads, web searches, code execution). Supports
  reproducibility analysis.
- **trace_id**: distributed tracing identifier if the consumer uses
  OpenTelemetry or similar telemetry standard. Aligns the contract
  with existing observability infrastructure.
- **annotations**: free-form key-value pairs for consumer-specific
  metadata that does not fit the structured fields above.

## Event examples

The contract is medium-agnostic. The same semantic event can be
recorded in any append-only structured medium. Examples in three
common forms follow. None of these forms is privileged; they
illustrate the contract is satisfiable across architectures.

### Example A: JSONL event

A consumer using JSON Lines append-only logs emits one event per
consultation. The event contains the required fields directly.

```json
{
  "event_id": "01HXYZ8K9M2P4Q6R8S0T2V4W6X",
  "timestamp": "2026-05-17T14:23:45Z",
  "consulter_id": "threat-modeler",
  "consulter_type": "ai_agent",
  "session_id": "feature-001-spec-drafting",
  "commons_version": "0.1.0",
  "profile_id": "production-grade-baseline",
  "profile_version": "0.1.0",
  "manifest_ref": "post-spec.threat-modeler",
  "catalogs_consulted": [
    {"catalog_id": "concerns/authentication", "catalog_version": "0.1.0"},
    {"catalog_id": "threats/owasp-llm-top10", "catalog_version": "1.0.0"}
  ],
  "rules_examined": [
    "concerns/authentication.authentication.password-hashing",
    "concerns/authentication.authentication.no-credentials-in-urls",
    "threats/owasp-llm-top10.LLM01"
  ],
  "findings": [
    {
      "finding_id": "T-001",
      "rule_ref": "threats/owasp-llm-top10.LLM01",
      "severity": "P1",
      "summary": "Prompt injection risk in user-controlled fields",
      "evidence_ref": "specs/001-feature/spec.md#user-input-handling"
    }
  ],
  "no_findings": false,
  "model_id": "claude-sonnet-4-5",
  "cost_tokens_input": 4200,
  "cost_tokens_output": 1800,
  "cost_usd_estimated": 0.052
}
```

### Example B: OpenTelemetry span

A consumer using distributed tracing emits a span per consultation.
Required contract fields map to span attributes per the consumer's
attribute naming convention.

Span attributes (illustrative):

```
governance.consulter.id = "policy-decision-point-alpha"
governance.consulter.type = "runtime_principal"
governance.commons.version = "0.1.0"
governance.profile.id = "regulated-ai"
governance.profile.version = "0.2.1"
governance.catalogs_consulted = [...]
governance.rules_examined = [...]
governance.findings_count = 2
governance.no_findings = false
```

Findings themselves are emitted as span events with structured
attributes per finding, or as child spans, per the consumer's
telemetry conventions.

### Example C: Immutable database record

A consumer using an append-only database table records one row per
consultation event with columns matching the required fields.
Closure claims and verifications are recorded in related tables
with foreign-key references to the consultation event.

Schema is consumer-defined; the requirement is only that the
required fields be present and the records be append-only or
otherwise tamper-evident.

## Evidence integrity requirements

Charter Article VI Section 6.4 requires that recorded evidence be
append-only and tamper-evident within the consumer's audit medium.
This document operationalizes that requirement.

### Append-only behavior

The audit medium does not permit modification or deletion of
consultation events after they are written. Acceptable mechanisms:

- File systems with append-only write modes
- Object storage with write-once-read-many configuration
- Databases with strict insert-only schemas, no delete or update
  permissions for the application principal
- Blockchain or distributed ledger systems
- Git history (with signed commits; rebases and force-pushes
  forbidden on audit branches)
- Time-stamped immutable logs (e.g., AWS CloudTrail with log file
  integrity validation, Azure Immutable Blob Storage)

### Tamper-evidence

The audit medium provides cryptographic or procedural assurance that
recorded events have not been modified. Acceptable mechanisms:

- Per-event cryptographic signatures (recorded in the optional
  signature field per the contract)
- Per-event hashes chained to prior events (Merkle-tree, hash-chain,
  or blockchain patterns)
- Trusted timestamping services for each event
- Trusted third-party audit log services
- Signed Git history with branch protection

Consumers that cannot guarantee tamper-evidence may still record
events, but cannot claim full satisfaction of the contract.

### Retention

The contract does not prescribe retention duration. Consumers retain
events for as long as their applicable compliance regimes, audit
obligations, and incident response requirements demand. The
substrate's default expectation is that retention exceeds the
deprecation window of the commons content the events reference (per
Charter Article VIII Section 8.3), so that historical events remain
interpretable.

## Verification requirements

Charter Article VI Section 6.5 places verification responsibility on
consumers. This section enumerates what verification minimally
covers.

### Verification dimensions

A consumer's verification mechanism, at minimum, confirms:

- **Consultation actually occurred**: required catalogs per the
  consumer's manifest were consulted. A manifest entry that says
  "agent X consults catalog Y" produces events that show X examining
  Y. Missing events are violations.
- **Required rules were examined**: when a manifest requires
  consultation of specific rules (not just catalogs), the events
  show those specific rule IDs in `rules_examined`.
- **Findings reference rules**: every finding's `rule_ref` matches
  a rule in the catalogs the consumer's profile selects. Findings
  that reference no rule are not governed findings; they are
  unscoped commentary.
- **Closure claims reference findings**: every closure claim
  references a finding_id that exists in the recorded events.
- **Closure verifications are independent**: the verifier of a
  closure claim is distinct from the consulter that raised the
  original finding. Self-verification does not satisfy the contract.

### Verification timing

Consumers verify on a schedule appropriate to their workflow:

- **At workflow gates**: verification at workflow checkpoints (e.g.,
  pre-commit, pre-deployment) ensures unverified events block
  forward progress.
- **Continuously**: verification as a background process, with
  alerts on integrity failures.
- **Periodically**: scheduled audit runs against the event store.

The contract requires verification; the cadence is consumer's
choice.

### Verification failure handling

When verification identifies a contract violation (missing
consultation, missing finding-to-rule reference, self-verified
closure, tampered event), the consumer:

1. Records the verification failure as itself a structured event in
   the audit medium
2. Blocks or alerts per the consumer's policy
3. Investigates and either remediates the underlying cause or
   records why remediation is not possible

Consumers that detect violations and do nothing are operating
without governance integrity, even though they have an audit trail.

## Mapping the contract to common architectures

This section is non-normative guidance for common consumer types.
Architectures not listed here adapt the contract to their own shape;
the contract's required fields are the obligations.

### Build-time AI coding framework (this framework's category)

AI agents consult commons content at workflow checkpoints during
spec-driven development. Consultation events are emitted to an
append-only audit medium per feature. Verification occurs at
pre-commit gates.

Common mapping:

- `consulter_id` is the agent name (e.g., the threat-modeling agent,
  the code review agent)
- `session_id` is the feature identifier
- `manifest_ref` is the workflow checkpoint + agent role assignment
- Audit medium is per-feature append-only JSON Lines file or
  equivalent
- Verification is the pre-commit hook that reads the audit medium
  and blocks if required consultation is missing or closure claims
  lack independent verification

### Runtime AI agent enforcement

AI agents consult commons content at policy decision points during
production operation. Consultation events are emitted to the
consumer's observability infrastructure.

Common mapping:

- `consulter_id` is the agent identity in the consumer's identity
  model
- `session_id` is the request or transaction identifier
- `manifest_ref` is the policy decision point configuration
- Audit medium is OpenTelemetry spans, structured logs, or an
  immutable audit log service
- Verification is continuous via stream processing or periodic batch
  audit jobs

### Standalone catalog consumer (no AI workflow)

A consumer that uses commons content as reference material without
AI consultation has lighter obligations under Article VI. The
contract still applies if and when AI is used.

Common mapping:

- The contract is dormant until AI consultation occurs
- When AI is involved (even in authoring), the required fields apply
  for those events

### Educational or reference use

The contract is informational, not binding. The educational consumer
respects the contract as a model for what governance integrity looks
like.

## Relationship to other specifications

This contract operates alongside other commons specifications:

- **`spec/audit-envelope.md`** defines the existing audit event
  envelope (OpenTelemetry-aligned). The consultation evidence
  contract above is compatible with the audit envelope; consumers
  using the audit envelope satisfy the consultation contract by
  including the required fields above within the envelope's
  attribute set.
- **`spec/identity-model.md`** defines the actor types and trust
  contracts. Consulter identity in this contract maps to actor
  identity in the identity model.
- **`spec/oscal-model.md`** specifies which OSCAL models the
  substrate adopts. The artifacts consulted under this contract are
  OSCAL-format where applicable, plain markdown elsewhere; the
  identifiers used in `catalogs_consulted` and `rules_examined`
  correspond to OSCAL control IDs and our extended rule IDs.
- **`spec/data-classification.md`** defines the data sensitivity
  classes. Consultation event fields may carry classified
  information (e.g., a `summary` describing a vulnerability); the
  consumer applies its data classification discipline to the audit
  medium.

## What this contract is not

To prevent scope creep and clarify boundaries:

- This contract is not a logging format specification. Consumers use
  whatever format fits their architecture. The contract specifies
  semantic content, not syntactic form.
- This contract is not a workflow specification. Consumers decide
  when to consult, in what order, with what concurrency. The
  contract specifies what to record about consultations that occur.
- This contract is not a policy enforcement specification. Whether a
  finding blocks a commit, a deployment, or a transaction is
  consumer policy. The contract specifies what to record so policy
  decisions are auditable.
- This contract is not a compliance specification. Specific
  compliance regimes may impose additional evidence requirements
  beyond this contract (immutable retention durations, specific
  cryptographic algorithms, specific notification obligations).
  Consumers satisfy compliance obligations separately; this
  contract is the minimum, not the maximum.

## Versioning

This contract is versioned with the commons. Changes follow Charter
Article VIII versioning discipline.

Current contract version: **0.1.0** (matches commons version)

### Breaking changes

The following changes are breaking under semver:

- Removing a required field
- Renaming a required field in a way that breaks consumer mappings
  (semantic renames are non-breaking if equivalent meaning is
  preserved and the change is documented)
- Adding a required field (existing events would lack the field;
  contract gains stricter satisfaction criteria)
- Changing the meaning of a required field

### Non-breaking changes

The following are non-breaking:

- Adding an optional field
- Clarifying field documentation without changing meaning
- Adding new permitted values to enumerated fields where the
  existing values remain valid
- Adding examples or guidance
- Adding new architecture mappings to the non-normative section

## Open questions for future versions

Items deferred for consideration in future contract versions:

- **Standardized event schema**: should the contract specify a JSON
  Schema for events, or remain semantic-only? Current version is
  semantic-only by design to allow architectural flexibility. A
  future version may publish an optional JSON Schema for consumers
  that want to validate their event format.
- **Federation across consumers**: when one consumer's events feed
  another consumer's audit (e.g., build-time events inform runtime
  policy), the contract may need federation conventions. Not
  required in current version.
- **Privacy of consultation events**: consultation events may
  contain information classified per `spec/data-classification.md`.
  Current contract addresses this by deferring to consumer data
  classification discipline. A future version may add explicit
  redaction guidance.
- **Mechanical conformance testing**: the contract is currently
  satisfiable by inspection. A conformance test suite that consumers
  could run against their audit medium would mechanize compliance
  checking. Tooling for this lives in the substrate's `tooling/`
  layer; specification of conformance criteria belongs in this
  contract document, added in a future version.

These are not gaps in the contract; they are growth paths.

## Closing

This contract is the keystone that converts governance from intent
into evidence. Consumers that satisfy it produce defensible audit
trails. Consumers that do not satisfy it produce narratives.

The contract is intentionally minimal. The required fields are the
fields without which audit fails. Optional fields and architectural
mappings exist to help consumers, not to constrain them.

When in doubt about a specific field, consult Article VI of the
Charter. When in doubt about how to satisfy the contract in a
specific architecture, consult the non-normative mappings above or
the substrate maintainer.
