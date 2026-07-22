// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Myoung Hong


// Policy: data-residency
// ID: data-residency
// Version: 1.0.0
// Maps to: GDPR (EU data sovereignty), data residency regulations
// Maps to: EU AI Act Art 10 (Data governance)
// Maps to: data-classification.md (Regulated level)
//
// Enforce geographic placement constraints on data access. Different
// data classifications have different residency requirements:
//
// - Regulated EU data: must stay in EU regions
// - Regulated US-CUI data: must stay in US regions
// - Restricted financial data: jurisdiction-specific
//
// The Endpoint's data_residency context value reflects where the
// request originated; resources have implicit residency via their
// classification.

// EU GDPR data (subset of Restricted classification representing
// EU personal data): forbid access from non-EU regions.

forbid (
    principal in [Governance::Human, Governance::AiDevTool, Governance::AiSubAgent, Governance::CiBot, Governance::ProductionAgent],
    action in [Governance::Action::"Read", Governance::Action::"Write", Governance::Action::"Edit"],
    resource is Governance::File
)
when {
    resource.classification == "restricted" &&
    context.data_residency != "eu-west" &&
    context.data_residency != "eu-central" &&
    context.data_residency != "eu-north" &&
    context.data_residency != "eu-south"
};

// US CUI (Controlled Unclassified Information) - subset of Regulated
// classification: forbid access from non-US regions.

forbid (
    principal in [Governance::Human, Governance::AiDevTool, Governance::AiSubAgent, Governance::CiBot, Governance::ProductionAgent],
    action in [Governance::Action::"Read", Governance::Action::"Write", Governance::Action::"Edit"],
    resource is Governance::File
)
when {
    resource.classification == "regulated" &&
    context.data_residency != "us-east" &&
    context.data_residency != "us-west" &&
    context.data_residency != "us-gov"
};

// External effect endpoints in EU regions: deny if request origin
// is non-EU. Prevents data exfiltration via API calls.

forbid (
    principal in [Governance::AiDevTool, Governance::AiSubAgent, Governance::ProductionAgent],
    action == Governance::Action::"ExternalEffect",
    resource is Governance::Endpoint
)
when {
    resource.category == "eu_data_processor" &&
    context.data_residency != "eu-west" &&
    context.data_residency != "eu-central"
};

// Allow when residency matches: this is the primary positive policy.
// Other policies (no-pii-access, etc.) still apply, but this one
// confirms the residency requirement is met.

permit (
    principal in [Governance::AiDevTool, Governance::AiSubAgent],
    action == Governance::Action::"Read",
    resource is Governance::File
)
when {
    resource.classification == "restricted" &&
    (context.data_residency == "eu-west" ||
     context.data_residency == "eu-central" ||
     context.data_residency == "eu-north" ||
     context.data_residency == "eu-south")
};
