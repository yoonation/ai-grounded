<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Cedar Policy Primitives

Reusable Cedar policy fragments for governance enforcement. These
policies are designed to be composed into project-specific policy
sets, not used standalone.

This directory follows the choice documented in
[../spec/policy-dsl-choice.md](../spec/policy-dsl-choice.md): Cedar
v4.x as the canonical authorization DSL.

## Entity model

All policies in this directory assume a common entity model. Each
consuming framework instantiates these entity types according to its
context.

### Principal types

Principals represent who is taking an action. The types align with
the identity model in [../spec/identity-model.md](../spec/identity-model.md):

    namespace Governance {
        entity Human;
        entity AiDevTool;
        entity AiSubAgent;
        entity CiBot;
        entity ProductionAgent;
    }

A principal of type `Governance::AiSubAgent` has attributes:

- `spawner` (entity reference to the spawning `AiDevTool` or another
  `AiSubAgent`)
- `principal` (entity reference to the originating `Human`, for trust
  chain attribution)
- `capabilities` (set of strings; the actions this sub-agent was
  configured to perform)
- `trust_score` (long, 0-100; degrades on suspicious behavior)

A principal of type `Governance::Human` has:

- `roles` (set of strings; organizational roles like "developer",
  "reviewer", "admin")
- `approvals_granted` (set of strings; ephemeral approvals granted
  this session, e.g., "restricted_read:session-123")

A principal of type `Governance::ProductionAgent` has:

- `version` (string)
- `deployed_by` (entity reference to deploying `Human`)
- `capabilities` (set of strings)
- `circuit_breaker_state` (string: "closed", "open", or "half_open")

### Action types

Actions are what is being attempted:

    namespace Governance {
        action "Read";
        action "Write";
        action "Edit";
        action "Execute";
        action "Spawn";
        action "ToolCall";
        action "ExternalEffect";
        action "Delete";
    }

`ExternalEffect` covers any action with observable consequences
outside the system (network requests, financial transactions, sending
email, etc.). Privileged actions that need extra scrutiny.

### Resource types

Resources are what the action is being taken against:

    namespace Governance {
        entity File;
        entity Tool;
        entity Agent;
        entity Endpoint;
        entity Secret;
    }

`File` resources have:

- `path_hash` (string; never raw path — see audit-envelope redaction)
- `classification` (string; one of "public", "internal",
  "confidential", "restricted", "regulated" per data-classification.md)
- `owner` (entity reference)

`Tool` resources have:

- `name` (string; e.g., "Read", "Edit", "Bash", "WebFetch")
- `category` (string; e.g., "filesystem", "network", "compute")
- `side_effects` (boolean; whether the tool has external effects)

### Context

Context is passed by the policy enforcement point at evaluation time:

- `request_time` (long; unix timestamp)
- `session_id` (string)
- `current_state` (record; engine state at evaluation time)
- `data_residency` (string; geographic region of request origin)
- `mfa_completed` (boolean; whether multi-factor auth was completed)

## How to use these policies

### As a consumer framework

Each Cedar policy in this directory is a fragment. Consumers compose
fragments into project-specific policy sets:

    cat governance-commons/policies/least-privilege-agent.cedar \
        governance-commons/policies/no-pii-access.cedar \
        governance-commons/policies/human-approval-required.cedar \
        my-project/policies/project-specific.cedar \
        > combined-policy.cedar

    cedar validate \
        --schema my-project/policies/schema.cedarschema \
        --policies combined-policy.cedar

The resulting `combined-policy.cedar` is what the consumer's policy
enforcement point loads.

### Policy evaluation flow

A consuming framework invokes the policy engine at decision points:

1. PEP (Policy Enforcement Point) intercepts an action attempt
2. PEP constructs a request: principal + action + resource + context
3. PEP calls the policy engine (Cedar evaluator)
4. Engine returns: `Allow` or `Deny` plus the policies that matched
5. PEP enforces the decision; logs to audit envelope
6. If denied, PEP may surface the deny reason to the user

### Default behavior

Cedar policies are deny-by-default. An action is allowed only when:

- At least one `permit` policy matches the request, AND
- No `forbid` policy matches the request

This means new actors and new actions are denied until explicitly
permitted. Adopt this discipline.

## Schema definition

The schema in [schema.cedarschema](./schema.cedarschema) formalizes
the entity model above. Cedar uses the schema for static validation:
it catches typos in attribute names at policy-compile time rather
than at runtime.

## Policy index

| Policy | Purpose |
|---|---|
| [least-privilege-agent.cedar](./least-privilege-agent.cedar) | Sub-agents can only invoke their explicitly-granted capabilities |
| [no-pii-access.cedar](./no-pii-access.cedar) | Block AI access to Restricted+ data without explicit approval |
| [human-approval-required.cedar](./human-approval-required.cedar) | Require human approval for irreversible actions |
| [tool-allowlist.cedar](./tool-allowlist.cedar) | Per-agent tool restrictions by category |
| [data-residency.cedar](./data-residency.cedar) | Geographic placement enforcement |
| [agent-trust-decay.cedar](./agent-trust-decay.cedar) | Reduce agent capabilities as trust score degrades |
| [cross-agent-handoff.cedar](./cross-agent-handoff.cedar) | Authorize inter-agent capability transfers |
| [no-credential-paths.cedar](./no-credential-paths.cedar) | Block AI access to credential file paths |

## Testing policies

Each `.cedar` file should have a companion `.test.json` with test
cases. Cedar's CLI runs these:

    cedar authorize \
        --schema schema.cedarschema \
        --policies least-privilege-agent.cedar \
        --request-json tests/least-privilege-agent.test.json

For now, test files are not in this initial commit — they are added
as policies are exercised in real consuming frameworks. The pattern
is documented here so future work has a target.

## Versioning policies

Cedar doesn't have native policy versioning. We use a convention:

- Filename suffix `-v1`, `-v2` for incompatible policy revisions
  (when the same policy name means something different)
- Policy ID comments at the top of each policy declare logical version
- Audit log records policy ID and version when decisions are evaluated

A policy revision that changes semantics is a breaking change for
consumers. Mark with `-v2` suffix; keep the original until consumers
migrate.

## Cedar resources

- Cedar language reference: https://docs.cedarpolicy.com
- Cedar GitHub: https://github.com/cedar-policy/cedar
- Cedar CLI: `cargo install cedar-policy-cli` (or via package managers)
- Microsoft Agent Governance Toolkit (uses Cedar):
  https://github.com/microsoft/agent-governance-toolkit

## Anti-patterns

These policy-authoring behaviors cause maintenance and security
problems:

- **Catch-all `permit` policies** — a policy with no `when` clause
  permits all matching principals/actions/resources. Default to
  narrow scope.
- **Negated forbid logic** — `forbid` with complex `when` conditions
  is harder to reason about than positive `permit` policies. Prefer
  `permit` with restrictive `when` clauses.
- **Embedding business logic** — Cedar policies authorize; they
  don't compute. A policy can deny based on a precomputed risk
  score; it shouldn't compute the risk score itself.
- **Hardcoded principal IDs** — policies referencing specific user
  IDs are brittle. Use role-based principal types instead.
- **Time-based conditions in seconds** — clock skew between PEP and
  enforcer creates surprises. Use minute or hour granularity.
- **Policies that depend on missing attributes** — Cedar treats
  missing attributes as evaluation errors. Either require them in
  the schema or check existence with `has`.

## License

Cedar policy text is original work in this commons, licensed
identically to the rest of the framework (see top-level LICENSE).
The Cedar language itself is Apache 2.0 (AWS upstream).
