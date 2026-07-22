<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Architecture Rationale

The architectural decisions encoded in this commons, with reasoning.
This document is the answer to "why is the commons structured this way"
for future readers (including future you).

## Layered architecture

The parent framework organizes concerns into six layers:

  L5 Artifacts     specs/, src/, docs/, tests/
  L4 Workflows     /plan, spec-driven ceremony, /review
  L3.5 Governance    audit log, attestation, compliance evidence
  L3 Capabilities    hooks, agents, MCP integrations
  L2 Knowledge     skills, rules, ADRs
  L1 Identity      CLAUDE.md principles, AGENTS.md
  L0 Foundation     mise, editorconfig, gitignore, OTel SDK

This commons sits *underneath* all layers as a substrate. It provides
the canonical definitions that L1-L5 reference.

Why a substrate rather than a layer: the artifacts here are not
sequenced in a workflow (unlike L4) and not loaded into context every
session (unlike L1). They are reference material consumed on demand by
multiple layers. Treating them as their own dependency layer would imply
sequencing they don't have.

## Why "commons" not "framework-core"

The naming is intentional. "Framework core" implies these artifacts
serve one framework. "Commons" implies they are shared infrastructure
that multiple frameworks can consume.

The parent build-time framework is the first consumer. A future runtime
governance framework will be the second. Both consume the same
identity model, the same threat catalogs, the same compliance mappings.
"Commons" names that relationship.

## Format choices: YAML for threats, OSCAL JSON for compliance

Catalogs use two different formats based on what's available upstream
and what fits the content:

### Threat catalogs → YAML

Threat content is descriptive prose (paragraphs explaining each
threat). YAML wins for this because:

- Multi-line strings (`|` and `>`) handle paragraphs naturally; JSON
 requires escaped newlines that destroy reviewability
- Comments are essential for explaining mapping decisions; JSON has
 no comments
- LAST_REVIEWED and UPSTREAM_SOURCE metadata stay readable in diffs

The risk: YAML's indentation-significance creates parsing footguns.
Mitigation: every catalog has a schema and CI validates against it.

### Compliance catalogs → OSCAL JSON

Compliance content has an established machine-readable standard:
NIST's Open Security Controls Assessment Language (OSCAL). We adopt
OSCAL natively rather than maintaining a parallel YAML representation.

This decision was made deliberately after considering custom YAML:

- NIST publishes OSCAL versions of 800-53, CSF, 800-171, and SSDF
 directly - no translation step needed
- Trestle provides tooling for OSCAL workspace management, validation,
 and updates
- Cross-framework mappings via OSCAL 1.2.0 Control Mapping model
- Aligned with federal compliance direction (July 2026 OSCAL mandate)

See `spec/oscal-model.md` for the full OSCAL adoption decision and
which OSCAL models we adopt versus defer.

### When to use which

| Content type | Format | Why |
|---|---|---|
| Threats, vulnerabilities, attack patterns | YAML | Descriptive prose, no upstream standard |
| Compliance controls, framework mappings | OSCAL JSON | NIST standard, tooling ecosystem |
| Policy primitives | Cedar | Authorization-specific DSL |
| Library context | YAML | Mixed prose and structured fields |
| Reference-only metadata | YAML | Lightweight, human-edited |

## Why Cedar for policy DSL

Cedar (AWS-originated, OSS) was chosen over alternatives (OPA/Rego,
custom DSL) for these reasons:

- Strong typing prevents whole classes of policy bugs (typos in
 attribute names fail at compile time, not runtime)
- Designed specifically for authorization with actor/action/resource
 semantics, matching the shape of governance policies
- Adopted by Microsoft Agent Governance Toolkit (the planned canonical
 runtime framework), creating natural alignment between build-time
 and future runtime policy expression
- Simpler mental model than Rego for engineers not already invested in
 the OPA ecosystem

Alternatives documented in `policy-dsl-choice.md`. If Cedar adoption
stalls or a regulatory body mandates a different DSL, the parent
framework wraps Cedar in a Strategy-pattern interface so the policy
engine can be swapped without changing consumer code.

## Why standards-aligned over self-defined

Catalogs use upstream standards' IDs as primary keys (LLM01, ASI03,
ATLAS-T0048, NIST AI RMF GOVERN-1.1, NIST 800-53 AC-2) rather than
commons-internal IDs.

The reasoning: when an auditor asks "what's your coverage for OWASP
LLM01?", we can answer directly with our catalog entry. If we'd
renumbered to commons-internal IDs, every audit conversation would
require a translation step, and that translation is itself a place
where errors and audit findings hide.

This is the same principle behind OSCAL itself (NIST's machine-readable
control catalog format): be a curator and mapper of standards, not a
parallel definition of them.

## Why no executable code

The commons contains no Python, no shell scripts, no executable
runtime. Everything is markdown, YAML, OSCAL JSON, Cedar policy text,
or JSON schema definitions.

This is deliberate. Executable code creates language and runtime
dependencies that limit portability. The runtime framework will be
written in a different language than the build-time framework (Go for
production agents vs Python/shell for build-time tooling); shared
executable code would force one language choice on both.

Reference data and prose are universally consumable. Each consuming
framework writes its own thin adapter to load and use commons content
in whatever language is appropriate.

Note: Trestle is *used* by consumers of this commons to manage the
OSCAL content, but Trestle itself is not part of the commons. The
commons holds OSCAL artifacts (data); Trestle is the tool a consumer
chooses to manipulate that data.

## Why one canonical maintainer per catalog

Each catalog's maintainer field names an individual, not a team.

Diffused responsibility is the dominant failure mode for compliance
catalog maintenance: "the team owns it" means nobody updates it.
Individual accountability with rotation (when the maintainer changes
roles or organizations) keeps the protocol grounded in human reality.

## Layering

Our architecture separates concerns into layers: this commons (universal
governance), the parent framework (build-time methodology built on the
commons), and individual projects (project-specific consumers on top of
the framework). Keeping the commons at the universal layer is what makes
it portable across frameworks and projects.

## Support for coordinator-implementor-verifier patterns

Many AI development workflows use a three-role pattern: something plans,
something implements, something verifies.

This commons supports all such patterns by providing:

- The identity model that names these roles consistently
- The audit envelope that records role transitions
- The threat catalogs that the verifier role checks against
- The compliance catalogs that map verifications to controls

Consumers can implement the roles however they prefer (sequential
sub-agents, parallel review, role-playing personas); the commons stays
the same.

## What this commons deliberately does not include

- **No project management vocabulary** (no "sprint", "epic", "story
 points"). These are methodology choices that should live in the
 consuming framework, not the shared commons.
- **No vendor-specific tool configurations** (no Claude Code hooks, no
 Cursor rules, no Codex memory format). These belong in consuming
 framework adapters.
- **No CI/CD platform assumptions** (no GitHub Actions YAML, no GitLab
 CI YAML). The attestation format specs are portable; specific CI
 implementations are framework adapter concerns.
- **No language-specific code style rules**. Belongs in framework
 skills/rules, not in shared commons.
- **No OSCAL System Security Plans, Assessment Plans, or POAMs**.
 These are organization-level artifacts produced by consumers, not
 by the commons. See `spec/oscal-model.md` for the OSCAL scoping
 decision.

If you find yourself wanting to add something in these categories,
the right place is in the parent framework or a consuming project,
not in commons.
