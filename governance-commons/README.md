<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Governance Commons

Portable governance primitives shared across AI development frameworks.

**Version**: see [VERSION](./VERSION)
**License**: same as parent framework
**Status**: Content-complete (25 stable concerns), ecosystem-complete
(5 stable profiles: the baseline plus four industry tilts), and
tooling-scaffolded. See [SUBSTRATE-FIT.md](./SUBSTRATE-FIT.md) for the honest
fit-by-shape assessment and the L1 enforcement caveat before adopting.

## What this is

A self-contained directory of governance artifacts that any AI development
framework can consume:

- **Identity model** - actor types and trust contracts
- **Audit event schema** - envelope shape for AI action logging
- **Threat catalogs** (YAML) - OWASP LLM, OWASP Agentic, MITRE ATLAS, STRIDE
- **Compliance catalogs** (OSCAL via Trestle) - NIST 800-53, NIST CSF,
 NIST 800-171, NIST 800-218 (auto-fetched from NIST); NIST AI RMF and
 EU AI Act (hand-authored OSCAL); ISO 42001 and SOC 2 TSC (reference-only
 due to copyright)
- **Policy primitives** - Cedar policy fragments for common patterns
- **Incident playbooks** - response procedures for common AI failure modes
- **Attestation formats** - SLSA and in-toto provenance specifications
- **Library context** - version-specific guidance for libraries that AI
 agents frequently hallucinate APIs for

## What this is not

- Not specific to any AI tool (Claude Code, Cursor, Codex, etc.)
- Not specific to any framework layer (build-time vs runtime)
- Not specific to any project type (greenfield, brownfield, library, app)
- Not a runtime library - these are reference artifacts, not executable code
- Not a substitute for upstream standards - this curates and cross-references
 authoritative sources rather than redefining them

## Why it exists separately

This directory was extracted from the parent framework with the intent of
becoming its own repository when a second consuming framework starts
(planned: a runtime governance framework for production AI agents,
distinct from this build-time framework).

By isolating governance artifacts now with strict "no outside references"
discipline (see [PORTABILITY.md](./PORTABILITY.md)), the eventual
extraction is a `git mv` operation rather than a refactor.

## How to use it

From within the parent framework, consumers reference governance-commons
artifacts by path. For example:

- A skill that needs OWASP LLM Top 10 references
 `governance-commons/catalogs/threats/owasp-llm-top10.yaml`
- A hook that emits audit events follows the schema in
 `governance-commons/spec/audit-envelope.md`
- A policy enforcement script reads
 `governance-commons/policies/no-pii-access.cedar`
- Compliance catalogs are managed via Trestle inside
 `governance-commons/catalogs/compliance/trestle-workspace/`

Catalogs use upstream standards' IDs as primary keys (LLM01, ASI03,
ATLAS-T0048, NIST AI RMF GOVERN-1.1, NIST 800-53 AC-2, etc.) so consumers
can cite by ID without needing the full content loaded into context.

## Layout

  governance-commons/
  ├── README.md            This file
  ├── VERSION              Semver of this commons
  ├── CHARTER.md           Supreme authority document (Articles I-IX)
  ├── CHANGELOG.md         Lifecycle transitions per Charter Article VIII
  ├── FUTURE.md            Substrate backlog and design debt
  ├── SUBSTRATE-FIT.md     Honest fit-by-shape assessment and the L1 caveat
  ├── PORTABILITY.md       Extraction plan and one-way reference rule
  ├── MAINTENANCE.md       Update protocol and review cadence
  ├── spec/                Stable governance specifications (prose)
  ├── catalogs/
  │  ├── concerns/         25 OSCAL concern catalogs (the engineering rule book)
  │  ├── threats/          Threat catalogs (STRIDE, OWASP LLM, OWASP ASI, OWASP AST, MITRE ATLAS)
  │  └── compliance/       Compliance catalogs (OSCAL via the Trestle workspace)
  ├── mappings/            Cross-taxonomy mappings (threats to concern rules)
  ├── profiles/            Production-grade baseline plus four industry-tilt profiles
  ├── decision-frameworks/ MADR decision templates (the L3 layer)
  ├── toolchain/           Tool registry and capability selection (L1 enforcement; bindings co-located per rule)
  ├── policies/            Cedar policy primitives
  ├── playbooks/           Incident response procedures
  ├── attestation/         SLSA and in-toto format specs
  ├── lib-context/         Library-specific AI guidance
  ├── schemas/             JSON schemas, one per artifact type
  ├── reference/           Portable consumption-contract demonstrations (agents, hooks, manifest, CI)
  └── tooling/             Tool skeletons (the maintained validators live in repo-root scripts/)

The counts above (25 concerns, 5 profiles, and so on) are the at-a-glance
figures; `VERSION`, `CHANGELOG.md`, and the validators are the authoritative
source if they ever disagree with this prose.

## Maintenance

See [MAINTENANCE.md](./MAINTENANCE.md) for the quarterly review protocol
and how to update catalogs when upstream standards change.

Threat catalogs include `LAST_REVIEWED` and `UPSTREAM_SOURCE` metadata so
staleness is detectable and the source of truth is always traceable.
Compliance catalogs use OSCAL's native metadata and are managed via
Trestle, which handles schema validation and structure on every change.
