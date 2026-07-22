<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# dispatch: the deterministic dispatcher

Replaces the orchestrator's routing. Given an approved `feature-concerns.yaml` and a
checkpoint, it organizes the plan's flat per-checkpoint agent list into the
framework's canonical wave structure, prunes to what the plan carries, and emits the
wave-ordered dispatch list plus the plan-sourced routing-decision event. The main
session executes the list.

## No judgment here

Which agents run was decided once by the concern-selector (the one reasoning step)
and recorded in the plan. The wave structure is fixed framework data. This script
organizes one against the other; it decides nothing. That is the point of retiring the
orchestrator as a reasoning agent: routing is deterministic once the plan exists.

## The canonical waves

The fixed dependency graph, the same structure the orchestrator encoded:

- C1: one parallel wave (staff-engineer, threat-modeler, performance-reviewer, production-readiness)
- C2: Wave 1 parallel (the four upstream), Wave 2 operational-architect, Wave 3 test-architect, Wave 4 adr-architect (each sequential)
- C3: Wave 1 parallel (staff-engineer, code-reviewer, security-reviewer), Wave 2 closure-auditor
- C4: closure-auditor (single)

An agent appears in its canonical wave only if the approved plan also carries it;
empty waves are dropped.

## Hard-fail discipline

If the plan names an agent that has no place in the checkpoint's canonical waves, the
dispatcher refuses to dispatch it and exits nonzero rather than routing it somewhere
it does not belong. That surfaces a plan-versus-graph inconsistency loudly.

## What the orchestrator did that this does not

The orchestrator's judgment enrichments are triaged elsewhere, not reproduced here:
cost estimation to the measurement backbone (which computes actual cost from events),
ADR recommendation to the operator-mark plus adr-architect mechanism (adr-architect
stays in the C2 wave table), cross-agent observations to the closure-auditor, and
tier stratification subsumed by the plan-approval gate.

## Exit codes

    0   dispatch list produced
    1   hard stop (no plan, no routing for the checkpoint, or an unplaceable agent)

## Run

    uv run --with pyyaml python3 tooling/dispatch/dispatch.py specs/001-feature --checkpoint C1

The core is pure stdlib; only the CLI reads the plan, so run via uv for PyYAML.

## Tests

    python3 tooling/dispatch/test_dispatch.py

## Boundaries

It dispatches from an approved plan; it does not produce the plan (concern-selector),
gate it (plan-gate), or compute the floor (dial). It is the mechanical step that turns
an approved plan into a wave-ordered invocation list.
