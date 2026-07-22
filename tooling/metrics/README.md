<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# metrics: the S5 measurement backbone

A deterministic, advisory tool that reads a feature's `events.jsonl` and feature
directory and emits a structured, per-dimension metrics report. It is the first
Phase B module of the SPS rewire, built standalone and unit-tested before any
wiring.

## What it is, and what it is not

It is a tool, not a hook and not a gate. You run it on demand and read its report.
It never blocks a commit and it never fires automatically. This placement under
`tooling/` mirrors the substrate's `governance-commons/tooling/` precedent for
deterministic governance computation: callable, unit-testable, output to stdout,
no lifecycle entanglement. If a result should ever block or fire on a trigger,
that is a hook; computing and reporting when asked is a tool, and this stays a
tool because Constraint 4 makes measurement advisory.

It emits no single aggregate quality or error score. A rolled-up number is a
vanity metric; the artifact is the per-dimension breakdown and the trend across
runs. A unit test enforces this: the report may carry no key named score,
confidence, error_rate, or similar.

## Run

    python3 tooling/metrics/measure.py specs/001-feature --base main
    python3 tooling/metrics/measure.py specs/001-feature --text

JSON by default; `--text` for a human summary. Exit code is always 0. Python 3.9+
stdlib only; no third-party packages.

## Metrics

Computed now from existing events:

- cost by agent and by checkpoint, and total estimated USD.
- catch-by-stage as a PROCESS PROXY: items raised by priority, by checkpoint. This
  counts what agents raised, not defects actually caught, and the report labels it
  as a proxy. It becomes outcome-based automatically when `defect-found` events are
  emitted (see below).
- routing mode per checkpoint: plan (the deterministic plan lookup) or fallback
  (the FIT light or full risk gate).
- consultation-evidence emitted per checkpoint (yes or no).
- closure activity counts (claimed, verified, rejected, overridden, deferred,
  declined).
- governance-to-code ratio: governance lines (all text files under the feature
  directory) over code lines (the feature's added source lines since the git base,
  excluding `specs/`). Code lines are best-effort via git and degrade to null with
  a note when no base resolves; the ratio is reported as null rather than guessed.

Defined as slots now, fed by later producers:

- criteria-coverage (the self-check scorer).
- duplication-flags (the duplication gate).
- the outcome layer: `defect-found` events with `caught_at` and `escaped_to`. This
  is the acknowledged gap the synthesis names; until those events are emitted,
  catch-by-stage is the process proxy. The slot is designed in so the trim trigger
  can be armed honestly later without a redesign.

## Inputs and the events contract

The tool reads `specs/NNN-feature/events.jsonl`, one JSON object per line. The
event shapes are the contract in `.specify/schemas/events.schema.json`, which this
module added (the shapes were previously only prose in
`.claude/docs/agent-coordination.md`). That schema adds the `checkpoint` field so
cost and catch attribute to a stage; events without it are bucketed as
`unattributed` and counted under `data_quality.events_missing_checkpoint`. The
tool reads defensively: malformed lines are recorded by number under
`data_quality.malformed_lines` and skipped, never raised, so events written before
the schema existed still load.

## Tests

    python3 -m unittest tooling.metrics.test_measure

The tests build their fixtures inline in temp directories, so they need no live
feature, plus one smoke test against `fixtures/sample-events.jsonl`.
