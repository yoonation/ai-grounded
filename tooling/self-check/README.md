<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# self-check: the closure-time acceptance-scenario scorer

Computes criteria-coverage and scope-delta at closure: which of the spec's
user-story acceptance scenarios are demonstrably addressed with evidence, and what
was touched beyond what was planned. Criteria-coverage is the loop's stop condition.

## The criterion is the acceptance scenario, not FR

spec-kit organizes around prioritized, independently-testable user stories whose
Given/When/Then acceptance scenarios are what a feature is validated against.
Functional requirements are a separate detail list that nothing downstream consumes
(tasks organize by user story, analyze infers the mapping). So the scorer keys on
the user-story acceptance scenario, the spec's actual testable unit. There is no FR
axis and no secondary FR report: if you want the detail behind a result, you follow
the story. A scenario's identity is the pair (story, scenario index), rendered
US<n>/<index>, matching how stock spec-kit numbers them (not a flat global ID).

## What it is, and what it is not

A tool, not a hook; it never blocks. No confidence or quality score: coverage is an
explicit numerator over the authoritative denominator, and the stop condition is a
derived boolean with named blocking reasons. Distinct from speckit-analyze, which is
plan-time story-to-task inference; this is closure-time scenario-to-evidence,
deterministic.

## Anti-self-attestation

- The authoritative scenario set comes from spec.md, parsed from the user-story
  blocks, not from the self-check, so a scenario silently omitted from the
  self-check is caught (missing_from_self_check) rather than letting the self-check
  define its own denominator.
- A scenario marked addressed with no evidence reference is flagged
  (addressed_without_evidence) and does not count as covered; whitespace-only
  evidence does not count.

## Inputs

- The spec (`<feature_dir>/spec.md`): parsed for `#### User Story N (Priority: PN)`
  headings and the numbered items under each `**Acceptance Scenarios**` block. This
  is the structure restored to the override spec-template; the scorer depends on it.
- The self-check (`<feature_dir>/self-check.yaml`), the input contract this module
  defines, awaiting its producer in Phase C:

      stories:
        - id: US1
          priority: P1
          scenarios:
            - index: 1
              addressed: true
              evidence: ["tests/filter.test.ts::secret filter", "src/filter.ts"]
            - index: 2
              addressed: false
              evidence: []
      scope:
        planned: ["src/filter.ts", "src/rank.ts"]
        touched: ["src/filter.ts", "src/rank.ts", "src/telemetry.ts"]

- Touched files for scope-delta: from git when `--base` is given (excluding specs/),
  otherwise from the self-check's `scope.touched`.

## Output

criteria_total, covered, coverage_count, coverage_fraction; gaps (unaddressed,
addressed_without_evidence, missing_from_self_check, extra_in_self_check);
scope_delta (creep, incomplete); criteria_met (the stop-condition boolean); and
blocking_reasons. Scope creep is advisory and does not fail the stop condition;
unaddressed, evidence-less, or missing scenarios do.

## Run

    uv run --with pyyaml python3 tooling/self-check/score.py specs/001-feature --base main --text

The pure core takes synthetic inputs and needs no spec and no YAML; only the CLI
reads the files and git, so it imports PyYAML lazily (run via uv). Exit code is
always 0.

## Tests

The directory name has a hyphen, so run the test file directly:

    python3 tooling/self-check/test_score.py

Pure-core tests use synthetic scenarios; a fixture under fixtures/sample-feature
demonstrates the gap reporting (one covered, one addressed without evidence, one
missing).

## Boundaries

It scores; it does not produce the self-check (the implement or self-check step,
wired in Phase C) and it does not gate. The spec is the authoritative scenario
source; the self-check is checked against it, not trusted to define it.
