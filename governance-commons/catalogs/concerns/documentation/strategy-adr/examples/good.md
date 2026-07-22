<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.strategy-adr documentation strategy ADR (good pattern)

Substrate-original good-pattern example for documentation.strategy-adr. The ADR decides
every required sub-decision, keeps the per-surface standard enforceable, and
draws the sibling boundaries.

## ADR excerpt (illustrative)

```markdown
# ADR-022: Documentation strategy

Status: Accepted   Owner: Platform   Review: annual + toolchain change

- Per-surface standard: public API surfaces carry a reference doc comment
  (purpose, parameters, errors); internal modules documented where
  non-obvious; decisions as ADRs; operations as setup + runbooks.
- Location: doc comments with code; narrative/reference under /docs;
  decisions under /docs/decisions; changelog at repo root; one entry point.
- Accuracy: doc update travels with the change; examples run as doc-tests in
  CI; quarterly accuracy review of public reference and runbooks.
- Decision records: MADR format; significance threshold = affects a public
  contract, a cross-team interface, or an operational procedure.
- Changelog: Keep a Changelog format; one entry per consumer-visible release.
- Placeholders: none in shipped docs; visible known-gap notices allowed.
- Boundaries: code structure -> code-organization; runbook telemetry ->
  observability; example execution -> testing.
```

Each sub-decision is resolved, the per-surface standard is concrete enough
for documentation.public-api-documented and documentation.accuracy-and-sync to enforce, and the boundaries are explicit.
