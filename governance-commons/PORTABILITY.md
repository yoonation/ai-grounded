<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Portability

This directory is designed to be portable. It will eventually become
its own repository (`ai-governance-commons` or similar) consumed by
multiple AI development frameworks.

## The portability rule

**Files inside `governance-commons/` MUST NOT reference any file or
directory outside `governance-commons/`.**

This is the single most important discipline for portability. Violations
turn the eventual extraction into a refactor instead of a `git mv`.

### What this means concretely

- No path references like `../docs/SPEC.md`, `../.claude/skills/`, etc.
- No assumptions about consuming framework layout
- No hardcoded tool names ("Claude Code does X")
- No embedded references to specific frameworks' commands or hooks
- No tool-specific syntax (Claude Code slash commands, Cursor rules, etc.)

### What is allowed

- References to other files within `governance-commons/` (e.g.,
 `catalogs/threats/owasp-llm-top10.yaml` from a skill in this directory)
- References to external standards by URL or canonical name (OWASP,
 NIST, ISO, Sigstore, OpenTelemetry)
- References to vendor-neutral tools (`cosign`, `cedar`, `cuelang`, etc.)
- Cross-references via standard IDs (LLM01, ASI03, NIST AI RMF GOVERN-1.1)

## Why portability matters

The eventual second consumer of this commons is a runtime governance
framework for production AI agents. That framework will share:

- The same threat models (OWASP LLM, OWASP Agentic)
- The same compliance mappings (EU AI Act, NIST AI RMF, ISO 42001)
- The same identity model (actor types and trust contracts)
- The same audit event envelope (OpenTelemetry-aligned)
- The same policy DSL (Cedar)
- The same playbook patterns

If those concepts diverge between build-time and runtime frameworks,
audit findings become possible: "compliance mapping for SOC 2 CC6.1
differs between your build pipeline and your production system."
Avoiding that requires the single-source-of-truth this commons provides.

## Extraction trigger

This directory becomes its own repository when:

1. A second framework starts consuming it (planned: runtime governance
  framework), OR
2. The commons reaches 1.0 stability and external organizations want to
  adopt it independently, OR
3. The parent framework is forked/adopted at scale and shared governance
  becomes a coordination need

Until any of those trigger, this lives inside the parent framework as a
ready-to-extract subdirectory.

## Extraction procedure

When extraction time comes:

1. Create new repository (e.g., `ai-governance-commons`)
2. `git mv governance-commons/ <new-repo>/` (or git filter-repo for history)
3. Update parent framework to reference commons as:
  - Git submodule (lockstep version, tight coupling), OR
  - Package dependency (looser coupling, versioned), OR
  - Documentation reference (loosest coupling, manual sync)
4. Verify no cross-references broke (the portability rule should make
  this verification trivial - if the rule was followed, nothing breaks)
5. Bump commons VERSION to 1.0 if mature enough
6. Document extraction date in this file for audit trail

## Verification

A simple grep can verify the portability rule is being followed:

  cd governance-commons/
  grep -rn -E '\.\./|/(\.claude|docs|specs|src|infra)/' . \
    --include="*.md" --include="*.yaml" \
    --include="*.cedar"

If the grep returns matches, those references must be removed or
converted to in-commons references before extraction.

## Extraction log

Record extraction events here when they happen:

  YYYY-MM-DD: extracted to <repo-url> at commons VERSION x.y.z
