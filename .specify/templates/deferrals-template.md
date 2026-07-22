<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Deferred concerns — feature [NNN-feature-name]

This file documents P2 concerns that have been deliberately
deferred to a future feature rather than addressed in this one.

Each `deferred` event in `events.jsonl` must have a matching entry
here. The `verify_loop_closure.py` pre-commit hook checks for both;
a deferred event without a rationale entry blocks the commit.

P1 concerns cannot be deferred. They must be closed in code, test,
ADR override, or spec amendment.

## How to add an entry

When deferring a P2 concern:

1. Tell main session: "Defer [ITEM-ID] to [target feature]. Reason:
   [brief rationale]."
2. Main session writes a `deferred` event to events.jsonl pointing
   to this file with anchor `#item-id`.
3. Add a section below using the template format. The section
   heading must contain the item ID for the hook to find it.

## Entry template

Copy this template for each deferral:

```markdown
## [ITEM-ID]

**Source agent**: [staff-engineer | threat-modeler | performance-reviewer | production-readiness | operational-architect | code-reviewer | security-reviewer]
**Priority**: P2
**Deferred to**: [target feature name or number]
**Decision-maker**: [your name]
**Date**: [YYYY-MM-DD]

**Original concern** (one-sentence summary):
[Briefly state what the concern was, in your own words]

**Why defer**:
[Why this concern is better addressed in the target feature.
Connect to project scope, timing, related work, or technical
constraints. Be specific enough that your future self (or a
teammate) understands the reasoning without needing to re-read the
original concern.]

**Plan for target feature**:
[How the concern will be addressed there. This isn't a contract —
it's a marker so the deferral isn't forgotten.]
```

## Grouped deferral (one entry, several items)

When several consolidated items defer together (for example, the
items closure-auditor merged at high confidence), you do not need a
separate heading per ID. One entry may cover them all if it carries a
structured `Source items:` line that lists every covered ID. The
`verify_loop_closure.py` hook matches a deferred event against EITHER
a heading that names the ID OR a `Source items:` line that lists it,
so a grouped entry documents all of its IDs.

```markdown
## [GROUP-TITLE]

**Source items**: [ITEM-ID-A], [ITEM-ID-B], [ITEM-ID-C]
**Source agent**: [agent(s)]
**Priority**: P2
**Deferred to**: [target feature name or number]
**Decision-maker**: [your name]
**Date**: [YYYY-MM-DD]

**Original concern** (one-sentence summary):
[What the consolidated concern was]

**Why defer**:
[Why these are better addressed together in the target feature]

**Plan for target feature**:
[How they will be addressed there]
```

The label may be written `Source items:` or `**Source items**:`; the
hook is tolerant of the bold marker. Each ID must be a recognizable
token (e.g. `SE-005`) on that single line.

## Entries

<!-- Add deferral entries below this line. The hook looks for either
     a section heading (## ... ITEM-ID) OR a structured
     "Source items:" / "**Source items**:" line that lists the ID, to
     verify each deferred event in events.jsonl has a corresponding
     rationale. -->
