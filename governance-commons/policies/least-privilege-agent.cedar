// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: least-privilege-agent
// ID: least-privilege-agent
// Version: 1.0.0
// Maps to: principles.md P5 (Least Privilege for AI)
// Maps to: OWASP LLM06 (Excessive Agency), ASI06 (Rogue Agents)
//
// Sub-agents may only invoke tools that are explicitly listed in
// their capabilities set. Defense against capability sprawl when
// sub-agent configurations grow tools without explicit grants.
//
// Default decision: deny. A sub-agent with no capabilities set
// can do nothing.

permit (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    principal.capabilities.contains(resource.name)
};

// Forbid clause for explicitness: even if some other permit policy
// matches, sub-agents cannot invoke tools outside their capabilities.
// This is belt-and-suspenders defense in depth.

forbid (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
unless {
    principal.capabilities.contains(resource.name)
};

// Production agents follow the same pattern but with the additional
// requirement that the circuit breaker is closed (i.e., the agent
// is not in a degraded state).

permit (
    principal is Governance::ProductionAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    principal.capabilities.contains(resource.name) &&
    principal.circuit_breaker_state == "closed"
};

forbid (
    principal is Governance::ProductionAgent,
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    principal.circuit_breaker_state == "open"
};
