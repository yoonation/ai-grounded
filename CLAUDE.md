<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Project: [PROJECT_NAME]

## Quick Facts
- **Stack**: [e.g., Terraform, Python, AWS]
- **Test**: `[e.g., pytest -v, terraform validate]`
- **Lint**: `[e.g., tflint, ruff check .]`
- **Format**: `[e.g., terraform fmt, black .]`
- **Build**: `[e.g., docker build ., terraform plan]`

## Key Directories
- Project code lives at the repo root following your stack's convention. The framework imposes no top-level code zone.
- `PROJECT-LOG.md` - project-scoped append-only log for cross-cutting observations (routed by closure-auditor on `cross-cutting: true`), cross-feature deferrals, and drift.
- `specs/` - per-feature spec-kit work, created at runtime. `specs/NNN-feature/reviews/` holds agent outputs; `specs/NNN-feature/events.jsonl` is the feature event log.
- `docs/decisions/` - ADRs (ships with `.gitkeep`).
- `.claude/`, `.specify/`, `governance-commons/`, `scripts/` - framework scaffolding. No project code here.
- `project-manifest.yaml` (repo root) - the single source of truth for which substrate content each checkpoint (C1-C4) consults: per-checkpoint catalog sets and `constitution-articles`. Agents load only their checkpoint's slice, never the whole governance-commons tree or the whole Charter. Forked from the substrate reference per the consumer-scaffold contract; see `.claude/docs/agent-coordination.md` ("Manifest-driven governance slicing").
- `presets/spec-driven-governance/` - vendored spec-kit preset and canonical source for the constitution template, the governance-aware spec template, and the framework command overrides (speckit-specify, speckit-clarify, speckit-plan, speckit-implement). Edit here, then `./scripts/bootstrap.sh` to propagate. Never edit `.specify/presets/...` (regenerated state) or the rendered `.claude/skills/speckit-*` files (derived output; edit canon and re-propagate).

## Architecture
[One sentence describing the main components. Update per project.]
See @docs/ARCHITECTURE.md for decisions and ADRs.

## Rules
- Never delete or modify tests to make them pass - fix the code
- Never hardcode credentials - use env vars, AWS SSM, or IAM roles
- Always run tests after every file change
- Keep diffs small - one task at a time
- Never run `terraform apply` without showing the plan first
- Never run `rm -rf` on any directory
- Add `*.tfstate`, `.env`, credentials to `.gitignore` if not already present

## Infrastructure Conventions
- Terraform: tag resources with `environment`, `team`, `project`; prefer `for_each` over `count`; `sensitive = true` for secret outputs
- AWS: prefer OIDC + IAM roles over long-lived access keys
- Containers: multi-stage builds, never run as root

## Security
- Validate and sanitize all inputs at system boundaries
- Use parameterized queries - never string-concatenate SQL
- Prefer IAM roles over long-lived credentials
- Flag any use of: `eval()`, `exec()`, `shell=True`, `os.system()`
- Never disable auth checks, SSL verification, or security headers
- Use a secrets manager for credentials, not `.env` in production
- Suggest least-privilege for any IAM policy or RBAC role

## Git Conventions
- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- Commit format: Conventional Commits (feat:, fix:, docs:, chore:)
- Never commit directly to main

## What Claude Gets Wrong Here
- [Add mistakes as you discover them per project]

## Compact Instructions
When compacting, preserve: modified files this session; current test status; active task and progress; errors/blockers; architecture decisions made this session.

## Verification
- If uncertain about a fact, say "I'm not sure" rather than guessing
- When referencing documentation, quote directly rather than paraphrasing
- After generating code, verify it compiles/runs before declaring done

## Constitution and principles

Every action in this repository respects the constitution at
`.specify/memory/constitution.md`. Article map (read the article for detail):

- **I - Spec-driven workflow**: non-trivial work flows spec → clarify → plan → tasks → implement, with `/speckit-analyze` for cross-artifact consistency. Trivial work (typos, dep bumps) may skip (Article I Section 1.2).
- **II - Engineering discipline**: exact version pinning (no `latest`); ADRs at `docs/decisions/ADR-NNN-*.md` are pre-build gates; anti-patterns (Section 2.5) require an ADR override; test discipline per Section 2.4.
- **III / VI - Agent coordination**: specialized sub-agents in `.claude/agents/` run upstream (challenge), formalize (ADR), design tests, then downstream (verify) and audit (closure). All invocations emit events to `events.jsonl`. AI cost discipline (Section 3.5): every invocation reports tokens and `estimated_usd` derived from `governance-commons/lib-context/ai-model-pricing.yaml`.
- **IV - Production readiness**: four-environment topology (local, integration, staging, prod); prod config verified before deploy (4.2); observability non-optional (4.3); the 8 distributed-computing fallacies are constraints.
- **V - Security**: threat models before implementation; data classification respected (5.3); compliance verified by security-reviewer (5.4).

When this file conflicts with the constitution, the constitution wins.

## Available sub-agents

Twelve specialized agents: eleven review agents in seven cognitive categories, plus a pre-construction discovery agent, each a sharply scoped lens. **Routing is a reasoning step plus deterministic tooling: the concern-selector decides once per feature which catalogs apply and which agents run at each checkpoint (the approved feature-concerns.yaml); the dispatcher (tooling) organizes that plan into per-checkpoint waves. You (the main Claude Code session) are the execution layer: you run the dispatcher, invoke the agents, save artifacts, and append events.**

- **Upstream challengers** (before implementation): **staff-engineer** (YAGNI, DRY-with-judgment, scope, timing, assumptions, technology selection), **threat-modeler** (STRIDE, OWASP LLM Top 10, OWASP Agentic ASI Top 10, MITRE ATLAS, compliance), **performance-reviewer** (CPU/memory/runaway loops/unbounded cost/scaling), **production-readiness** (deployment, topology, resilience, prod config).
- **Decision formalizers**: **adr-architect** (drafts ADRs from existing artifacts; Context and Alternatives pre-filled; Decision and Rationale marked DRAFT for human review).
- **Test design**: **test-architect** (tests from the spec's perspective, not the implementation).
- **Operational design**: **operational-architect** (SLI/SLO/error budgets, observability plans, runbook scaffolding; declines on pure IaC/library/CLI work without service semantics).
- **Downstream verifiers** (after implementation): **code-reviewer** (quality, correctness, anti-patterns, smells), **security-reviewer** (vulnerability scanning, audit-envelope enforcement, compliance config).
- **Audit**: **closure-auditor** (verifies pending items have valid closure evidence; semantic "did you do what you said?" judgment; not a re-review).
- **Routing**: **concern-selector** (read-only; once per feature at C1, resolves which catalogs apply and which agents run at each checkpoint within the profile bounds, into the approved feature-concerns.yaml). The dispatcher (`tooling/dispatch/dispatch.py`, deterministic tooling, not an agent) organizes the approved plan's agents into the canonical waves; the main session executes.

Scope discipline (NOT-clause pattern, 500-line tripwire, decline mechanism) and full invocation protocol: `.claude/docs/agent-coordination.md`.

## Running the dispatcher and persisting agent output

Sub-agents are read-only (`Read, Grep, Glob, Bash`); they produce analysis but cannot write. **You handle all persistence.** The canonical protocol is in `.claude/docs/agent-coordination.md` ("Main session responsibility", "Subagent responsibility", "Hook protocol"). Operationally:

1. Run `tooling/dispatch/dispatch.py specs/NNN-feature --checkpoint <Cn>`; it emits the wave-ordered dispatch list and a `routing_decision_event`. Save the output to `specs/NNN-feature/reviews/dispatch-plan-checkpoint-N.md` and append the `routing_decision_event` verbatim.
2. Execute the waves in order: dispatch a parallel wave as one Task batch (shared `parallel_group_id`); a sequential wave waits for the prior wave's events to persist. The plan was operator-approved, so there is no per-invocation tier gate.
3. For each agent: pass the context the plan specified, extract its frontmatter, append it as one JSON line to `events.jsonl`, and save its artifact to the specified path.
4. **closure-auditor** additionally emits a "Recommended events" section; append those JSON lines **verbatim** (no reformatting). Surface any rejections or unaddressed items before commit.
5. If a return is missing frontmatter or an artifact path, ask the agent to re-emit rather than guessing.

**Tool selection**: use Write for both the event append and the artifact save. For artifacts over ~30KB (threat models, review reports), use Write in one call, not `cat << EOF` heredocs (they fail Claude Code's parser over ~30KB). Use Edit only for incremental refinement of an existing file.

## Closure signaling

As the user addresses concerns, they tell you what they did and you write the matching event to `events.jsonl`: `closure-claimed` (code/adr/spec_amendment/test evidence), `deferred` (P2 only, with a matching `deferrals.md` entry), or `overridden` (ADR accepts residual). closure-auditor verifies these at C3 and pre-commit; the hook enforces at commit. **P1 cannot be deferred** - close in code, override via ADR, or amend the spec. Exact event shapes (`closure-claimed`, `closure-verified`, `closure-rejected`, `overridden`, `deferred`, `declined`) with the `closure_evidence` sub-object: `.claude/docs/agent-coordination.md` "Event log". Signal incrementally as you go, not in a batch.

## Workflow

1. `/speckit-specify` → `/speckit-clarify`.
2. **C1 (post-spec)**: run `/speckit-workflow-post-spec` - the concern-selector proposes the plan, you approve it, the dispatcher dispatches the C1 upstream challengers; save artifacts with priorities in `items_raised`; append events.
3. Address concerns by priority: **P1** must close (code/test/ADR/spec) before commit; **P2** close or document a deferral; **P3** opportunistic. Signal closures as you go.
4. `/speckit-plan` → **C2 (post-plan)**: the dispatcher dispatches the plan's C2 reviewers and test-architect; ADR drafting is a conditional user-triggered step for unresolved P1/P2.
5. `/speckit-tasks` → `/speckit-implement`.
6. **C3 (post-impl)**: the dispatcher dispatches code-reviewer, security-reviewer (if the plan scoped it), and closure-auditor last. Fix rejected closures and re-claim.
7. **C4 (pre-commit)**: optionally re-invoke `@closure-auditor` for late changes.
8. `git commit` - `verify_loop_closure.py` blocks if any P1/P2 lacks required evidence. Address and retry. Merge.

### Specialist trigger conditions (summarized from each agent's description line in `.claude/agents/`; the agent files are authoritative)

| Agent | Trigger |
|---|---|
| staff-engineer | Always for non-trivial specs |
| threat-modeler | authn, authz, Confidential+ data, external interfaces, or AI agent capabilities |
| performance-reviewer | provisions any cloud resource with operational surface (storage/compute/network/locking/replication), processes data at scale, has latency/throughput targets, or runs agentic loops (sufficient on its own; no latency target needed) |
| production-readiness | produces a deployable artifact |
| operational-architect | user-facing service with availability/perf expectations, or on-call/SLA/uptime concerns |
| test-architect | Always after plan |
| adr-architect | concerns need formal decisions, clarify answers warrant ADRs, or anti-pattern overrides needed |
| code-reviewer | Always post-implementation |
| security-reviewer | threat-modeler ran, or impl touches authn/authz/Confidential+/external interfaces/AI agents |
| closure-auditor | Always at C3; user-invoked at pre-commit |

## Considered and rejected

Framework scope decisions are recorded in `FUTURE.md` (considered-and-rejected) to prevent re-litigation. Highlights: super-agents (token economics + specialization is the distinctive claim), postmortem-author and product-ideation agents (out of scope), performance-advisor and pair-programmer agents (rejected), and the executive orchestrator (blocked by anthropics/claude-code#4182; the routing layer was first an advisory router, then retired entirely in favor of the deterministic dispatcher). Loop-closure split is settled: the dispatcher routes deterministically from the approved plan, closure-auditor verifies semantics, hook enforces mechanics. Record any new rejection there with a date and rationale.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->
