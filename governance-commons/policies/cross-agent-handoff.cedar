// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: cross-agent-handoff
// ID: cross-agent-handoff
// Version: 1.0.0
// Maps to: principles.md P5 (Least Privilege)
// Maps to: OWASP ASI07 (Cross-Agent Privilege Escalation), ASI03 (Identity Abuse)
//
// When agents delegate tasks to other agents, capability checks must
// happen at the boundary. An agent cannot request actions that exceed
// its own capabilities by asking another agent to perform them.
//
// This policy treats the Spawn action and inter-agent ToolCall as
// requiring that the spawner's capabilities are a superset of the
// spawned agent's intended capabilities.

// Forbid spawning agents with capabilities the spawner doesn't have.
// The spawner cannot grant privileges it lacks itself - prevents
// privilege escalation through indirection.

forbid (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    // The spawned agent should not have capabilities the spawner
    // hasn't been granted (via its principal human's approvals).
    // Simplified check: each capability in the resource.capabilities
    // must be in the spawner's principal's approvals.
    resource.capabilities.contains("Bash") &&
    !principal.principal.approvals_granted.contains("can_spawn_with_bash")
};

forbid (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    resource.capabilities.contains("ExternalEffect") &&
    !principal.principal.approvals_granted.contains("can_spawn_with_external")
};

forbid (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    resource.capabilities.contains("Delete") &&
    !principal.principal.approvals_granted.contains("can_spawn_with_delete")
};

// Sub-agents cannot spawn other sub-agents at all (avoid nested
// delegation chains that diffuse responsibility).

forbid (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
);

// Production agents may spawn child agents but only if the spawned
// agent's capabilities are a strict subset of the spawner's.

forbid (
    principal is Governance::ProductionAgent,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    // Strict subset check: any capability in the child not in the
    // parent is a violation.
    resource.capabilities.contains("Bash") &&
    !principal.capabilities.contains("Bash")
};

forbid (
    principal is Governance::ProductionAgent,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    resource.capabilities.contains("ExternalEffect") &&
    !principal.capabilities.contains("ExternalEffect")
};

forbid (
    principal is Governance::ProductionAgent,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    resource.capabilities.contains("Delete") &&
    !principal.capabilities.contains("Delete")
};
