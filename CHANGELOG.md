<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Changelog

All notable changes to AI Grounded are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-21

Initial public release.

### Added

- Spec-driven workflow on GitHub spec-kit (specify, clarify, plan, tasks,
  implement).
- A 7-article project constitution with pre-build gates and ADR discipline.
- Twelve specialized AI sub-agents (eleven review agents across seven
  cognitive categories plus a pre-construction discovery agent) with
  wave-based parallel dispatch.
- Priority-aware loop closure across three layers: user claim, semantic
  audit (closure-auditor), and a mechanical pre-commit hook.
- Governance substrate (`governance-commons/`): OSCAL compliance catalogs,
  threat catalogs (STRIDE, OWASP LLM Top 10, OWASP Agentic ASI Top 10,
  MITRE ATLAS), concern catalogs, Cedar policies, attestation specs, and
  incident playbooks.
- Spec-kit preset architecture so customizations survive upstream refreshes.
- Deterministic tooling under `tooling/` with unit tests, plus a local
  pre-commit gate chain (secret scan, schema/manifest validation, quality
  checks, loop-closure verification).
