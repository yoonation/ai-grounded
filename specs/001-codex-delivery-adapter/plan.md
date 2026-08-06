# Implementation Plan: Codex Local Delivery Adapter

**Branch**: `001-codex-delivery-adapter` | **Date**: 2026-08-06 | **Spec**: [spec.md](spec.md)

## Summary

Add a project-scoped Codex delivery adapter around the existing governance
substrate. Keep `.claude/` as the canonical agent-prompt source, add Codex
configuration and render targets, and preserve all existing Git enforcement.

## Technical Context

**Language/Version**: Python 3.12, TOML, JSON, Markdown

**Testing**: Existing stdlib Python test pattern (`test_*.py`)

**Target Platform**: Codex CLI, desktop app, and IDE local projects

**Constraints**: Codex-specific behavior remains in `.codex/` and `.agents/`;
Claude-specific behavior and all Git gates remain compatible.

## Design

1. Generate compact Codex TOML agent definitions from an explicit Python
   registry. Each definition references the canonical Claude prompt and has a
   read-only sandbox default.
2. Render framework extension commands to both `.claude/skills/` and
   `.agents/skills/`; Codex renders use `$speckit-*` command references.
3. Use a portable Python hook-policy adapter for Codex lifecycle hooks. Codex
   sandbox permissions provide the hard secret-file boundary; hooks provide
   branch and command protections plus report-only linting.
4. Extend bootstrap and documentation to verify and explain both integrations.
5. Pin the supported Codex capability baseline at `0.146.1` and expose a local
   probe that validates the installed CLI version, required configuration, agent
   registry, and rendered skill locations before governed work begins.
6. Keep credential-path rules in one reviewed Python registry. Render the
   project permission profile from that registry and use the same matcher in
   lifecycle policy, so configuration and hook checks cannot silently diverge.
7. Treat lifecycle-hook input as an authorization boundary: require the
   documented pre-use payload shape, return Codex's structured deny response,
   and use an explicit read-only shell allowlist on `main`.

## Ownership and provenance

| Asset family | Canonical source | Derived output / enforcement | Direct edits |
|---|---|---|---|
| Role behavior | `.claude/agents/<name>.md` | `.codex/agents/<name>.toml` via `tooling/codex/generate_agents.py` | TOML prohibited |
| Framework commands | `.specify/extensions/*/commands/*.md` | `.claude/skills/`, `.agents/skills/` via `tooling/skill-drift/render.py` | Rendered skills prohibited |
| Sensitive path classes | `tooling/codex/policy_registry.py` | `.codex/config.toml` via `tooling/codex/generate_config.py`; lifecycle matcher | Generated config prohibited |
| Lifecycle behavior | `.codex/hooks/policy.py` and tests | `.codex/hooks.json` invokes the policy | Hook JSON is authored |
| Integration base assets | Spec-Kit manifests | `.specify/integrations/*.manifest.json` | Managed assets refreshed only through Spec-Kit |

## C1 corrective decisions

ADRs `ADR-003` and `ADR-004` record the authority/isolation and provenance/
compatibility decisions raised by C1. They are drafted for maintainer approval
before the feature is accepted.

## Constitution Check

The feature changes local agent capabilities and therefore uses least
privilege, threat-aware review, deterministic validation, and the existing
loop-closure gate. No production service, data migration, or external API is
introduced.
