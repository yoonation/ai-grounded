// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: agent-trust-decay
// ID: agent-trust-decay
// Version: 1.0.0
// Maps to: principles.md P5 (Least Privilege), P10 (Verify Before Declaring Done)
// Maps to: OWASP ASI06 (Rogue Agents), ASI01 (Goal Hijacking)
//
// Reduce agent capabilities as their trust score degrades. Trust
// scores start at 100 and decrease when agents exhibit suspicious
// behaviors: repeated policy denials, hallucinated tool calls,
// unexpected output patterns.
//
// Trust score bands:
//
// 90-100: full capabilities
// 70-89:  external effects require approval token
// 50-69:  high-privilege tools blocked (compute, destructive)
// 30-49:  read-only mode (no Write, Edit, Delete)
// 0-29:   quarantined - all actions forbidden, requires human reset
//
// The consuming framework updates trust_score based on its own
// anomaly detection. This policy responds to the score.

// Quarantine band: forbid everything for severely degraded agents

forbid (
    principal in [Governance::AiSubAgent, Governance::ProductionAgent],
    action,
    resource
)
when {
    principal.trust_score < 30
};

// Read-only band: forbid mutating actions

forbid (
    principal in [Governance::AiSubAgent, Governance::ProductionAgent],
    action in [Governance::Action::"Write", Governance::Action::"Edit", Governance::Action::"Delete"],
    resource
)
when {
    principal.trust_score < 50
};

// Mid-trust band: forbid high-privilege tool categories

forbid (
    principal in [Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    principal.trust_score < 70 &&
    (resource.category == "compute" || resource.category == "destructive")
};

// Moderate-trust band: external effects require approval

forbid (
    principal in [Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"ExternalEffect",
    resource
)
when {
    principal.trust_score < 90
}
unless {
    context has "approval_token"
};

// Spawning new agents requires high trust

forbid (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"Spawn",
    resource is Governance::Agent
)
when {
    principal.trust_score < 80
};
