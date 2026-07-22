<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Project Log

This file is the project's append-only log for cross-feature observations that don't belong to any single feature. It is project-scoped, not framework-scoped (the framework's backlog lives in `FUTURE.md`, also at the repo root).

Three categories of entries land here:

1. **Cross-cutting observations** - Engineering observations raised by framework agents during feature work that apply across the project rather than to a single feature. Routed here by `closure-auditor` when an agent flags an item as `cross-cutting: true`.
2. **Decisions deferred** - P2 items deferred across features that aren't yet ready for an ADR. When the same deferral recurs in 3+ features, consider escalating to an ADR or addressing.
3. **Architectural drift** - Patterns the framework's agents notice spanning multiple features (e.g., "three features now use ad-hoc retry logic; consider a shared retry library").

## How entries get here

- **From agents** (automatic via closure-auditor): when an agent flags a finding as `cross-cutting: true` in its frontmatter, closure-auditor appends a structured entry under "Cross-cutting observations" below.
- **From you** (manual): add notes any time. The framework doesn't require entries to be agent-sourced.

## Promotion path

An entry that recurs in 3+ features OR escalates to a P1 concern should graduate to a project ADR (`docs/decisions/ADR-NNN.md`). When that happens, leave the original entry here with a `-> Promoted to ADR-NNN` note. Don't delete; preservation is the point of an append-only log.

---

## Cross-cutting observations

<!-- Agent-routed entries land here. Format:
### YYYY-MM-DD - <short title>

**Source:** `<agent-name>` at C<checkpoint>, feature `NNN-feature-name`, invocation `<ULID>`.
**Why it's cross-cutting:** <why the agent flagged it as project-wide rather than feature-specific>.
**Why it matters:** <what would happen if ignored across the project>.
**Recommended action:** <what to do, or "monitor for recurrence">.
-->

(none yet)

---

## Decisions deferred

<!-- Cross-feature deferrals. Format:
### YYYY-MM-DD - <short title>

**Originating feature:** `NNN-feature-name`
**Item ID:** `<source-item-id>`
**Why deferred:** <reason>
**Trigger to revisit:** <event that escalates this; usually "if recurs in N features" or "if production incident touches this">
-->

(none yet)

---

## Architectural drift

<!-- Patterns spanning features. Format:
### YYYY-MM-DD - <short title>

**Observed in:** features `NNN`, `NNN`, ... (list each)
**Pattern:** <what's happening>
**Risk:** <what this becomes if unchecked>
**Mitigation candidate:** <a possible solution; not yet decided>
-->

(none yet)
