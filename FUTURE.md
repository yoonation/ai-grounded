<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Future Considerations

This document tracks framework extensions deferred for later. The
twelve-agent + spec-kit + governance-commons architecture is
intentionally bounded. Adding agents has compounding cost: prompt
maintenance, coordination complexity, cognitive load on the routing layer.

Most future framework growth happens by **expanding existing agents'
scope** when concrete triggers fire, not by adding new agents. The
500-line tripwire and decline mechanism documented in
`.claude/docs/agent-coordination.md` keep this honest - when a
proposed scope expansion would push an existing agent past 500 lines,
it becomes a candidate for a new agent rather than a scope expansion.

Items here have been considered. They are not all "yes, eventually."
Some are "no, here's why" - that's the explicit
**considered-and-rejected** tracking. Surfacing rejections prevents
re-litigating the same decisions.

Items graduate to the framework when:

- A concrete failure mode demonstrates the gap
- The cost of adding the capability is lower than the cost of the gap
- An owner is committed to maintaining the addition

## Top priority: Brownfield onboarding workflow

**Priority:** P2 (not blocking own use; blocking if framework is offered to others for retrofit)

**Trigger:** Anyone (including the framework author) tries to adopt this framework into an existing codebase rather than starting from a fresh template clone.

**Context:** The framework's `docs/RETROFIT.md` is a thoughtful menu of adoptable parts ranked by integration cost (Tier 1 substrate → Tier 2 automation → Tier 3 conventions). But the actual onboarding experience for retrofit users is manual: read the menu, pick parts, copy files, write a constitution by hand. The community has built explicit brownfield workflows that reduce this to a few slash commands. This framework should match that bar before being marketed for retrofit use.

### Research findings from existing brownfield approaches

EPAM "Using Spec-Kit for Brownfield Codebase" article (December 2025) outlines a four-step approach that works for production systems:

- **Step 1 - Constitution from the codebase**: Don't author manually. Have the AI analyze the existing codebase exhaustively and derive principles directly from observed conventions, naming patterns, architecture, and existing rules files (`.cursor/rules/`, ESLint configs, etc.). Generates `.specify/memory/constitution.md` that reflects ACTUAL standards, not generic best practices from training data. Uses prompt like: *"As this is a pre-existing brownfield project I need you to analyze the codebase exhaustive and in-depth. Do NOT skim over but use multiple iterations to do a deep analysis."*

- **Step 2 - Specs per feature, not per codebase**: Don't try to reverse-engineer specs for the whole system. Author a spec only for the next change. Spec density grows naturally in frequently-touched areas; rarely-touched code stays uncovered. This is the *incremental brownfield* approach (intent-driven.dev calls it this; uses RepoMix to package context).

- **Step 3 - Plan with brownfield framing**: The plan converts existing architecture + new feature scope into concrete file paths and integration strategy. Spec-kit's "Constitution Check" section becomes "Existing Architecture Preservation" and "Backward Compatibility" articles.

- **Step 4 - Tasks ordered for safety**: Additive migrations only. Backward-compatible changes. Don't rewrite, extend.

Community brownfield extensions to reference when building this:

- **`/speckit.brownfield-bootstrap`** (spec-kit issue github/spec-kit#1436): adds a single command that scans codebase, generates tailored constitution + templates, merges rather than overwrites
- **`Quratulain-bilal/spec-kit-brownfield`** (GitHub): four-command flow: `/speckit.brownfield.scan` → `bootstrap` → `validate` → `migrate`
- **`mnriem/spec-kit-aspnet-brownfield-demo`** (GitHub): 307K-line .NET CMS, two features added entirely through agents - real-world proof
- **`mnriem/spec-kit-go-brownfield-demo`** (GitHub): NASA Hermes ground support, telemetry dashboard added
- **spec-kit Discussion #1119**: multi-repo brownfield with Radius project, worked without additional config (specs in one repo, code in another)
- **Mintlify official tutorial** "Brownfield Enhancement" (Taskify WebSocket notifications): documents `specify init . --ai claude --force` to merge spec-kit into existing project without deleting code
- **`docs/RETROFIT.md`** (this framework): the manual adoption ladder

### What this framework already supports for brownfield (no work needed)

- **governance-commons/** - pure substrate. Drop-in. No code changes required to the existing project.
- **Threat catalogs, compliance catalogs, Cedar policies, playbooks** - reference material. Works immediately as documentation.
- **`.claude/` agents** - once Claude Code is set up, agents read whatever spec exists. They don't assume the spec was written from scratch.
- **Pre-commit hook** - `verify_loop_closure.py` only checks `specs/NNN-feature/events.jsonl` for the current feature. Doesn't care about the surrounding codebase age.
- **Constitution + ADR discipline** - adoptable as conventions any time.
- **`docs/RETROFIT.md`** - documents the adoption ladder explicitly.

### What's missing for brownfield (the gap this entry tracks)

1. **No brownfield bootstrap script**. `scripts/bootstrap.sh` verifies framework files are present but doesn't help a user analyze an existing codebase and derive a constitution.

2. **No "scan and derive constitution" workflow**. EPAM and community both emphasize: have the AI derive the constitution from the existing codebase. Framework ships a greenfield constitution template; no scan-and-derive command exists.

3. **No brownfield-specific constitution articles**. The Mintlify tutorial adds "Existing Architecture Preservation" and "Backward Compatibility" articles. Framework's constitution is greenfield-flavored.

4. **No `/speckit-workflow-brownfield-analyze`** command. Community pattern is one slash command that does the analysis. Framework would need a new workflow extension command (and matching skill) to match.

5. **Multi-repo brownfield not addressed**. Some projects span 5+ repos. Framework assumes one repo.

### Resolution options when triggered

**Option (a) - Brownfield bootstrap variant script:**

Ship `scripts/bootstrap-brownfield.sh` alongside `scripts/bootstrap.sh`. Different entry point, same idempotent verification at the end. Adds:
- Detect existing project: language, framework, build tooling
- Ask user 4-5 questions: security classification, regulatory context, team size, monorepo or single
- Generate an analysis prompt the user feeds to Claude Code that produces a derived constitution
- Add brownfield-specific constitution articles
- Note which framework parts are recommended (substrate yes immediately; full agent workflow only after team buy-in)

Cost estimate: 1-2 days.

**Option (b) - `/speckit-workflow-brownfield-analyze` extension command:**

Add `.specify/extensions/workflow/commands/speckit.workflow.brownfield-analyze.md` and matching skill in `.claude/skills/speckit-workflow-brownfield-analyze/`. Invokes a project-analysis flow: read codebase, derive conventions, produce draft constitution + threat-model context. Output goes to `reviews/brownfield-analysis.md` in a feature-zero directory (e.g., `specs/000-brownfield-bootstrap/`).

Cost estimate: 1-2 days.

**Option (c) - Both (a) and (b):**

The bootstrap script gates initial onboarding; the workflow command runs once main session is active. Both reference each other. Most complete experience for retrofit users.

Cost estimate: 2-3 days for both.

**Option (d) - Adopt a community extension verbatim:**

Vendor `Quratulain-bilal/spec-kit-brownfield` or similar as a bundled extension under `.specify/extensions/brownfield/`. Apache 2.0 compatible. Cost: a few hours to integrate and document, but inherits maintenance of an upstream community project.

### Why deferred

Framework is currently used greenfield for own features. Brownfield onboarding hasn't been a blocker. Becomes urgent only if:
- The framework is offered publicly to others (a decision worth its own discussion)
- The framework is retrofitted into an existing codebase
- A specific project requires brownfield adoption that can't be served by RETROFIT.md's manual menu

### Cross-ref

- `docs/RETROFIT.md` - existing manual retrofit menu (the fallback if this workflow isn't built)
- EPAM blog: `https://www.epam.com/insights/ai/blogs/using-spec-kit-for-brownfield-codebase`
- Spec-kit Mintlify brownfield tutorial
- Spec-kit issue #1436 (brownfield-bootstrap proposal)
- intent-driven.dev "Spec-Driven Development with Brownfield Projects" (incremental approach using RepoMix)

## Workflow: risk-gated default path

**Priority:** P1 (sets the default execution posture for every feature).

**Status:** `[PLANNED]`.

**Trigger:** Now. Adopt as the standing routing rule for new features.
It requires no new agents and no substrate changes.

**Context:** The full workflow (specify, clarify, post-spec, plan,
post-plan, tasks, implement, post-impl, pre-commit) with multi-agent
review at three checkpoints is correct for production-grade,
security-relevant, long-lived, expensive-to-get-wrong work. Applied
uniformly to every feature it becomes the ceremony that `docs/FIT.md`
warns about: the failure mode of a governance framework is being
bypassed, not being incomplete. Right-sized ceremony is already a
constitutional principle (Article I permits skipping the workflow for
trivial work); this item makes it the default routing rule rather than
a discretionary exception.

**The rule.** Every feature gets a spec and the deterministic pre-commit
loop-closure gate, always; those are never gated. The expensive part,
the multi-agent review checkpoints, is gated on the four `docs/FIT.md`
conditions (production-grade, real security or compliance, decisions
outlive the author, expensive to get wrong):

- Trips two or more conditions: full path (all three checkpoints,
  multi-agent review).
- Trips zero or one: light path (spec, one quality pass, the automated
  gate), with the option to escalate to the full path on demand.

The gate self-assessment is recorded in the feature's `events.jsonl` so
the routing decision is itself auditable.

**Why this preserves every check.** No check is removed; the automated
gate runs on both paths and the full suite remains one escalation away.
Only the amount of manual review applied per feature changes, and it
changes by a documented rule instead of by discipline under deadline.
This is consistent with the `Accelerate` (DORA) finding that automated
checks plus right-sized review achieve the control goal without the cost
of heavyweight approval on every change.

**First move.** Add the gate self-assessment to
`/speckit-workflow-post-spec` (the post-spec checkpoint already runs there) so it
emits a light-or-full routing decision; wire the light path to invoke a
single quality pass instead of the full review wave.

**Source.** 2026-05 architecture simplification review; `docs/FIT.md`
four-condition test; constitution Article I trivial-work exemption.

## Tier 1: Scope expansions to existing agents

Most specialized review concerns belong inside existing agents rather
than as new standalone agents. Each entry below has:

- A specific trigger condition
- The existing agent it expands
- The new responsibility being added

Plan to expand when the trigger fires, not before.

| Concern | Trigger | Expands which agent | Notes |
|---|---|---|---|
| **API design review** | Project adds public REST/GraphQL/gRPC API | code-reviewer (post-impl) and staff-engineer (pre-impl) | REST/GraphQL conventions, versioning strategy, error semantics, OpenAPI completeness, idempotency, pagination |
| **Accessibility review** | Project has user-facing UI (web or mobile) | code-reviewer | WCAG conformance, keyboard navigation, screen reader compatibility, focus management |
| **Concurrency review** | Code introduces locks, async, or parallel processing | code-reviewer (impl-level) and staff-engineer (design-level) | Race conditions, deadlocks, async/await correctness, channel discipline, distributed locking patterns |
| **AI cost tracking (specialized)** | Framework AI spend exceeds budget for two consecutive months | measurement backbone (tooling/metrics) | Aggregate events.jsonl across features, identify high-cost patterns, recommend model downgrades. Lives in the measurement backbone because cost discipline is a coordination responsibility per Article III §3.5, and the backbone already aggregates per-agent cost from events. |
| **Model tier guidance per agent** | Per-feature total AI cost consistently exceeds $5-10 | measurement backbone (tooling/metrics) | Each agent's model (opus / sonnet) is currently specified in its frontmatter without documented rationale. When per-feature cost crosses budget thresholds, document a decision framework: which agents genuinely need opus (semantic judgment: closure-auditor, threat-modeler, staff-engineer, security-reviewer) vs which could run on sonnet (mechanical pattern matching: code-reviewer, performance-reviewer, test-architect). Captured during Phase 2.5.4 design discussion. |
| **Cost telemetry aggregation per feature** | Third feature workflow completed | measurement backbone (tooling/metrics) | Framework records per-agent cost in events.jsonl but does not aggregate. Need running cost total surfaced at each checkpoint so the user sees accumulated spend before invoking the next batch. Capture feature 001 ($1.93 through C1) as baseline benchmark; compare features 002 and 003 to detect cost drift early. Lives in the measurement backbone because cost discipline is a coordination concern per Article III §3.5. |
| **FinOps / infrastructure cost optimization** | Project's infrastructure cost exceeds team thresholds | production-readiness | Cost-of-ownership analysis for cloud resources, reserved-capacity recommendations, autoscaling-vs-fixed-fleet decisions |
| **Migration architecture** | Project includes DB schema changes or large refactors | staff-engineer | Strangler fig, parallel change, expand-contract, schema migration safety, rollback plans |
| **Privacy impact assessment** | Project processes Restricted-classified personal data | security-reviewer | DPIA structure, data minimization analysis, retention compliance, cross-border transfer review |
| **SBOM / supply chain verification** | Project targets SLSA Level 3+ or has supply-chain attestation requirements | security-reviewer | SBOM completeness, license compliance, dependency provenance, build-trust verification |
| **Chaos engineering test design** | Project has documented resilience requirements | test-architect | Failure injection scenarios, dependency degradation, network partition simulation |
| **Database schema specialist** | DB-heavy features arrive (schema design, query optimization is the work) | staff-engineer (pre-impl) and code-reviewer (impl-level) | Index design, constraint enforcement, migration safety, query plan review |
| **Data quality review** | Project includes data pipelines | code-reviewer | Validation, drift detection, lineage, freshness, quality SLOs |
| **Drift detection** | IaC baseline established and project operates in environments where manual changes can occur | production-readiness | Detects manual changes to production resources, recommends remediation |

## Tier 2: Possible new agents

These have clear use cases but warrant separate agents because their
scope is genuinely orthogonal to existing agents, OR their prompt
would push an existing agent past the 500-line tripwire.

| Item | Trigger | Notes |
|---|---|---|
| **Documentation-architect agent** | When external documentation matures into a deliverable in its own right (developer docs portal, customer-facing guides) | Information architecture, audience-appropriate writing, completeness verification. Separate from existing agents because its scope is the documentation product, not the engineering work. |
| **Compliance-evidence-collector agent** | Need automated evidence collection for SOC 2 / FedRAMP / similar audits | Continuously gathers OSCAL control evidence across the project. Separate from security-reviewer because evidence gathering is ongoing, not per-feature. |
| **On-call / incident-responder agent** | Need incident management integration | Acts during incidents; high stakes, requires careful design. NOT a postmortem author - see considered-and-rejected. |

## Tier 3: Speculative

Mentioned in conversations, no concrete plan. May graduate to Tier 1
or Tier 2 with specific evidence; may move to considered-and-rejected
with rationale.

- Multi-repo coordination (cross-repo refactors)
- Dependency-update-strategist (when to upgrade what)
- Threat-modeler-v2 with attack tree generation
- Performance-regression-detector (continuous perf monitoring vs baselines)
- Spec-quality-reviewer (specs about specs - "is this spec well-written?")

## Partial-fit project roadmap

Per `docs/FIT.md`, four project categories have **Partial** fit today
but a concrete path to **Strong** fit through framework growth. This
section tracks the framework additions needed for each category.

### Mobile apps (iOS, Android, React Native, Flutter)

Framework additions needed to earn Strong fit:

- OWASP MASTG (Mobile Application Security Testing Guide) catalog
  added to `governance-commons/catalogs/threats/`
- OWASP MASVS (Mobile App Security Verification Standard) profile
  for the OSCAL catalogs
- Mobile-specific lib-context YAMLs (React Native, Flutter, SwiftUI,
  Jetpack Compose)
- Mobile-specific playbook (app-store-rejection, certificate-expiry,
  signing-key-compromise)
- performance-reviewer scope expansion: battery profiling, network
  conditions, background execution limits, memory pressure
- threat-modeler scope expansion: device permissions, deep links,
  biometric auth, secure storage, certificate pinning

### Web frontends (React, Vue, Svelte, Angular SPAs)

Framework additions needed to earn Strong fit:

- OWASP ASVS Frontend profile for the OSCAL catalogs
- WCAG accessibility catalog added to `governance-commons/catalogs/`
- Frontend-specific lib-context YAMLs (React, Vue, Svelte, Angular)
- Core Web Vitals performance reference in lib-context (LCP, INP, CLS)
- performance-reviewer scope expansion: bundle size, hydration cost,
  client-side rendering performance
- threat-modeler scope expansion: CSP/SRI configuration, prototype
  pollution, framework-specific patterns
- code-reviewer scope expansion: accessibility review when UI work
  is in scope (per Tier 1 above)

### Libraries and SDKs

Framework additions needed to earn Strong fit:

- Semver catalog and breaking-change taxonomy in
  `governance-commons/catalogs/`
- API versioning ADR template variant (deprecation timelines,
  migration paths)
- Lib-author-specific playbook (breaking-change-announcement,
  downstream-consumer-impact-analysis)
- staff-engineer scope expansion: API design discipline (consistency
  with platform idioms, surface area discipline, deprecation cadence)
- Multi-language binding guidance for libraries with C/C++/Rust cores

### CLI tools (shipped to users)

Framework additions needed to earn Strong fit:

- CLI design conventions catalog (POSIX argument conventions, exit
  code semantics, completion script generation)
- Cross-platform distribution playbook (homebrew, scoop, apt, dnf,
  binary releases, code signing per platform)
- Lib-context for common CLI frameworks (Click, Cobra, Clap,
  Commander, Typer)
- CLI-specific constitution amendment or extension (UNIX philosophy
  alignment, composability with pipes, predictable output formats)
- Lighter-weight workflow variant for typical CLI feature scope

## Manifest dependency-graph validation (consumer side)

**Priority:** P1 (build note attached to the manifest format work, which is already on the critical path)

**Trigger:** The governance manifest format is built. The manifest maps each checkpoint and agent to the substrate catalogs and constitution slices it must consult. The moment that mapping exists as a file the routing layer and agents read, it can contain the same structural defects any dependency graph can: cycles, references to catalogs that do not exist, duplicate entries.

**Context:** The consumer-side manifest is a directed graph. Checkpoints depend on prior checkpoints; agents depend on the catalogs named for them; constitution slices reference articles that must exist. Without validation, a malformed manifest fails silently at runtime: an agent is told to consult a catalog that was renamed, or a checkpoint references an agent that was retired, and the consuming agent either skips the consultation or errors mid-wave. Both are worse than failing loudly at build time.

This is the consumer-layer half of a pattern that also appears on the substrate side (catalog-to-catalog cross-reference validation on the substrate side). The two halves share an implementation reference but validate different graphs: this entry validates the manifest the runtime consumes; the substrate entry validates cross-references between authored catalogs.

### Implementation reference

OpenSpec's artifact-graph validator (`src/core/artifact-graph/schema.ts`, reviewed at source) is a clean, compact reference for exactly this: roughly a hundred lines doing depth-first cycle detection, requires-reference resolution against a known-ID set, and duplicate-ID detection, with the cycle path reported on failure. Mirror its three checks rather than inventing validation from scratch:

1. **Duplicate detection** - no checkpoint or agent entry appears twice.
2. **Reference resolution** - every catalog, constitution article, and agent named in the manifest resolves to something that exists in the substrate or the agent roster.
3. **Cycle detection** - checkpoint dependencies form a DAG, not a loop.

### Where it runs

Validation runs at framework build time (when the manifest is assembled or changed), before the runtime ever consumes it. The runtime should never receive an invalid manifest. This keeps the failure at authoring time, where it is cheap, rather than mid-wave, where it is expensive and confusing.

### Shared implementation decision (resolved)

The manifest validator and the substrate-side catalog cross-reference validator share ONE implementation, not two parallel ones. Decision and rationale:

- **One shared graph-validation module, two thin adapters.** The core module takes a generic graph (labeled nodes plus directed dependency edges) and runs the three checks: duplicate-ID detection, reference resolution against the known-ID set, and DFS cycle detection with the cycle path reported. The manifest validator is a thin adapter that parses the manifest into that node/edge form; the catalog cross-reference validator is a thin adapter that parses catalog cross-references into the same form. The three checks are the same algorithm regardless of whether a node is a checkpoint or a catalog; only the parsing differs. Two implementations would duplicate the DFS and risk divergent cycle-detection behavior and error formats.

- **Both live in the framework's `scripts/`.** This is not a cross-world coupling. The substrate's existing validators (`scripts/validate-catalogs.sh`, `scripts/validate-profiles.sh`, and the rest) already live in the root `scripts/` directory, not inside `governance-commons/`; the substrate is pure content and all validation tooling is framework tooling. The manifest validator (consumer content) and the catalog cross-reference validator (substrate content) are both framework tooling operating on different content, so they sit naturally side by side and share the module without either world depending on the other in a new way.

- **Python, invoked by the existing bash orchestration.** Graph traversal with recursion and cycle-path reconstruction is fragile in bash 3.2 (the substrate scripts' compatibility target). Python is already a hard dependency: `check-jsonschema` is a Python tool and `.claude/hooks/verify_loop_closure.py` already establishes author-written Python as first-class. The shared module is Python; the existing bash validators (and `validate-all.sh`) invoke it the same way they orchestrate the current validators, preserving the established pattern.

- **Suggested shape:** a shared module (for example `scripts/lib/graph_validation.py`) exposing the three checks over a generic graph, plus two entry points (`scripts/validate-manifest.*` and `scripts/validate-catalog-refs.*`) that parse their respective sources and call it. `validate-all.sh` gains the catalog-refs entry; the manifest entry runs at manifest-build time on the consumer side.

### Why P1 not deferred

This is not really a future feature; it is a build note on the manifest work already prioritized. When the manifest lands, its validator should land with it. Tracking it here so the validator is not forgotten as a separate step.

### Cross-reference

- Substrate-side companion: catalog cross-reference DAG validation on the substrate. Same shared module; build the two together so the graph core is written once.
- Depends on: the manifest format itself (the P1 manifest-implementation item).

## Considered and rejected

Tracking decisions explicitly to prevent re-litigation.

### Postmortem-author agent

**Considered**: agent that drafts blameless postmortems from incident
data.

**Rejected because**: the framework's value proposition is producing
production-grade code that anticipates traps. Postmortems are about
what happens AFTER traps fire - a different lifecycle phase entirely.
The trap-anticipation work IS captured by threat-modeler, performance-reviewer,
and production-readiness; they surface the kinds of issues that, if
ignored, become postmortems later. Adding postmortem authorship would
stretch the framework's scope beyond engineering into incident
management.

**Revisit if**: the framework explicitly expands into post-incident
lifecycle support (currently out of scope per design discussion in
Phase 2.5.2).

### Product / feature ideation agent

**Considered**: agent that discusses what features make sense for an
application - market analysis, investor narrative, customer fit.

**Rejected because**: this is product management, not engineering.
Upstream of the framework's spec-driven workflow, which assumes a
feature description already exists. Stretching the framework into
product strategy would (a) compete with dedicated product tools
(Linear, Aha, ProductBoard), (b) require domain expertise the
framework doesn't model, (c) probably underperform - product
strategy needs context AI can't synthesize from a constitution.
Adjacent to BMAD's territory; intentionally not duplicated here.

**Revisit if**: a specific narrow product-engineering bridge use case
emerges (e.g., translating PRD into spec.md) with bounded scope.

### Super-agents combining multiple cognitive lenses

**Considered**: combining multiple agents into "super-agents" (e.g.,
one general-review agent instead of separate code-reviewer +
security-reviewer + performance-reviewer).

**Rejected because**: token economics favor specialized agents.
A focused specialist with a tight prompt processes a spec for ~30k
tokens. A super-agent doing three lenses against the same spec is
~80k tokens - more than three separate invocations because each
concern's context bloats the others. Also: specialized agents have
sharper output, easier skip semantics, and clearer tool allowlists.
The framework's value comes from the specialized-cognitive-lens
claim, not from "one big AI does everything."

**Revisit if**: model context windows grow such that token economics
flip, OR a use case emerges where cross-lens correlation in a single
context matters more than sharp specialization.

**Revisited 2026-05-29** during an architecture simplification review
that proposed consolidating the then-eleven agents into roughly five (merging
the post-implementation reviewers into one graded reviewer). Re-rejected
on the original token-economics grounds: a single reviewer loading five
lenses' worth of catalog context per invocation reproduces the
token-bloat problem that is the framework's number-one open question, and
same-family reviewers hit a correlated-error ceiling that fewer-but-broader
agents do not fix. The quality lever is layer diversity and measurement
(see `docs/ENHANCEMENT-ROADMAP.md` P0 item 2), not agent count in either
direction. Recorded to prevent re-litigation.

### BMAD framework

**Considered**: as an alternative to spec-kit for spec-driven workflow.

**Rejected because**: BMAD is designed for enterprise teams with
defined roles (analyst, architect, scrum master, dev, QA). The
overhead of maintaining role personas for a solo developer is high
relative to value delivered. spec-kit's lighter weight and tighter
integration with Claude Code is a better fit.

**Revisit if**: team grows past 5+ contributors with specialization,
or BMAD's tooling evolves toward solo-dev ergonomics.

### Generic "performance optimization" agent

**Considered**: agent that suggests performance improvements.

**Rejected because**: collapses into the optimization-theater
anti-pattern. Without profiler data, suggestions are speculative.
Real optimization needs measurement first. The performance-reviewer
agent covers the high-value case (catching resource-exhaustion
patterns before production).

**Revisit if**: profiling integration matures and an agent can
operate on real data rather than guesses.

### Automated documentation generator

**Considered**: agent that writes docs from code.

**Rejected because**: generated docs are usually useless. They
either restate the code (no value) or invent plausible-sounding
but incorrect descriptions. Good docs require human judgment
about what the reader needs.

**Revisit if**: a specific high-value use case emerges (e.g., API
reference from OpenAPI spec, where source-of-truth is well-defined).

### Refactoring-specialist agent

**Considered**: agent dedicated to refactoring suggestions.

**Rejected because**: refactoring decisions are tightly coupled
to feature work. The staff-engineer agent already raises refactor
opportunities when they're relevant. A dedicated agent would
either duplicate this or focus on speculative refactoring (anti-pattern).

**Revisit if**: large legacy migration project surfaces with
specific refactoring patterns to apply systematically.

### Convention-enforcer agent

**Considered**: agent that enforces project-specific conventions.

**Rejected because**: that's what linters and formatters are for.
Agents are expensive cognitive work; checking that imports are
sorted is not cognitive work.

**Revisit if**: project develops conventions that can't be expressed
in linter rules (rare; usually means the convention is wrong).

### Pair-programmer agent

**Considered**: continuous companion during implementation.

**Rejected because**: Claude Code itself already serves this role.
The twelve agents are for **discrete cognitive tasks** with bounded
scope, not for general assistance.

**Revisit if**: a specific pair-programming subtask emerges that's
distinct from general Claude Code use.

### Test-runner / CI-debugger agent

**Considered**: agent that runs tests and explains failures.

**Rejected because**: test-running is mechanical; debugging failures
is the human's job (with Claude Code's general assistance). A
dedicated agent adds no value beyond running `pytest` and reading
the output.

**Revisit if**: CI failures involve recurring patterns that
benefit from specialized analysis (e.g., flaky test detection
across hundreds of runs).

### Architecture-diagram-generator

**Considered**: agent that generates Mermaid/architecture diagrams.

**Rejected because**: diagrams generated from code drift quickly
from intent. Diagrams should express intent (what the architect
wanted), not just what currently exists. Human-authored is better.

**Revisit if**: a specific diagram type emerges that's mechanical
(e.g., sequence diagrams from OpenTelemetry traces).

### Code-archeology agent

**Considered**: agent that explains "why is this code this way?"
by walking git history.

**Rejected because**: useful occasionally, but rare enough that
on-demand `git blame` + `git log` + Claude Code's general
assistance handles it.

**Revisit if**: legacy codebase migration project surfaces with
heavy archeology needs.

### License-compliance reviewer

**Considered**: agent that checks dependency licenses.

**Rejected because**: tooling like FOSSA, Snyk, OSV-scanner handles
this better than an LLM agent. The supply-chain check in
security-reviewer covers the common cases.

**Revisit if**: license complexity grows (e.g., shipping software,
distributing binaries, license obligations beyond use).

### Executive workflow-orchestrator (sub-agent invoking other sub-agents)

**Considered**: workflow-orchestrator as executor - invokes upstream
challengers, downstream verifiers, and closure-auditor directly via
the Task tool rather than producing a plan for the main session to
execute.

**Rejected because**: Claude Code platform limitation
(anthropics/claude-code#4182) prevents sub-agents from invoking
other sub-agents via Task. Phase 2.5.3 adopted the advisory router
pattern as a workaround: orchestrator produces structured plans
with tier markers; main session executes. The forced separation
turned out to be a feature - routing and execution are different
cognitive concerns and benefit from being in different layers. The
orchestrator focuses on which-agents-when without the entanglement
of also persisting state and managing parallel batches.

**Superseded**: the routing layer was later retired entirely (Phase C).
Routing proved fully deterministic given the operator-approved plan, so it
became the dispatcher (`tooling/dispatch/dispatch.py`), not an agent. An
executive orchestrator is moot - there is no routing agent left to make
executive; the main session runs the dispatcher (tooling) and invokes the
agents directly. The #4182 limitation no longer bears on routing.

## events.jsonl drift instrumentation and the error model

**Priority:** P1 (cheap, high-leverage, and the buildable precursor to the
P0 error-budget work; it makes drift visible before any golden dataset
exists).

**Trigger:** Wanting to know whether the framework is drifting (governance,
routing, scope, cost) or whether a cost or quality change actually held,
without waiting for the full evaluation harness. A first live feature
run is the first producer of the events this consumes.

**Context:** "Error" was conflated across four distinct things (correctness,
completeness, intent drift, judge error) on two axes (product versus judge).
`docs/ERROR-AND-DRIFT-MODEL.md` now defines them operationally and separates
error (distance from a known-correct answer) from drift (directional movement
over iterations). That model shows a useful split: a real subset of drift is
measurable from `events.jsonl` today with arithmetic alone, while correctness
and judge accuracy need ground truth that does not yet exist.

**The work, phased (full detail in `docs/ERROR-AND-DRIFT-MODEL.md`):**

- **Phase 1 (buildable now, no schema change):** a read-only reducer that turns
  a feature's or an aggregate's `events.jsonl` into a drift vector:
  closure-rejection rate, routing-versus-findings mismatch (a `light`-routed
  feature that later raises a P1 or a threat/security finding), deferral aging,
  override trend, P1-at-commit (a guardrail-breach counter), cost-per-feature
  drift, and decline rate per agent. Descriptive only; never a gate.
- **Phase 2 (one additive, non-enforcing event):** a `verification` event so
  deterministic check outcomes (test, build, lint, hook) enter the stream,
  giving correctness (E1) a measured home. No cooling-off (changes no gate).
- **Phase 3 (the P0 error-budget item / F2):** closure-auditor calibration and
  per-layer accuracy against a labeled golden dataset, which is the only point
  at which an acceptable error rate becomes a number. Seeded by the live-test
  events.

**Why P1 not deferred:** Phase 1 costs little, has no dependency, and converts
the abstract "are we drifting?" worry into a small JSON object the author can
watch each feature. It also de-risks F2 by proving the event stream carries
the needed signal before the harness is built.

**Cross-reference:** `docs/ERROR-AND-DRIFT-MODEL.md` (the model and the event
shapes), `docs/ENHANCEMENT-ROADMAP.md` P0 item 2 (the calibration this leads
to), `docs/FOUNDATIONS.md` (the self-evaluation and error-budget open
question), `.claude/docs/agent-coordination.md` (the event log the reducer
reads).

## Recurring review processes

The framework has maintenance cadences. These reviews keep the
framework current as the world changes.

| Review | Cadence | Trigger | Owner |
|---|---|---|---|
| **Agent roster review** | Annual | Year boundary | Principal |
| **Scope discipline audit** | Annual | Year boundary; per `.claude/docs/agent-coordination.md` audit checklist | Principal |
| **lib-context review** | Quarterly | Quarter boundary | Principal |
| **Threat catalog review** | Quarterly | OWASP/MITRE releases | Principal |
| **AI pricing review** | Quarterly | Quarter boundary | Principal |
| **Environment topology review** | Annual | Year boundary | Principal |
| **Constitution review** | Annual | Year boundary | Principal |
| **OSCAL profile review** | Annual + on regulatory changes | Compliance need | Principal |
| **Cedar policy review** | Semi-annual | Policy gap surfacing | Principal |
| **Playbook review** | Annual | Year boundary | Principal |
| **Considered-and-rejected review** | Annual | Year boundary | Principal |
| **Partial-fit roadmap review** | Annual | Year boundary; per `docs/FIT.md` partial-fit categories | Principal |
| **Decline-event calibration** | Per project; or quarterly aggregate | Repeated declines from same agent | Principal |

Each review asks:

1. Is this still right? (does evidence support keeping it?)
2. Is anything missing? (have failure modes emerged?)
3. Is anything obsolete? (have circumstances changed?)
4. Should anything graduate from FUTURE.md?

Output of each review: the decisions made are recorded by updating or graduating the affected `FUTURE.md` entries.

## References

- Constitution: `.specify/memory/constitution.md`
- Agent coordination: `.claude/docs/agent-coordination.md`
- Project fit: `docs/FIT.md`
- AI compatibility: `docs/AI-COMPATIBILITY.md`
- Retrofit guide: `docs/RETROFIT.md`
- Governance commons: `governance-commons/`
- ADR pattern: `docs/decisions/`
