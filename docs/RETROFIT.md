<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Retrofitting onto Existing Projects

This document explains which parts of the framework can be adopted
into an existing project and what each part costs to integrate.

Retrofit here means picking specific framework parts and adopting
them, not adopting the whole framework. The framework was designed
greenfield, where you clone the template before writing code. Most
real projects don't get that luxury - they exist already.

This is a menu, not a runbook. You read it, decide which parts
fit your situation, and adopt those. Skipping the rest is fine.

## What retrofit means

The framework has substrate, automation, and conventions. Each
layer has different retrofit costs:

- **Substrate** (governance-commons): data, references, and
  specifications. Drop-in compatible with any project.
- **Automation** (`.claude/`, `.specify/`): requires Claude Code or
  spec-kit and changes how work gets done.
- **Conventions** (constitution, ADR discipline, spec-driven
  workflow): require team agreement and change the development
  workflow itself.

Adopt by layer. Start with substrate. Move to automation only if
the substrate proves valuable. Adopt conventions only with team
buy-in.

## The five retrofittable parts, ranked by adoption cost

### Tier 1: Drop-in (no project changes required)

These parts are pure data. They don't change how your project
works. You copy them in, reference them from your existing
documentation or AI prompts, and that's the adoption.

**1.1 Threat catalogs** (`governance-commons/catalogs/threats/`)

Four YAML files: STRIDE, OWASP LLM Top 10, OWASP Agentic ASI Top 10,
MITRE ATLAS. Each is a structured threat taxonomy with identifiers,
descriptions, common vectors, and mitigations.

- **What you get**: a shared reference for threat modeling
  conversations and security reviews. Anyone (human or AI) doing
  security work on your project can reference threat IDs (LLM01,
  AML.T0040) instead of restating threats from scratch.
- **What it costs**: ~5 minutes to copy in. Zero team training.
- **Integration**: copy the four YAML files to
  `governance-commons/catalogs/threats/` in your project. Reference
  them in your existing security docs by ID. Done.

**1.2 Incident playbooks** (`governance-commons/playbooks/`)

Nine markdown files covering specific AI-adjacent incident types:
runaway agent loop, credential leak in prompt, prompt injection
detected, compromised MCP server, model output leaking PII, model
version rollback, audit log tampering, unauthorized agent action.

- **What you get**: ready-made incident response runbooks for
  AI-specific incident classes that most companies don't have
  playbooks for yet.
- **What it costs**: ~10 minutes to copy and read. Optional: tailor
  the contact list and escalation paths to your team.
- **Integration**: copy `governance-commons/playbooks/` directory.
  Add a link to it from your existing incident response
  documentation.

**1.3 Library context YAMLs** (`governance-commons/lib-context/`)

Seven YAML files documenting hallucination-prone APIs: terraform-aws,
langchain, langgraph, pydantic, fastapi, cedar, plus an AI model
pricing reference. Each documents common AI-induced errors (wrong
function signatures, deprecated patterns, version-dependent
behavior).

- **What you get**: a defense against AI tools inventing function
  signatures or recommending deprecated patterns for these libraries.
- **What it costs**: ~5 minutes to copy. Useful only if your project
  uses any of these libraries.
- **Integration**: copy `governance-commons/lib-context/` directory.
  Reference relevant YAMLs in your AI tool's system prompt or
  CLAUDE.md.

### Tier 2: Moderate (requires some integration work)

These parts need supporting infrastructure or selection decisions.
They're still valuable as drop-in references but cost more to wire
up correctly.

**2.1 OSCAL compliance catalogs** (`governance-commons/catalogs/compliance/`)

Six OSCAL catalogs (NIST 800-53, 800-171, 800-218 SSDF, CSF v2,
EU AI Act, AI RMF) plus four profiles tailoring them. Machine-readable
compliance control catalogs in NIST's standard format.

- **What you get**: a structured map of compliance controls your
  project can claim coverage on. Useful for SOC 2 audits, FedRAMP
  paths, EU AI Act preparation, customer security questionnaires.
- **What it costs**: ~30 minutes to a few hours, depending on how
  deep you go. Drop-in copy is easy; meaningful adoption requires
  selecting a profile (which subset of controls applies to your
  project) and mapping your existing controls to catalog IDs.
- **Integration path**:
  1. Copy `governance-commons/catalogs/compliance/` directory
  2. Read the four profiles (`ai-security-baseline`, `federal-bridge`,
     etc.) and pick the one closest to your compliance posture
  3. Walk through the profile's control list and mark which controls
     your project already satisfies (in a separate `compliance-status.md`)
  4. Use IBM compliance-trestle (`pipx install compliance-trestle`)
     to query, validate, and generate compliance reports from the
     catalog
- **Caveats**: NIST OSCAL catalogs are public domain (no license
  concern). EU AI Act mapping is referenced but not yet a full OSCAL
  profile in the framework.

**2.2 Cedar policies** (`governance-commons/policies/`)

Eight Cedar policy files: agent-trust-decay, cross-agent-handoff,
data-residency, human-approval-required, least-privilege-agent,
no-credential-paths, no-pii-access, tool-allowlist. AWS Cedar is
the policy DSL.

- **What you get**: machine-evaluable runtime policies for AI agent
  permissions, data residency enforcement, PII access control. If
  you have agentic AI workloads, these are non-trivial to write from
  scratch.
- **What it costs**: ~1-3 days, primarily because you need a Cedar
  runtime in your stack to enforce them.
- **Integration path**:
  1. Copy `governance-commons/policies/` directory
  2. Decide your enforcement layer: Amazon Verified Permissions
     (managed), `cedar-policy/cedar` SDK in your application, or
     `cedar-policy/cedar-for-k8s` for Kubernetes admission control
  3. Adapt the principal, action, and resource definitions in the
     policies to your actual entity model
  4. Test the policies against your application's authorization flows
- **Caveats**: the framework's Cedar policies are designed for the
  identity model in `governance-commons/spec/identity-model.md` (three
  principal types: developer, AI tool, tool instance). If your
  project has a different identity model, you'll adapt or rewrite
  the policies.

**2.3 Attestation specifications** (`governance-commons/attestation/`)

Four markdown specs: SLSA v1.0 provenance, in-toto Statement format,
cosign signing, and the framework's audit envelope. These are
specifications describing how to produce SLSA-compliant provenance
for AI-assisted work.

- **What you get**: a starting point for supply chain attestation
  in projects that need SLSA Level 2+ (federal contractors, regulated
  industries, sensitive AI/ML pipelines).
- **What it costs**: ~1-2 weeks of build pipeline work, mostly
  outside the framework. The specs are short; implementing them is
  the cost.
- **Integration path**:
  1. Copy `governance-commons/attestation/` directory as a reference
  2. Add SLSA provenance generation to your build pipeline (the
     `slsa-github-generator` GitHub Action is the easiest entry
     point for GitHub-hosted projects)
  3. Add cosign signing to attestations
  4. Wire the resulting in-toto statements into your existing audit
     trail
- **Caveats**: the framework's attestation specs assume a target
  posture, not a current state. You're adopting a destination; the
  journey is yours.

### Tier 3: Hard (requires team adoption + workflow change)

These parts change how work gets done. They're not files you copy;
they're commitments. Adopt only with team agreement.

**3.1 Constitution** (`.specify/memory/constitution.md`)

Seven articles with specific rules: spec-driven workflow, exact
version pinning, ADRs before non-trivial decisions, threat modeling
for external interfaces, environment topology awareness, loop
closure mandatory, AI involvement transparency.

- **What you get**: a written, ratified set of engineering principles
  that constrain how the project evolves. Reduces drift over time.
  Useful for compliance documentation
  and onboarding.
- **What it costs**: hard. The constitution will conflict with how
  your existing project actually operates. Almost any non-trivial
  existing project violates several articles on day 1.
- **Integration path** (phased):
  1. Copy `.specify/memory/constitution.md` and read it with the
     team
  2. Walk through each article and identify which the project already
     satisfies and which it doesn't
  3. For each violated article, write an ADR documenting why the
     violation is accepted for now (date-stamped) and what triggers
     remediation
  4. Adopt new articles only as ratchets: new code must satisfy
     them; old code is grandfathered until touched
  5. Add the constitution reference to your project's CONTRIBUTING.md
     so new contributors see it
- **Honest caveats**: full constitutional compliance on an existing
  project is rarely achievable without significant rework. The
  realistic adoption is "new work follows; old work is grandfathered
  with compliance debt ADRs." If your team can't agree to that, skip
  this part - adopting a constitution you don't intend to honor is
  worse than not adopting one.

**3.2 Spec-driven workflow** (`.specify/`)

Spec-kit infrastructure: templates for specs, plans, tasks. Slash
commands (in supported AI tools) for `/speckit-specify`,
`/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`,
`/speckit-implement`, etc. A discipline of writing the spec before
writing the code.

- **What you get**: traceability from intent to implementation.
  Specifications, plans, and task lists become first-class artifacts
  reviewed alongside code. Useful for compliance evidence, code
  review quality, AI-assisted development with reduced rework.
- **What it costs**: medium-high. Spec-kit itself installs quickly
  (`specify init --here --ai <your-tool>`). The cost is changing
  how work gets done. Engineers used to opening a branch and writing
  code now write a spec, get it clarified, write a plan, and only
  then write code.
- **Integration path**:
  1. Read `SETUP.md` for spec-kit installation
  2. Decide scope: all new features, or just specific high-risk
     features (security work, infrastructure changes, AI agent
     work)?
  3. Install spec-kit: `specify init --here --ai claude` (or your
     preferred tool)
  4. Run one feature through the workflow as a pilot, measure
     overhead, decide whether to expand
- **Honest caveats**: the workflow adds ceremony. For a one-line
  bug fix, the spec/plan/tasks pipeline is overkill. The constitution
  explicitly permits skipping the workflow for trivial work (Article
  I Section 1.2). Setting the threshold is a team decision. Without
  team agreement, the workflow gets followed inconsistently and
  loses value.

**3.3 The twelve sub-agents** (`.claude/agents/`)

Twelve specialized Claude Code sub-agents: eleven review agents organized into seven
cognitive categories, plus a pre-construction discovery agent:

- **Routing**: concern-selector (resolves the per-feature plan once at C1) +
  the dispatcher (deterministic tooling that places the plan's agents into waves)
- **Upstream challengers**: staff-engineer, threat-modeler,
  performance-reviewer, production-readiness
- **Decision formalizers**: adr-architect
- **Operational design**: operational-architect
- **Test design**: test-architect
- **Downstream verifiers**: code-reviewer, security-reviewer
- **Audit**: closure-auditor (semantic verification of claimed
  closures; emits closure-verified/closure-rejected events)
- **Discovery (pre-construction)**: discovery-agent (fresh-eyes reuse
  survey over the capability index before construction; proposes reuse,
  invoked by the implement skill, not in a checkpoint wave)

Each is a read-only advisor with its own context window and cognitive
scope. Concerns carry P1/P2/P3 priorities assigned by the raising
agent.

- **What you get**: specialized cognitive lenses applied to specs,
  plans, and code. The framework's most distinctive feature.
  Specifically useful for: principled pushback before
  implementation, proactive threat modeling, performance/scaling
  analysis on plans, production readiness review, operational design,
  and audit-trail verification post-implementation.
- **What it costs**: requires Claude Code. See AI-COMPATIBILITY.md
  for what you can do with other AI tools. The mechanical
  enforcement layer (`verify_loop_closure.py` hook) is tool-agnostic
  and works for any AI that writes closure-claimed events.
- **Integration path**:
  1. Install Claude Code (`brew install claude` or
     `curl -fsSL https://claude.ai/install.sh | sh`)
  2. Copy `.claude/agents/`, `.claude/docs/`, `.claude/hooks/` from
     this framework to your project root
  3. Copy `.specify/templates/deferrals-template.md` for the P2
     deferral mechanism
  4. Verify your project's CLAUDE.md describes the dispatch protocol and
     closure signaling (see `.claude/docs/agent-coordination.md` and the
     "Running the dispatcher and persisting agent output" and "Closure
     signaling protocol" sections of the framework's CLAUDE.md)
  5. Activate the pre-commit gates: `git config core.hooksPath .githooks`
     (the `.githooks/pre-commit` dispatcher and its `.githooks/pre-commit.d/`
     gates are tracked in the repo; do not install in `.git/hooks/`, which
     `core.hooksPath` makes inert)
  6. Test by running `/speckit-workflow-post-spec` against an existing spec to
     see the plan the concern-selector produces and the dispatcher dispatches
- **Caveats**: the sub-agents read from `specs/NNN-feature/` paths.
  If you're not using the spec-driven workflow (Tier 3.2), the
  sub-agents have nothing to read. The twelve sub-agents are most
  useful with the workflow; in isolation they degrade to "ask Claude
  for analysis," which Claude already does without the sub-agent
  feature.

The Python hook (`verify_loop_closure.py`) is pure stdlib and works
even without Claude Code, supporting non-Claude AI tools that write
`closure-claimed` events directly.

## The honest "when not to bother"

Retrofit is not always worth it. Skip the framework entirely if:

- **Your project is end-of-life.** Sunset code doesn't need new
  governance. Bug-fix-only-mode projects gain nothing from a
  constitution.
- **Your team is two people and you trust each other completely.**
  The framework's value is in coordination, transparency, and
  asynchronous review. Tight pairs already have all of that
  informally.
- **Your project already has a well-functioning equivalent.** If
  you have working RFCs, ADRs, threat modeling cadence, and a
  spec-driven workflow that the team respects - don't replace it.
  Maybe steal the threat catalogs and Cedar policies; leave the
  rest.
- **You can't get team buy-in on the conventions.** The constitution
  and spec-driven workflow only work if the team agrees. Without
  buy-in, you'll get adoption theater: documents that exist but
  aren't actually consulted.
- **The cost of stopping ongoing feature work to adopt is higher
  than the benefit.** Retrofit is overhead. If your team is in
  delivery crunch, defer.

The substrate (Tier 1 + Tier 2) is almost always worth adopting
even when the rest isn't. The conventions (Tier 3) are not.

## Full retrofit (going all-in)

If you've evaluated the tiers above and decided to adopt everything,
the procedure is essentially "treat your existing project as a fresh
clone." Follow `SETUP.md` for installation, then:

1. Back up your project (branch or full clone)
2. Copy the framework files following the tier order:
   - Tier 1 directories (threats, playbooks, lib-context)
   - Tier 2 directories (compliance, policies, attestation)
   - Tier 3 files (constitution, spec-kit init, sub-agents)
3. Resolve file-level conflicts:
   - Existing README.md: keep yours, optionally add a "framework
     adoption" section pointing to the framework docs
   - Existing LICENSE: keep yours (the framework's Apache 2.0 is
     suggestive, not mandatory)
   - Existing CONTRIBUTING.md: keep yours, optionally reference the
     framework's constitution
   - Existing CLAUDE.md: merge - preserve project-specific
     customizations at the top, add the framework's "Project
     Constitution and Principles," "Available Sub-agents,"
     "Running the dispatcher," and "Workflow" sections
   - Existing AGENTS.md: merge similarly
   - Existing `.gitignore`, `.editorconfig`, `.mise.toml`: merge
     entries; don't overwrite
   - Existing `.mcp.json`: merge the `mcpServers` block; the
     framework's default is `{"mcpServers": {}}` (empty but valid JSON).
     See `docs/MCP-SERVERS.md` for examples of common servers and
     security guidance.
4. Write a `docs/decisions/ADR-001-framework-adoption.md` documenting
   the date of retrofit, which tiers you adopted, and the rationale
5. Add compliance-debt ADRs (`ADR-002` through whatever) for
   constitution articles your existing code doesn't satisfy yet
6. Run one feature end-to-end through the workflow as validation
7. Train the team on the workflow if you haven't already

## License reconciliation

The framework is Apache 2.0. Your project may not be.

**If your project is Apache 2.0**: no action needed.

**If your project is MIT or BSD**: Apache 2.0 substrate code can be
included; mark it as Apache 2.0 in your NOTICE file (create one if
absent). MIT/BSD project files stay MIT/BSD.

**If your project is GPL v3 or AGPL v3**: Apache 2.0 is compatible
with GPL v3+ in one direction (you can include Apache 2.0 code in a
GPL project). The reverse is not true. Mark the substrate's origin
in NOTICE.

**If your project is proprietary**: Apache 2.0 permits inclusion in
proprietary projects. Preserve copyright notices and the NOTICE file
content where you adopt framework files.

**If your project has no LICENSE**: this is a deeper problem than
retrofit. Talk to your legal team before adopting any open-source
substrate.

The framework's NOTICE file (`NOTICE` at the repo root) is the
attribution mechanism for Apache 2.0. When you adopt framework parts
into your project, the attribution requirement transfers - your
project's NOTICE file should acknowledge the framework's origin.
A one-line entry is sufficient:

```
This project includes content from ai-grounded
(https://github.com/<your-username>/ai-grounded),
Copyright 2026 [Framework author], licensed under Apache 2.0.
```

## Maintenance after retrofit

Adopted parts drift over time as the upstream framework evolves.
Strategy options:

**Option A: pin and never update.** Treat the adopted parts as a
one-time copy. Simplest. You miss bug fixes and improvements.

**Option B: track upstream manually.** Periodically (quarterly?) do
a `diff -r` against the latest framework version and apply
relevant changes. Highest control, highest effort.

**Option C: git subtree or submodule for governance-commons.**
Track `governance-commons/` as a subtree from the upstream
framework repo. Pull updates with `git subtree pull`. Works well
for the substrate; less well for the automation layer (your
project's `.claude/` will diverge by design as you customize
agents).

**Option D: rebase the entire project onto a newer framework
version.** Only sensible if the framework is your project's
foundation and you're committed to staying synchronized.

For most projects, Option A or B is right. The framework's substrate
doesn't change rapidly; quarterly sync is usually enough.

## See also

- `SETUP.md` - full setup procedure (assumes fresh clone)
- `AI-COMPATIBILITY.md` - what you give up with non-Claude AI tools
- `governance-commons/PORTABILITY.md` - anti-coupling rules that
  make the substrate retrofit-friendly
- `governance-commons/MAINTENANCE.md` - quarterly review cadences
  for the substrate after adoption
- `FUTURE.md` - items deliberately not in the framework yet (with
  rationale); useful when deciding whether to retrofit something
  the framework doesn't have but you do
