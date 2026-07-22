<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Principles

The architectural principles that govern AI-assisted development
within frameworks consuming this commons. These are stable values
expressed at the right level of abstraction to outlast specific tool
choices.

This document is referenced by consuming frameworks' identity layers
(e.g., parent framework's CLAUDE.md cites principles defined here)
and is the canonical source - the consuming framework should not
duplicate principle content, only cite it.

## P1: Contracts not installations

Frameworks specify *what* must be present, not *how* it gets there.

A tool's required version is a framework concern. A tool's
installation method is an environment concern. Frameworks that assume
installation paths become coupled to those paths; frameworks that
specify contracts remain portable.

**Examples**:
- Secrets handling: contract is "env vars present at runtime";
 installation is any vault the developer prefers
- Tool versioning: contract is "Python 3.12+"; installation is any
 package manager
- AI assistant: contract is "AGENTS.md compatible"; installation is
 any compatible tool

**What this rules out**: hard-coding `1password-cli`, `homebrew`,
`/opt/homebrew/`, vendor-specific install paths.

## P2: Defense in depth

Multiple layers of decreasing strictness protect against AI mistakes
and adversarial behavior:

1. **Deterministic gates** (hooks, pre-commit, CI checks) - 100%
  enforced, cannot be overridden by AI
2. **Context-aware guidance** (rules with file-pattern activation) - 
  loaded conditionally, ~80-90% followed
3. **Always-loaded principles** (CLAUDE.md, AGENTS.md) - every
  session, ~80% followed
4. **Specs and constitution** (spec-driven style) - loaded for
  spec-driven workflow commands, define feature-specific contracts
5. **Post-action review** (`/review` agents, drift detection) - 
  catches what passed the earlier layers

No single layer is sufficient. Each catches different failure modes.

**Operational implication**: When adding a new control, ask "which
layer does this belong in?" Trying to enforce something in CLAUDE.md
that should be a hook produces ~80% compliance; the right layer
produces 100%.

## P3: Right-sized ceremony

Process scales with problem size. Trivial work has trivial overhead.

**Examples**:
- Typo fixes: just edit, no ceremony
- Standard features: spec-first via `/plan`, one interview, fresh
 session to implement, review at the end
- Complex multi-component features: full spec-driven ceremony with
 constitution check, clarify, plan, tasks, analyze, implement
- Bugfixes touching documented specs: surgical bugfix workflow, not
 full ceremony

**What this rules out**: forcing every change through the heaviest
workflow. Trivial work paying ceremony cost is the dominant failure
mode of overweight frameworks.

## P4: Read before write

AI must understand existing patterns before producing new code.

The single most powerful defense against code-style drift (the same
function getting written three different ways across three sessions)
is requiring the AI to read existing implementations first. Patterns
get absorbed; consistency emerges as a byproduct.

**Operational implication**: Specs and plans must identify Reference
Implementations - existing files in the codebase that demonstrate the
patterns the new code should follow. This is not optional.

**What this rules out**: AI producing code based on its training-data
priors when the project already has its own conventions.

## P5: Least privilege for AI

AI components get the minimum capabilities needed for their task.

**Examples**:
- Code-reviewer sub-agent: read-only (Read, Grep, Glob, Bash). Never
 Edit or Write. Reviewers report; humans decide.
- Production agents (runtime framework): default deny, explicit allow
 per capability via policy
- AI dev tools: limited by hooks and rules to project directories,
 excluded from sensitive paths

**What this rules out**: blanket "full access" configurations.
"Convenient" privilege expansion has bitten every team that's tried
it; we don't repeat that mistake here.

## P6: Spec-anchored, not spec-as-source

Specs guide implementation. Code remains the executable artifact.

This positions us against the "spec is the source code, code is
generated" framing (spec-as-source-of-truth toolchains). The
practical reality: LLMs are non-deterministic; specs reduce variance
but cannot eliminate it. Treating the spec as source means re-running
generation produces drift.

We treat specs as the *intent contract*: the spec says what should be
true, and the implementation is verified to match. When they diverge,
either the spec was wrong (update the spec) or the code was wrong
(fix the code) - but the code is what runs.

**Operational implication**: drift detection compares spec to code;
neither is authoritative on its own. Both are versioned, both are
reviewed, both are part of the truth.

## P7: Vendor-agnostic projection

Project beliefs work across AI vendors via standard formats.

The framework's strongest features may be vendor-specific (Claude
Code hooks, subagents with model selection), but the *principles* and
*knowledge* must be portable.

**Examples**:
- AGENTS.md projects principles to Cursor, Codex, Continue, etc.
- Skills/rules in markdown are consumable by any AI assistant
- Audit log envelope is OpenTelemetry-aligned, not Claude-specific
- Provenance attestations follow SLSA, not GitHub-specific

**What this rules out**: encoding beliefs in ways that only work with
one vendor. Vendor-specific implementations of universal principles
are fine; vendor-specific principle storage is not.

## P8: Evolutionary architecture

Architectural changes happen via reviewed amendments (ADRs), not
silent drift.

When a principle, threat catalog, compliance mapping, or
architectural decision changes:

1. Propose the change in an ADR (Architecture Decision Record)
2. Document the trigger that made the change needed
3. Document the alternatives considered and why each was rejected
4. Get explicit approval (PR review for teams, self-review with
  24-hour cooling for solo work)
5. Update the relevant artifact AND the commons together

**What this rules out**: ad-hoc changes that bypass the amendment
process. Audit findings often come from "we changed our policy but
didn't update the documentation."

## P9: Two-way doors are cheap; one-way doors get specs

Reversible work skips ceremony; irreversible work gets formal
specification.

Borrowed from Amazon's working-backwards / PR-FAQ discipline. Most
software changes are reversible (revert, fix forward). Some are not
(database schema changes, public API changes, infrastructure
deletions, customer-facing decisions). The latter get full ceremony;
the former don't need it.

**What this rules out**: heavy process for low-stakes decisions.

## P10: Verify before declaring done

After generating code, the AI verifies it compiles, tests pass,
hooks didn't block, and the spec's invariants hold. Only then does
it declare the task complete.

**Operational implication**: Every spec includes an invariants section
that the AI checks against. Every `/review` runs before "done" is
declared. Every CI run validates against the spec.

**What this rules out**: AI declaring success based on the appearance
of completion. The single most common AI failure mode is producing
plausible-but-wrong code; verification is the defense.

## P11: AI authorship is recorded, not hidden

Every action an AI took on the codebase is recorded in the audit log
and surfaced in provenance attestations.

Not because AI authorship is shameful - it isn't - but because:

- Compliance frameworks (EU AI Act Article 12, parts of NIST AI RMF)
 treat AI-assisted code as a fact that must be recorded
- Reviewers need to know what was AI-generated to apply appropriate
 scrutiny
- Future debugging benefits from knowing "this function was written
 by Claude in session X; here's the spec it was working from"

**Operational implication**: Commit messages preserve AI co-authorship
(e.g., `Co-Authored-By: Claude <noreply@anthropic.com>`); audit logs
record actor type per action; provenance attestations include a
digest of the audit log.

## P12: Honest acknowledgment of non-determinism

LLMs are non-deterministic. Specs reduce variance; they don't
eliminate it. Re-running generation may produce different code.

This is named as a principle to prevent two failure modes:

- **Overpromising deterministic builds**: A framework that claims
 "spec-driven means reproducible" creates audit problems when
 reality doesn't match. Acknowledge the gap; document the
 mitigation (temperature 0, version pinning, post-generation
 verification).
- **Treating non-determinism as failure**: When two runs produce
 slightly different code that both satisfy the spec, both are
 correct. The spec is what matters; surface-level code differences
 are not.

**Operational implication**: "Deterministic mode" flags exist but
are documented honestly - they reduce variance, not eliminate it.

## Why these twelve

These principles cover the architectural-level decisions consumers
need to make consistently. Operational decisions (specific tool
choices, file layouts) live in consuming frameworks, not here.

Adding new principles is a minor version bump of the commons. Removing
or fundamentally changing a principle is a major version bump. Either
requires the amendment process described in P8.

## Cross-framework consistency

The runtime governance framework (planned) will consume these same
principles. Defense in depth applies there too, just with different
substrate (Cedar policies and policy engines rather than hooks and
rules). Least privilege applies there too, just with different
mechanisms (capability tokens, scoped credentials).

Sharing these principles across both frameworks ensures that the
gap between build-time and runtime is *implementation*, not
*philosophy*.

## References

- NIST AI RMF (informs P11 AI authorship recording)
- EU AI Act Articles 11, 12, 14 (informs P11 and P10)
- Amazon working-backwards (informs P9 two-way doors)
- Martin Fowler / Birgitta Böckeler on SDD limitations (informs P12
 non-determinism honesty)
- OWASP / OSCAL (informs P2 defense in depth pattern)
- Twelve-Factor App (informs P1 contracts-not-installations pattern)
