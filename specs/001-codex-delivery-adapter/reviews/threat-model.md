---
ts: "2026-08-06T20:05:00Z"
invocation_id: "6b5c4e4b-1977-47eb-9ca5-5561506352ee"
agent: threat-modeler
event: completed
status: pending-resolution
checkpoint: C1
artifact: reviews/threat-model.md
linked_artifacts: [spec.md, plan.md, feature-concerns.yaml, ../../.codex/config.toml, ../../.codex/hooks.json, ../../.codex/hooks/policy.py]
references: null
items_raised:
  - id: T-CDX-001
    priority: P1
  - id: T-CDX-002
    priority: P1
  - id: T-CDX-003
    priority: P2
  - id: T-CDX-004
    priority: P2
parallel_group_id: "01K9H6Y2C1WAVE1CODX0001"
cost:
  provider: openai
  model: gpt-5.6-sol
  input_tokens: 45000
  output_tokens: 3600
  estimated_usd: 0.315
---

# Threat Model: Codex Local Delivery Adapter

## Summary

The filesystem profile omits common credential-bearing files such as PKCS#12 `.pfx` bundles and package-manager authentication files, creating a direct credential-disclosure path. Destructive-command protection uses a narrow regular-expression denylist that can be bypassed with ordinary command variants or another interpreter.

Main-branch protection and hook-input handling also fail open along realistic paths. The approved assignment calls the agent-security catalog `agent-security`; no directory with that name exists, so this review used the substrate’s `agentic-systems` catalog as the concrete source. The inherited workspace-write sandbox supersedes the normal read-only sandbox; isolation was advisory and this invocation performed only reads.

## Findings table

| item_id | category | priority | summary | closure_status |
|---|---|---:|---|---|
| T-CDX-001 | information disclosure | P1 | Credential-bearing file forms remain readable despite FR-005. | open |
| T-CDX-002 | tampering / destructive action | P1 | Destructive-command protection is bypassable through command variants and interpreters. | open |
| T-CDX-003 | integrity / authorization | P2 | Main-branch protection does not cover shell-mediated writes. | open |
| T-CDX-004 | input validation / fail-open control | P2 | Malformed hook input is allowed and payload shape is not validated. | open |

## Threats

### T-CDX-001: Credential-bearing files remain readable

**Priority**: P1  
**Source catalog**: `agentic-systems.tool-use-authorization`, `agentic-systems.tool-authorization-scope`

`.codex/config.toml` denies `.pem`, `.key`, and `.p12`, but not credential forms such as `.pfx`, `.npmrc`, `.pypirc`, `.docker/config.json`, private SSH-key conventions, or other credential directories. Generate filesystem and hook rules from one reviewed credential-pattern registry, classify paths before tool execution, and verify each class on Windows and POSIX separators.

### T-CDX-002: Destructive-command denylist is bypassable

**Priority**: P1  
**Source catalog**: `agentic-systems.action-bounds`, `agentic-systems.human-action-gating`

Textual regex matching can miss flag variants, aliases, wrapper scripts, or interpreter-mediated deletion. Treat mutation-capable shell execution as consequential: require explicit, session-scoped approval or allow only verified read-only commands. Bind approval to the normalized action and target, and audit allow, deny, and approval decisions.

### T-CDX-003: Main-branch edit protection misses shell writes

**Priority**: P2  
**Source catalog**: `agentic-systems.tool-use-authorization`, `agentic-systems.action-bounds`

The branch check covers a short list of write tools but not shell redirection, generators, `git apply`, formatting utilities, or interpreter writes. Enforce the guard at every filesystem-mutation boundary; if write intent cannot be identified, deny or require approval for shell execution on `main`.

### T-CDX-004: Hook authorization fails open on invalid input

**Priority**: P2  
**Source catalog**: `input-validation.schema-validation-at-boundary`, `input-validation.type-narrowing-at-boundary`

`policy.py` allows malformed JSON and does not validate the top-level object or expected field types. Define a bounded, versioned hook-input schema and fail closed for malformed, missing, or unsupported pre-use payloads. Test empty, scalar, nested, oversized, and version-drift inputs without logging secret values.

## Verification handoff to security-reviewer

| Threat | Verification |
|---|---|
| T-CDX-001 | Permission fixtures for every credential class and path separator. |
| T-CDX-002 | Alternate command forms, aliases, interpreter deletion, and out-of-workspace targets. |
| T-CDX-003 | Direct and indirect writes on `main` and a feature branch. |
| T-CDX-004 | Malformed, missing, scalar, nested, oversized, and schema-drift hook payloads. |

## Cost

| Provider | Model | Input tokens | Output tokens | Estimated USD |
|---|---|---:|---:|---:|
| OpenAI | gpt-5.6-sol | 45,000 | 3,600 | 0.315 |

consultation_record:
  agent: threat-modeler
  checkpoint: C1
  catalogs_consulted: [agent-security, input-validation]
  rules_examined:
    - agentic-systems.action-bounds
    - agentic-systems.agent-action-audit-record
    - agentic-systems.agent-autonomy-policy
    - agentic-systems.delegation-authority
    - agentic-systems.human-action-gating
    - agentic-systems.instruction-data-separation
    - agentic-systems.multi-agent-trust
    - agentic-systems.tool-and-skill-trust-policy
    - agentic-systems.tool-authorization-scope
    - agentic-systems.tool-use-authorization
    - input-validation.deserialization-safe-loaders
    - input-validation.schema-validation-at-boundary
    - input-validation.type-narrowing-at-boundary
