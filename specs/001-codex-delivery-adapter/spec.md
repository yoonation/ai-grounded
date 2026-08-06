# Feature Specification: Codex Local Delivery Adapter

**Feature Branch**: `001-codex-delivery-adapter`

**Created**: 2026-08-06

**Status**: Implementing

**Input**: Add a first-class local Codex delivery layer while preserving the existing Claude Code delivery and all deterministic governance controls.

## User Scenarios & Testing

### User Story 1 - Run governed work in Codex (Priority: P1)

A developer opens a template-derived repository in Codex and can invoke the
spec-driven workflow, use the appropriate review roles, and rely on the same
event-log and pre-commit enforcement used by Claude Code.

**Independent Test**: In a clean clone with both integrations installed, Codex
discovers the skills and all twelve named review roles; a sample feature can
pass through a checkpoint and the existing pre-commit hook still evaluates it.

**Acceptance Scenarios**:

1. **Given** a trusted local Codex project, **When** a developer starts a
   feature, **Then** `$speckit-*` skills and the Codex agent roster are
   discoverable.
2. **Given** a checkpoint dispatch, **When** review roles run, **Then** their
   artifacts and events follow the existing coordination protocol.

---

### User Story 2 - Retain Claude compatibility (Priority: P1)

A team that already uses Claude Code can update to the template without losing
its skills, agents, hooks, or Git gate behavior.

**Independent Test**: Existing Claude skill-drift and hook tests continue to
pass after the Codex assets are introduced.

**Acceptance Scenarios**:

1. **Given** both integrations are installed, **When** the bootstrap script
   runs, **Then** it verifies both paths without changing the current default
   integration.

---

### User Story 3 - Keep Codex local work constrained (Priority: P2)

A developer receives protections against reading sensitive files, editing the
main branch, and executing destructive commands while using Codex locally.

**Independent Test**: Hook fixtures demonstrate blocked and allowed requests;
the configuration contains denied secret-path rules.

## Requirements

### Functional Requirements

- **FR-001**: The template MUST include trusted-project Codex configuration,
  twelve named custom agents, lifecycle hooks, and Codex-readable skills.
- **FR-002**: Codex agents MUST retain the existing `.claude/agents/*.md`
  prompts as their behavioral source of truth and default to read-only mode.
- **FR-003**: Codex integration MUST coexist with Claude integration; it MUST
  NOT alter the existing default integration.
- **FR-004**: Framework extension commands MUST render to both Claude and
  Codex skill locations and have deterministic drift validation.
- **FR-005**: Codex configuration MUST deny access to environment, credential,
  certificate, key, and secrets files.
- **FR-006**: Documentation and bootstrap checks MUST describe both supported
  delivery paths and their trust/setup requirements.
- **FR-007**: The adapter MUST define and verify a minimum supported Codex CLI
  version before a developer relies on its GPT-5.6 models, custom agents,
  hooks, permission profiles, or Windows sandbox settings.
- **FR-008**: Sensitive-path protection in the Codex permission profile and
  lifecycle policy MUST derive from one reviewed registry and fail closed for
  malformed pre-use hook payloads.
- **FR-009**: On `main`, Codex lifecycle policy MUST deny direct edits and
  shell commands that are not explicitly classified as read-only.

## Success Criteria

- **SC-001**: Twelve Codex agent configurations match the expected names,
  model tiers, efforts, and source prompts.
- **SC-002**: All extension command renders pass dual-target skill-drift
  validation.
- **SC-003**: Policy hook tests cover allowed operations and every blocked
  protection category.
- **SC-004**: Existing repository tests remain green and Git gates remain
  unchanged in behavior.
- **SC-005**: Capability, credential-path, malformed-input, and main-branch
  shell-policy fixtures fail deterministically when their safeguards regress.

## Assumptions

- Local Codex supports trusted project `.codex/` configuration, native skills,
  hooks, and the specified `gpt-5.6-sol` and `gpt-5.6-terra` models.
- If a caller explicitly overrides a child agent's sandbox, the dispatcher
  records a visible warning and continues, rather than claiming enforced
  isolation.
- ChatGPT Work and plugin packaging are outside this feature.
