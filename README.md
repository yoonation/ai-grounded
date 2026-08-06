<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/ai-grounded-logo-dark.svg">
    <img alt="AI Grounded" src="docs/assets/ai-grounded-logo-light.svg" width="380">
  </picture>
</p>

<p align="center"><strong>Spec-driven AI governance for production code.</strong></p>

<p align="center">
  <a href="LICENSE"><img alt="License: Apache 2.0" src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"></a>
  <a href="CONTRIBUTING.md"><img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg"></a>
  <a href="CODE_OF_CONDUCT.md"><img alt="Contributor Covenant" src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg"></a>
</p>

# AI Grounded

A spec-driven development template that combines GitHub spec-kit, a
7-article project constitution, twelve specialized AI sub-agents (eleven review agents organized
into seven cognitive categories, plus a pre-construction discovery agent) with priority-aware loop closure, and a
governance substrate (OSCAL compliance catalogs, threat catalogs, concern
catalogs, Cedar policies, attestation specs, incident playbooks).

Cloned and customized, this template gives any new project the scaffolding
to do spec-first work with rigorous engineering and security discipline
without rebuilding the infrastructure each time.

For the durable "why" behind the design, read `docs/FOUNDATIONS.md`. This
file is the operational orientation only and deliberately delegates
volatile detail (exact inventories, counts, milestone status) to the
documents that own it, so it stays stable as the project grows.

## What this is for

The template targets work that needs all of:

- A written specification before code is written (spec-driven development)
- Multiple specialized AI cognitive lenses applied to specs, plans, and
  code (not a single chat-style agent)
- Governance traceability (which agent flagged what, who resolved it, why)
- Compliance awareness (GDPR, HIPAA, SOC 2, EU AI Act, NIST 800-53, NIST
  800-171, NIST CSF v2, NIST AI RMF, NIST SSDF, ISO 42001, SOC 2 TSC)
- Threat-modeling discipline (STRIDE, OWASP LLM Top 10, OWASP Agentic ASI
  Top 10, MITRE ATLAS)
- Cost discipline for AI-assisted work (provider-agnostic, queryable)

It does not target throwaway prototypes, one-off scripts, or learning
exercises. The constitution explicitly permits skipping the workflow for
trivial work. See `docs/FIT.md` for which project types fit, today and on
the roadmap.

## Quick start

```bash
# 1. Start a new project from this template (or click "Use this
#    template" on GitHub, then clone your new repo)
git clone https://github.com/yoonation/ai-grounded.git my-project
cd my-project

# 2. Reset git history to start fresh on the new project
rm -rf .git
git init
git add .
git commit -m "chore: initialize from ai-grounded"

# 3. Install runtimes pinned in .mise.toml
mise install

# 4. Run the bootstrap (canonical setup step). It verifies prerequisites
#    and framework files, installs the spec-kit preset, activates the
#    loop-closure hook via core.hooksPath, and smoke-tests it.
./scripts/bootstrap.sh

# 5. Confirm spec-kit sees the installed delivery integrations
specify check

# 6. Start your first feature in the delivery you chose
# Claude Code: /speckit-specify Create a feature that does X
# Codex:       $speckit-specify Create a feature that does X
```

`./scripts/bootstrap.sh` is the canonical setup step: it is the only step
that installs the spec-kit preset and activates the pre-commit hook (it sets
`core.hooksPath .githooks`, which is wiped when you reset git history in step
2, so the hook is inert until bootstrap re-arms it). If you choose not to run
bootstrap, you must activate the hook manually; see SETUP.md Step 7.

If `specify` is not installed yet, see [SETUP.md](SETUP.md). If runtimes
are not installed, see [PREREQUISITES.md](PREREQUISITES.md).

## What you get

### Layout (top level)

```
ai-grounded/
├── README.md                  This file (orientation)
├── PREREQUISITES.md           Tool versions and install commands
├── SETUP.md                   Step-by-step setup procedure
├── CONTRIBUTING.md            How to propose changes
├── CLAUDE.md                  Claude Code memory file (constitution + workflow)
├── AGENTS.md                  Cross-tool agent reference (Zed, Cursor, etc.)
├── FUTURE.md                  Deferred items with 4-tier prioritization
├── .specify/                  Spec-kit workflow infrastructure (constitution, templates, extensions)
├── .claude/                   Claude Code config (twelve agents, skills, coordination doc, hooks)
├── governance-commons/        Reusable governance substrate (see its own README for layout)
├── presets/                   Vendored spec-kit preset (spec-driven-governance)
└── docs/                      Framework documentation (see below)
```

The `governance-commons/` substrate owns and documents its own internal
layout, inventory, and counts in `governance-commons/README.md`. This
README does not duplicate them, because the substrate evolves
milestone-to-milestone and a duplicated inventory here would go stale.

### docs/

- `FOUNDATIONS.md` - the durable identity, philosophy, mental model, and a
  capability register (what the framework has versus wants)
- `ENHANCEMENT-ROADMAP.md` - the prioritized menu of candidate work
- `ERROR-AND-DRIFT-MODEL.md` - the operational model for error and drift
- `agentic-design-patterns-reference.md` - the design rubric the framework
  is measured against
- `BEST-PRACTICES.md` - Claude Code operational guidance
- `FIT.md` - which project types fit, today and on the roadmap
- `RETROFIT.md` - adopting the framework on existing projects
- `AI-COMPATIBILITY.md` - cross-tool compatibility matrix
- `GATES.md` - the commit-time gate chain and tooling inventory
- `ARCHITECTURE.md`, `SPEC.md` - project templates
- `MCP-SERVERS.md` - how to configure `.mcp.json`
- `decisions/` - ADRs (one per significant decision)

### The twelve sub-agents

Claude Code consumes the role definitions directly. Codex consumes matching
`.codex/agents/*.toml` adapters, which load the canonical prompts from
`.claude/agents/` and default to a read-only sandbox. See
[docs/CODEX.md](docs/CODEX.md) for local setup and model mapping.

Each agent has a specific cognitive role and explicit coordination
relationships with the others. Coordination protocol is documented in
`.claude/docs/agent-coordination.md`. Categories enforce single
responsibility per agent.

| Category | Agent | Model | Role |
|---|---|---|---|
| Routing | concern-selector | sonnet | Read-only; resolves per-feature scope and routing into feature-concerns.yaml within the profile bounds |
| Upstream challengers | staff-engineer | opus | Principled pushback on specs/plans; assigns P1/P2/P3 |
| Upstream challengers | threat-modeler | opus | Proactive STRIDE/OWASP LLM/OWASP ASI/MITRE ATLAS with compliance mapping |
| Upstream challengers | performance-reviewer | sonnet | Resource safety, runaway prevention, scaling failures |
| Upstream challengers | production-readiness | opus | Environment topology, deployment, observability, resilience |
| Decision formalizers | adr-architect | sonnet | Drafts ADRs from existing artifacts |
| Operational design | operational-architect | opus | SLI/SLO/error budget; observability instrumentation; runbook scaffolding |
| Test design | test-architect | sonnet | Test design from spec; coordinates perf tests |
| Downstream verifiers | code-reviewer | sonnet | Quality, smells, anti-patterns, missing tests |
| Downstream verifiers | security-reviewer | opus | Vulnerabilities, audit envelope, compliance, threat-mitigation verification |
| Audit | closure-auditor | opus | Verifies pending-resolution items have valid closure evidence |
| Discovery | discovery-agent | sonnet | Read-only; pre-construction reuse survey over the capability index; proposes reuse, does not build the index or enforce |

### The workflow

For typical feature work the order is:

1. `/speckit-specify` to capture intent
2. `/speckit-clarify` to resolve ambiguity
3. Run `/speckit-workflow-post-spec`: the concern-selector resolves the plan
   once, you approve it, then the dispatcher dispatches the C1 challengers
4. Review concerns by priority; address P1 (must close), decide P2,
   note P3; signal closures as you go
5. `/speckit-plan`
6. Run `/speckit-workflow-post-plan` (the dispatcher dispatches plan-time reviewers)
7. Review ADR drafts if produced
8. `/speckit-tasks`, then `/speckit-implement`
9. Keep signaling closures as you implement
10. Run `/speckit-workflow-post-impl` (the dispatcher dispatches code-reviewer +
    security-reviewer in parallel, then closure-auditor)
11. Review the closure-auditor report; fix or override rejected closures
12. `git commit` - the pre-commit hook blocks commits with missing or
    rejected closures; address blockers and retry. Emergency override via
    `SKIP_LOOP_VERIFY=1` plus a non-empty `SKIP_LOOP_VERIFY_REASON`
    (the hook refuses the bypass without the reason)

For trivial work (typo fixes, dependency bumps, single-line changes), skip
the workflow per constitution Article I Section 1.2.

### Priority-aware loop closure

Every concern an upstream agent raises carries a priority. P1 (must-close)
blocks commit unless closed in code, test, ADR override, or spec
amendment. P2 (should-close) blocks unless closed or documented as a
deferral. P3 is informational. Closure runs in three layers: user
signaling (claim), semantic verification (closure-auditor), and mechanical
enforcement (the pre-commit hook). Each layer's failure mode is caught by
the next, and the framework stays usable for non-Claude tools (layers 1
and 3 work without layer 2).

### Preset architecture

The framework's customizations to spec-kit are vendored as a spec-kit
preset at `presets/spec-driven-governance/`, so they survive spec-kit
upgrades (`specify init --here --force`) that refresh the stock templates.
The preset ships the 7-article constitution template, the governance-aware
spec template, and a Write-to-Edit cosmetic fix for `/speckit-specify` and
`/speckit-clarify`. Template resolution is a 4-layer priority stack
(project overrides, installed presets, extensions, stock spec-kit).
Bootstrap installs and refreshes the preset:

```bash
./scripts/bootstrap.sh
```

Do not edit files inside `.specify/presets/spec-driven-governance/`
directly; that directory is spec-kit-managed runtime state regenerated
from `presets/` on every bootstrap, and is in `.gitignore`. See
`CONTRIBUTING.md` for the full modify-and-propagate workflow.

## Reading order

If you are new to this template:

1. `README.md` (this file) for orientation
2. `docs/FOUNDATIONS.md` for the durable identity and philosophy
3. `PREREQUISITES.md` to install the tools
4. `SETUP.md` to bring up a new project
5. `.specify/memory/constitution.md` for what governs work in this repo
6. `.claude/docs/agent-coordination.md` for how the agents work together
7. `governance-commons/README.md` for the governance substrate

If you are coming back after time away:

1. `FUTURE.md` for the current backlog, the roadmap, and what was rejected
2. `docs/decisions/` for the decision history
3. `governance-commons/MAINTENANCE.md` for the quarterly review schedule

## Status

The framework's foundational layers (governance substrate, spec-kit
integration, sub-agents, priority-aware loop closure, preset architecture)
are in place. The governance substrate is on its own milestone track; the
current substrate version and milestone status live in
`governance-commons/VERSION` and `governance-commons/CHANGELOG.md`, and the
roadmap and deferred items live in `FUTURE.md`. The capability register in
`docs/FOUNDATIONS.md` is the single at-a-glance view of what the framework
has versus what it intends to have.

This README is reviewed at the milestone and year boundaries, not
continuously. If it needs editing more than once per milestone, it is
carrying detail that belongs in a document that owns that detail; move the
detail rather than syncing the README.

## Versioning

The template follows semantic versioning (recorded in `VERSION` when
present and in git tags). Component versions are pinned in `.mise.toml`
(Python 3.12, Node 22, Terraform 1.12); spec-kit installs from git main;
Claude Code installs latest via npm. Governance and threat catalogs follow
their upstream maintainers; review cadences are in
`governance-commons/MAINTENANCE.md`.

## Contributing

Issues, discussions, and pull requests are welcome. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the workflow (including DCO sign-off),
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations, and
[SECURITY.md](SECURITY.md) for private vulnerability reporting.

## License

Apache-2.0. See [LICENSE](LICENSE); third-party attributions are in
[NOTICE](NOTICE) and [THIRD-PARTY-LICENSES/](THIRD-PARTY-LICENSES/).

## Acknowledgments

This template integrates and customizes GitHub spec-kit (the spec-driven
workflow), NIST OSCAL (machine-readable compliance catalogs), IBM
compliance-trestle (OSCAL tooling), OWASP (LLM Top 10 and Agentic ASI Top
10 catalogs), MITRE (the ATLAS catalog), AWS Cedar (the policy DSL), and
the SLSA Framework and in-toto (attestation specs).

## Questions

If setting this up for the first time and something is not covered, check
SETUP.md's troubleshooting section, then `specify check`, then
`mise doctor`.
