<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# task-granularity: the oversized-task gate

Reads a tasks.md and flags tasks too coarse to be a single, independently deliverable
unit, before they enter the line. The fifth and last standalone Phase B tool.

## What it is, and what it is not

A tool, not a hook; it never blocks. It reports violations and a `passes` verdict;
failing the plan-to-tasks checkpoint on a blocking violation is the Phase C wiring
step. It emits no aggregate score. The split of an oversized task is the plan agent's
judgment; the detection is what this does.

## Format compatibility

The task-line format is stock spec-kit's, confirmed against both the resolved
tasks-template (there is no tasks override, so resolve_template returns stock) and
the speckit-tasks skill's format rules. The canonical line is
`- [ ] [TaskID] [P?] [Story?] Description with file path`. The skill requires the
[Story] tag only on user-story-phase tasks, so setup, foundational, and polish tasks
are legitimately story-less; the vague-task signal keys on the story tag precisely so
it does not false-positive on those. Placeholder TXXX lines (ID not T followed by
digits) are skipped.

## Rules

Blocking:
- multi-story: more than one [USn] tag on a task. spec-kit's format is singular
  [Story?]; a task spanning stories is outside its own format and breaks the
  independent-testability the flow depends on.
- schema-plus-behavior mix: a labeled heuristic, not a parser of intent. Trips when
  the description hits both a data keyword (model, schema, migration, entity, ...) and
  a behavior keyword (implement, service, endpoint, handler, ...), or when the task
  touches both a models/ path and a services or endpoint path. Two clean tasks, one
  creating a model and one implementing a service, do not trip; a single task doing
  both does.

Advisory:
- too-many-files: more than --max-files distinct file paths (default 5, the synthesis
  bound; configurable).
- vague task: a story-tagged task with no file path. Advisory rather than blocking
  because spec-kit's own sample tasks (for instance "Add validation and error
  handling") omit paths, so blocking would flag patterns spec-kit itself ships.

## Output

tasks_total; violations (each task_id, line, severity, rule, detail); blocking_count;
advisory_count; and passes (true when there are no blocking violations). Advisory
violations do not affect passes.

## Run

    python3 tooling/task-granularity/check.py specs/001-feature/tasks.md --text
    python3 tooling/task-granularity/check.py specs/001-feature/tasks.md --max-files 5

Stdlib only, no YAML. Exit code is always 0.

## Tests

The directory name has a hyphen, so run the test file directly:

    python3 tooling/task-granularity/test_check.py

A fixture under fixtures/sample-tasks.md exercises all four rules plus the exemptions
(story-less setup tasks, the TXXX placeholder, and the clean separated model and
service tasks).

## Boundaries

It detects; it does not split tasks (the plan agent's job) and it does not gate (it
reports, never blocks). Same-shape coarseness is what it catches; whether a split is
the right design is human and plan-agent judgment.
