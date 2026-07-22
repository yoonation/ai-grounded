<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Enhancement roadmap

A single reviewable list of candidate work to improve the framework,
synthesized from the root backlog (`FUTURE.md` for the agent roster) and
the agentic-design-patterns reference.

This is a menu, not a commitment. Each item is something you can choose to
apply or not. Items are not deleted when deferred; they stay here with a
status tag.

## How to read this

Priority tiers follow a P0-P3 index, extended to cover the
substrate-design-debt and agent-roster items:

- **P0** blocks or undermines everything else; every other item compounds
  against these if they are not addressed first.
- **P1** sets architectural direction; decisions here shape downstream work.
- **P2** is a design improvement that should wait until the relevant P0/P1
  item lands.
- **P3** is future work once the foundations are stable.

Status tags use the same legend as `FOUNDATIONS.md`: `[IMPLEMENTED]`,
`[PARTIAL]`, `[PLANNED]`, `[ASPIRATIONAL]`, `[REJECTED]`. The durable
architectural forks behind several of these are in the `FOUNDATIONS.md`
open-questions
section. This roadmap is the actionable companion: FOUNDATIONS states the
fork, this doc states the work and the recommended first move.

This roadmap covers framework *enhancements*. It is distinct from the
substrate *authoring* milestone roadmap (M4 through M9), which is the plan
for authoring the remaining concern catalogs.

## Scope boundary that governs several items

Charter Article III 3.2 forbids AI from authoring rule-intent text. Several
items below (loop-world evolution, SkillOpt, the context-encoder agent)
are scoped by it: they may operate on lib-context, mappings, and exported
artifacts, but never on concern-catalog rule intent. Where an item touches
this line, it is noted.

---

## P0: do these first

### 1. Token-bloat reduction program

**What.** Reduce always-loaded and per-invocation context so the framework
stops producing the context-rot problem it exists to solve. Always-loaded
preamble (CLAUDE.md, AGENTS.md, the constitution) plus large agent prompts
and catalogs run to tens of thousands of tokens before any work starts.

**Why.** Direct tension with the Small Grounded Requests principle. Every
other roadmap item makes loading heavier unless this lands first. Highest
self-identified priority.

**The eight mitigations, ordered by ease and leverage.**
1. Prompt caching with explicit cache breakpoints on catalog loading. The
   lowest-friction win; ship first regardless of other choices. `[PLANNED]`
2. Model routing per agent (opus for judgment, sonnet/haiku for mechanical).
   `[PLANNED]`
3. Manifest-driven lazy catalog slicing (agents read manifest-specified
   slices, not whole files). `[PLANNED]`
4. Constitution slicing per agent (most agents need 2-3 articles, not 853
   lines). `[ASPIRATIONAL]`
5. Agent-prompt deduplication (extract shared framework summaries to a
   shared location, reference rather than inline). `[ASPIRATIONAL]`
6. CLAUDE.md and AGENTS.md diet (audit every line; target both under 150 to
   200 lines). `[ASPIRATIONAL]`
7. Catalog-format slimming (OSCAL metadata to a sidecar, keep intent plus
   examples plus severity in the loadable file). `[ASPIRATIONAL]`
8. Rule-deferral via summarization (auto-generated catalog summary loads by
   default, full catalog loads on explicit request). `[ASPIRATIONAL]`

**First move.** Ship prompt caching (1) and start the CLAUDE.md/AGENTS.md
diet (6). For high-openness execution, pick the smallest set (1, 3, 6) and
ship before reaching for more.

**Source.** FOUNDATIONS open question "token bloat."

### 2. Self-evaluation and error-budget instrumentation

**What.** Define an acceptable error rate as a number, define "wrong"
operationally, and measure per-layer accuracy and correlation, starting
with closure-auditor (the keystone with no outer auditor). The operational
definition of "wrong" (the four error types E1 to E4, the product-versus-judge
axes, and error-versus-drift) lives in `docs/ERROR-AND-DRIFT-MODEL.md`; this
item is that model's Phase 3.

**Why.** The framework has every verification layer reliability engineering
calls for and zero measured error rates on any of them except the
deterministic pre-commit hook. AI reviewer layers are in one model family,
so their errors are correlated and do not compose to the naive multiplied
reliability. The framework cannot honestly tell a consumer what reliability
they are buying at what cost until this exists. This is the framework's
self-evaluation weakness.

**Components.**
- A golden dataset of 10 to 20 real code snippets with known issues.
- LLM-as-judge harness measuring per-layer accuracy.
- closure-auditor calibration (the single most important measurement).
- A precursor that needs no golden dataset: the `events.jsonl` drift vector
  (closure-rejection rate, routing-versus-findings mismatch, deferral aging,
  override trend, P1-at-commit, cost drift, decline rate), buildable now from
  existing event types. Tracked in root `FUTURE.md`; see ERROR-AND-DRIFT-MODEL
  Phase 1.
- A `verification` event so deterministic check results (test, build, lint,
  hook) enter the stream, giving correctness (E1) a measured home
  (ERROR-AND-DRIFT-MODEL Phase 2).
- Diversity of layers over quantity: vary model family, prompting strategy,
  deterministic checks, and sampled human review.
- Metrics beyond accuracy (per the agentic-design-patterns rubric):
  decision-path visibility, per-step metrics, drift tracking.

**First move.** Build the closure-auditor calibration harness against a
small golden dataset. Everything else extends from that measurement.

**Status.** `[ASPIRATIONAL]`. **Source.** Review
finding; agentic-design-patterns rubric; FOUNDATIONS open question
"self-evaluation and error-budget gap"; `docs/ERROR-AND-DRIFT-MODEL.md`.

### 3. Cross-boundary coordination hardening

**What.** Make the substrate's coordination across five boundaries
explicit, with primitives and attestation discipline for each: across
sessions over time, across humans on a team, across parallel agents, across
model vendors, across model versions.

**Why.** Every model upgrade (Opus 4.8 and successors) narrows the
within-session value of governance content. The defensible position is the
coordination a single model session never touches. The substrate has strong
within-substrate coordination (lifecycle, versioning, OSCAL) and almost no
explicit across-substrate coordination.

**Concrete moves, in the recommended hardening order (4, 5, 3,
1, 2 by leverage).**
- Boundary 4 (vendors): SKILL.md export and AGENTS.md as entry point; see
  P0 item 4 below.
- Boundary 5 (versions): per-rule `compatible-model-versions` metadata plus
  build-time validation; see P1 items.
- Boundary 3 (agents): manifest plus substrate-as-MCP-server; see P1 items.
- Boundary 1 (sessions): a `current-substrate-state` pointer plus
  decision-path retrieval; see P1 items.
- Boundary 2 (humans): CODEOWNERS, a multi-author attestation Charter
  amendment, review rotation.

**Status.** `[ASPIRATIONAL]`. **Source.** FOUNDATIONS
open question "cross-boundary coordination under model-version pressure".

### 4. Operational delivery layer: plugins, SKILL.md, hooks

**What.** Package substrate content as installable plugins that bundle
SKILL.md skills (just-in-time knowledge), settings.json hooks (enforced
gates), and an MCP server (live tool access). The substrate already has the
content; this is the missing packaging and distribution layer.

**Why.** Without this, substrate content lives as files the agent may or may
not read. With it, content runs as one-command-installable plugins. The
industry (Anthropic, OpenAI, AWS, Google, NVIDIA) has converged on this
host-plus-MCP-plus-skills-plus-rules pattern.

**The five concrete substrate-side moves.**
1. Plugin manifest export pipeline: a deterministic build emitting one
   plugin per concern from canonical OSCAL, published to a separate
   marketplace repo. `[ASPIRATIONAL]`
2. SKILL.md authoring discipline: per-concern SKILL.md whose frontmatter
   carries substrate metadata and whose body is a short intro with
   supporting files loaded only when referenced (progressive disclosure).
   Mechanical export from OSCAL, so Charter 3.2 is preserved. `[ASPIRATIONAL]`
3. settings.json hook templates per profile: L1 PostToolUse hooks (format
   checks, scanner runs), L2 Agent hooks (review subagent on high-risk
   actions), Stop hooks (session-close validation). `[ASPIRATIONAL]`
4. MCP server for catalog access (M5 deliverable): `query_catalog`,
   `get_rule`, `list_applicable_rules`, `get_decision_framework` over the
   OSCAL files. `[PLANNED]`
5. Pre-compute context-encoder agent (Meta-inspired): a background tool that
   reads a consumer repo and emits a tiny per-repo context file the host
   loads at session start instead of the full catalog set. Encodes rather
   than authors, so not blocked by Charter 3.2. `[ASPIRATIONAL]`

**Vendor practices worth adopting:**
Anthropic hook precedence (deny over defer over ask over allow) and the
block-source pattern; Codex 100-percent-PR-review as enforcement-via-agent
and test-first with AGENTS.md; Kiro one-click "powers" registry bundling and
multi-model routing; Google multi-host portability through standardized
skills; NVIDIA bidirectional MCP and OpenTelemetry observability (emit
events.jsonl in OTel format); Meta pre-compute and tribal-knowledge
encoding (validates the playbook category); Netflix centralized context plus
configuration-management discipline.

**Honest gaps to plan for.** Plugin distribution becomes infrastructure work
(a GitHub Actions pipeline). Hook reliability becomes a substrate quality
property (fail-open on internal errors, fail-closed on policy decisions,
paired test discipline). Plugin governance scales with plugin count and
needs a bundle mechanism by substrate 1.5 or later.

**First move.** Author one worked plugin (authentication) by hand to lock
the shape, then build the export pipeline to generate the rest.

**Source.** FOUNDATIONS open questions on Agent Skills
and packaging; RESEARCH industry-convergence entry.

---

## P1: architectural direction

These set direction; several are decisions as much as work. Each is a fork
recorded in the FOUNDATIONS open-questions section.

- **Manifest implementation.** Build the manifest format so agents read
  per-checkpoint slices. Direct fix for P0 item 1. Includes deriving each
  checkpoint's rule set from the profile via a selector rather than a
  hand-listed enumeration, so the profile stays the single source of truth
  and `project-manifest.yaml` cannot drift from it. `[PLANNED]`
- **Risk-gated default workflow path.** Make the light-or-full routing
  decision the default: every feature gets a spec and the deterministic
  pre-commit gate, while the multi-agent review checkpoints are gated on
  the four `docs/FIT.md` conditions (two or more triggers the full path).
  Removes no check; right-sizes the manual ceremony so the framework is
  run rather than bypassed. Detail in root `FUTURE.md`. `[PLANNED]`
- **Constitution slicing.** Same mechanism applied to the constitution.
  Depends on the manifest landing first. `[ASPIRATIONAL]`
- **AI-safety / agentic-AI concern catalog (M5).** Eleven coverage-gap
  records across four mappings point to it. Direct relevance to the AI
  Security Architect framing. Open decision: one catalog or two
  (responsible-ai for the model layer, agentic-systems for orchestration).
  M5 now also includes authoring the **OWASP Agentic Skills Top 10**
  threat catalog (AST01-10, a distinct OWASP project from the ASI Agentic
  Applications Top 10 already shipped) plus an AST-to-concerns mapping,
  covering the skill layer that the framework's own `.claude/skills/`
  exposes. This completes the three-layer threat picture (model /
  orchestration / skill). The AST artifact is at candidate stage upstream,
  so the catalog is authored narrow and upstream-anchored with a maturity
  note rather than as a comprehensive build. `[PLANNED]`
  `[PLANNED]`
- **Catalog-format escape decision.** The framework's initial target was 50-line
  catalogs; reality is 1,500 to 3,800 lines. Decide: is OSCAL the runtime
  carrier or only the authoritative archive, with slim Markdown derivatives
  loaded at runtime? `[ASPIRATIONAL]`
- **No-loop versus loop evolution.** Decide whether the substrate evolves
  continuously from feature signals or stays static between manual reviews.
  External evidence increasingly favors loop in production; Charter 3.2
  bounds it to lib-context and mappings. Charter-level decision. `[ASPIRATIONAL]`
- **Lib-context as governance-overlay.** Shrink lib-context cards from
  "teach the library" to "the governance-overlay slice domain skills omit."
  Addresses P0 token bloat (60 to 70 percent reduction projected) and slows
  lib-context decay. `[ASPIRATIONAL]`
- **Plugin-shaped versus template-shaped packaging.** Likely a hybrid:
  plugin-shaped substrate, template-shaped consumer side. Phase 3.0-level
  decision that shapes discovery, adoption, and upgrades. `[ASPIRATIONAL]`
- **Per-rule validity windows (time-scoping).** Add effective-from,
  optional effective-until, and optional jurisdiction-scope as first-class
  rule properties. Lifecycle state is coarser than this. Relevant for
  regulatory work with effective dates. `[ASPIRATIONAL]`
- **Decision-path retrieval primitive.** Embedding-based retrieval over
  historical ADRs so an agent can surface "three prior decisions in similar
  contexts" alongside the abstract decision framework. Raw material exists in
  events.jsonl plus ADRs. `[ASPIRATIONAL]`
- **AGENTS.md and SKILL.md as runtime delivery format.** Author in OSCAL,
  export SKILL.md for any standards-conforming host. Hardens the cross-vendor
  boundary. `[ASPIRATIONAL]`
- **Per-rule compatible-model-versions metadata.** Record which model
  versions a rule has been validated against, with measured accuracy, so a
  new model release flags rules needing re-validation. Pairs with build-time
  validation. Hardens the cross-version boundary. `[ASPIRATIONAL]`
- **Hooks as policy-as-code at the agent layer.** Lift enforcement from the
  git layer (pre-commit, after the work is done) into the session via
  PreToolUse hooks (block edits to secrets files, block destructive
  commands, require approval before posting). The deterministic L1 layer of
  the error-budget stack. `[ASPIRATIONAL]`
- **Pre-compute context-encoder agent.** The manifest concept at Meta scale;
  see P0 item 4 move 5. `[ASPIRATIONAL]`
- **Registry-ID drift remediation (Tier 1).** A large share of upstream L1
  references are reported dead. This is a credibility risk for an
  audit-grade tool, making Tier 1 worth doing early.
  `[PLANNED]`

---

## P2: design improvements that wait for P0/P1

**Research-pattern adoption (patterns, not frameworks).**
- Test-time-compute selection (RTV) at high-stakes checkpoints only (rule
  promotion, contested P1 closures, ADR overrides). Universal use would
  multiply cost. `[ASPIRATIONAL]`
- SkillOpt pattern for catalog and lib-context evolution under bounded
  validated edits. Scope to lib-context and mappings per Charter 3.2.
  Recommended path: park now, adopt the pattern (not the framework) later.
  `[ASPIRATIONAL]`
- Optimization landscape strong defaults: prompt caching and constitutional
  self-critique (nearly free, high leverage), lazy catalog loading via
  manifest, budget circuit breakers. The remaining candidates (CoVe, process
  reward models, Voyager-style skill library, plan caching,
  self-consistency voting) are a menu, not a checklist. `[ASPIRATIONAL]`
- Build-time agent regression testing: when an agent prompt changes, replay
  it against historical features to confirm it still raises the right items.
  SkillOpt held-out validation applied at the agent-prompt level. Connects
  to the error-budget P0. `[ASPIRATIONAL]`

**Observability (from the agentic-design-patterns rubric and NVIDIA
practice).** Emit events.jsonl in OpenTelemetry format for ingestion by
existing platforms; add decision-path visibility, per-step metrics, drift
tracking, and replayability. `[ASPIRATIONAL]`

**Substrate design debt (listed here for visibility).** L2 binding format schema
validation; L2 binding metadata-drift check; decision-framework body
validation; CodeQL as a parallel binding kind; Trestle integration
evaluation; OSCAL schema migration consideration; usability-statement
publication (M6/M7); L1-enforcement coverage disclosure in the
consumer-facing surface; registry-ID audit tooling skeleton (M8). Mixed
`[PLANNED]` and `[ASPIRATIONAL]`.

**Agent roster (tracked in root `FUTURE.md`).** Tier 1 scope expansions to
existing agents (API design, accessibility, concurrency, AI cost tracking,
model-tier guidance, cost telemetry/FinOps, migration architecture, privacy
impact, SBOM/supply-chain, chaos engineering, DB schema, data quality, drift
detection). Tier 2 new agents (documentation-architect,
compliance-evidence-collector, on-call/incident-responder). `[PLANNED]`

**Storage and vocabulary.** Graph view derived from OSCAL for runtime query
performance (OSCAL stays canonical; a loader builds a property-graph index).
Vocabulary refinements: "applicability" alongside "manifest," "decision
context" over "governance assets." Reframe the Amazon outage evidence
(the AI-as-cause claim is disputed). `[ASPIRATIONAL]`

---

## P3: future, once foundations are stable

- **Brownfield onboarding workflow** and the partial-fit roadmap (mobile,
  web frontends, libraries/SDKs, CLI tools). Top-priority entry in root
  `FUTURE.md`, but gated behind the P0/P1 foundations. `[PLANNED]`
- **Packaging shape (plugin vs template).** May ship both packaging shapes,
  or launch with plugin-shaped substrate alone (open question under the
  packaging decision). `[ASPIRATIONAL]`
- **Multi-project, executive reporting, leadership tooling.** v8 Phases 3.8
  to 3.11. `[ASPIRATIONAL]`
- **Tier 3 speculative agents.** Root `FUTURE.md`. `[ASPIRATIONAL]`

---

## Explicitly rejected (do not revisit without new information)

Recorded so they are not re-proposed. Full rationale in root `FUTURE.md`
"Considered and rejected."

- Super-agents combining multiple cognitive lenses (token economics).
  `[REJECTED]`
- Generic "performance optimization" agent, automated documentation
  generator, refactoring-specialist, convention-enforcer, pair-programmer,
  test-runner/CI-debugger, architecture-diagram-generator, code-archeology,
  postmortem-author, product-ideation agents (each rejected for a specific
  reason in `FUTURE.md`). `[REJECTED]`
- Adopting BMAD as the framework. `[REJECTED]`

---

## Companion documents

- `FOUNDATIONS.md` for the durable identity and the open architectural
  questions behind the P0 and P1 items.
- `FUTURE.md` (root) for full detail on the agent roster.
