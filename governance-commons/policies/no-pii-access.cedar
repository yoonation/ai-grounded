// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: no-pii-access
// ID: no-pii-access
// Version: 1.0.0
// Maps to: data-classification.md (Restricted and Regulated levels)
// Maps to: GDPR Art 32, HIPAA 164.312, SOC2 CC6.7
// Maps to: OWASP LLM02 (Sensitive Information Disclosure)
//
// Block AI access to data classified Restricted or higher without
// explicit approval token in the session. Regulated level cannot
// be accessed by AI at all.
//
// Approval tokens are session-scoped strings of the form
// "<classification>_<action>:<session_id>" that the human grants
// per-file, per-session.

// Public and Internal data: allow read for AI tools.
// This is the common case for source code, public docs, etc.

permit (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Read",
    resource is Governance::File
)
when {
    resource.classification == "public" ||
    resource.classification == "internal"
};

permit (
    principal is Governance::AiSubAgent,
    action == Governance::Action::"Read",
    resource is Governance::File
)
when {
    resource.classification == "public" ||
    resource.classification == "internal"
};

// Confidential data: requires session-level approval from principal.
// The principal (human) must have granted the "confidential_read"
// approval at session start or per-request.

permit (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Read",
    resource is Governance::File
)
when {
    resource.classification == "confidential" &&
    principal.principal.approvals_granted.contains("confidential_read")
};

// Restricted data: requires file-specific approval token.
// The PEP constructs the token as
// "restricted_read:<session_id>:<resource.path_hash>" and the human
// must have granted that exact token.

permit (
    principal is Governance::AiDevTool,
    action == Governance::Action::"Read",
    resource is Governance::File
)
when {
    resource.classification == "restricted" &&
    principal.principal.approvals_granted.contains(
        "restricted_read:" + context.session_id + ":" + resource.path_hash
    ) &&
    context.mfa_completed
};

// Regulated data: forbid AI access entirely. No approval token
// override possible. If AI assistance is needed for code that
// processes regulated data, it works against synthetic test data.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"Read",
    resource is Governance::File
)
when {
    resource.classification == "regulated"
};

// Write operations on Restricted or Regulated: forbid AI entirely.
// AI can read with approval; AI never writes data at these levels.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action in [Governance::Action::"Write", Governance::Action::"Edit", Governance::Action::"Delete"],
    resource is Governance::File
)
when {
    resource.classification == "restricted" ||
    resource.classification == "regulated"
};
