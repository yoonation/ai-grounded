// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: tool-allowlist
// ID: tool-allowlist
// Version: 1.0.0
// Maps to: principles.md P5 (Least Privilege for AI)
// Maps to: OWASP LLM03 (Supply Chain), ASI02 (Tool Misuse)
//
// Restrict which tool categories are accessible by which agent types.
// Provides defense in depth alongside per-capability checks: even if
// a capability is granted, the tool category must still be permitted
// for that principal type.
//
// Tool categories used in this policy (matches Tool.category attribute):
// - "filesystem": Read, Edit, Write, Glob, Grep, etc.
// - "network": WebFetch, WebSearch, etc.
// - "compute": Bash, Execute, code-runners
// - "ai_orchestration": Spawn sub-agents, ToolCall to other agents
// - "destructive": Delete, force operations

// Code-review sub-agents: read-only filesystem operations only.
// This is the canonical pattern: reviewers report, don't modify.
//
// Sub-agents matching this pattern have name starting with "reviewer"
// in their parent agent's spawn configuration.

forbid (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    principal.capabilities.contains("reviewer_role") &&
    resource.category != "filesystem"
};

forbid (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    principal.capabilities.contains("reviewer_role") &&
    resource.side_effects == true
};

// CI bots: filesystem and network reads only, no compute beyond
// the bot's defined scope, no destructive actions.

forbid (
    principal is Governance::CiBot,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    resource.category == "destructive"
};

forbid (
    principal is Governance::CiBot,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    resource.category == "compute" &&
    resource.side_effects == true
};

// Production agents: deny compute category by default unless the
// agent's deployer explicitly granted compute capabilities.

forbid (
    principal is Governance::ProductionAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    resource.category == "compute"
}
unless {
    principal.capabilities.contains("compute_authorized")
};

// AI dev tools: allow all tool categories the human principal has
// access to. Constrained by other policies (no-pii-access,
// human-approval-required, etc).

permit (
    principal is Governance::AiDevTool,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    resource.category == "filesystem" ||
    resource.category == "network" ||
    resource.category == "compute" ||
    resource.category == "ai_orchestration"
};

// Destructive category requires explicit capability grant even for
// AI dev tools.

forbid (
    principal is Governance::AiDevTool,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    resource.category == "destructive"
}
unless {
    principal.principal.approvals_granted.contains("destructive_tools")
};
