// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: human-approval-required
// ID: human-approval-required
// Version: 1.0.0
// Maps to: principles.md P9 (One-way doors get specs), P5 (Least Privilege)
// Maps to: EU AI Act Art 14 (Human oversight)
// Maps to: OWASP LLM06 (Excessive Agency), ASI09 (Inadequate Human Oversight)
//
// Irreversible actions require explicit human approval. The approval
// token is session-scoped and includes the action category to prevent
// approval bleed between unrelated decisions.
//
// Categories of irreversible actions:
// - Delete on any file resource
// - ExternalEffect on financial, communication, or production endpoints
// - Spawn of agents with elevated capabilities

// Delete requires approval token regardless of classification.
// Even Public files: deletion is irreversible.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"Delete",
    resource is Governance::File
)
unless {
    context has "approval_token" &&
    context.approval_token == "delete:" + context.session_id + ":" + resource.path_hash
};

// External effects on production endpoints require approval.
// Endpoints flagged as external = true represent observable consequences
// outside the system: API calls, emails, payments, etc.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"ExternalEffect",
    resource is Governance::Endpoint
)
when {
    resource.external == true
}
unless {
    context has "approval_token" &&
    context.approval_token == "external_effect:" + context.session_id + ":" + resource.url_hash
};

// Specific category: financial endpoints require MFA-completed
// approval. Even if approval token is present, MFA must have happened
// this session.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"ExternalEffect",
    resource is Governance::Endpoint
)
when {
    resource.category == "financial"
}
unless {
    context.mfa_completed == true &&
    context has "approval_token" &&
    context.approval_token == "financial:" + context.session_id + ":" + resource.url_hash
};

// Spawning sub-agents with capabilities including "Bash" or "Execute"
// requires approval. These are the most privilege-rich capabilities
// and should be intentional grants.

forbid (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    resource.capabilities.contains("Bash") ||
    resource.capabilities.contains("Execute")
}
unless {
    context has "approval_token" &&
    context.approval_token == "spawn_privileged:" + context.session_id + ":" + resource.name
};
