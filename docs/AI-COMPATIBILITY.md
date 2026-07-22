<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# AI Compatibility

This document explains which parts of the framework work with which AI
coding tools, and what you give up if you use something other than
Claude Code.

The short version: the substrate is AI-agnostic; the automation layer
is Claude-Code-specific. You can use the framework with any AI tool,
but you keep more of its value with Claude Code.

## Two layers

The framework is intentionally architected as two layers:

**Substrate** — the governance and workflow specification. AI-agnostic
by design. Lives in `governance-commons/` (constitution principles,
threat catalogs, OSCAL compliance catalogs, Cedar policies,
attestation specs, incident playbooks, library context) and `.specify/`
(the spec-driven workflow infrastructure from GitHub spec-kit, which
itself supports 20+ AI tools).

**Delivery** — the automation that makes the substrate enforceable
without manual effort. Currently Claude-Code-specific. Lives in
`.claude/` (the twelve specialized sub-agents — eleven review agents organized into seven
cognitive categories, plus a pre-construction discovery agent — the spec-kit skills, the loop-closure hook,
the coordination protocol).

The substrate is the framework. The delivery is how the framework
gets executed. A different delivery layer (Cursor rules, Cline modes,
Codex commands) could be built on the same substrate.

## Compatibility matrix

| Capability | Substrate or Delivery? | Claude Code | Cursor | Cline / Roo | Codex CLI | Gemini CLI | Copilot | Aider | Generic AI |
|---|---|---|---|---|---|---|---|---|---|
| Constitution as enforced principles | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| OSCAL compliance catalogs | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| Threat catalogs (STRIDE, OWASP, MITRE) | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| Cedar policies for agent runtime | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| Attestation specs (SLSA + in-toto) | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| Incident playbooks | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| Library context (lib-context YAMLs) | Substrate | Full | Full | Full | Full | Full | Full | Full | Full |
| Spec-driven workflow (spec → plan → tasks → implement) | Substrate | Full via skills | Full via slash commands | Full via commands | Full via prompt | Full via prompt | Full via prompt | Full via prompt | Manual |
| Twelve specialized sub-agents (eleven review agents — upstream challengers, decision formalizers, test design, operational design, downstream verifiers — plus a pre-construction discovery agent) | Delivery | Full | None — must invoke manually as prompts | None | None | None | None | None | None |
| Checkpoint routing (concern-selector plan + dispatcher at four checkpoints) | Delivery | Full | Manual (human plays the routing role) | Manual | Manual | Manual | Manual | Manual | Manual |
| Operator plan approval (approve the routing plan before dispatch) | Delivery | Full | Manual judgment | None | None | None | None | None | None |
| Decline mechanism (agents emit not-applicable for out-of-scope work) | Delivery | Full | None — human filters manually | None | None | None | None | None | None |
| Automated agent event log (events.jsonl) | Delivery | Full | None — must write manually | None | None | None | None | None | None |
| Loop closure verification (closure-auditor semantic + git hook mechanical) | Delivery | Full (closure-auditor in-session + git hook) | Git hook only, manual events | Git hook only | Git hook only | Git hook only | Git hook only | Git hook only | Git hook only |
| Pre-commit loop-closure hook | Delivery | Full | Full (works regardless of AI tool) | Full | Full | Full | Full | Full | Full |
| Memory file convention | Delivery | `CLAUDE.md` | `.cursor/rules/` + `AGENTS.md` | `.clinerules/` | `AGENTS.md` | `GEMINI.md` + `AGENTS.md` | `.github/copilot-instructions.md` | `CONVENTIONS.md` | Project-specific |
| Agent coordination protocol | Delivery | Full | Manual | Manual | Manual | Manual | Manual | Manual | Manual |

## What you get with Claude Code

The full framework. Specifically:

- All substrate capabilities listed above
- Twelve specialized sub-agents: eleven review agents in seven cognitive categories plus a discovery agent
  (upstream challengers, decision formalizers, test design,
  operational design, downstream verifiers, audit, routing), invokable
  as `@staff-engineer`, `@threat-modeler`, etc., each with constrained
  tool access and specific cognitive lenses
- The **concern-selector** agent that resolves, once per feature, which
  catalogs apply and which agents run at each of four artifact-boundary
  checkpoints (post-spec, post-plan, post-implementation, pre-commit), and the
  deterministic dispatcher (`tooling/dispatch`) that organizes that approved
  plan into per-checkpoint waves
- The **adr-architect** agent that drafts ADRs from existing
  artifacts with hybrid human-in-the-loop interaction (pre-fills
  Context and Alternatives; marks Decision and Rationale as DRAFT
  for human review)
- The **operational-architect** agent that produces SLO/observability/
  runbook artifacts when the project has user-facing service
  requirements
- The decline mechanism — agents emit `declined` events with status
  `not-applicable` when invoked against work outside their scope,
  enabling routing calibration over time
- spec-kit slash commands as native Claude Code skills
  (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`,
  `/speckit-implement`, plus eight others)
- Automatic git branch creation for new features
- The coordination protocol (main session reads CLAUDE.md, sub-agents read agent-coordination.md)
- Loop-closure verification at both the Claude Code in-session layer
  (closure-auditor) and the git pre-commit hook layer
  (defense-in-depth at commit time)
- Cost tracking per agent invocation, aggregated per feature in
  `events.jsonl`

This is the version the framework was designed for. Documentation
assumes this configuration unless explicitly noted otherwise.

## What you get with other AI tools

The substrate, plus partial automation depending on the tool.

The substrate alone is substantial:

- Spec-driven workflow enforced by `.specify/` infrastructure
  (spec-kit supports your tool natively via `--ai <name>` flag
  during `specify init`)
- Constitutional principles in `.specify/memory/constitution.md`
  that any AI tool can read and follow when prompted
- Compliance catalogs (NIST 800-53, NIST 800-171, NIST CSF v2,
  NIST SSDF, NIST AI RMF, EU AI Act) in OSCAL format, readable by
  any tool
- Threat catalogs (STRIDE, OWASP LLM Top 10, OWASP Agentic ASI,
  MITRE ATLAS) in YAML, referenceable from any tool's prompts
- Cedar policies enforceable at runtime regardless of which AI
  tool generated the code
- Attestation specifications for SLSA-compliant supply chain
  provenance, applicable to any build pipeline
- Incident response playbooks, useful regardless of which AI tool
  caused the incident
- The git pre-commit hook (`verify-loop-closure.sh`) still works,
  but only if your tool actually writes events.jsonl

What you don't get:

- The specialized sub-agent roster. You can replicate their
  cognitive lenses by manually prompting your tool with their
  prompt content (in `.claude/agents/*.md`), but you lose the
  isolated tool allowlists, the routing/execution separation, and the
  automatic invocation patterns.
- Checkpoint routing. You play the routing role manually,
  deciding which lenses apply to each feature, invoking them as
  prompts, and tracking their output. The plan-approval step
  (approve the routing plan before dispatch) becomes your judgment
  call.
- Decline mechanism. With Claude Code, agents push back on
  misrouted invocations. With other tools, you filter manually —
  if you prompt your AI with the threat-modeler persona on a spec
  with no security surface, the AI will produce something rather
  than declining.
- Automated events.jsonl writes. You'd need to write events
  yourself or build an equivalent automation layer for your tool.
- Loop closure verification at the in-session layer. The git hook
  still works, but it catches issues at commit time rather than
  during the workflow.
- Pre-built coordination between specialized agents. The
  `agent-coordination.md` protocol assumes the Claude Code
  main-session-and-subagent pattern.

## Specific tool guidance

### Cursor

Run `specify init --here --ai cursor` to install spec-kit's Cursor
integration. Spec-kit ships Cursor slash commands as
`.cursor/commands/`, so `/specify`, `/plan`, `/tasks`, `/implement`
work natively.

For the specialized agents, the closest Cursor equivalent is custom
modes in `.cursor/rules/`. You can copy the content of
`.claude/agents/<agent>.md` into a Cursor rule and invoke that mode
when you want that lens applied. You lose tool allowlist enforcement
(Cursor modes don't restrict tools by name) but keep the cognitive
scope. The routing layer doesn't translate cleanly —
you play that role manually by deciding which Cursor modes to invoke
per phase of the spec-driven workflow.

Cursor's memory file is `AGENTS.md` plus `.cursor/rules/`. The
framework's `AGENTS.md` already contains cross-tool guidance;
add Cursor-specific rules in `.cursor/rules/` referencing the
constitution and agent prompts.

### Cline / Roo Code

Cline reads `.clinerules/` for its memory. Copy the contents of
`CLAUDE.md` and `AGENTS.md` into `.clinerules/` files.

Cline's "custom modes" feature is the closest analog to Claude
Code's specialized sub-agents. Each mode can have its own system
prompt; copy the agent prompts into modes. Cline's mode system also
supports tool restrictions per mode, so you can approximate the
read-only sub-agent pattern fairly faithfully.

The routing layer doesn't translate cleanly. Cline
doesn't have a "meta-mode" that invokes other modes; you'd invoke
modes manually at each checkpoint.

Cline does not have hooks. Loop-closure verification falls back
to the git pre-commit hook only.

### Codex CLI / OpenAI

Run `specify init --here --ai codex` to install spec-kit's Codex
integration.

Codex CLI's memory file is `AGENTS.md`. The framework's `AGENTS.md`
is already populated with cross-tool guidance.

Codex does not have a sub-agents feature equivalent to Claude Code.
You manually invoke specialized analysis by pasting the relevant
agent prompt into your conversation, or by setting up reusable
prompt templates in your shell. The routing role is yours —
the framework's trigger conditions (visible in `AGENTS.md`) tell
you when each agent applies.

Note: Codex CLI works with both OpenAI and Anthropic models. The
framework is model-agnostic as long as the tool supports the
spec-driven workflow.

### Gemini CLI / Google AI

Run `specify init --here --ai gemini` for spec-kit integration.

Gemini's memory file is `GEMINI.md` alongside `AGENTS.md`. The
framework only ships `AGENTS.md`; you would need to create
`GEMINI.md` if Gemini-specific guidance is needed beyond what
`AGENTS.md` already provides.

Gemini CLI does not support sub-agents. Use manual prompt injection
for the agent lenses, and play the routing role yourself per
the trigger conditions in `AGENTS.md`.

### GitHub Copilot

Run `specify init --here --ai copilot` for spec-kit integration.

Copilot's memory file is `.github/copilot-instructions.md`. The
framework does not ship one; copy relevant parts of `CLAUDE.md`
(constitution reference, security rules, infrastructure conventions)
into `.github/copilot-instructions.md`.

Copilot has no sub-agents and no hooks. The substrate and the
spec-driven workflow are usable; the automation layer is not.

### Aider / Continue

Aider reads `CONVENTIONS.md`. Continue uses `.continue/` config.

Both work with the substrate via prompt-injection of agent
prompts. Neither has a native sub-agents feature.

### Bring your own (any AI tool)

The framework works with any AI tool that can read project files
and follow instructions. The minimum viable workflow:

1. Have the AI read `.specify/memory/constitution.md` at session start
2. Have the AI read `AGENTS.md` (cross-tool memory)
3. For new features, follow the spec-kit workflow manually:
   create `specs/NNN-feature/spec.md`, then `plan.md`, then
   `tasks.md`, etc., following the templates in `.specify/templates/`
4. For analytical passes (threat modeling, performance review,
   etc.), paste the relevant agent prompt from `.claude/agents/`
   as a system prompt or starting prompt
5. Play the routing role manually per the trigger conditions
   in `AGENTS.md` — decide which agent lenses apply, in what order
6. Write `events.jsonl` entries manually after each analysis pass
   if you want loop-closure verification to work

This is more manual than Claude Code, but the substrate's enforcement
quality (constitution rules, threat catalogs, OSCAL controls) is
preserved.

## The honest tradeoffs

What specifically degrades when you don't use Claude Code:

**Cognitive isolation between agents.** Claude Code's sub-agent
feature gives each agent its own context window. When you invoke
`@threat-modeler`, that agent doesn't see the rest of your
conversation history — it sees only the prompt, the spec, and
the threat catalogs. This isolation produces more focused output.
Other tools mix all context together, which can lead to drift.

**Tool allowlist enforcement.** Claude Code lets you declare each
agent's allowed tools (`tools: Read, Grep, Glob, Bash` for
read-only). The framework's read-only-subagent security model
depends on this enforcement. Every sub-agent is read-only; the main
session (not a sub-agent) performs writes and runs the dispatcher, so
there is no wider-access agent exception. Other tools either don't
have this concept or implement it differently.

**Checkpoint routing.** Claude Code's concern-selector decides which
specialists apply per feature and the dispatcher runs them at four
artifact-boundary checkpoints; closure-auditor verifies loop closure.
With other tools, you make the routing decisions manually. The trigger
conditions in `AGENTS.md` are guidance; the routing logic is yours.

**Plan approval.** Claude Code's model has the operator approve the
concern-selector's routing plan once before the dispatcher dispatches;
that is the human-in-the-loop gate. With other tools you apply your own
judgment about when to ask, when to act, and when to confirm.

**Decline mechanism.** With Claude Code, agents push back on
misrouted invocations by emitting `declined` events. With other
tools, your AI will produce something rather than declining — you
filter relevance manually.

**Coordination protocol automation.** The main-session-and-subagent
pattern (main session writes files and runs the dispatcher, sub-agents
return content) relies on Claude Code's two-tier execution model. Other tools
have one tier — you and the AI. You'd write everything yourself.

**Cost tracking precision.** Claude Code reports per-invocation
token counts cleanly. Other tools report differently (Cursor
shows cumulative, Codex CLI shows per-call, Continue depends on
the model). The framework's cost discipline (Article III Section
3.5) is harder to enforce uniformly across tools.

**Hook enforcement at the in-session layer.** The canonical
enforcement gate is the git pre-commit hook
(`.claude/hooks/verify-loop-closure.sh` → `verify_loop_closure.py`),
which fires on every commit regardless of AI tool. Claude Code
additionally supports optional in-session enforcement via
`PostToolUse` hooks — same Python script wired into Claude Code's
hook config for defense in depth. Other AI tools don't have an
equivalent in-session hook surface; they rely on the git pre-commit
hook only, which still catches everything before commit.

What does NOT degrade:

- The substrate itself. Constitution, threat catalogs, OSCAL
  controls, Cedar policies, attestation specs, playbooks, and
  lib-context YAMLs are all data that any AI tool can read.
- The git pre-commit hook. Independent of AI tool choice.
- The spec-driven workflow. Spec-kit supports 20+ tools natively.
- The audit trail format. JSONL events are tool-agnostic; you
  just need to write them.
- The agent prompts themselves. They're plain markdown; any AI
  tool can use them as system prompts or role definitions.

## Migration paths

### Claude Code → another AI tool

Rare. The substrate stays in place. You delete or ignore the
`.claude/` directory, install your tool's spec-kit integration
(`specify init --here --ai <tool>`), copy the agent prompts you
want into your tool's equivalent format, and configure manual
or scripted events.jsonl writes. You take over the routing
role that the concern-selector and dispatcher played.

Existing `events.jsonl` files remain valid as historical record.
Existing `specs/` artifacts (specs, plans, threat models, ADRs,
operational designs) remain valid; they're plain markdown.

### Another AI tool → Claude Code

Common, since most teams start with what they have. The substrate
should already work without modification. Run `specify init --here
--ai claude --force` to install Claude Code's spec-kit integration
alongside whatever you had. Copy `.claude/` from a template project
or clone `https://github.com/yoonation/ai-grounded.git`. Configure the git pre-commit hook
to use `.claude/hooks/verify-loop-closure.sh`. The routing layer (concern-selector + dispatcher)
activates immediately on the next feature workflow.

If you have existing `events.jsonl` files from manual writes, they
should validate against the schema in
`.claude/docs/agent-coordination.md`. If not, fix the schema
mismatches. The newer schema fields (closure_evidence, declined
events) won't be in your historical events but that's fine — they
apply going forward.

### Multi-tool teams

The framework is compatible with multi-tool teams as long as
everyone respects the substrate. One developer uses Claude Code,
another uses Cursor, another uses Codex — all read the same
constitution, threat catalogs, and OSCAL controls. The agent-level
automation differs per developer, but the artifacts produced
(spec.md, plan.md, threat-model.md, ADRs, operational-design.md,
events.jsonl) follow the same format.

The risk is uneven enforcement: the Claude Code developer's PRs
will have richer audit trails than the Cursor developer's PRs.
This is fine for accountability but uneven for review. Address
by training the team on manual workflow for non-Claude tools,
or by accepting the asymmetry.

## When to use what

**Use Claude Code if:**

- You want the full framework with minimal manual effort
- You value the cognitive isolation of sub-agents
- You want automatic checkpoint routing and loop-closure
  verification
- Your security posture requires tool-allowlist-enforced read-only
  agents
- You want the decline mechanism to filter misrouted work
  automatically
- You want the framework's end-to-end execution to run
  start to finish in one tool

**Use another AI tool if:**

- Organizational mandate (your company uses Cursor / Copilot /
  Codex enterprise)
- Cost or licensing reasons (e.g., committed OpenAI spend)
- Tool-specific features outweigh sub-agents for your use case
  (e.g., Cursor's Composer for refactoring, Aider's git-aware
  edits)
- You're willing to do more manual prompt-pasting and play the
  routing role yourself in exchange for tool flexibility

**Use no AI tool:**

- The substrate is still valuable as a documentation and
  governance framework. Constitution, threat catalogs, OSCAL
  controls, Cedar policies, playbooks, and spec templates all
  work for human-only teams. The framework's spec-driven
  workflow is older than AI coding tools and was designed for
  humans.

## See also

- `governance-commons/PORTABILITY.md` — anti-coupling rules
  enforced on the substrate
- `governance-commons/spec/principles.md` — the agnostic-vs-vendor-
  specific tradeoff acknowledged in the substrate's design
- `governance-commons/spec/identity-model.md` — the multi-tool
  identity model that distinguishes developer, AI tool, and
  tool instance as separate principals
- `.claude/docs/agent-coordination.md` — the Claude-Code-specific
  protocol that this document references as the "delivery layer";
  contains the scope discipline principles (NOT-clause pattern,
  500-line tripwire, decline mechanism)
- `docs/FIT.md` — which project types benefit most from the
  framework
- `docs/RETROFIT.md` — adopting the framework on existing projects
- `SETUP.md` — installation steps; includes the `specify init
  --ai <tool>` flag for non-Claude tools
