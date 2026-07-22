<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Audit Event Envelope

Defines the structure of audit log entries emitted by frameworks
consuming this commons. The envelope is aligned with OpenTelemetry
semantic conventions where they exist, and extended for AI-specific
concerns where they do not yet.

## Format

Audit events are written as JSON Lines (JSONL) - one event per line,
each line a complete JSON object. Append-only.

This format was chosen because:

- Universally readable (no install dependency for inspection)
- Append-only matches the immutability semantics of audit logs
- Auditor-friendly (handles in any SIEM, queryable with `jq`)
- Hash-chainable for tamper evidence
- Compatible with OpenTelemetry collectors for shipping to backends

## Envelope schema

Every event has these top-level fields:

  {
   "schema_version": "1.0.0",
   "ts": "2026-05-11T18:32:01.123Z",
   "event_id": "01HXYZW...",
   "session_id": "01HXYAB...",
   "actor": { ... },
   "event_type": "...",
   "subject": { ... },
   "outcome": "...",
   "prev_hash": "sha256:...",
   "this_hash": "sha256:..."
  }

### Field definitions

**`schema_version`** (string, required) - Semver of this envelope
schema. Consumers MUST check this field and fail loudly on unknown
major versions.

**`ts`** (string, required) - ISO 8601 UTC timestamp with millisecond
precision. Always UTC; never local time. Auditors comparing logs
across regions need consistent timezone.

**`event_id`** (string, required) - Globally unique event identifier.
ULID format recommended (lexicographically sortable, embeds
millisecond timestamp). UUIDv7 also acceptable.

**`session_id`** (string, required) - Identifier for the session this
event belongs to. Groups related events. Format same as event_id.
For CI runs, this is the CI run ID. For interactive sessions, it's
generated at session start.

**`actor`** (object, required) - Who took the action. See
[identity-model.md](./identity-model.md) for actor types.

  "actor": {
   "type": "ai_dev_tool",
   "id": "claude-code-1.0.4",
   "principal": {
    "type": "human_user",
    "id": "<github-handle-or-os-username>"
   },
   "spawner": null
  }

The `principal` field captures the human ultimately responsible (the
trust chain root). The `spawner` field, when present, captures the
immediate parent in the trust chain (e.g., for `ai_sub_agent`, the
spawning `ai_dev_tool`).

**`event_type`** (string, required) - What happened. Controlled
vocabulary (see Event types section below).

**`subject`** (object, required) - What the event acted on. Shape
depends on event type, but always includes a `type` field.

  "subject": {
   "type": "file",
   "path_hash": "sha256:...",
   "path_classification": "internal"
  }

Sensitive subject details (file paths, command arguments, parameters)
are hashed or redacted at emit time. See "Redaction" section below.

**`outcome`** (string, required) - `success`, `failure`, `blocked`,
or `partial`.

**`prev_hash`** (string, required) - SHA-256 hash of the previous
event in this log. For the first event in a log, the value is
`"sha256:0000...0000"` (64 zeros). Forms the hash chain for tamper
evidence.

**`this_hash`** (string, required) - SHA-256 hash of the canonical
JSON representation of this event with `this_hash` set to empty
string. Computed at emit time. Verifiable by anyone replaying the
log.

### Optional fields

**`details`** (object, optional) - Event-specific structured data.
Schema varies per event type. Safe for inclusion (no secrets).

**`policy_decision`** (object, optional) - Present when a policy
engine evaluated this action.

  "policy_decision": {
   "policy_id": "no-pii-access",
   "policy_version": "1.2.0",
   "decision": "deny",
   "reason": "subject.path matches pii_pattern"
  }

**`tokens`** (object, optional) - Cost telemetry, when available.

  "tokens": {
   "input": 4123,
   "output": 892,
   "cache_read": 18000,
   "cache_write": 0,
   "model": "claude-opus-4-7"
  }

**`compliance_tags`** (array of strings, optional) - IDs of compliance
controls relevant to this event. Used by `/audit-export` to build
control-mapped evidence reports.

  "compliance_tags": ["SOC2-CC6.1", "NIST-AI-RMF-MEASURE-2.7"]

**`trace_id`** and **`span_id`** (strings, optional) - OpenTelemetry
trace context when the framework integrates with distributed tracing.

## Event types

A controlled vocabulary. Adding new event types is a minor version
bump of this schema.

### Build-time event types (consumed by this framework)

- `session_start` - A user session begins
- `session_end` - A user session ends
- `tool_invocation` - An ai_dev_tool invokes a tool (Edit, Bash, etc.)
- `hook_blocked` - A hook blocked an action
- `policy_evaluated` - A policy was evaluated (may have allowed or
 denied)
- `agent_spawned` - A sub-agent was created
- `agent_completed` - A sub-agent finished
- `command_executed` - A slash command ran
- `spec_created` - A spec was written
- `spec_updated` - A spec was modified
- `review_invoked` - A code review was performed
- `provenance_emitted` - A SLSA attestation was generated
- `framework_warning` - A framework-internal warning (staleness, etc.)

### Runtime event types (reserved for runtime framework)

- `agent_action` - A production agent took an action
- `tool_call` - A production agent called a tool
- `policy_denied` - Runtime policy denied an action
- `circuit_broken` - A circuit breaker fired
- `trust_score_updated` - An agent's trust score changed

These are defined here for forward consistency but not emitted by
build-time consumers.

## Redaction

Audit logs MUST NOT contain raw secrets, raw PII, or unredacted
sensitive paths. Redaction happens at emit time, in the emitter:

- File paths: full path replaced with `sha256(path)` plus classification
 level (see `data-classification.md`)
- Bash command arguments: arguments matching gitleaks/trufflehog
 patterns replaced with `<REDACTED:secret>`
- Environment variable values: never logged; only names
- Function parameters: when audit captures parameters, complex values
 are summarized (length, type) rather than dumped

The redaction rules are enforced by the emitting framework; the
envelope schema cannot enforce them after the fact.

## Two-tier logging

Frameworks consuming this commons SHOULD implement two tiers:

- **`verbose.jsonl`** - captures every action, regardless of
 governance significance. Useful for debugging. Local, gitignored,
 rotated quickly (e.g., 7 days). May contain higher-volume,
 lower-signal entries.
- **`audit.jsonl`** - captures only governance-significant events.
 Goes to auditors. Slower-volume, higher-signal. Retained per
 retention policy (e.g., 90 days for SOC 2 alignment).

Both follow this envelope schema. The split is filtering, not
schema divergence.

## Hash chain verification

Verifying a log's integrity:

1. Read the first event. Confirm `prev_hash` is all-zeros.
2. Compute `sha256` of the first event with `this_hash` field empty.
  Compare to the stored `this_hash`.
3. Read the second event. Confirm its `prev_hash` matches the first
  event's `this_hash`.
4. Compute `sha256` of the second event. Compare to stored.
5. Continue through the log.

Any mismatch indicates tampering or corruption. A small shell script
can do this verification with `jq` and `sha256sum`.

This is symmetric hashing, not asymmetric signing. For higher-assurance
contexts requiring non-repudiation, see Asqav's ML-DSA-65 approach.
Hash chaining is appropriate for build-time audit; cryptographic
signing is appropriate for production-grade runtime audit.

## OpenTelemetry alignment

This envelope follows OpenTelemetry semantic conventions where
possible:

- `ts` aligns with OTel `Timestamp`
- `actor` aligns with OTel `Resource` attributes
- `event_type` aligns with OTel `event.name`
- `trace_id`/`span_id` are OTel native fields
- `tokens` follows the in-progress OTel GenAI semantic conventions

When OTel GenAI conventions stabilize, this envelope will be revised
to match. The migration plan: new schema_version, backward-compatible
transformation script for older logs.

## Schema versioning

This schema follows semver:

- **Patch**: Documentation clarifications, no field changes
- **Minor**: New optional fields, new event types, new outcome values
- **Major**: Breaking changes to existing fields, removal of fields,
 renamed fields

Consumers MUST handle minor version changes by ignoring unknown
optional fields and unknown event types (logging a warning, not
failing).

## Validation

A JSON Schema for this envelope is at
`spec/audit-envelope.schema.json`. Consumers MUST validate emissions
against the schema in CI; failed validation fails the build.

## Anti-patterns

These envelope behaviors create audit problems:

- **Local timestamps** - auditors comparing logs need UTC; mixing
 timezones creates correlation errors
- **Sequential integer IDs** - leaks volume information, creates
 collision risk across distributed emitters; use ULID/UUIDv7
- **Logging raw paths** - see Redaction section; paths can leak PII
 or sensitive directory structures
- **Embedding actual file content** - audit logs are not backups;
 reference content by hash, not value
- **Missing prev_hash on chained logs** - breaks tamper evidence
- **Renaming the schema_version field** - defeats the whole point
 of versioning
