<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Identity Model

Defines the actor types that participate in AI-assisted development and
their trust contracts. This model is referenced by audit events, policy
evaluation, attestation generation, and incident response.

This is one of the most stable concepts in the commons - the categories
of actors change slowly because they reflect fundamentally different
trust relationships, not implementation details.

## Actor types

There are five actor types. Every action recorded in an audit log is
attributed to exactly one.

### `human_user`

A natural person directly issuing instructions through an interactive
interface (terminal, IDE, chat).

**Trust contract**: The human is the principal authority for their
own session. Hooks and policies may block specific actions but the
human cannot be denied general agency over their own work.

**Authentication**: OS user account, IDE login, or session token from
identity provider. The framework does not authenticate the human; it
trusts the OS-level authentication of the session.

**Authorization**: Whatever the OS user account has plus whatever
project-level role-based controls add (e.g., CODEOWNERS, branch
protection).

**Examples**: A developer typing into Claude Code. An engineer
reviewing a PR. A maintainer updating governance commons.

### `ai_dev_tool`

An AI coding assistant operating during development (build-time).
Claude Code, Cursor, GitHub Copilot, Codex, Continue, Aider, etc.

**Trust contract**: Acts on behalf of a `human_user`. Every action is
ultimately attributable to the human who invoked the tool. The tool
itself has no independent authority - it executes the human's
delegated capability.

**Authentication**: The tool authenticates itself to the LLM provider
(API key, session token). The framework does not authenticate the
tool; it trusts the user's choice of tool.

**Authorization**: Restricted to what the human's session can do.
Additionally restricted by hooks (deterministic blocks), rules
(advisory guidance), and tool-specific allow/deny lists.

**Examples**: Claude Code running `/plan`. Cursor in Composer mode.
Copilot generating code in an IDE.

### `ai_sub_agent`

A specialized AI agent spawned by an `ai_dev_tool` for a specific
sub-task. Runs in its own context window. Has its own tool restrictions.

**Trust contract**: Acts on behalf of the spawning `ai_dev_tool`,
which in turn acts on behalf of the `human_user`. Three-link chain
of attribution. Sub-agents are typically more restricted than their
spawner (least privilege).

**Authentication**: Inherited from spawner.

**Authorization**: Subset of spawner's, defined in sub-agent
configuration (e.g., `tools: Read, Grep, Glob, Bash` in a Claude Code
agent definition restricts to read-only).

**Examples**: A code-reviewer sub-agent invoked by `/review`. A
security-reviewer running in isolated context. A research sub-agent
spawned to investigate dependencies before writing code.

### `ci_bot`

An automated system running in continuous integration with no
human-in-the-loop at execution time.

**Trust contract**: Acts on behalf of the policies configured at CI
setup time. Cannot make ad-hoc authorization decisions. Must fail
closed when policies are ambiguous.

**Authentication**: CI platform credentials (GitHub Actions OIDC,
GitLab CI variables, Jenkins service account).

**Authorization**: Defined by CI configuration. Typically read-only
for analysis jobs, scoped-write for deployment jobs.

**Examples**: GitHub Actions running `/review` automatically on PRs.
CI job generating SLSA provenance attestation. Drift detection
running on schedule.

### `production_agent`

An AI agent running in production as part of a deployed system. Takes
autonomous actions against real systems, real data, real users.

**Trust contract**: Acts on behalf of the deploying organization
under policy enforcement. Unlike `ai_dev_tool`, this actor is not
operating under direct human supervision. Every action must be
authorized by runtime policy.

**Authentication**: Production credentials (service account, OIDC
token, etc.).

**Authorization**: Defined by runtime policy engine (Cedar policies
in this commons). Default deny.

**Examples**: A LangGraph multi-agent system in production. An agent
processing customer support tickets. An autonomous trading agent.

**Note**: `production_agent` is defined here for cross-framework
consistency. This build-time framework does not invoke production
agents during development. The runtime governance framework (planned)
will be the primary consumer of `production_agent` semantics.

## Trust chain

Actions flow through chains of attribution:

  human_user → ai_dev_tool → ai_sub_agent → (action)
  human_user → ai_dev_tool → (action)
  human_user → (action)
  ci_bot → (action)
  production_agent → (action)

Audit events capture the full chain when applicable (see
`audit-envelope.md`). This lets reviewers and auditors trace any
action back to the originating principal.

## Why these categories

Five categories may seem arbitrary but each represents a distinct
trust relationship:

| Actor | Direct human supervision? | Authorized at session time or policy time? | Operates in dev or prod? |
|---|---|---|---|
| human_user | Self | Session | Either |
| ai_dev_tool | Yes (interactive) | Session | Dev |
| ai_sub_agent | Yes (transitive) | Session | Dev |
| ci_bot | No | Policy (CI config) | Either |
| production_agent | No | Policy (runtime) | Prod |

These distinctions matter because incident response, audit findings,
and compliance evidence differ per category. "An agent did X" is too
coarse for SOC 2 or EU AI Act Article 12. "A `production_agent`
authorized by runtime policy R-117 did X" is the level of detail
required.

## What this model does not address

- **Multi-tenancy**: This commons does not define how actors map to
 tenants in a multi-tenant deployment. That's a deployment concern
 the consuming framework handles.
- **Delegation between humans**: When one human acts on behalf of
 another (e.g., assistant scheduling meetings), that's outside the
 scope of AI governance.
- **Federation between AI providers**: When an AI tool delegates to
 another AI tool (e.g., Claude Code calls a different LLM via API),
 we treat the called LLM as a sub-component of the `ai_dev_tool`,
 not a separate actor.

## Schema

Actor types follow the vocabulary defined in this document. A dedicated
JSON Schema for actor types is not shipped yet.

## References

- NIST SP 800-162 Attribute-Based Access Control (informs the
 actor/action/resource/context model)
- OAuth 2.0 (informs the delegation chain semantics)
- AWS IAM principal types (informs the human-vs-service-vs-role
 distinction)
- OpenTelemetry resource semantic conventions (informs actor metadata
 in audit events)
