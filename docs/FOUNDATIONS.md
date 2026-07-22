<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Foundations

The durable "why" of this framework: its identity, its philosophy, the
mental model it operates under, and an at-a-glance register of what it
has versus what it intends to have.

This document holds the framework's stable narrative and claims. It does
not restate the substrate's twelve architectural principles, which are
canonical in `governance-commons/spec/principles.md` (P1-P12) and are
referenced here, never duplicated.

Reading order for newcomers: `README.md`, then this file, then
`governance-commons/README.md`, then `.claude/docs/agent-coordination.md`.

---

## Conventions and extension

These conventions are defined once here and referenced by the other
companion documents (for example `docs/ENHANCEMENT-ROADMAP.md`).

### Status legend (has versus wants)

Every capability and claim in the companion documents carries one tag so
a reader can tell reality from intention at a glance. The legend mirrors
the substrate's own lifecycle vocabulary in
`governance-commons/spec/rule-lifecycle.md` rather than inventing a
parallel system.

| Tag | Meaning | Maps to existing vocabulary |
|---|---|---|
| `[IMPLEMENTED]` | The framework has this capability now, verifiable in the repo | STABLE / feature-complete |
| `[PARTIAL]` | Exists but with known, documented gaps | draft / feature-complete-with-gap-records |
| `[PLANNED]` | Committed on the roadmap | FUTURE.md accepted item / a milestone |
| `[ASPIRATIONAL]` | Wanted, not yet committed | FUTURE.md speculative (Tier 3) |
| `[REJECTED]` | Considered and rejected | FUTURE.md considered-and-rejected |

`[REJECTED]` entries link to the FUTURE.md rationale so decisions are not
re-litigated.

### How to extend these documents

Changes follow the substrate's existing amendment discipline (P8 in
`governance-commons/spec/principles.md`), not a new parallel process:

1. Propose the change with the trigger that makes it needed.
2. Record alternatives considered and why each was rejected.
3. For solo work, self-review with a 24-hour cooling interval before
   promoting any item from `[ASPIRATIONAL]` or `[PLANNED]` to
   `[IMPLEMENTED]`.
4. Update the owning document only. Each fact lives in exactly one place:
   the narrative and claims here. Never restate a fact across documents;
   cross-reference instead.

Review cadence: these documents are reviewed at the milestone and
year-boundary cadences already listed in `FUTURE.md`.

---

## Capability register

The single at-a-glance view of what the framework has versus what it
wants. It does not replace `README.md` (status), `docs/FIT.md` (project
fit), or the `FUTURE.md` backlog; it points to them.

| Capability | Status | Evidence or pointer |
|---|---|---|
| Spec-driven workflow on spec-kit (specify, clarify, plan, tasks, implement) | `[IMPLEMENTED]` | `.specify/`, `README.md` workflow |
| Risk-gated default workflow path (light or full, gated on FIT conditions) | `[PLANNED]` | root `FUTURE.md` "Workflow: risk-gated default path" |
| 7-article project constitution | `[IMPLEMENTED]` | `.specify/memory/constitution.md` |
| Twelve specialized sub-agents (eleven review in seven categories + discovery) | `[IMPLEMENTED]` | `.claude/agents/`, `.claude/docs/agent-coordination.md` |
| Wave-based parallel dispatch with sequential wave gating | `[IMPLEMENTED]` | `.claude/docs/agent-coordination.md` |
| Priority-aware loop closure (three layers: claim, semantic audit, mechanical hook) | `[IMPLEMENTED]` | `closure-auditor.md`, `verify_loop_closure.py` |
| Read-only advisor agents (parallel reads, single-threaded writes, gated actions) | `[IMPLEMENTED]` | agent tool allowlists; Cedar `tool-allowlist.cedar` |
| Governance substrate: threat catalogs (STRIDE, OWASP LLM, OWASP Agentic ASI, MITRE ATLAS) | `[IMPLEMENTED]` | `governance-commons/catalogs/threats/` |
| Eleven concern catalogs (OSCAL, L1/L2/L3 rules) | `[IMPLEMENTED]` | `governance-commons/catalogs/concerns/` |
| Compliance catalogs and mappings (NIST 800-53/171/SSDF/CSF, NIST AI RMF, EU AI Act; ISO 42001, SOC 2 reference-only) | `[IMPLEMENTED]` | `governance-commons/catalogs/compliance/`, `mappings/` |
| Cedar policy primitives and incident playbooks | `[IMPLEMENTED]` | `governance-commons/policies/`, `playbooks/` |
| Attestation specs (SLSA, in-toto) | `[IMPLEMENTED]` | `governance-commons/attestation/` |
| Spec-kit preset architecture (customizations survive upstream refresh) | `[IMPLEMENTED]` | `presets/spec-driven-governance/`, `README.md` |
| Cost attribution per agent invocation (events.jsonl) | `[IMPLEMENTED]` | constitution Article III 3.5 |
| L1 mechanical enforcement via capability gates (retired registry-id model replaced) | `[IMPLEMENTED]` | 62 `binding.yaml` files, all `capability-bound`, resolved through `governance-commons/toolchain/`; the registry-id audit and its remediation tiers were retired with that model |
| Self-evaluation harness for the framework's own agent and catalog outputs | `[ASPIRATIONAL]` | gap analyzed in `docs/ERROR-AND-DRIFT-MODEL.md` |
| AI safety and agentic-systems concern catalogs | `[IMPLEMENTED]` | `governance-commons/catalogs/concerns/agentic-systems/` (12 rules) and `responsible-ai/`; OWASP agentic threat catalogs under `catalogs/threats/` |
| Terraform/IaC complete coverage (infrastructure-misconfiguration, data-classification) | `[PARTIAL]` | substrate M4 active; infrastructure-misconfiguration authored, data-classification pending |
| Brownfield onboarding workflow | `[PLANNED]` | root `FUTURE.md` (P2) |
| Mobile, web-frontend, library, CLI full fit | `[PLANNED]` | `docs/FIT.md` roadmap; root `FUTURE.md` partial-fit roadmap |
| Cost-telemetry aggregation and model-tier guidance per agent | `[PLANNED]` | root `FUTURE.md` Tier 1 (measurement backbone) |
| Governance drift scanner (code-level) | `[ASPIRATIONAL]` | framework Phase 3.3 |
| Mid-session agent-drift mitigation | `[ASPIRATIONAL]` | framework Phase 3.4 |
| Executive reporting, compliance-evidence generation, multi-project dashboards | `[ASPIRATIONAL]` | framework Phase 3.8-3.11 |
| Governance evolution loop (rule-learning, human-approved promotion) | `[ASPIRATIONAL]` | framework Phase 3.12 |
| Prompt caching with explicit cache breakpoints for catalog loading | `[ASPIRATIONAL]` | lowest-friction mitigation for the token-bloat concern; see open questions |
| Manifest-driven lazy catalog and constitution slicing | `[IMPLEMENTED]` | `project-manifest.yaml` checkpoint slices wired through `tooling/compose/compose_context.py` and `tooling/constitution/inject.py`; per-agent article slices in every agent file |
| Model routing per agent (opus for judgment, sonnet for scaffolded review, haiku for mechanical) | `[IMPLEMENTED]` | `model:` field in every `.claude/agents/*.md` frontmatter (authoritative); tier rationale and verified pricing in `governance-commons/lib-context/ai-model-pricing.yaml` selection_guidance |
| SKILL.md export and plugin packaging of substrate content | `[ASPIRATIONAL]` | OSCAL-as-archive, SKILL.md-as-runtime; see open questions |
| Loop-world substrate evolution (per-feature learning signal) | `[ASPIRATIONAL]` | no-loop today; external evidence (SkillOpt, test-time compute, decision-context-graph) shifts the default; see open questions |
| Error-budget calibration (measured per-layer accuracy and correlation) | `[ASPIRATIONAL]` | the self-evaluation gap; operational model in `docs/ERROR-AND-DRIFT-MODEL.md` |
| events.jsonl drift vector (closure-rejection, routing-versus-findings mismatch, deferral aging, override trend, cost drift) | `[PARTIAL]` | `tooling/metrics/measure.py` computes the event-derived measures on demand; the drift-vector alarms of `docs/ERROR-AND-DRIFT-MODEL.md` Phase 1 remain unbuilt |
| Super-agents combining multiple review lenses | `[REJECTED]` | root `FUTURE.md` considered-and-rejected (token economics) |
| Automated documentation generator, postmortem author, generic perf-optimizer | `[REJECTED]` | root `FUTURE.md` considered-and-rejected |

---

## The core insight: the governance layer is the identity

The framework's distinguishing identity is not its agents, its loop
closure, or its wave dispatch. It is the governance layer: a first-class
body of human-authored, machine-readable, version-controlled engineering
governance that the AI is required to consult while it generates and
reviews code, and is verifiable to have consulted.

The constitution is the entry point. The governance substrate
(`governance-commons/`) is the active rule book. The agents are workers
that consult governance. The audit trail verifies governance was applied.
Loop closure enforces consequences when governance is violated.
Everything else is in service of governance enforcement.

The underlying principle: quality, security, and performance in
AI-generated code do not come from the model's training-data consensus.
They come from explicit governance assets the AI must consult, with
evidence that it did. Without catalogs, the approach is only a
description; with catalogs it is operational: the framework ensures AI
writes code that complies with the rules the project requires, across
security, performance, cost, code quality, compliance, and operations,
and catches AI drift both in produced code and while the AI is producing
it.

---

## Philosophy: Small Grounded Requests

The operating principle:

> Every AI request is a small focused task grounded in a specific
> constitution slice and specific governance assets. Larger work is
> decomposed into many small grounded requests with explicit state
> preservation across them.

This is a response to context rot: model performance degrades as context
grows, well before the window limit, and for coding agents this is the
primary failure mode rather than model capability. The principle's
operational consequences run through the whole framework:

- Wave-based agent dispatch (each invocation is a small focused request)
- Specialized agents per concern, no generalists
- A governance manifest telling each agent which slice to consult
- Concern-based catalogs, each a focused slice of the rule space
- Per-feature audit logs that bound context per feature
- ADRs as cross-task state preservation
- Layer 1 mechanical enforcement (tool checks instead of AI judgment)

Constitution slicing keeps the constitution itself from becoming a
context problem: the manifest specifies which articles apply per agent
per checkpoint, with a hard cap on injected context per invocation
(roughly 30-50K tokens, below the context-rot inflection point).

What the principle does not solve, stated honestly: coordination
overhead, cross-task coherence, the holistic nature of some Layer 3
judgments, and the risk of losing serendipitous connections through
decomposition. These are mitigated (ADRs, audit logs, keeping novel work
in Layer 3) but not eliminated.

---

## The mental model: layers 0 through 3

Business owners and engineers see different things in "production ready."
The framework names four layers to make the difference explicit.

- **Layer 0 (functional, business cares):** does it work, did the
  deadline get hit, are users not complaining. Explicitly outside the
  substrate's scope.
- **Layer 1 (mechanical, engineering cares):** will it pass automated
  standards checks. Deterministic, tool-verifiable.
- **Layer 2 (semantic, engineering cares):** will this be maintainable in
  six months. Interpretable patterns, reviewer-enforced.
- **Layer 3 (judgmental, engineering cares):** were the right trade-offs
  made. Subjective, contextual, decision-framework supported.

Layers 1 to 3 are invisible to business owners until they cause incidents.
Under pressure to ship Layer 0 fast, Layers 1 to 3 erode silently. The
framework is the engineer's structural defense against the AI's natural
tendency to optimize Layer 0 at the expense of 1 to 3.

This is why the framework declares aggressively at Layers 1 and 2 and
provides decision support, not rules, at Layer 3. The roughly 80 percent
of production code that is glue (CRUD, validation, error handling,
logging, data access) benefits from uniformity, and AI writes it well
when given the substrate to consult. The roughly 20 percent that requires
engineering judgment stays human-led, supported by Layer 3 decision
frameworks and ADRs.

**Robotic code is the feature, not a bug.** Uniform, predictable,
standards-compliant glue code is exactly what the substrate is for. The
judgment-heavy minority is where humans stay in the loop.

---

## Catalog quality is the constraint

The catalogs are the framework's most effort-intensive asset: authoring
OSCAL concern catalogs at full depth is months of work. Their value is
conditional, and the condition is non-negotiable: the catalogs
have to be good. A sloppy catalog is a precision instrument pointed in
the wrong direction. The AI consults it faithfully and produces wrong code
with high confidence, and the audit trail makes "we followed the rules"
provable, which is excellent when the rules are right and disastrous when
they are wrong. Bad rules are worse than no rules. This is why authoring
discipline (validate against real code, mark lifecycle explicitly, justify
every rule with concrete examples, author three slowly and well rather
than ten quickly) matters more than catalog count. The current `[PARTIAL]`
status of L1 enforcement coverage is the live instance of this risk and is
tracked for remediation.

---

## Drift coverage

The framework addresses six drift types. It owns governance drift and
mid-session agent drift; it integrates existing solutions for spec,
dependency, and knowledge drift; and it adds light orchestration for
contextual drift across handoffs. Owning the first two depends on the
catalogs existing, which is why substrate authoring is the foundation
everything else builds on.

---

## Independent external validation

Google's Agent Development Kit invoice-processing sample independently
converged on substantially the same architecture: a constitution as
source of truth, an acting agent paired with an adversarial critic agent
that can stop or allow continuation, and a learning loop that promotes
recurring patterns into a rule base under human approval. Two independent
teams arriving at constitution-as-source-of-truth, three-layer
decomposition, the adversarial reviewer pattern, and structured rule
catalogs is meaningful validation of the direction.

---

## Open architectural questions

These are durable, unresolved questions from the framework's design
thinking. They are recorded here so they are not lost or re-discovered.
Each is a real fork, not a settled position.

**Token bloat versus the framework's own philosophy (the sharpest one).**
The framework risks producing the context-rot problem it exists to solve.
Always-loaded preamble (CLAUDE.md, AGENTS.md, the constitution) runs to
tens of thousands of tokens before any work starts; agent prompts and
concern catalogs are large; a single threat-modeling invocation can load a
very large amount of catalog content. This is in direct tension with Small
Grounded Requests. The articulated answers already exist (manifest-driven
slicing, constitution slicing, prompt caching, model routing per agent,
agent-prompt deduplication, catalog-format slimming); none is built yet.
Open question: is the OSCAL format the right runtime carrier or only the
right authoritative archive, with slim derivatives loaded at runtime? This
is the highest-priority architectural concern and it compounds: every other
roadmap item makes loading heavier unless this is addressed first.

**The self-evaluation and error-budget gap.** The framework has every
verification layer reliability engineering calls for and zero measured
error rates on any of them except the deterministic pre-commit hook. The
AI reviewer layers are in one model family, so their errors are correlated
and do not compose to the naive multiplied reliability; stacking more
same-family reviewers hits a ceiling set by what they all miss in common.
closure-auditor is the keystone and has no outer auditor. This is the same
self-evaluation gap. Open question: define the acceptable error
rate as a number, define "wrong" operationally, measure per-layer accuracy
and correlation (closure-auditor first), and add diversity of layers
(model family, prompting strategy, deterministic checks, sampled human
review) rather than quantity. The operational definition of "wrong," the
four error types, the error-versus-drift distinction, and the
`events.jsonl` drift vector that is buildable today are documented in
`docs/ERROR-AND-DRIFT-MODEL.md`.

**No-loop versus loop evolution.** Today every feature runs against a
static substrate; knowledge from each closure stays trapped in that
feature's log. A loop world treats each feature as both an execution and a
training signal that improves the substrate for the next feature. External
evidence (SkillOpt, the test-time-compute paper, the decision-context-graph
framework) increasingly favors loop in production. The constraint: Charter
Article III 3.2 forbids AI authoring rule intent, so any loop can evolve
lib-context and mappings but not concern-catalog rule text. Open question:
is loop the direction, and if so on which artifacts and at what cadence?

**Lib-context as governance-overlay.** As domain plugin ecosystems mature
(AWS, Microsoft, and others shipping comprehensive domain skills),
lib-context should shrink from "teach the agent the library" to "the
governance-overlay slice domain skills omit" (for example, how a
LangGraph checkpointer can persist secrets, not how to use LangGraph).
This both addresses the token-bloat concern and slows lib-context decay,
because governance principles outlast specific APIs.

**Agent Skills versus AI agents.** An AI agent is a runtime actor; an
Agent Skill is packaged knowledge an agent loads when relevant. Much of the
substrate (concern catalogs, lib-context, playbooks, decision frameworks)
is skill-shaped in everything but filename, and repackaging it as SKILL.md
would yield cross-host portability with a mechanical rename. The twelve
sub-agents stay agents.

**Packaging shape: plugin versus template.** The substrate
(`governance-commons/`) is plugin-shaped and could be installed into
existing projects; the consumer-side machinery (constitution, agents,
hooks, loop closure) is template-shaped and needs to come with the project
structure. The likely resolution is a hybrid: plugin-shaped substrate,
template-shaped consumer side. This is a Phase 3.0-level decision that
shapes discovery, adoption, and upgrades.

**Cross-boundary coordination under model-version pressure (the five
coordination boundaries).** Each model upgrade (Opus 4.8 and successors)
narrows the within-session value of governance content. The substrate's
durable value is increasingly the coordination it provides across
boundaries a single model session never touches: across agents in a wave,
across features over time, across the human-AI approval gate, across tools
and hosts, and across the audit boundary where evidence must persist. The
implication is to harden these cross-boundary mechanisms rather than rely
on per-rule content that the next model will increasingly know on its own.

## Companion documents

- `docs/ENHANCEMENT-ROADMAP.md` - the prioritized menu of candidate work
  that acts on these open questions
- `docs/agentic-design-patterns-reference.md` - the design rubric the
  framework is measured against
- `docs/FIT.md` - which project types fit, today and on the roadmap
- `FUTURE.md` - the backlog
- `governance-commons/spec/principles.md` - the canonical P1-P12
