<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# ADR-003: Codex agent authority and isolation

**Status**: Draft — requires maintainer approval
**Date**: 2026-08-06
**Decision-maker**: Maintainer (pending)
**Related artifacts**: `.codex/agents/`, `.codex/config.toml`, `docs/CODEX.md`

## Context

The Codex delivery layer introduces twelve named governance roles. C1 found
that their model choice, authority, write boundary, and Windows sandbox fallback
were implicit rather than a recorded architectural decision.

## Decision

Each named role is advisory and inherits its behavioral contract from the
canonical `.claude/agents/<name>.md` prompt. The parent session alone writes
artifacts and `events.jsonl`. Role TOML defaults to `read-only`; native Windows
uses the `elevated` sandbox to enforce that default. If Codex reports that a
parent override or unavailable sandbox weakens isolation, the dispatcher records
a prominent advisory-isolation warning and continues only with parent-owned
persistence.

No child may invoke another role, write files, or perform consequential external
actions. Human approval remains required for any new permission mode, trusted
hook, or model/runtime change outside this ADR's pinned baseline.

## Alternatives considered

- Give children workspace-write access: rejected because it breaks independent
  review isolation.
- Stop every review when Windows cannot enforce read-only: rejected because the
  documented advisory path preserves evidence while making the weaker boundary
  visible.
- Duplicate canonical prompts in `.codex/agents/`: rejected because prompt
  drift would undermine shared governance.

## Consequences

The framework retains a usable Windows fallback but does not overclaim
enforcement. Operators must review warnings in the dispatch artifact, and a
maintainer must approve this ADR before feature acceptance.
