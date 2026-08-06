<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# ADR-004: Codex provenance and capability baseline

**Status**: Draft — requires maintainer approval
**Date**: 2026-08-06
**Decision-maker**: Maintainer (pending)
**Related artifacts**: `tooling/codex/`, `.agents/skills/`, `.codex/hooks/`

## Context

The local adapter depends on GPT-5.6 role models, custom agents, project hooks,
permission profiles, and native Windows sandbox behavior. C1 found that using
an unbounded `@latest` installation instruction did not make that capability
contract reproducible or testable.

## Decision

AI Grounded supports Codex CLI `0.146.1` or later for this adapter. A local
capability probe verifies the installed version, all twelve generated roles,
the generated permission profile, and required shared skills. Role TOML and
permission configuration are generated artifacts with named source registries
and drift checks; lifecycle behavior remains authored Python covered by tests.

Credential paths are declared once in the reviewed registry and rendered into
both the Codex profile and the hook matcher. Updates to the registry, generated
assets, hooks, or the capability baseline require review and rerunning the
probe.

## Alternatives considered

- Support every Codex version that starts successfully: rejected because model
  and sandbox behavior changed within the tested setup.
- Keep static duplicated path lists: rejected because C1 demonstrated drift.
- Package the adapter as a hosted plugin now: deferred; this decision covers
  only trusted local Codex projects.

## Consequences

Operators upgrade Codex before use. The adapter gains an explicit support floor
and auditable generated-asset provenance, at the cost of a small local check.
This ADR requires maintainer approval before feature acceptance.
