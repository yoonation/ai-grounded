// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: no-credential-paths
// ID: no-credential-paths
// Version: 1.0.0
// Maps to: data-classification.md (Restricted level for credentials)
// Maps to: OWASP LLM02 (Sensitive Information Disclosure), MITRE ATLAS AML.T0055
//
// Block AI access to known credential file patterns. Defense in depth
// beyond classification-based blocking: even if a credential file's
// classification metadata is missing, the path pattern alone triggers
// the block.
//
// This policy operates on Secret resource type, which the consuming
// framework's PEP classifies based on path patterns at evaluation
// time. Common credential paths:
//
// - .env, .env.local, .env.production, etc.
// - secrets/, credentials/, .secrets/
// - *.pem, *.key, *.p12, *.pfx, *.crt
// - .aws/credentials, .ssh/id_rsa, .ssh/id_ed25519
// - 1password-cli temp files, op-cache directories
// - .npmrc, .pypirc (may contain auth tokens)
// - .gnupg/ directory
// - .docker/config.json (may contain registry tokens)

// Forbid any read by AI of Secret resources, period.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent, Governance::CiBot],
    action == Governance::Action::"Read",
    resource is Governance::Secret
);

// Forbid AI from writing to credential paths (preventing AI from
// accidentally writing credentials into wrong location)

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent, Governance::CiBot],
    action in [Governance::Action::"Write", Governance::Action::"Edit"],
    resource is Governance::Secret
);

// Forbid AI from invoking tools whose category is "credential_access"
// (tools like password managers, secret vaults). The human accesses
// these directly; AI never invokes them on the human's behalf.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"ToolCall",
    resource is Governance::Tool
)
when {
    resource.category == "credential_access"
};

// Human principals can access credentials normally (they're the
// owners; this policy only restricts AI principals).
//
// Note: no positive permit for Human + Secret here because that's
// the default OS-level authorization, not something this policy
// engine should override.
