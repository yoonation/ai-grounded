<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Changelog

This file records all lifecycle transitions of Governance Commons
content per Charter Article VIII and `spec/rule-lifecycle.md`.

The format follows [Keep a Changelog](https://keepachangelog.com/)
with substrate-specific sections per `spec/rule-lifecycle.md`:

- **Added**: new draft or stable content entering the substrate
- **Promoted**: draft -> stable transitions
- **Deprecated**: stable -> deprecated transitions
- **Retired**: deprecated -> retired transitions
- **Abandoned**: draft -> retired transitions (draft content removed)
- **Changed**: editorial corrections, profile modifications, schema
  updates
- **Migration**: guidance for consumers reacting to lifecycle
  changes

The substrate version (in `VERSION`) follows semantic versioning.
Each version increment corresponds to one or more entries below.

## [Unreleased]

### Changed

- **AI model pricing verified and corrected (lib-context).** Verified
  2026-07-04 against the provider pricing docs: Fable 5 confirmed at
  10.00/50.00 (the UNVERIFIED flag lifted; classifier-fallback billing,
  128K output cap, batch rate, and the 30-day-retention/no-ZDR compliance
  posture recorded), Haiku 4.5 corrected from a stale 0.80/4.00 to
  1.00/5.00, and Opus 4.7/4.6 corrected from 15.00/75.00 (an Opus 4.0/4.1-era
  rate) to their actual 5.00/25.00 with fast-mode notes. The cost-computation
  example recomputed on current Opus 4.8 rates. A framework_routing block was
  added to selection_guidance naming the agent frontmatter `model:` fields as
  the authoritative routing source and recording the tier rationale,
  including why Fable 5 carries no standing agent assignment.

## [1.3.0] - 2026-07-04

**Hardening-campaign release.** Consolidates the single-source-of-truth
sweep: the legacy rule-id migration (889 files), the orphaned
concern-catalog schema retirement, the manifest rule-list
resolution-by-removal with refreshed pins, the cloud-scaling catalog
expansion (7 to 19 patterns), and the toolchain-refactor documentation
corrections. Reference-manifest material changes accompany this minor bump
per the manifest's own guarantee note.

### Retired

- **`schemas/concern-catalog.schema.json` retired (orphaned schema of the
  retired single-file catalog model).** The schema validated the pre-refactor
  single-file `catalogs/concerns/*.oscal.yaml` catalogs and still enforced the
  retired lowercase L-numbered control-id pattern; the toolchain refactor
  moved validation to the source layer (`concern.schema.json`,
  `rule.schema.json`, `binding.schema.json` via `tooling/assemble/validate.py`)
  and nothing has referenced this schema since (grep-verified across tooling,
  gates, Makefile, CI reference workflow, and schema $refs). Retired rather
  than modernized: the artifact class it validated no longer exists, and the
  assembled `dist/` catalogs are generated output of validated sources.
  Migration: consumers who validated single-file catalogs against this schema
  should validate sources against the source-layer schemas, or treat `dist/`
  as generated. Doc pointers in `schemas/README.md` (table refreshed to the
  live 11-schema inventory), `spec/catalog-format.md`, and
  `catalogs/README.md` updated; the FUTURE OSCAL-migration entry now names
  the profile schema only. A dist-output validator, if ever wanted, is a new
  build, not this schema.

### Changed

- **Legacy rule-id prose sweep (shape A, resolved-by-migration).** The
  capability-gate toolchain refactor renamed every rule's `id:` but left the
  support prose unswept: 229 distinct retired L-numbered tokens across 889
  files (concern examples, checklists, decision files, rule.yaml prose,
  the baseline profile's selection remarks, mapping rationales and
  relation-id labels, specs, reference agents and templates, one CHARTER
  example passage, and the assembled dist/ output). The mapping table was
  built by triangulation from each rule folder's own frontmatter anchors
  (211/226 tokens, zero conflicts) plus adjacent descriptive prose for the
  remainder, every entry verified against a live rule.yaml before rewriting.
  Rewrites: prose tokens to dotted current ids; mapping relation-id labels to
  the owasp-top10 slug convention; checklist/test-template
  `substrate-rule-href` values (which pointed at the retired single-file
  catalog paths) to the co-located `rule.yaml`; decision.md `framework-id`
  frontmatter to the `<concern>.<rule-slug>` scheme (33 files); range
  mentions to plain-language phrasing; the extension-contract custom-catalog
  identifier convention to the current scheme; the CHARTER example id as an
  editorial correction under the Charter's own editorial-changes provision.
  `dist/` reassembled from the swept sources; the retired vocabulary now
  survives only in historical records (CHANGELOG, FUTURE, framework-review
  snapshots, the SUBSTRATE-REFERENCE snapshot) plus one illustrative mention
  in catalogs/README. FUTURE.md entry marked RESOLVED same-day.

- **Manifest rule lists removed (resolved-by-removal of the profile-duplication
  drift source).** The consumer `project-manifest.yaml` and the reference
  `reference/manifest/governance-manifest.yaml` pre-commit checkpoints each
  enumerated retired L1 registry-id rule IDs (50 and 47 respectively) that
  resolved to nothing after the capability-gate toolchain refactor. Both lists
  are deleted; each checkpoint now declares `rules: []` with the resolved
  profile as the selection mechanism, and FUTURE.md "Manifest rule lists
  duplicate the profile" is marked RESOLVED-BY-REMOVAL with the selector design
  retained should rule-level targeting return. Both manifests' commons-version
  pins refreshed to 1.2.0 (they read 1.0.1 and 0.5.0); decision-framework
  identifiers rewritten from retired flat madr names to the live
  `<concern>.<rule-slug>` scheme resolving to co-located `decision.md` files,
  every id verified against disk.

- **Toolchain-refactor documentation residue corrected.** Four documents still
  described the retired L1 binding model as current: `catalogs/README.md`
  (retired `<PREFIX>-<LAYER>-<NUMBER>` identifier convention and single-file
  `concerns/*.oscal.yaml` layout presented as the live model),
  `spec/consumer-scaffold.md` Section 4.2 (bindings described as declaring
  `rule-format: semgrep-pattern-v1`; zero of the 62 on-disk bindings do, all
  are `capability-bound`), the reference CI workflow's engine and Step 4
  comments, and the consumer-side `30-sast` gate comment citing the retired
  registry-id audit document as an existing path. All four now describe the
  capability-gate model, with the retired convention noted as historical where
  useful for reading old records. The same audit found the refactor never swept
  support prose: ~365 concern support files, the assembled dist/ catalogs, the
  baseline profile, and several specs still cross-reference rules by retired
  L-numbered ids with no machine mapping; recorded as a FUTURE.md entry
  ("Legacy rule-id references in support prose") rather than swept here.

### Added

- **Cloud-scaling failure-mode catalog expanded from consumer canon (12 new
  patterns, draft).** `catalogs/design-patterns/cloud-scaling-failure-modes.yaml`
  grew from 7 to 19 patterns by promoting the performance-reviewer agent's
  inline AWS failure-mode rubric into provider-neutral substrate entries
  (FW-001-style canon promotion, same move as the traditional OWASP Top 10
  table): cold-start latency, implicit concurrency ceilings, execution-time
  caps, missing ingress throttles, capacity-mode mismatch, autoscaler reaction
  lag, telemetry volume/cardinality cost, delayed-metrics feedback,
  connection-drain deploy stalls, hidden network bandwidth ceilings,
  control-plane rate limits on the data path, and per-item crypto calls. Three
  further rubric items folded into existing patterns (hot partition,
  sequential prefix, connection-per-request). Descriptions are
  substrate-original paraphrase, provider-neutral with AWS naming as the
  documented exemplar per the catalog's own convention. The consumer agent was
  dereferenced to consult the catalog by id, removing the dual-home canon.

- **OWASP Top 10 (2025) to concerns mapping (draft).**
  `mappings/owasp-top10-to-concerns.oscal.yaml` closes the one threat spine that
  had a catalog but no concern mapping: the traditional OWASP Top 10 was the sixth
  threat catalog against five mappings, so its coverage was not legible to the
  mapping-coverage-reporter and MASTER-GRID's "mapped to concerns" claim for it was
  aspirational. The mapping records 54 `addressed-by` relations across all ten 2025
  categories (SSRF mapped under A01 per the 2025 consolidation), each target-rule a
  live substrate rule id (50 distinct rules; several mitigate more than one
  category), with A06 Insecure Design honestly recorded as partial
  coverage (design-forcing strategy rules plus the threat-modeler review pass, not
  a full secure-design methodology at L1/L2). Promoted to `stable` by the substrate
  author in the same session via a recorded Charter Section 2.4.1 override: the
  author elected same-session attestation (drafted and attested 2026-07-01) to
  unblock feature-006, expressly waiving the one-calendar-day minimum interval. The
  attestation-mechanism prop records this as an author override, not an observed
  interval. MASTER-GRID mapping count reconciled 5 to 6 and the mapping-coverage-reporter
  README updated to list six mappings.

- **Wired MASTER-GRID counts as a commit-time drift gate.** The count tool gained
  a `--check` mode that recomputes every section-4 count from the filesystem and
  compares it to the numbers committed in `docs/MASTER-GRID.md` (per-concern table
  rows, layer totals, and the threat/profile/mapping/pattern/test-template
  scalars), reporting each mismatch; `--strict` makes drift exit non-zero. A new
  report-only pre-commit gate, `.githooks/pre-commit.d/90-master-grid-counts`,
  runs it when a commit touches any section-4 count source (concern catalogs,
  threat or design-pattern catalogs, profiles, mappings) or the index, so the
  authoritative
  index can no longer silently fall behind the substrate it indexes (the failure
  that produced the L2 130-vs-131 and design-pattern 4-vs-9 drift). This is the
  same generated-plus-drift-check idiom as `00-gate-inventory`.
  `tooling/grid-counts/test_counts.py` forces scalar drift, table-row drift, and
  the strict/advisory exit-code split. Regenerating `docs/GATES.md` to register the
  gate also cleared its standing staleness. Deliberately NOT built: a check that
  the concern `summary` fields still describe their rules; that is a semantic
  judgment, not a mechanical comparison, so a script would only give false
  assurance (summary accuracy stays a review-time concern; presence is already
  schema-enforced).

- **Added a deterministic count tool for MASTER-GRID (`tooling/grid-counts/counts.py`).**
  MASTER-GRID's "what exists today" counts were hand-authored and had drifted.
  The tool recomputes every count directly from the filesystem using the same
  paths the assembler validator uses, tallies rules per concern by `layer`
  (mechanical -> L1, semantic -> L2, judgmental -> L3), and self-verifies that the
  per-concern sums reconcile to the layer totals and the total rule count
  (non-zero exit on mismatch). It emits the section-4 block ready to paste, so the
  index can be regenerated instead of hand-edited and cannot silently drift the
  same way again.

- **Populated the `summary` field on the 23 concerns that lacked it.** The
  `concern.yaml` schema carries a `summary` (the one-line scope signal that
  replaced the old per-catalog `Scope:` line), but only `authentication` and
  `authorization` had one authored; the L1 re-cut left the other 23 empty. Each
  now carries a summary derived from that concern's own rules. This is the cheap
  routing signal the concern-selector reads, restored across the full grid.

### Changed

- **Promoted `docs/MASTER-GRID.md` from draft to stable and reconciled its
  counts.** MASTER-GRID was the only artifact repo-wide still marked
  `Status: DRAFT for review` while serving as the authoritative always-start-here
  index; every rule, concern, and decision was already stable. Before flipping the
  header, its counts were reconciled to filesystem ground truth (verified by the
  new `tooling/grid-counts/counts.py`): the L2 total corrected 130 -> 131 and the
  `code-organization` row 4 -> 5 (one semantic rule was uncounted); the threat
  band gained OWASP Top 10 as the sixth spine (was present in `catalogs/threats/`
  but absent from the index); design patterns moved from a "planned"/empty spine
  to a present band of 9 catalogs (was listed as 4); test templates 101 -> 102;
  and mappings (5) were added to the totals. The L2/L3 detail-inventory spokes
  remain `Status: planned` because those documents genuinely do not exist yet.
  No substrate VERSION bump: this promotes a doc index and adds a reporting tool;
  it changes no assembled substrate content.

- **Adopted the Opus 4.8 / Sonnet 5 model generation: refreshed pricing and
  added per-agent effort dials.** Two coordinated edits for one initiative.
  (1) `lib-context/ai-model-pricing.yaml` now carries `claude-opus-4-8`
  (5.00/25.00), `claude-sonnet-5` (3.00/15.00 standard, with the 2.00/10.00
  introductory window through 2026-08-31 noted), and `claude-fable-5` (flagged
  as an unverified estimate pending the pricing page), corrects the 4.6/4.7/5
  generation context windows to 1M, records the Sonnet 5 tokenizer change
  (~30 percent more tokens for the same text), and adds a `security_caveat`
  that security review and threat modeling stay on Opus because Sonnet 5 has
  deliberately low cyber capability and cyber safeguards. On the first-party
  Anthropic API the `sonnet` and `opus` aliases the agents already use resolve
  to Sonnet 5 and Opus 4.8 (Claude Code v2.1.197+ / v2.1.154+), so no agent
  model strings needed changing. (2) All 12 agents in `.claude/agents/` gained
  an `effort` frontmatter dial on a conservative three-tier map: `high` for the
  deep-judgment, high-stakes agents (security-reviewer, threat-modeler,
  staff-engineer, closure-auditor), `medium` (the recommended default) for the
  review and drafting agents (code-reviewer, performance-reviewer,
  test-architect, adr-architect, discovery-agent, production-readiness,
  operational-architect), and `low` for the one pure-routing agent
  (concern-selector, which runs the deterministic dial). `xhigh` is left unused
  as a standing setting by design; `max` is legacy (Opus 4.6 only) and is not
  used.

- **Repointed and bounded the `concern-selector` agent.** The agent read each
  concern's `Scope:` line, a signal the re-cut removed, so on a real feature it
  fell back to reading rule bodies across 226 rules (~3.8 MB) and risked wandering
  into the adjacent multi-megabyte `compliance/` tree, costing tens of thousands
  of tokens. It now reads only `concerns/*/concern.yaml` (the `summary`, with
  `name` and `characteristic` as fallback) and is explicitly barred from rule
  subdirectories and from the `compliance/`, `threats/`, and `design-patterns/`
  trees during selection. The read collapses from ~1000 files plus a large
  neighbor to 25 small YAML files. It also now calls out, by name, any concern
  whose `concern.yaml` lacked a `summary` (where it routed on `name` and
  `characteristic` alone), so a substrate gap surfaces to the operator instead of
  being silently absorbed into a thinner routing decision.
- **The concern schema now requires a non-empty `summary`.** `concern.schema.json`
  lists `summary` in `required` with `minLength: 1`, so `validate.py` reports any
  concern missing one as it validates each `concern.yaml`: a warning in solo mode,
  a blocking error in published mode, the same severity model every schema rule
  follows. This closes the gap that let 23 concerns ship without the routing
  signal the concern-selector depends on.

### Fixed

- **FW-005-A: the clarify close-recommendation now derives from the coverage
  delta.** The clarify skill's step 8 emitted a fixed "proceed to PLAN or re-run
  CLARIFY" next-step that did not consume the coverage summary the same step
  computed one section earlier, so it could route the operator past the post-spec
  re-routing checkpoint that a newly surfaced concern requires. It now recommends
  `/speckit-workflow-post-spec` before plan when a clarification resolved a
  routing-relevant concern (the condition the `after_clarify` hook already names),
  and plan otherwise. Applied to both the preset command and the installed skill;
  logged as the second documented modification from upstream spec-kit in the
  command's provenance comment.
- **FW-005-A (generalized), adr-architect seam: Decision coverage now derives from
  the required-item set.** Feature 005 showed the same synthesis-drops-analysis
  signature at multiple seams beyond clarify; this addresses the adr-architect
  instance, where a composite ADR (e.g., ADR-009's five required items) drafted
  most items concretely and thinned the last (the ISO-42001 clause map) to a
  passing mention. adr-architect now enumerates the required sub-decisions from
  the motivating artifacts first, then requires every item to be either a concrete
  Decision statement or a named Open Question, with no softened middle. The other
  named seams (remediation menu wording, per-item C1/C2 closure signaling) remain
  open for the isolated framework run.
- **FW-005-A (generalized), analyze remediation seam: remediation enforcement now
  derives from severity.** The speckit-analyze skill could describe a finding's fix
  as a note or advisory even when the finding violated a constitution MUST or left
  a required gate missing. It now derives a remediation class from the severity and
  constitution/gate mapping it already assigns: a CRITICAL or MUST-violating finding
  requires an enforced, fail-closed remediation and is never surfaced as a note in
  the Recommendation column, Next Actions, or the remediation offer. The
  closure-signaling seam remains open for a separate delta.

- **FW-005-A (generalized), closure-signaling seam: closure discovery is now
  deterministic and the auditor only judges.** The closure-auditor previously did
  its own mechanical passes in the LLM - enumerating pending items from
  events.jsonl, indexing closure activity, and grepping the codebase and git
  commits for item-ID references - before making any semantic call, reconstructing
  50+ closure events by hand on a real feature. That mechanical half is now a
  deterministic script, `tooling/closure/scan.py`, which emits per pending P1/P2
  item its recorded closure events, its candidate code/commit references, and a
  classification (`claimed`, `discovered`, or `unaddressed`), matching the event
  schema in `.claude/hooks/verify_loop_closure.py`. The `closure-auditor` agent and
  the closure contract in `.claude/docs/agent-coordination.md` now consume that
  output and spend the LLM only where judgment is required: reading each
  candidate's cited code and deciding whether it addresses the concern. This keeps
  the deterministic-where-no-reasoning / LLM-only-for-judgment split, removes the
  hand reconstruction, and preserves independent discovery of unsignalled closures
  (the scan's `discovered` class). `tooling/closure/test_scan.py` covers the three
  classifications, P3 exclusion, legacy string items, deferred-at-root, git-absent
  grace, and the self-reference exclusion. This closes the last of the four
  FW-005-A generalized seams (clarify, adr-architect, analyze remediation, closure
  signaling).

## [1.2.0] - 2026-06-30

**Promotes the data-model-single-source-of-truth rule to stable** under Charter
Section 2.4.1 solo-author attestation (rule authored 2026-06-28, its bindings
2026-06-29, attested 2026-06-30, so the one-calendar-day cooling-off is satisfied;
reviewer `myoung-self-attested`). This release also consolidates the OBS-003
neutral-state fix and the rule's completion, both merged after 1.1.0.

### Added

- **Completed the `data-model-single-source-of-truth` rule to the full rule-folder
  structure.** Authored `examples/good.md` and `examples/anti-pattern.md` (the latter
  the FW-001 operator/persona instance), a `checklist.md` review binding, and a
  `test-template.md` test binding, mirroring `duplication-and-abstraction`. The rule
  satisfies the validator's per-layer artifact check on its own, so the assembler
  validator stays strict with no draft carve-out. Designated CODEORG-L2-005. Promoted
  to stable in this release (see Promoted).

### Changed

- **Reconcile recognizes the uninstantiated-template neutral state (OBS-003).** A
  manifest that asserts no `context` facts is treated as an uninstantiated template
  (this repo's own state), so `reconcile` reports not-applicable rather than
  defaulting the facts to lowest and computing a floor. Asserting any single fact
  engages the dial (the rest still default to lowest), so a real project cannot slip
  past the floor by omitting context. The framework's own `project-manifest.yaml`
  context is emptied to this neutral state, with the dial facts kept as documented
  comments for instantiation. This resolves the live half of OBS-003: the framework
  reported a floor-versus-ceiling conflict against itself only because it asserted
  project facts it does not have; the empty-ceiling premise from the original OBS-003
  note was a separate FW-006 symptom, already addressed.

### Promoted

- `code-organization.data-model-single-source-of-truth`: draft (2026-06-28) to stable
  (2026-06-30) under Charter Section 2.4.1 solo-author attestation. Reviewer
  `myoung-self-attested`; cooling-off satisfied (the rule and its bindings were
  authored on prior calendar days). The rule and its `checklist.md` and
  `test-template.md` bindings move to stable together at designator CODEORG-L2-005.
  Intent, examples, and the layer artifacts were reviewed against
  `spec/rule-lifecycle.md` and the Article II Section 2.3 quality bar; provenance is
  complete; no conflict with existing substrate content.

## [1.1.0] - 2026-06-29

**Release cut consolidating post-1.0.1 work, with one draft to stable
promotion.** The promotion (the technology-selection decision framework) is made
under Charter Section 2.4.1 solo-author attestation: it was authored 2026-06-28
and attested 2026-06-29, satisfying the one-calendar-day cooling-off (reviewer
`myoung-self-attested`). Everything else in this release is reference content
(the OWASP Top 10 2025 and design-pattern catalogs, the OSCAL compliance
artifacts), tooling (the reconcile gate), draft additions, or corrections and
changes, none of which requires attestation per Section 2.4.1. This release
covers the L1 enforcement re-cut from the tool-bindings model to the
capability-gate toolchain model, the realization of the design-pattern catalog
kind, the documentation currency pass, and the security, compliance, and
decision-framework additions merged after 1.0.1.

### Added

- **Design-pattern catalog kind, realized.**
  `schemas/design-pattern-catalog.schema.json` (draft, schema-version 0.1.0)
  and nine authored reference catalogs under `catalogs/design-patterns/`:
  `solid.yaml` (5 principles), `design-principles.yaml` (8 principles),
  `gang-of-four.yaml` (23 patterns), `architecture.yaml` (17 architecture and
  system-design patterns), `domain-driven-design.yaml` (16 patterns),
  `distributed-systems-fallacies.yaml` (8 fallacies),
  `cloud-scaling-failure-modes.yaml` (7 failure modes),
  `complexity-classes.yaml` (8 classes), and `code-smells.yaml` (25 smells).
  All descriptions are substrate-original
  paraphrase of public design concepts; no source text, code, or diagrams are
  reproduced. Modeled on the threat catalogs as review-cadence reference
  content, not on the draft/stable rule lifecycle. Validation folded into
  `tooling/assemble/validate.py`; the schema rides to stable with a future
  design-pattern content event per the schema-rides-content precedent.
- **OWASP Top 10 2025 threat catalog.** `catalogs/threats/owasp-top10.yaml`: the
  current eighth-edition OWASP Top 10 (2025) as a substrate threat catalog,
  replacing the inline 2021 table that lived in `security-reviewer.md`. Ten
  entries A01 to A10 as substrate-original summaries with attribution to the
  CC BY source; review-cadence reference content, sibling to the LLM and ASI
  catalogs.
- **OSCAL compliance artifacts.** An EU AI Act high-risk profile, a
  hand-authored GDPR catalog (16 articles), a hand-authored HIPAA Security Rule
  catalog (22 standards), and a PCI-DSS v4.0.1 reference-only entry, under the
  trestle workspace and `catalogs/compliance/`. Obligation statements are
  substrate-original; copyright-restricted sources are reference-only.
- **FW-003 reconcile gate.** `tooling/dial/reconcile.py` and its tests, and
  `.githooks/pre-commit.d/80-reconcile` (report-only, `RECONCILE_STRICT`), which
  fails loud when the dial floor exceeds the manifest ceiling and names three
  resolutions without auto-applying any. `docs/GATES.md` regenerated.
- **Forcing-function gates for the FW-001 data-model fix and the rename seam.**
  `tooling/data-model-normalization/` (IMP-12): the deterministic half of the
  FW-001 fix, confirming `data-model.md` carries an explicit normalization
  declaration so a data model cannot ship without stating its
  single-source-of-truth decision; staff-engineer judges correctness, citing
  `code-organization.data-model-single-source-of-truth`.
  `tooling/rename-integrity/` (IMP-13): a bulk-rename token check that counts old
  and new identifier occurrences on disk after a substitution, so a rename is
  verified by raw counts (old expected at zero, new propagation footprint shown)
  rather than a prose consistency sweep.
- `decision-frameworks/technology-selection.madr.md` (framework-version 0.1.0,
  entered draft 2026-06-28): the decision framework whose output is the bootstrap
  stack ADR, realizing the gap that surfaced when staff-engineer's inline canon
  moved to the substrate. Promoted to stable in this release (see Promoted).
- `catalogs/concerns/code-organization/data-model-single-source-of-truth/rule.yaml`
  (draft, entered draft 2026-06-28): a semantic concern rule requiring the data
  model to declare which fields are shared across a referencing dimension and
  normalized to one home. Remains at draft; its examples, checklist, and
  test-template are not yet authored.

### Promoted

- `decision-frameworks.technology-selection`: draft (2026-06-28) to stable
  (2026-06-29) under Charter Section 2.4.1 solo-author attestation. Reviewer
  `myoung-self-attested`; cooling-off satisfied (more than one calendar day
  between authoring and attestation). Intent, decision drivers, considered
  options, and outcome were reviewed against `spec/decision-framework-format.md`;
  provenance is complete; no conflict with existing substrate content.

### Removed

- **The L1 tool-bindings model.** Removed `tool-bindings/` (the per-rule
  static-analysis bindings that referenced upstream Semgrep rules by
  registry-id) and the four binding schemas (`static-analysis-binding`,
  `review-checklist`, `test-template`, `decision-framework`). The registry-id
  audit, the `tooling/registry-audit/` skeleton, and
  `docs/registry-id-audit-2026-05.md` were retired with it. The associated
  drift-remediation design debt in `FUTURE.md` is superseded (the drift it
  tracked no longer exists).
- **The standalone shell validators.** `scripts/validate-*.sh` retired;
  validation of concerns, rules, bindings, registry, selection, profiles,
  threat catalogs, mappings, and design-pattern catalogs is consolidated into
  the single `tooling/assemble/validate.py`, run by `make gc-validate`.

### Changed

- **L1 enforcement re-cut to the capability-gate toolchain model.** Each
  mechanical rule names a capability gate (for example `sast`, `secrets`,
  `lint`) that `toolchain/registry.yaml` and `toolchain/selection.yaml` resolve
  to a pinned OSS tool through the rule's co-located `binding.yaml`;
  `tooling/floor-generator/` emits the pre-commit config, CI workflow, and
  review checklist from the resolved toolchain. The SAST gate resolves to
  OpenGrep with a consumer-supplied maintained rule set. Schemas:
  `binding.schema.json`, `registry.schema.json`, `selection.schema.json`.
- **L1 posture to realized (Option A).** With no per-rule registry references
  left to drift, L1 is documented as authoritative alongside L2 and L3; the
  only consumer step is operational (wire the tools via the generated floor,
  supply the SAST rule set). Updated `SUBSTRATE-FIT.md`,
  `spec/consumer-scaffold.md`, `project-manifest.yaml`, `FUTURE.md`, and
  `docs/MASTER-GRID.md`.
- **MASTER-GRID per-concern recount.** The L1/L2/L3 table was recounted to
  verified primary-home counts (summing to 62 / 130 / 33 = 225, matching
  `gc-validate`), correcting stale totals (was 85 static-analysis bindings /
  140 checklists / 33) and the table's summing note.
- **Documentation currency.** Repointed the retired `validate-profiles`
  reference (`tooling/profile-resolver/README.md`) to `make gc-validate`;
  corrected the design-pattern catalog format in `spec/catalog-format.md`
  (flat reference catalogs, not OSCAL `.oscal.yaml`); fixed dead
  `../toolchain/README.md` links to `../tooling/toolchain/README.md`
  (`spec/catalog-format.md`, `spec/substrate-scope.md`); updated the
  `mappings/README.md` inventory to the five authored threat-to-concern
  mappings with the three compliance mappings marked planned; and removed dead
  doc pointers (`L1-source-of-truth-map.md` in MASTER-GRID,
  `docs/ENHANCEMENT-ROADMAP.md` in FUTURE).
- **security-reviewer reconciled to the new substrate artifacts.** The inline
  OWASP Top 10 table was dereferenced to cite `catalogs/threats/owasp-top10.yaml`
  (2025), and the compliance section now points GDPR, HIPAA, EU AI Act, PCI, and
  SOC2 at their real OSCAL profiles, catalogs, and references rather than
  flagging them as absent.
- **technology-selection wiring.** `concern-selector` references the framework as
  the bootstrap stack-ADR source; `staff-engineer` references the resulting stack
  ADR for per-feature conformance; `code-reviewer` cites the added hygiene smells
  in `code-smells.yaml`.

## [1.0.1] - 2026-06-05

**Corrections release plus a Charter amendment. No new stable content
is promoted in this release.** Every content change below is a
correction as defined by the Charter Section 2.4.1 corrections clause
introduced in this release (it preserves the substance of existing
content and adds no new stable content), so no solo-author attestation
or cooling-off interval applies. The one net-new artifact pair (the
threat-catalog schema and its validator) enters at draft lifecycle
status, which has never required attestation. The Charter amendment is
recorded under Governance below and in `CHARTER.md` Article IX
Section 9.5.

### Added

- `schemas/threat-catalog.schema.json` (draft, schema-version 0.1.0):
  the first schema for threat catalogs, closing the validation gap that
  `validate-catalogs.sh` explicitly defers. It validates the shared
  structure of all five threat catalogs (a metadata block plus at least
  one item collection keyed `categories`, `threats`, or `techniques`,
  each item carrying `id` and `name`) without constraining
  per-taxonomy item fields. Rides to stable with a future threat-catalog
  content event per the schema-rides-content precedent.
- `scripts/validate-threats.sh`: validator for `catalogs/threats/*.yaml`
  against the new schema, modeled on `validate-catalogs.sh`. Wired into
  `scripts/validate-all.sh` as validator 6. New full-suite baseline:
  25 catalogs, 5 profiles, 85 static-analysis bindings, 33 decision
  frameworks, 241 L2 bindings, 5 threat catalogs (25/5/85/33/241/5).

### Changed

- **Profile UUID collision corrected.** In
  `profiles/production-grade-baseline.oscal.yaml`, two back-matter
  resources shared one UUID (`e1f2a3b4-...`). The Configuration-Management
  resource was reassigned a fresh UUID
  (`799f1ad4-362a-4e96-8428-d0a96a409097`); Infrastructure-Misconfiguration
  retains the original. No inbound references existed, so no other file
  changed.
- **Broken L3 reference corrected.** In
  `catalogs/concerns/input-validation.oscal.yaml`, the input-validation
  decision-framework href was repaired from
  `../input-validation-strategy.madr.md` to
  `../../decision-frameworks/input-validation-strategy.madr.md`.
- **Malformed threat catalogs repaired.** `catalogs/threats/stride.yaml`
  and `catalogs/threats/owasp-agentic-asi-2026.yaml` were invalid YAML
  (1-space indentation units left list-item continuation keys shallower
  than their item key). Both were reindented to valid 2-space YAML with
  all values preserved verbatim (verified by parse and item-count
  round-trip: STRIDE-S/T/R/I/D/E and ASI01 through ASI10). All five
  threat catalogs now validate.
- **Stale example references corrected.** In `spec/catalog-format.md`,
  the `AUTH-L1-001` example link block was updated to resolvable paths:
  the binding directory rename (`tool-bindings/semgrep/` to
  `tool-bindings/static-analysis/`) with the accurate filename
  (`auth-l1-001-password-hashing.yaml`), and the missing `catalogs/`
  segment added to the threats and compliance example hrefs.
- **SPDX headers added.** Six substrate files that were missing the
  `SPDX-License-Identifier: Apache-2.0` header received it:
  `catalogs/compliance/README.md`,
  `catalogs/compliance/UPDATE_RUNBOOK.md`,
  `catalogs/compliance/iso-42001/reference.yaml`,
  `catalogs/compliance/soc2-tsc/reference.yaml`,
  `lib-context/README.md`, and `policies/README.md`.
- **Portability cleanup (consumer-tool references removed).** Live
  substrate content was scrubbed of references to a specific consumer
  toolchain, per the `PORTABILITY.md` one-way-reference rule, in
  preparation for extraction and publication. Genericized:
  `reference/agents/` (three reference agents),
  `spec/consumer-scaffold.md`, `spec/principles.md`,
  `spec/architecture-rationale.md`, `spec/data-classification.md`, and
  `FUTURE.md`. The reference agents remain portable contract
  demonstrations; only the consumer-specific placement assumption was
  removed. Consumer-toolchain integration guidance now lives in the
  parent layer (the spec-driven-governance preset README), not in the
  substrate. Historical CHANGELOG entries that record past placement
  decisions were intentionally left intact as an audit record.
- **CHANGELOG heading hygiene.** Added the missing
  `## [0.6.0] - 2026-05-30` heading over the M3 session entries, and
  removed the stray `[Unreleased]` labels from nine historical session
  blocks (relabeled to the release each shipped in). Exactly one
  `[Unreleased]` block now exists. Heading text only; no released
  content was altered.

### Governance

- **Charter amended to 1.0.0 (discipline-relaxing, breaking per
  Article IX Section 9.2).** Section 2.4.1 (solo-author attestation) was
  reopened. The prior version-1.0.0 close is superseded; solo-author
  attestation is extended through the substrate's private-development
  phase, with the eligibility condition and the sunset trigger re-based
  from "version 1.0.0" to "repository made public." A corrections clause
  was added defining that corrections to existing content are not new
  promotions and require neither attestation nor cooling-off. Article IX
  Section 9.5 was updated: the Charter version is bumped 0.2.0 to 1.0.0,
  the previously-omitted 1.0.0 close is recorded alongside this reopen,
  and the stale "pre-stable status (0.x)" statement is corrected to
  reflect stable (1.0.0) status. See `CHARTER.md` Section 2.4.1 and
  Section 9.5.

## [1.0.0] - 2026-06-07

### Substrate 1.0.0 release (M8 and M9 combined)

The substrate reaches 1.0.0. M8 (tooling skeletons) and M9 (the 1.0 release)
are combined into this single release at the substrate-author's direction;
the intermediate 0.11.0 version is folded into 1.0.0 rather than tagged
separately. With this release the substrate is content-complete (25 stable
concerns), ecosystem-complete (5 stable profiles), tooling-scaffolded, and
ships a published, honest fit statement. The roadmap (M0 through M9) is
complete.

This is a release consolidation, not a content authoring or attestation
event. It promotes no new catalog or profile content to stable and attests
no new governance content; per the no-cooling-off-for-non-attesting-close
convention, it lands on the same calendar day as the M8 authoring. The
five-validator suite is unchanged at 25 / 5 / 85 / 33 / 241.

**M8 tooling skeletons (consolidated into 1.0.0).** The tooling/ directory,
previously a placeholder, now ships six tool skeletons (registry-audit,
profile-resolver, mapping-coverage-reporter, lint-config-generator,
catalog-validator, tailoring-agent) and an updated index. Per Charter Article
VII and the description-not-implementation discipline, these are documented
contracts with at most a thin read-only reference script, not maintained
runtime. See the combined M8 authoring entry below for the per-tool detail.

**Published fit statement (M9).** Added SUBSTRATE-FIT.md at the substrate
root: the honest, consumer-facing fit-by-shape assessment (best fit
application backends; good fit AI/ML and agentic systems, IaC and data
pipelines, regulated industries via the four industry-tilt profiles) with
the L1 enforcement caveat as a prominent named section. This resolves the
FUTURE.md usability-statement-publication and L1-coverage-gap-disclosure
entries (the honesty-about-L1-maturity cluster) and Open Question 6
(external publication timing).

**L1 maturity disclosure (M9).** The L1 enforcement caveat (about 45 of 306
L1 references verifiably alive upstream; 23 of 47 bindings with zero live
references; L2 and L3 are the dependable surface; treat L1 as advisory, not a
blocking gate) is now stated in the consumer-facing surface: SUBSTRATE-FIT.md
and a companion note in spec/consumer-scaffold.md Section 4. The M8
registry-audit tooling operationalizes the FUTURE.md four-tier remediation
that the caveat points to.

**Charter amendment, Section 2.4.1 (M9, Article IX).** Reaching 1.0.0 fired
the Charter Section 2.4.1 sunset (solo-author attestation). Per the sunset
clause, the Charter is amended under Article IX: Section 2.4.1 is closed as a
path for new stable promotions effective 1.0.0; all content promoted under it
through this release retains its stable status and is not retroactively
invalidated; future stable promotions require Section 2.4 (second-human
review), and a renewed solo-author path would require a fresh Article IX
amendment. The substrate honors its own sunset rather than relaxing the
discipline. The amendment lands at the major-version increment per Article IX
Section 9.2.

**What 1.0.0 asserts.** The schema set, the OSCAL catalog format, the profile
model (including profile-of-a-profile industry tilts), and the lifecycle and
attestation discipline are stable; breaking changes require a major-version
bump (Charter Article VIII). All 25 concerns and 5 profiles are stable and
immutable except through the deprecation and retirement path. 1.0.0 does not
assert that the L1 mechanical layer is fully enforceable upstream; it asserts
that the authored governance content is complete and stable and that the L1
maturity status is disclosed.

**Housekeeping at the release.** Refreshed four M2-era profile back-matter
resource descriptions (error-handling, testing-strategy, logging,
supply-chain) from stale draft-lifecycle language to stable (resolving the
decision-41 and Open Question 12 cleanup). Updated the README status from
pre-release to 1.0.0 with a SUBSTRATE-FIT.md pointer. Removed the now-vestigial
tooling/.gitkeep (the directory has content). No catalog, profile selection,
binding, decision-framework, or schema content changed.

### M8 (combined): substrate tooling skeletons authored

M8 (substrate tooling) lands the tooling-skeleton layer the roadmap has
carried since the project's scope decision (tooling skeletons as folder
structure with READMEs). The substrate's tooling/ directory, previously a
placeholder, now realizes the planned utilities it had declared, plus the
registry-audit tool that the M3 L1-enforcement honesty caveat motivates. All
skeletons were authored in one combined session; profiles are not involved
and no catalog, binding, or decision-framework content changed.

Per Charter Article VII and discipline rule 11, these are skeletons (a
documented contract, a procedure, and at most a thin read-only reference
script), not maintained runtime products. The reference scripts are bash
3.2 compatible, take no network access, and perform read-only analysis of
the substrate's own published content. Tooling is not OSCAL content and is
not on the catalog draft-to-stable lifecycle; the five-validator suite is
unchanged (25 / 5 / 85 / 33 / 241).

**Added (under governance-commons/tooling/).**
- registry-audit/: audits L1 binding registry-ids against their upstream
  source of truth and classifies each reference alive, drifted, or dead;
  backs the FUTURE.md four-tier registry-ID remediation and reproduces the
  report shape of docs/registry-id-audit-2026-05.md. Ships a read-only
  reference script (extract-registry-ids.sh) for the extraction step.
- profile-resolver/: resolves profile-of-a-profile inheritance to a flat
  effective profile (selected controls with effective severity and
  provenance); documents the resolution semantics for the M7 industry
  tilts. Ships a read-only reference script (list-profile-overrides.sh).
- mapping-coverage-reporter/: reports cross-taxonomy mapping coverage
  (relations, distinct source items, target concerns, coverage-gap
  entries) across the five mappings. Ships a read-only reference script
  (report-mapping-coverage.sh).
- lint-config-generator/: documents the contract for assembling a
  static-analysis config from selected, live L1 bindings; sequenced after
  registry-audit so generated configs omit dead identifiers. README-only.
- catalog-validator/: documents the validation contract and records the
  cross-file href-resolution gap as the extension point; the maintained
  validators remain scripts/validate-*.sh. README-only.
- tailoring-agent/: forward-looking, consumer-side AI-assisted tailoring
  workflow; README-only, explicitly future, bounded by Article III (AI
  proposes, humans approve) and Article VII.
- Updated tooling/README.md index to the realized utility set with status.

No VERSION bump (stays 0.10.0); stable consolidation and the version bump
are the M8 close.

## [0.10.0] - 2026-06-07

### M7 close consolidation (Path A)

The M7 milestone closes. The four M7 industry-tilt profiles authored at
draft in the combined Sessions 1 to 4 (financial-services, regulated-ai,
healthcare, fedramp) are promoted to stable in one discrete consolidation
event per the Path A precedent settled at the M1 through M6 closes (the
seventh consecutive Path A close). Substrate version bumped 0.9.0 to 0.10.0.
The session entry that follows this consolidation block records the
authoring of the four profiles; this block records the close. The substrate
now ships five stable profiles: the production-grade-baseline plus four
industry tilts.

**Promotion to stable.** All four industry-tilt profiles advanced from
profile version 0.1.0 to 1.0.0 and from lifecycle-status draft to stable,
with an entered-stable-at of 2026-06-07 and a profile-attestation prop added
to each. The profile-attestation prop is the profile-level analogue of the
catalog-attestation prop, confirmed as the design decision at M7 Session 0;
it carries value myoung-self-attested with a remarks block recording the
Charter Section 2.4.1 attestation at the M7 close. The
production-grade-baseline profile was not modified (it was already stable).
No catalog, decision-framework, or binding content changed at the M7 close;
the close operates only on the four industry profiles and the substrate
version.

**Batch attestation.** Attested under Charter Section 2.4.1 (solo-author
attestation) on 2026-06-07. Cooling-off honored: the four profiles were
authored at draft on 2026-06-06, a calendar day prior to this attestation.

**Substrate ecosystem milestone complete.** M7 delivered the first
expansion beyond the single baseline profile: four industry-tilt profiles
covering financial-services, regulated-ai, healthcare, and fedramp. The
remaining road to a 1.0.0 release is M8 (substrate tooling skeletons:
registry-audit tooling) and M9 (substrate 1.0 release with a published,
honest fit statement) which lands version 1.0.0.

### M7 Sessions 1 to 4 (combined): four industry-tilt profiles authored at draft

M7 (substrate ecosystem) opens its authoring with all four industry-tilt
profiles authored at draft in one combined session, per the M7 Session 0
plan. Each profile is a profile-of-a-profile that imports
production-grade-baseline via a single include-all (inheriting all baseline
rule selections) and then elevates, through a modify block of severity
alters, the rules that its regulatory regime makes critical. Inheritance is
profile-of-a-profile (the profile schema import href accepts a parent
profile); each altered control-id was verified to resolve against the
baseline selections and each parent-profile import href was verified
manually (validate-profiles does not resolve cross-file hrefs).

**Added.** Four industry-tilt profiles under profiles/, each at profile
version 0.1.0, profile-kind industry-tilt, lifecycle-status draft,
commons-version 0.9.0:
- financial-services.oscal.yaml (16 severity elevations; PCI-DSS, SOX,
  GLBA, FFIEC): data classification and handling, encryption key
  management, audit logging and retention, third-party and supply-chain
  risk, detection and monitoring, records-destruction guards, change
  control, and availability.
- regulated-ai.oscal.yaml (17 elevations; EU AI Act, NIST AI RMF, ISO/IEC
  42001): responsible-AI controls and documentation, agent permission
  boundaries, privacy and data governance for training and inference data,
  data classification, and post-market monitoring and incident detection.
- healthcare.oscal.yaml (16 elevations; HIPAA Security Rule, Privacy Rule,
  HITECH): minimum-necessary PHI handling and privacy, PHI classification
  and transmission security, person-or-entity authentication and access
  control, ePHI encryption key management, guarded PHI and media disposal,
  and audit-control logging and retention.
- fedramp.oscal.yaml (17 elevations; FedRAMP, NIST SP 800-53 Rev. 5, FIPS
  199): supply-chain risk, configuration management, continuous monitoring,
  cryptographic key protection, audit logging and retention, and dependency
  provenance and flaw remediation.

Each profile carries a back-matter resource pointing to the parent baseline
profile. The production-grade-baseline profile is the parent and was not
modified. The profile-attestation prop (analogous to catalog-attestation)
and promotion to lifecycle-status stable are deferred to the M7 close
consolidation per the Path A precedent; the earliest M7-close attestation
date is a subsequent calendar day per Charter Section 2.4.1.

## [0.9.0] - 2026-06-06

### M6 close consolidation (Path A)

The M6 milestone closes. The four M6 concerns authored at draft across
Sessions 1 through 4 (configuration-management, feature-flags,
backup-recovery, documentation) are promoted to stable in one discrete
consolidation event per the Path A precedent settled at the M1, M2, M3, M4,
and M5 closes (the sixth consecutive Path A close). Substrate version bumped
0.8.0 to 0.9.0. The session entries that follow this consolidation block (M6
Sessions 1 through 4) record the authoring of each concern; this block
records the close. With these four concerns stable, the 25-concern substrate
inventory is complete.

**Promotion to stable.** All four M6 concern catalogs advanced from catalog
version 0.1.0 to 1.0.0 and from catalog-status in-development to
feature-complete, with a catalog-attestation prop added to each and every
control and the catalog metadata flipped from lifecycle-status draft to
stable (an entered-stable-at of 2026-06-06 added alongside each
entered-draft-at). The four paired L3 decision frameworks (MADRs:
configuration-management-strategy, feature-flags-strategy,
backup-recovery-strategy, documentation-strategy) advanced to
lifecycle-status stable, framework-version 1.0.0, with reviewer, reviewed,
entered-status-at, and attestation-mechanism added. All 20 paired L2
bindings (12 review checklists and 8 test templates across the four
concerns) advanced to lifecycle-status stable, binding-version 1.0.0, with
the same four attestation fields added, per the parent-inheritance precedent
(Section 10 settled decision 23). commons-version on the promoted MADRs and
bindings was left at the 0.8.0 authoring version per the M1 through M5
precedent; only framework-version and binding-version bump to 1.0.0. L1
static-analysis bindings carry no lifecycle field and were not modified.

**Batch attestation.** Attested under Charter Section 2.4.1 (solo-author
attestation) on 2026-06-06. Cooling-off honored: every M6 concern was
authored on a calendar day prior to this attestation
(configuration-management and feature-flags on 2026-06-04; backup-recovery
and documentation on 2026-06-05).

**Substrate inventory complete.** The 25-concern inventory targeted by M6 is
complete and stable. The remaining road to a 1.0.0 release is M7 (substrate
ecosystem: industry-tilt profiles), M8 (substrate tooling skeletons), and M9
(substrate 1.0 release with a published, honest fit statement).

### M6 Session 1: configuration-management concern authored at draft

The configuration-management concern is authored at draft, the first of
four low-depth concerns that complete the substrate concern inventory in
M6 (configuration-management, feature-flags, backup-recovery,
documentation). Depth classification (low, 3 to 6 rules) was pre-cleared
against spec/substrate-scope.md, where the concern is already listed; no
depth-classification amendment was required.

**Added.** The configuration-management concern catalog
(catalogs/concerns/configuration-management.oscal.yaml) at catalog version
0.1.0, catalog-status in-development, lifecycle-status draft, with 5 rules
within the low-depth band: 2 L1 mechanical (CONFIG-L1-001 no hardcoded
environment-varying configuration in source; CONFIG-L1-002 no swallowing
default on a required configuration read), 2 L2 semantic (CONFIG-L2-001
startup validation and fail-fast; CONFIG-L2-002 explicit layering,
precedence, environment parity, and the secret-reference boundary), and 1
L3 judgmental (CONFIG-L3-001 configuration-management strategy ADR). Two
L1 static-analysis bindings (substrate-authored semgrep-pattern-v1), three
review checklists (CONFIG-L2-001, CONFIG-L2-002, CONFIG-L3-001), two test
templates (CONFIG-L2-001, CONFIG-L2-002), one paired L3 MADR
(decision-frameworks/configuration-management-strategy.madr.md), and ten
examples (paired good and anti-pattern for each rule) were added, all at
draft. Concern boundaries were documented in the catalog header against
secrets-management (config carries non-secret values; secrets are
referenced by indirection), the forthcoming feature-flags concern
(static-versus-dynamic split), and infrastructure-misconfiguration
(application runtime config versus IaC resource config).

**Changed.** The production-grade-baseline profile imports the
configuration-management catalog with all 5 rules selected, adds 5 alter
blocks at catalog-default severities, and adds a back-matter resource;
rule-selection-count advanced from 164 to 169.

Stable promotion of the configuration-management concern is deferred to
the M6 close consolidation per the Path A precedent; the earliest M6-close
attestation date is a subsequent calendar day per Charter Section 2.4.1.

### M6 Session 2: feature-flags concern authored at draft

The feature-flags concern is authored at draft, the second of four
low-depth concerns that complete the substrate concern inventory in M6
(configuration-management, feature-flags, backup-recovery, documentation).
Depth classification (low, 3 to 6 rules) was pre-cleared against
spec/substrate-scope.md, where the concern is already listed; no
depth-classification amendment was required.

**Added.** The feature-flags concern catalog
(catalogs/concerns/feature-flags.oscal.yaml) at catalog version 0.1.0,
catalog-status in-development, lifecycle-status draft, with 5 rules within
the low-depth band: 2 L1 mechanical (FLAG-L1-001 explicit fail-static
default at every flag evaluation; FLAG-L1-002 no live flag pinned to a
constant or short-circuited in source), 2 L2 semantic (FLAG-L2-001 staged
rollout through provider targeting with a clean, deterministic evaluation
context; FLAG-L2-002 flag lifecycle discipline with owner, type, and
expiry per flag and a kill switch that works without a deploy), and 1 L3
judgmental (FLAG-L3-001 feature-flags strategy ADR). Two L1
static-analysis bindings (substrate-authored semgrep-pattern-v1), three
review checklists (FLAG-L2-001, FLAG-L2-002, FLAG-L3-001), two test
templates (FLAG-L2-001, FLAG-L2-002), one paired L3 MADR
(decision-frameworks/feature-flags-strategy.madr.md), and ten examples
(paired good and anti-pattern for each rule) were added, all at draft.
Concern boundaries were documented in the catalog header against
configuration-management (the static-versus-dynamic split),
secrets-management (no secret values in evaluation context), and
experimentation and authorization.

**Changed.** The feature-flags concern finalizes the static-versus-dynamic
boundary with configuration-management in both catalogs: the
configuration-management catalog header note and the CONFIG-L2-002
out-of-scope statement were updated from forthcoming-and-when-authored
language to the finalized cross-reference naming FLAG-L3-001 (surgical
edits limited to the two boundary statements). The production-grade-baseline
profile imports the feature-flags catalog with all 5 rules selected, adds 5
alter blocks at catalog-default severities (high, medium, high, high, high),
and adds a back-matter resource; rule-selection-count advanced from 169 to
174.

Stable promotion of the feature-flags concern is deferred to the M6 close
consolidation per the Path A precedent; the earliest M6-close attestation
date is a subsequent calendar day per Charter Section 2.4.1.

### M6 Session 3: backup-recovery concern authored at draft

The backup-recovery concern is authored at draft, the third of four
low-depth concerns that complete the substrate concern inventory in M6
(configuration-management, feature-flags, backup-recovery, documentation).
Depth classification (low, 3 to 6 rules) was pre-cleared against
spec/substrate-scope.md, where the concern is already listed; no
depth-classification amendment was required.

**Added.** The backup-recovery concern catalog
(catalogs/concerns/backup-recovery.oscal.yaml) at catalog version 0.1.0,
catalog-status in-development, lifecycle-status draft, with 5 rules within
the low-depth band: 2 L1 mechanical (BACKUP-L1-001 every declared backup or
snapshot resource sets an explicit non-zero retention; BACKUP-L1-002 an
irreversible bulk-data-destruction operation is not executed unguarded in
application or migration code), 2 L2 semantic (BACKUP-L2-001 backups are
proven recoverable by a scheduled restore test; BACKUP-L2-002 backup
coverage matches the protection inventory and recovery objectives are
defined and met), and 1 L3 judgmental (BACKUP-L3-001 backup-and-recovery
strategy ADR). Two L1 static-analysis bindings (substrate-authored
semgrep-pattern-v1), three review checklists (BACKUP-L2-001, BACKUP-L2-002,
BACKUP-L3-001), two test templates (BACKUP-L2-001, BACKUP-L2-002), one
paired L3 MADR (decision-frameworks/backup-recovery-strategy.madr.md), and
ten examples (paired good and anti-pattern for each rule) were added, all at
draft. Per the cost-model-selection and dependency-management precedent for
operational low-depth concerns, the L1 rules carry no CWE prop. Concern
boundaries were documented in the catalog header against data-classification
(owns the protection inventory and tiers), reliability (data-restore path
versus service-failover path), observability and monitoring-alerting
(delivers backup and restore-test alerting), and
infrastructure-misconfiguration (secures the backup storage; backup-recovery
makes it recoverable), with the encryption keys and restore credentials
deferred to secrets-management.

**Changed.** The production-grade-baseline profile imports the
backup-recovery catalog with all 5 rules selected, adds 5 alter blocks at
catalog-default severities (high, medium, high, high, high), and adds a
back-matter resource; rule-selection-count advanced from 174 to 179.

Stable promotion of the backup-recovery concern is deferred to the M6 close
consolidation per the Path A precedent; the earliest M6-close attestation
date is a subsequent calendar day per Charter Section 2.4.1.

### M6 Session 4: documentation concern authored at draft

The documentation concern is authored at draft, the fourth and last of the
low-depth concerns that complete the substrate concern inventory in M6
(configuration-management, feature-flags, backup-recovery, documentation).
This session completes the 25-concern substrate inventory. Depth
classification (low, 3 to 6 rules) was pre-cleared against
spec/substrate-scope.md, where the concern is already listed; no
depth-classification amendment was required.

**Added.** The documentation concern catalog
(catalogs/concerns/documentation.oscal.yaml) at catalog version 0.1.0,
catalog-status in-development, lifecycle-status draft, with 5 rules within
the low-depth band: 2 L1 mechanical (DOC-L1-001 every public or exported API
surface carries a doc comment; DOC-L1-002 shipped documentation and doc
comments contain no unresolved placeholder or TODO markers), 2 L2 semantic
(DOC-L2-001 documentation stays accurate and in sync with the code it
describes; DOC-L2-002 significant decisions and operational knowledge are
recorded and discoverable), and 1 L3 judgmental (DOC-L3-001 documentation
strategy ADR). Two L1 static-analysis bindings (substrate-authored
semgrep-pattern-v1), three review checklists (DOC-L2-001, DOC-L2-002,
DOC-L3-001), two test templates (DOC-L2-001, DOC-L2-002), one paired L3 MADR
(decision-frameworks/documentation-strategy.madr.md), and ten examples
(paired good and anti-pattern for each rule) were added, all at draft. Per
the operational low-depth precedent, the L1 rules carry no CWE prop.
Severities are calibrated to a quality concern: accuracy (DOC-L2-001) is the
single high-severity rule, because documentation that is wrong is more
dangerous than documentation that is absent, with the presence, recording,
and strategy rules at medium and the placeholder rule at low. Concern
boundaries were documented in the catalog header against code-organization
(structure versus explanation), observability and monitoring-alerting
(runbooks versus operational telemetry), and testing (executable examples),
with a scope clarification that the substrate's own internal documents are
out of scope.

**Changed.** The production-grade-baseline profile imports the documentation
catalog with all 5 rules selected, adds 5 alter blocks at catalog-default
severities (medium, low, high, medium, medium), and adds a back-matter
resource; rule-selection-count advanced from 179 to 184.

Stable promotion of the documentation concern is deferred to the M6 close
consolidation per the Path A precedent; the earliest M6-close attestation
date is a subsequent calendar day per Charter Section 2.4.1. With this
session the 25-concern substrate inventory is complete; the M6 close (Path A,
0.8.0 to 0.9.0) promotes the four M6 concerns to stable in one consolidation.

## [0.8.0] - 2026-06-04

### M5 close consolidation (Path A)

The M5 milestone closes. The four M5 concerns authored at draft across
Sessions 1, 2, 4, and 5 (responsible-ai, agentic-systems, privacy,
monitoring-alerting) and the owasp-ast-to-concerns mapping authored at
Session 3 are promoted to stable in one discrete consolidation event
per the Path A precedent settled at the M1, M2, M3, and M4 closes (the
fifth consecutive Path A close). Substrate version bumped 0.7.0 to
0.8.0. The session entries that follow this consolidation block (M5
Sessions 1 through 5) record the authoring of each concern, the AST
threat catalog, and the AST mapping; this block records the close. All
21 concerns are now stable.

**Promotion to stable.** All four M5 concern catalogs advanced from
catalog version 0.1.0 to 1.0.0 and from catalog-status in-development
to feature-complete, with a catalog-attestation prop added to each and
every control and the catalog metadata flipped from lifecycle-status
draft to stable (an entered-stable-at of 2026-06-04 added alongside
each entered-draft-at). The 11 paired L3 decision frameworks (MADRs:
four responsible-ai, four agentic-systems, two privacy, one
monitoring-alerting) advanced to lifecycle-status stable,
framework-version 1.0.0, with reviewer, reviewed, entered-status-at,
and attestation-mechanism added. All 49 paired L2 bindings (33 review
checklists and 16 test templates across the four concerns) advanced to
lifecycle-status stable, binding-version 1.0.0, with the same four
attestation fields added, per the parent-inheritance precedent
(Section 10 settled decision 23). The owasp-ast-to-concerns mapping
advanced from version 0.1.0 to 1.0.0 and lifecycle-status draft to
stable, with entered-stable-at, reviewer, reviewed, and
attestation-mechanism added and ai-assistance set to
drafted-and-reviewed (the ASI-mapping promotion precedent).
commons-version on the promoted MADRs and bindings was left at the
0.7.0 authoring version per the M1-M4 precedent; only framework-version
and binding-version bump to 1.0.0. L1 static-analysis bindings carry no
lifecycle field and were not modified. The OWASP Agentic Skills Top 10
(AST10) threat catalog is a review-cadence reference catalog, not on
the draft-to-stable lifecycle, and was not modified.

**Batch attestation.** Attested under Charter Section 2.4.1
(solo-author attestation) on 2026-06-04. Cooling-off honored: every M5
concern and the mapping was authored on a calendar day prior to this
attestation (responsible-ai 2026-06-02; agentic-systems, the AST
catalog and mapping, privacy, and monitoring-alerting on 2026-06-03).

**Open Question 7 closed (AI safety / agentic concern split and depth):
resolved.** The responsible-ai / agentic-systems split, the high-depth
classification of both, and the skill-layer threat binding (the AST10
catalog and owasp-ast-to-concerns mapping) were settled across M5
Sessions 1 through 3 (Section 10 settled decisions 31, 32, 33). The
three-layer threat picture is complete: OWASP LLM Top 10 (model),
OWASP Agentic ASI (orchestration), OWASP Agentic Skills Top 10 (skill).

**Profile back-matter.** The four M5 concern back-matter resources were
refreshed from draft language to stable language (catalog version
1.0.0, catalog-status feature-complete) at substrate version 0.8.0.

### Validation state at close

21 catalogs PASS (four now at stable, version 1.0.0; all 21 concerns
stable) / 1 profile PASS (imports and describes all 21 concerns in
back-matter) / 77 SA bindings PASS / 29 MADRs PASS (eleven now at
stable) / 221 L2 bindings PASS (forty-nine now at stable). No
validation regressions. Rule selection count unchanged at 205;
promotion changes lifecycle, not selection.

---


M5 work lands here. M5 opens AI/ML and operational coverage:
responsible-ai (high depth), an adjacent agentic-systems concern, the
OWASP Agentic Skills Top 10 threat catalog, privacy (building on the
data-classification scheme), and monitoring-alerting.

### M5 Session 1: responsible-ai concern authored at draft; agentic-systems classified

The first M5 authoring session lands the `responsible-ai` concern at draft
and the depth-classification amendment that the M5 Session 2 `agentic-systems`
concern depends on. No stable promotions and no VERSION bump this session;
stable promotion of all M5 concerns batches at the M5 close per the Path A
precedent (settled decisions 21, 26, 30).

#### Added

- `catalogs/concerns/responsible-ai.oscal.yaml` at draft (catalog version
  0.1.0, catalog-status in-development). High-depth concern, 12 rules: 2 L1
  mechanical (RAI-L1-001 model documentation artifact, RAI-L1-002 AI
  disclosure marker), 6 L2 semantic (RAI-L2-001 data governance, RAI-L2-002
  fitness evaluation, RAI-L2-003 output safety, RAI-L2-004 explanation and
  recourse, RAI-L2-005 model provenance, RAI-L2-006 decision record-keeping),
  4 L3 judgmental (RAI-L3-001 responsible-AI policy, RAI-L3-002 fairness
  objective, RAI-L3-003 model-drift monitoring, RAI-L3-004 human oversight).
  Anchored to NIST AI RMF and EU AI Act. Layer split is L2-and-L3-heavy
  because responsible AI is judgment-dominated; the substrate does not
  manufacture L1 rules to balance layers.
- L1 static-analysis bindings (2): `rai-l1-001-model-documentation-artifact`,
  `rai-l1-002-ai-disclosure-marker`. Both static-analysis variant,
  substrate-authored semgrep-pattern-v1 patterns (no native linter detects
  the AI-governance-specific shapes).
- L2 review checklists (6) for RAI-L2-001 through RAI-L2-006 and L3 review
  checklists (4) for RAI-L3-001 through RAI-L3-004 (reviewing the consumer's
  ADR), all at draft.
- L2 test templates (3) for the testable L2 rules: RAI-L2-002 (evaluation
  gate), RAI-L2-003 (output-safety controls), RAI-L2-005 (model lineage
  exposure).
- L3 MADR decision frameworks (4): `responsible-ai-policy`,
  `responsible-ai-fairness-objective`, `responsible-ai-drift-monitoring`,
  `responsible-ai-human-oversight`, all at draft.
- Paired good and anti-pattern examples (24) under
  `examples/responsible-ai/`.

#### Changed

- `spec/substrate-scope.md`: added `agentic-systems` to the high-depth
  concern tier (~12 rules; OWASP ASI Top 10, OWASP Agentic Skills Top 10,
  MAESTRO, NIST AI RMF) with a concern-boundary paragraph recording the
  responsible-ai / agentic-systems seam (system-property versus
  control-loop-security). This is the depth-classification amendment the M5
  Session 2 agentic-systems authoring requires (anti-drift signal 10). Adding
  a concern to a depth tier is non-breaking per the document's own versioning
  rule.
- `profiles/production-grade-baseline.oscal.yaml`: imports the
  responsible-ai catalog and selects all 12 rules, with per-rule alters
  (profile-selection-rationale and severity, catalog defaults preserved) and
  a back-matter resource describing the catalog (every-concern-has-a-resource
  pattern per resolved Open Question 10).

### M5 Session 2: agentic-systems concern authored at draft

The second M5 authoring session lands the `agentic-systems` concern at draft,
the second of the two split AI concerns (responsible-ai owns the model and
system properties; agentic-systems owns the security of the autonomous action
loop). The depth-classification gate was pre-cleared by the M5 Session 1
scope amendment. No stable promotions and no VERSION bump this session; stable
promotion of all M5 concerns batches at the M5 close per the Path A precedent
(settled decisions 21, 26, 30, 31).

#### Added

- `catalogs/concerns/agentic-systems.oscal.yaml` at draft (catalog version
  0.1.0, catalog-status in-development). High-depth concern, 12 rules: 2 L1
  mechanical (AGENT-L1-001 tool authorization scope, AGENT-L1-002 agent
  action audit record), 6 L2 semantic (AGENT-L2-001 tool-use authorization,
  AGENT-L2-002 instruction/data separation, AGENT-L2-003 action bounds,
  AGENT-L2-004 human action gating, AGENT-L2-005 delegation authority,
  AGENT-L2-006 agent memory integrity), 4 L3 judgmental (AGENT-L3-001 agent
  autonomy and authorization policy, AGENT-L3-002 human-action-gating policy,
  AGENT-L3-003 multi-agent trust and delegation, AGENT-L3-004 tool and skill
  trust policy). Anchored to OWASP Agentic Security Initiative Top 10, OWASP
  Agentic Skills Top 10, MAESTRO, and NIST AI RMF. Layer split is
  L2-and-L3-heavy because agent security is authorization-and-design-dominated;
  the substrate does not manufacture L1 rules to balance layers.
- L1 static-analysis bindings (2): `agent-l1-001-tool-authorization-scope`,
  `agent-l1-002-agent-action-audit-record`. Both static-analysis variant,
  substrate-authored semgrep-pattern-v1 patterns (no native linter detects
  the agent-specific shapes).
- L2 review checklists (6) for AGENT-L2-001 through AGENT-L2-006 and L3 review
  checklists (4) for AGENT-L3-001 through AGENT-L3-004 (reviewing the
  consumer's ADR), all at draft.
- L2 test templates (5) for the testable L2 rules: AGENT-L2-001 (call-time
  authorization), AGENT-L2-003 (action bounds), AGENT-L2-004 (action gate),
  AGENT-L2-005 (delegation authority), AGENT-L2-006 (memory integrity).
  AGENT-L2-002 (instruction/data separation) is review-and-probe only because
  separation under adversarial input cannot be proven by a finite test.
- L3 MADR decision frameworks (4):
  `agent-autonomy-and-authorization-policy`,
  `agent-human-action-gating-policy`, `multi-agent-trust-and-delegation`,
  `agent-tool-and-skill-trust-policy`, all at draft.
- Paired good and anti-pattern examples (24) under
  `examples/agentic-systems/`.

#### Changed

- `profiles/production-grade-baseline.oscal.yaml`: imports the
  agentic-systems catalog and selects all 12 rules, with per-rule alters
  (profile-selection-rationale and severity, catalog defaults preserved) and
  a back-matter resource describing the catalog (every-concern-has-a-resource
  pattern per resolved Open Question 10).

### M5 Session 3: OWASP Agentic Skills Top 10 threat catalog and mapping authored

The third M5 authoring session lands the OWASP Agentic Skills Top 10 (AST10)
threat catalog and its mapping to substrate concerns, the skill-layer
counterpart to the existing OWASP LLM Top 10 (model layer) and OWASP Agentic
ASI Top 10 (orchestration layer). Authored after the agentic-systems concern
(M5 Session 2) exists, so the skill-layer threats bind to real substrate
rules. This closes the last open part of Open Question 7 (the skill-layer
threat binding). The threat catalog is a reference catalog (review-cadence
lifecycle, not the draft-to-stable concern lifecycle); the mapping is at draft
and batches to stable at the M5 close per the Path A precedent.

#### Added

- `catalogs/threats/owasp-agentic-skills-top10.yaml`: the AST01-10 threat
  taxonomy for the agentic skill layer (the reusable, named behaviors an agent
  loads and invokes). AST01 Malicious Skills, AST02 Supply Chain Compromise,
  AST03 Over-Privileged Skills, AST04 Insecure Metadata, AST05 Unsafe
  Deserialization, AST06 Weak Isolation, AST07 Update Drift, AST08 Poor
  Scanning, AST09 No Governance, AST10 Cross-Platform Reuse. Anchored to the
  OWASP Agentic Skills Top 10 (1.0-2026, CC-BY-SA-4.0); threat descriptions,
  vectors, and mitigations are substrate-original paraphrase with no verbatim
  upstream text. Same YAML structure as the OWASP LLM Top 10 catalog.
- `mappings/owasp-ast-to-concerns.oscal.yaml` at draft: 26 relations mapping
  all ten AST risks to substrate concern rules, principally the agentic-systems
  tool and skill trust policy (AGENT-L3-004) and secondarily tool-use
  authorization (AGENT-L2-001), scope declaration (AGENT-L1-001), action
  bounds (AGENT-L2-003), action audit (AGENT-L1-002), and the autonomy policy
  (AGENT-L3-001), plus supply-chain (provenance, signing), input-validation
  (safe deserialization), dependency-management (pinning), secrets-management
  (least-privilege credentials), and logging (audit-trail integrity). Four
  coverage gaps record the skill-layer dimensions the substrate addresses only
  partially: metadata-honesty static detection (AST04), host-mode isolation
  defaults (AST06), behavioral skill scanning (AST08), and cross-platform
  metadata loss (AST10), each a platform-side or scanner-side property the
  substrate's first-party-code rules inform but do not fully own. The fifth
  cross-taxonomy mapping. Validates against `schemas/mapping.schema.json`.

#### Changed

- `mappings/README.md`: added the OWASP AST to concerns row to the mapping
  index table.

### M5 Session 4: privacy concern authored at draft

The fourth M5 authoring session lands the privacy concern at medium depth (9
rules). Privacy builds on the data-classification concern: data-classification
owns the sensitivity scheme, and privacy adds the personal-data regulatory
layer (lawful basis, consent, purpose limitation, minimization, data-subject
rights, and retention) on top of it. The boundary is coordinated from the
privacy side: privacy cross-references the DATA-L1-001 label as its
precondition rather than restating classification, defers automated-decision
rights to responsible-ai (RAI-L2-004, RAI-L3-004), and cross-references logging
(LOG-L2-001 retention, LOG-L2-003 redaction) rather than duplicating either.
Authored at draft and batched to stable at the M5 close per the Path A
precedent.

#### Added

- `catalogs/concerns/privacy.oscal.yaml` at draft (catalog version 0.1.0,
  catalog-status in-development): 9 rules across three layers. L1 mechanical:
  PRIV-L1-001 (every personal field carries a processing-purpose and
  lawful-basis annotation, on top of the DATA-L1-001 label) and PRIV-L1-002
  (no personal data in URL path segments or query strings, where it leaks into
  logs, history, and referrer headers). L2 semantic: PRIV-L2-001 (lawful basis
  per purpose, consent valid and withdrawable), PRIV-L2-002 (purpose limitation
  and minimization, secondary use gated on a compatible basis), PRIV-L2-003
  (data-subject rights operable end to end across every store), PRIV-L2-004
  (retention period per category, deletion or irreversible anonymization at
  expiry), and PRIV-L2-005 (processor data-processing agreements and
  cross-border transfer safeguards, review-only). L3 judgmental: PRIV-L3-001
  (lawful-basis, consent, records-of-processing, and DPIA-trigger policy ADR)
  and PRIV-L3-002 (data-subject-rights and retention architecture ADR). Anchored
  to GDPR (Regulation 2016/679), CCPA and CPRA, ISO/IEC 27701, and the NIST
  Privacy Framework; all references are substrate-original paraphrase with no
  verbatim upstream text. Validates against `schemas/concern-catalog.schema.json`.
  Twentieth concern catalog.
- `tool-bindings/static-analysis/priv-l1-001-personal-data-purpose-annotation.yaml`
  and `priv-l1-002-no-personal-data-in-url.yaml`: substrate-authored
  semgrep-pattern-v1 bindings for the two mechanical rules, with Presidio (MIT)
  disclosed as a complementary PII-detection surface for PRIV-L1-001. No native
  linter detects an undeclared personal-data purpose or personal data flowing
  into a URL, so detection is substrate-original patterns per framework with the
  which-fields-are-personal heuristic boundary disclosed.
- `tool-bindings/review-checklist/`: 7 review checklists, one per L2 and L3 rule
  (PRIV-L2-001 through PRIV-L3-002).
- `tool-bindings/test-template/`: 4 framework-agnostic test templates for
  PRIV-L2-001 through PRIV-L2-004. PRIV-L2-005 has no test template because the
  obligation (processor agreements and transfer mechanisms) is contractual, not
  code-testable, mirroring AGENT-L2-002.
- `decision-frameworks/privacy-lawful-basis-and-consent-policy.madr.md` and
  `privacy-data-subject-rights-and-retention.madr.md` at draft: the two L3
  decision frameworks, each a portfolio of sub-decisions (basis per purpose,
  consent model, legitimate-interest assessment, records of processing, DPIA
  trigger, and special-category handling for the first; store inventory, erasure
  propagation, portability format, request handling, and retention schedule for
  the second). Validate against `schemas/decision-framework.schema.json`. The
  27th and 28th decision frameworks.
- `examples/privacy/`: 9 paired good and anti-pattern examples, one pair per
  rule.

#### Changed

- `profiles/production-grade-baseline.oscal.yaml`: imported the privacy concern
  catalog with all 9 rule ids selected, added a profile-level alter block per
  rule (selection rationale, severity-override matching the catalog default, and
  AI-assistance provenance), and added a Privacy Concern Catalog back-matter
  resource. Catalog default severities preserved (PRIV-L2-001/002/003 and
  PRIV-L3-001/002 at high; PRIV-L1-001/002 and PRIV-L2-004/005 at medium).

### M5 Session 5: monitoring-alerting concern authored at draft

The fifth and final M5 authoring session lands the monitoring-alerting concern
at medium depth (8 rules). monitoring-alerting owns the operations layer of
alerting (detection coverage, severity-based routing and escalation, the alert
lifecycle, meta-monitoring of the alerting pipeline, and on-call coverage) that
the observability concern explicitly defers to it: OBS-L2-003 owns the
per-alert-rule hygiene and OBS-L3-001 owns the SLO and error-budget policy, and
monitoring-alerting consumes the severity label and the SLOs those rules define
rather than redefining them. The boundary is coordinated from the
monitoring-alerting side: it cross-references observability (OBS-L2-003,
OBS-L3-001) and reliability (RELY-L2-004 health signals as an input it may alert
on) rather than restating any of them. Authored at draft and batched to stable
at the M5 close per the Path A precedent. This completes the M5 authoring
sessions; the M5 close consolidation follows.

#### Added

- `catalogs/concerns/monitoring-alerting.oscal.yaml` at draft (catalog version
  0.1.0, catalog-status in-development): 8 rules across three layers. L1
  mechanical: MON-L1-001 (every alert route resolves to a configured, non-empty
  receiver, so no alert is silently dropped) and MON-L1-002 (no silence, mute,
  or inhibition is open-ended; every suppression carries an expiry). L2
  semantic: MON-L2-001 (detection coverage of critical user-facing failure modes
  and SLO-burn conditions), MON-L2-002 (severity-based routing and escalation to
  a secondary on no-acknowledgement), MON-L2-003 (alert lifecycle: acknowledge,
  silence-with-expiry, auto-resolve, resolution signal), MON-L2-004 (pipeline
  liveness via a dead-man's-switch heartbeat, and runbook reachability for
  paging alerts), and MON-L2-005 (on-call rotation covers every hour with a
  defined handoff, review-only). L3 judgmental: MON-L3-001 (alerting-strategy
  ADR). Anchored to the Google SRE Book (Monitoring Distributed Systems,
  Practical Alerting, Being On-Call), the Google SRE Workbook (Alerting on
  SLOs), and the Prometheus alerting and Alertmanager documentation; all
  references are substrate-original paraphrase with no verbatim upstream text.
  Validates against `schemas/concern-catalog.schema.json`. Twenty-first concern
  catalog.
- `tool-bindings/static-analysis/mon-l1-001-alert-route-resolves-to-receiver.yaml`
  and `mon-l1-002-silence-carries-expiry.yaml`: substrate-authored
  semgrep-pattern-v1 bindings for the two mechanical rules, targeting alerting
  configuration (Alertmanager YAML and tracked vendor equivalents). No native
  linter detects an orphaned alert route or an open-ended silence, so detection
  is substrate-original patterns with the runtime-reachability and runtime-UI
  silence gaps disclosed.
- `tool-bindings/review-checklist/`: 6 review checklists, one per L2 and L3 rule
  (MON-L2-001 through MON-L3-001).
- `tool-bindings/test-template/`: 4 framework-agnostic test templates for
  MON-L2-001 through MON-L2-004. MON-L2-005 has no test template because its
  subject is a human on-call rotation, not code-testable, mirroring PRIV-L2-005
  and AGENT-L2-002.
- `decision-frameworks/monitoring-alerting-strategy.madr.md` at draft: the L3
  decision framework, a portfolio of seven sub-decisions (coverage philosophy,
  severity-to-routing matrix, escalation and on-call model, alert lifecycle,
  meta-monitoring approach, post-incident feedback loop, and ownership and
  review cadence). Validates against `schemas/decision-framework.schema.json`.
  The 29th decision framework.
- `examples/monitoring-alerting/`: 8 paired good and anti-pattern examples, one
  pair per rule.

#### Changed

- `profiles/production-grade-baseline.oscal.yaml`: imported the
  monitoring-alerting concern catalog with all 8 rule ids selected, added a
  profile-level alter block per rule (selection rationale, severity-override
  matching the catalog default, and AI-assistance provenance), and added a
  Monitoring and Alerting Concern Catalog back-matter resource. Catalog default
  severities preserved (MON-L2-001/002 and MON-L3-001 at high; MON-L1-001/002
  and MON-L2-003/004/005 at medium).

## [0.7.0] - 2026-06-01

### M4 close consolidation (Path A)

The M4 milestone closes. The six M4 concerns authored at draft across
Sessions 1 through 6 (infrastructure-misconfiguration, code-organization,
reliability, performance-database, performance-caching,
data-classification) are promoted to stable in one discrete consolidation
event per the Path A precedent settled at M1 close, M2 close, and M3
close. Substrate version bumped 0.6.0 to 0.7.0. The session entries that
follow this consolidation block (M4 Sessions 1 through 6) record the
authoring of each concern; this block records the close.

**Promotion to stable.** All six concern catalogs advanced from catalog
version 0.1.0 to 1.0.0 and from catalog-status in-development to
feature-complete, with a catalog-attestation prop added to each and every
control and the catalog metadata flipped from lifecycle-status draft to
stable (an entered-stable-at of 2026-06-01 added alongside each
entered-draft-at). The six paired L3 decision frameworks (MADRs) advanced
to lifecycle-status stable, framework-version 1.0.0, with reviewer and
reviewed fields added. All 66 paired L2 bindings (review checklists and
test templates) across the six concerns advanced to lifecycle-status
stable, binding-version 1.0.0, with reviewer and reviewed fields added,
per the parent-inheritance precedent (Section 10 settled decision 23). L1
static-analysis bindings carry no lifecycle field and were not modified.

**Batch attestation.** Attested under Charter Section 2.4.1 (solo-author
attestation) on 2026-06-01. Cooling-off honored: every M4 concern was
authored on a calendar day prior to this attestation (Sessions 4 through 6
on 2026-05-31; Sessions 1 through 3 on earlier days). This batch
attestation supersedes the deferred and non-cooling-off-honoring M4
Session 1 attestation logged in HANDOFF Section 10 decision 27 (commit
b800be1); the infrastructure-misconfiguration catalog-attestation prop
records the supersession.

**Open Question 10 resolved (back-matter consistency): backfill.** The
profile back-matter previously described every M1 through M3 concern and
infrastructure-misconfiguration but omitted code-organization,
reliability, performance-database, performance-caching, and
data-classification. Resolution: backfill, restoring the established
pattern in which every imported concern carries a back-matter resource.
Five resources added (one per omitted concern), each describing the
concern at stable. The infrastructure-misconfiguration resource's
provisional draft language was refreshed to its stable state. The
no-per-catalog-resource alternative was considered and rejected as the
higher-risk change (it would have required removing twelve existing
resources). Recorded as settled decision 30.

**Open Question 9 closed (multi-ecosystem-linter binding variant):
not-needed.** Across all six M4 concerns, every L1 binding fit either the
substrate-authored-pattern static-analysis variant or an existing
registry-reference variant; the per-rule mixed-variant approach (settled
decision 29) absorbed every L1 need without the proposed
ecosystem-iterating linter-rule variant. Closed as not-needed; the
schema-rides-content path remains available if a future milestone ever
surfaces the shape.

### Validation state at close

17 catalogs PASS (six now at stable, version 1.0.0) / 1 profile PASS (now
imports and describes all seventeen concerns in back-matter) / 69 SA
bindings PASS / 18 MADRs PASS (six now at stable) / 172 L2 bindings PASS
(sixty-six now at stable). No validation regressions. Rule selection count
unchanged at 164; promotion changes lifecycle, not selection.

### Note (out of scope, observed at M4 close)

Two minor pre-existing inconsistencies were observed and deliberately left
for a future cleanup to keep the M4 close scope tight: (1) the M3 close
bumped the substrate to 0.6.0 but did not add a [0.6.0] release heading
(its sessions remain under [Unreleased] (M3 Session N) blocks below); and
(2) four back-matter resources for already-stable M1/M2 concerns
(authorization, input-validation, observability, cost-model-selection)
retain provisional "selections will revisit at stable" language from their
own authoring. Neither affects validation or rule behavior.

---

**M4 Session 6: data-classification concern authored at draft. M4
authoring phase complete.**
Sixth and final specialized concern in the M4 milestone. Nine rules at
draft (3 L1 mechanical, 5 L2 semantic, 1 L3 judgmental) plus 33
supporting artifacts. Medium-depth concern (6-10 rule band), L2-heavier
than a balanced medium concern because classification correctness and
per-class handling are judgment-heavy and the mechanically checkable
surface is narrow. This session completes the M4 authoring phase; all six
M4 concerns are now authored at draft. No VERSION change at this session;
the M4 close consolidation (a discrete subsequent-calendar-day step) will
promote all six concerns to stable and bump to 0.7.0 per Path A.

### Added

- **Concern catalog (draft):**
  `catalogs/concerns/data-classification.oscal.yaml` with 9 rules
  (DATA-L1-001 through L1-003, DATA-L2-001 through L2-005, DATA-L3-001).
  L1: every persisted data model carries a classification label; data
  classified above the lowest tier is not written to logs in plaintext;
  classification labels use the closed scheme vocabulary
  (public/internal/confidential/restricted). L2: classification is correct
  and complete including derived and aggregated data; classified data is
  encrypted at rest and in transit per class; access is least-privilege
  need-to-know per class and auditable; retention and disposal follow the
  per-class policy; classification propagates through copies, derivations,
  exports, and caches (most-restrictive-wins). L3: a documented
  data-classification policy ADR. The catalog states its boundary
  discipline in five header notes: infrastructure-misconfiguration owns
  provision-time tag enforcement (IAC-L2-006) while this concern owns the
  scheme and per-class handling and is the authoritative source for the
  data-sensitivity tag vocabulary; secrets-management owns credentials
  while this owns classified business and personal data; performance-
  caching owns cache mechanics while DATA-L2-005 owns what may be cached
  where; code-organization owns structure in the general; privacy (M5)
  will add the personal-data regulatory layer on top of this scheme.

- **Three L1 static-analysis bindings (draft):**
  `tool-bindings/static-analysis/data-l1-001-model-classification-label.yaml`,
  `data-l1-002-no-classified-data-in-logs.yaml`,
  `data-l1-003-closed-vocabulary.yaml`. All three use the
  `static-analysis` variant with substrate-authored `semgrep-pattern-v1`
  patterns because no mature native linter detects these
  classification-specific shapes (an unlabeled persisted model, a
  classified field in a log, an out-of-vocabulary label); the
  no-classified-data-in-logs binding discloses gitleaks (MIT) and the
  Semgrep registry secret and PII rules as `status: secondary`
  complementary sources. This all-substrate-pattern outcome across the
  final M4 concern confirms the multi-ecosystem-linter binding variant
  (Open Question 9) was not needed for any of the six M4 concerns.

- **Six review checklists + five test templates (draft):**
  `tool-bindings/review-checklist/data-l2-001-classification-correctness.md`
  through `data-l2-005-propagation-inheritance.md`, plus
  `data-l3-001-data-classification-policy.md`; and
  `tool-bindings/test-template/data-l2-001-classification-correctness.md`
  through `data-l2-005-propagation-inheritance.md`. Each checklist carries
  the `review-triggers` frontmatter array; each template is
  `framework-agnostic: true` and enumerates classification test scenarios
  (most-restrictive-wins for derived data, a classified store rejecting an
  unencrypted connection, a principal without the role denied read,
  disposal of data past retention including backups, a tier refused a
  class it cannot meet). All satisfy their schemas.

- **One L3 decision framework (draft):**
  `decision-frameworks/data-classification-policy.madr.md`. Portfolio of
  six sub-decisions (the scheme and closed vocabulary, the determination
  rule including aggregation, the per-class handling matrix, the
  propagation rules, the tag-and-label binding to IAC-L2-006, and
  ownership and review cadence) plus a review cadence. Mirrors the
  caching-strategy and data-access-performance-strategy MADR precedents.

- **18 paired examples (good + anti-pattern) at**
  `examples/data-classification/`, one pair per rule. Substrate-original
  illustrations (no reproduced third-party code); filenames match the
  catalog example-good and example-bad link hrefs exactly.

### Changed

- **Profile updated:** `profiles/production-grade-baseline.oscal.yaml`
  now imports the data-classification catalog; selects all 9 rules at
  catalog-default severity (5 high, 4 medium); rule-selection-count
  advanced from 155 to 164; last-modified already at 2026-05-31 from M4
  Session 1.

- **Depth classification confirmed (no amendment):** `spec/substrate-
  scope.md` already classifies data-classification as a medium-depth
  concern (6-10 rule band, line 307); the 9-rule catalog sits within band,
  so no scope amendment was required this session.

### Validation state at session close

17 catalogs PASS / 1 profile PASS / 69 SA bindings PASS /
18 MADRs PASS / 172 L2 bindings PASS. No validation regressions.

### Open question (no action this session)

The profile back-matter resource inconsistency carried from M4 Sessions 2
through 5 remains open. M4 Session 1 added a back-matter resource for the
infrastructure-misconfiguration catalog; Sessions 2 (code-organization),
3 (reliability), 4 (performance-database), 5 (performance-caching), and
this session (data-classification) did not. Flagged for reconciliation at
M4 close: either backfill the missing back-matter resources or formally
adopt the no-per-catalog-resource convention and record the decision. No
action this session, to follow the most recent committed precedent.

### Path A precedent and cooling-off

All M4 Session 6 artifacts at `lifecycle-status: draft`. Per Path A
precedent settled at M1 close, M2 close, and M3 close, stable promotion is
deferred to the M4 close consolidation. Per Charter Section 2.4.1
cooling-off rule, attestation will occur in a discrete commit on a
calendar day subsequent to the authoring commits. With the M4 authoring
phase now complete, the next discrete step is the M4 close consolidation:
promote all six M4 concerns draft to stable, batch-attest, resolve the
back-matter question above, and bump 0.6.0 to 0.7.0.

---

**M4 Session 5: performance-caching concern authored at draft.**
Fifth of six specialized concerns in the M4 milestone. Nine rules at
draft (3 L1 mechanical, 5 L2 semantic, 1 L3 judgmental) plus 33
supporting artifacts. Medium-depth concern (6-10 rule band), the second
performance concern and the deliberate complement to
performance-database (avoid the datastore versus use it well). The split
is slightly L2-heavier than the three-L1 medium precedents because
caching is invalidation- and judgment-heavy and the mechanically
checkable surface is genuinely narrow. No VERSION change at this session;
M4 close consolidation will bump to 0.7.0 alongside the other
M4-milestone concerns per Path A precedent.

### Added

- **Concern catalog (draft):**
  `catalogs/concerns/performance-caching.oscal.yaml` with 9 rules
  (CACHE-L1-001 through L1-003, CACHE-L2-001 through L2-005,
  CACHE-L3-001). L1: a bounded time-to-live on every cache write; no
  per-item cache call in a loop where a batch operation exists (the cache
  N+1); namespaced, structured cache keys rather than bare or
  raw-concatenated strings. L2: invalidation correctness so a write does
  not leave a stale cached copy; stampede or thundering-herd protection on
  hot keys; the cache is optional to correctness and a miss, timeout, or
  outage degrades to the source of record; an explicit staleness budget
  per cached item; the cache backend bounded by a configured maximum and
  an eviction policy. L3: a documented caching strategy ADR. The catalog
  states its boundary discipline in five header notes: performance-database
  owns using the datastore well while this concern owns avoiding it via a
  cache; reliability owns the general degradation posture (RELY-L2-002)
  and the in-process unbounded buffer (RELY-L1-001) while this concern owns
  the cache-tier applications (CACHE-L2-003 cache-as-optional, CACHE-L2-005
  backend bounding); observability owns measuring cache behavior; data-
  classification owns what may be cached where; error-handling owns the
  retry and timeout on the miss-path fetch.

- **Three L1 static-analysis bindings (draft):**
  `tool-bindings/static-analysis/cache-l1-001-ttl-on-write.yaml`,
  `cache-l1-002-no-cache-call-in-loop.yaml`,
  `cache-l1-003-namespaced-keys.yaml`. All three use the `static-analysis`
  variant with substrate-authored `semgrep-pattern-v1` patterns because no
  mature native linter detects these cache-specific shapes (a missing
  cache time-to-live, a cache N+1, a bare cache key); each binding
  discloses its evasions and, for the namespaced-keys rule, its
  deliberately heuristic nature. The all-substrate-pattern outcome
  confirms the multi-ecosystem-linter binding variant (Open Question 9)
  was not needed for this concern either.

- **Six review checklists + five test templates (draft):**
  `tool-bindings/review-checklist/cache-l2-001-invalidation-strategy.md`
  through `cache-l2-005-bounded-eviction.md`, plus
  `cache-l3-001-caching-strategy.md`; and
  `tool-bindings/test-template/cache-l2-001-invalidation-strategy.md`
  through `cache-l2-005-bounded-eviction.md`. Each checklist carries the
  `review-triggers` frontmatter array; each template is
  `framework-agnostic: true` and enumerates caching test scenarios
  (read-after-write invalidation, single recomputation under concurrent
  miss, a read that survives a cache outage or timeout, a value not served
  past its staleness budget, an in-process cache that evicts at capacity).
  All satisfy their schemas.

- **One L3 decision framework (draft):**
  `decision-frameworks/caching-strategy.madr.md`. Portfolio of seven
  sub-decisions (what is cached and never cached, cache topology and
  tiers, key and namespace conventions, invalidation model per data class,
  staleness budget per data class, failure posture, sizing and eviction)
  plus a review cadence. Mirrors the data-access-performance-strategy and
  reliability-strategy MADR precedents and cross-references the data-access
  sibling.

- **18 paired examples (good + anti-pattern) at**
  `examples/performance-caching/`, one pair per rule. Substrate-original
  illustrations (no reproduced third-party code); filenames match the
  catalog example-good and example-bad link hrefs exactly.

### Changed

- **Profile updated:** `profiles/production-grade-baseline.oscal.yaml`
  now imports the performance-caching catalog; selects all 9 rules at
  catalog-default severity (5 high, 4 medium); rule-selection-count
  advanced from 146 to 155; last-modified already at 2026-05-31 from M4
  Session 1.

- **Depth classification confirmed (no amendment):** `spec/substrate-
  scope.md` already classifies performance-caching as a medium-depth
  concern (6-10 rule band); the 9-rule catalog sits within band, so no
  scope amendment was required this session.

### Validation state at session close

16 catalogs PASS / 1 profile PASS / 66 SA bindings PASS /
17 MADRs PASS / 161 L2 bindings PASS. No validation regressions.

### Open question (no action this session)

The profile back-matter resource inconsistency carried from M4 Sessions 2
through 4 remains open. M4 Session 1 added a back-matter resource for the
infrastructure-misconfiguration catalog; Sessions 2 (code-organization),
3 (reliability), 4 (performance-database), and this session
(performance-caching) did not. Flagged for reconciliation at M4 close:
either backfill the missing back-matter resources or formally adopt the
no-per-catalog-resource convention and record the decision. No action this
session, to follow the most recent committed precedent mid-milestone.

### Path A precedent and cooling-off

All M4 Session 5 artifacts at `lifecycle-status: draft`. Per Path A
precedent settled at M1 close, M2 close, and M3 close, stable promotion is
deferred to M4 close consolidation. Per Charter Section 2.4.1 cooling-off
rule, attestation will occur in a discrete commit on a calendar day
subsequent to the authoring commits.

---

**M4 Session 4: performance-database concern authored at draft.**
Fourth of six specialized concerns in the M4 milestone. Twelve rules
at draft (5 L1 mechanical, 6 L2 semantic, 1 L3 judgmental) plus 43
supporting artifacts. High-depth concern (10-15 rule band), the
second high-depth concern in M4 after infrastructure-misconfiguration.
No VERSION change at this session; M4 close consolidation will bump to
0.7.0 alongside the other M4-milestone concerns per Path A precedent.

### Added

- **Concern catalog (draft):**
  `catalogs/concerns/performance-database.oscal.yaml` with 12 rules
  (PERFDB-L1-001 through L1-005, PERFDB-L2-001 through L2-006,
  PERFDB-L3-001). L1: no query in a load-scaled loop (the N+1
  pattern); bounded result sets with an explicit LIMIT; explicit
  column projection rather than a wildcard; pooled connections rather
  than per-request construction; non-blocking migrations for index
  and locking DDL. L2: index alignment to access patterns;
  transaction scope and isolation minimized with no external I/O
  inside a transaction; connection-pool sizing for workload, the
  database ceiling, and the serverless case; keyset pagination over
  deep OFFSET; set-based bulk operations; read-replica routing with
  per-path lag tolerance. L3: documented data-access performance
  strategy ADR. The catalog states its boundary discipline explicitly
  in five header notes: performance-caching (a separate M4 concern)
  owns avoiding the datastore via a cache, while this concern owns
  making datastore access efficient; observability owns measurement;
  reliability owns the pool as a survival resource (existence and
  isolation) while this concern owns it as a throughput resource
  (sizing); error-handling and input-validation own the per-call-site
  triad and untrusted input respectively.

- **Five L1 static-analysis bindings (draft):**
  `tool-bindings/static-analysis/perfdb-l1-001-no-query-in-loop.yaml`
  through `perfdb-l1-005-non-blocking-migrations.yaml`. These use a
  per-rule mixed-variant split according to the detection reality, not
  one variant forced across all five (anti-drift signal 16):
  L1-001/002/003/004 use the `static-analysis` variant with
  substrate-authored `semgrep-pattern-v1` patterns because no mature
  native linter detects these query-shape defects, with the runtime
  N+1 detectors (nplusone, the Django Debug Toolbar, the bullet gem)
  and SQLFluff for raw SQL disclosed as the complementary detection
  surface; L1-005 uses `registry-reference-with-complementary-tools`
  because mature native tooling exists and is strong (squawk
  require-concurrent-index-creation and the locking-DDL family, with
  strong_migrations as the Rails complementary tool). The variant
  split is documented inline in each binding header. This confirms the
  multi-ecosystem-linter binding variant (Open Question 9) was not
  needed: the per-rule split sufficed.

- **Six L2 review checklists + one L3 review checklist (draft):**
  `tool-bindings/review-checklist/perfdb-l2-001-index-alignment.md`
  through `perfdb-l2-006-replica-routing.md`, plus
  `perfdb-l3-001-data-access-strategy.md`. Each carries the
  substrate-required `review-triggers` frontmatter array; all satisfy
  `review-checklist.schema.json`.

- **Six L2 test templates (draft):**
  `tool-bindings/test-template/perfdb-l2-001-index-alignment.md`
  through `perfdb-l2-006-replica-routing.md`. All
  `framework-agnostic: true`; each enumerates reliability-style
  performance test scenarios (index-scan plan assertion, no external
  I/O inside a transaction, pool-exhaustion fast-fail, flat keyset
  page cost, bounded statement count under volume, primary routing for
  read-your-writes) with pass criteria.

- **One L3 decision framework (draft):**
  `decision-frameworks/data-access-performance-strategy.madr.md`.
  Portfolio-of-sub-decisions structure (workload characterization,
  indexing posture, connection topology, transaction and consistency
  policy, pagination and bulk-IO conventions, read-scaling model) plus
  a review cadence. Mirrors the reliability-strategy MADR precedent and
  cross-references it as the related sibling that owns the pool as a
  survival resource.

- **24 paired examples (good + anti-pattern) at**
  `examples/performance-database/`, one pair per rule.
  Substrate-original illustrations (no reproduced third-party code);
  filenames match the catalog example-good and example-bad link hrefs
  exactly.

### Changed

- **Profile updated:** `profiles/production-grade-baseline.oscal.yaml`
  now imports the performance-database catalog; selects all 12 rules
  at catalog-default severity (7 high, 5 medium); rule-selection-count
  advanced from 134 to 146; last-modified already at 2026-05-31 from
  M4 Session 1.

- **Depth classification confirmed (no amendment):** `spec/substrate-
  scope.md` already classifies performance-database as a high-depth
  concern (10-15 rule band); the 12-rule catalog sits within band, so
  no scope amendment was required this session.

### Validation state at session close

15 catalogs PASS / 1 profile PASS / 63 SA bindings PASS /
16 MADRs PASS / 150 L2 bindings PASS. No validation regressions.

### Open question (no action this session)

The profile back-matter resource inconsistency carried from M4
Sessions 2 and 3 remains open. M4 Session 1 added a back-matter
resource for the infrastructure-misconfiguration catalog; Sessions 2
(code-organization), 3 (reliability), and this session
(performance-database) did not. The back-matter therefore describes
every M1 through M3 concern and infrastructure-misconfiguration but
omits code-organization, reliability, and performance-database.
Flagged for reconciliation at M4 close: either backfill the missing
back-matter resources or formally adopt the no-per-catalog-resource
convention and record the decision. No action this session, to follow
the most recent committed precedent mid-milestone.

### Path A precedent and cooling-off

All M4 Session 4 artifacts at `lifecycle-status: draft`. Per Path A
precedent settled at M1 close, M2 close, and M3 close, stable
promotion is deferred to M4 close consolidation. Per Charter Section
2.4.1 cooling-off rule, attestation will occur in a discrete commit on
a calendar day subsequent to the authoring commits.

---

**M4 Session 3: reliability concern authored at draft.**
Third of six specialized concerns in the M4 milestone. Eight rules
at draft (3 L1 mechanical, 4 L2 semantic, 1 L3 judgmental) plus 29
supporting artifacts. Medium-depth concern (6-10 rule band),
structurally mirroring the observability and code-organization
concerns (3 L1 / 4 L2 / 1 L3). No VERSION change at this session;
M4 close consolidation will bump to 0.7.0 alongside the other
M4-milestone concerns per Path A precedent.

### Added

- **Concern catalog (draft):** `catalogs/concerns/reliability.oscal.yaml`
  with 8 rules (RELY-L1-001 through L1-003, RELY-L2-001 through
  L2-004, RELY-L3-001). L1: bounded in-memory buffers, queues, and
  caches; tracked async tasks with no fire-and-forget; no synchronous
  blocking calls on async or event-loop paths. L2: idempotency of
  retryable and redelivered operations, graceful degradation for
  non-critical dependencies, failure isolation and bulkheads,
  liveness-versus-readiness health signaling. L3: documented
  reliability-strategy ADR. The catalog states its boundary
  discipline explicitly: error-handling owns the per-call-site
  retry, timeout, and circuit-breaker triad; observability owns
  measurement (SLOs, alerts, instrumentation); reliability owns the
  system-level survival of partial failure. Each L1 rule carries a
  layer-boundary disclosure separating the mechanical claim from the
  semantic judgment, and the catalog cross-references the
  error-handling and observability concerns at the boundaries.

- **Three L1 static-analysis bindings (draft):**
  `tool-bindings/static-analysis/rely-l1-001-bounded-buffers.yaml`,
  `rely-l1-002-tracked-async-tasks.yaml`,
  `rely-l1-003-no-blocking-in-async.yaml`. These deliberately use two
  different binding variants according to the detection reality, not
  one variant forced across all three (anti-drift signal 16):
  rely-l1-001 uses the `static-analysis` variant with substrate-
  authored `semgrep-pattern-v1` patterns (unbounded `asyncio.Queue()`,
  `queue.Queue(maxsize=0)`, and unbounded list/dict accumulators)
  because no mature native linter detects unbounded-buffer
  accumulation, and the binding discloses the resulting native-
  coverage gap honestly. rely-l1-002 and rely-l1-003 use variant-3
  registry-reference-with-complementary-tools because mature native
  rules exist and are strong: Ruff RUF006 (asyncio-dangling-task)
  and typescript-eslint no-floating-promises for tracked tasks; the
  Ruff ASYNC family (blocking-open, blocking-sleep, blocking-http)
  and ESLint no-sync for blocking-in-async. The variant split is
  documented inline in each binding header.

- **Four L2 review checklists + one L3 review checklist (draft):**
  `tool-bindings/review-checklist/rely-l2-001-idempotency.md`
  through `rely-l2-004-health-signaling.md`, plus
  `rely-l3-001-reliability-strategy.md`. Each carries the
  substrate-required `review-triggers` frontmatter array; all satisfy
  `review-checklist.schema.json`.

- **Four L2 test templates (draft):**
  `tool-bindings/test-template/rely-l2-001-idempotency.md` through
  `rely-l2-004-health-signaling.md`. All `framework-agnostic: true`;
  each enumerates 5-6 reliability test scenarios (duplicate-delivery
  convergence, dependency-failure fallback, pool-exhaustion
  isolation, probe-contract correctness under warmup and shutdown)
  with pass criteria and cadence.

- **One L3 decision framework (draft):**
  `decision-frameworks/reliability-strategy.madr.md`.
  Portfolio-of-sub-decisions structure (failure-mode catalog,
  dependency-criticality classification, delivery and idempotency
  semantics, resource-isolation model, health-and-recovery model,
  degradation policy) plus a review cadence. Mirrors the
  infrastructure-security-baseline, observability-slo-policy, and
  code-organization-strategy MADR precedents.

- **16 paired examples (good + anti-pattern) at**
  `examples/reliability/`, one pair per rule. Substrate-original
  illustrations (no reproduced third-party code); filenames match
  the catalog example-good and example-bad link hrefs exactly.

### Changed

- **Profile updated:** `profiles/production-grade-baseline.oscal.yaml`
  now imports the reliability catalog; selects all 8 rules at
  catalog-default severity (7 high, 1 medium for the orchestrated-
  environment health-signaling rule); rule-selection-count advanced
  from 126 to 134; last-modified already at 2026-05-31 from M4
  Session 1.

- **Depth classification confirmed (no amendment):** `spec/substrate-
  scope.md` already classifies reliability as a medium-depth concern
  (6-10 rule band); the 8-rule catalog sits within band, so no scope
  amendment was required this session.

### Validation state at session close

14 catalogs PASS / 1 profile PASS / 58 SA bindings PASS /
15 MADRs PASS / 137 L2 bindings PASS. No validation regressions.

### Open question (no action this session)

The profile back-matter resource list is inconsistent across the M4
milestone. M4 Session 1 added a back-matter resource describing the
infrastructure-misconfiguration catalog; M4 Session 2 (code-
organization) did not, and this session follows the Session 2
precedent and likewise adds no reliability resource. The back-matter
therefore describes every M1 through M3 concern and infrastructure-
misconfiguration, but omits code-organization and reliability.
Flagged for reconciliation at M4 close consolidation: either backfill
back-matter resources for code-organization and reliability, or
formally adopt the no-per-catalog-resource convention and record the
decision. No action this session, to avoid diverging from the most
recent committed precedent mid-milestone.

### Path A precedent and cooling-off

All M4 Session 3 artifacts at `lifecycle-status: draft`. Per Path A
precedent settled at M1 close, M2 close, and M3 close, stable
promotion is deferred to M4 close consolidation. Per Charter Section
2.4.1 cooling-off rule, attestation will occur in a discrete commit
on a calendar day subsequent to the authoring commits.

---

**M4 Session 2: code-organization concern authored at draft.**
Second of six specialized concerns in the M4 milestone. Eight rules
at draft (3 L1 mechanical, 4 L2 semantic, 1 L3 judgmental) plus 29
supporting artifacts. Medium-depth concern (6-10 rule band),
structurally mirroring the observability concern (3 L1 / 4 L2 /
1 L3). No VERSION change at this session; M4 close consolidation
will bump to 0.7.0 alongside the other M4-milestone concerns per
Path A precedent.

### Added

- **Concern catalog (draft):** `catalogs/concerns/code-organization.oscal.yaml`
  with 8 rules (CODEORG-L1-001 through L1-003, CODEORG-L2-001
  through L2-004, CODEORG-L3-001). L1: function length, cyclomatic
  plus cognitive complexity, no first-party import cycles. L2:
  module-boundary cohesion, dependency direction and layering,
  public-interface minimalism, duplication versus abstraction. L3:
  documented code-organization strategy ADR. Each rule carries a
  layer-boundary disclosure separating the mechanical claim from the
  semantic judgment, and cross-references the dependency-management
  and testing-strategy concerns.

- **Three L1 static-analysis bindings (draft):**
  `tool-bindings/static-analysis/codeorg-l1-001-function-length.yaml`,
  `codeorg-l1-002-cyclomatic-complexity.yaml`,
  `codeorg-l1-003-no-import-cycles.yaml`. All variant-3 registry-
  reference-with-complementary-tools, mapping per-ecosystem native
  linter and graph-analyzer rules (Ruff, ESLint, golangci-lint,
  Clippy, Checkstyle/PMD, RuboCop; import-linter, eslint-plugin-
  import, dependency-cruiser, ArchUnit). Variant 3 was chosen over
  multi-ecosystem-orchestration (variant 4) deliberately: variant 4's
  ecosystem-detections items are schema-locked to dependency-manager
  fields and cannot carry a per-language linter rule identifier,
  whereas variant 3's referenced-rules array and free-form registry
  string hold the native rule mapping without hybridizing fields
  (anti-drift signal 16). The choice is documented inline in each
  binding header.

- **Four L2 review checklists + one L3 review checklist (draft):**
  `tool-bindings/review-checklist/codeorg-l2-001-module-boundary-cohesion.md`
  through `codeorg-l2-004-duplication-and-abstraction.md`, plus
  `codeorg-l3-001-organization-strategy.md`. Each carries the
  substrate-required `review-triggers` frontmatter array; all satisfy
  `review-checklist.schema.json`.

- **Four L2 test templates (draft):**
  `tool-bindings/test-template/codeorg-l2-001-module-boundary-cohesion.md`
  through `codeorg-l2-004-duplication-and-abstraction.md`. All
  `framework-agnostic: true`; each enumerates 5-6 architecture-test
  scenarios (layering contracts, fan-in measurement, clone triage,
  internal-leak detection) with pass criteria and cadence.

- **One L3 decision framework (draft):**
  `decision-frameworks/code-organization-strategy.madr.md`.
  Portfolio-of-five-sub-decisions structure (architectural style,
  module-boundary policy, dependency rule and enforcement,
  cross-cutting placement, repository topology) plus a review
  cadence, with seven decision drivers. Mirrors the infrastructure-
  security-baseline and observability-slo-policy MADR precedents.

- **16 paired examples (good + anti-pattern) at**
  `examples/code-organization/`, one pair per rule. Substrate-
  original illustrations (no reproduced third-party code); filenames
  match the catalog example-good and example-bad link hrefs exactly.

### Changed

- **Profile updated:** `profiles/production-grade-baseline.oscal.yaml`
  now imports the code-organization catalog; selects all 8 rules at
  catalog-default severity; rule-selection-count advanced from 118 to
  126; last-modified already at 2026-05-31 from M4 Session 1.

- **Depth classification confirmed (no amendment):** `spec/substrate-
  scope.md` already classifies code-organization as a medium-depth
  concern (6-10 rule band); the 8-rule catalog sits within band, so
  no scope amendment was required this session.

### Validation state at session close

13 catalogs PASS / 1 profile PASS / 55 SA bindings PASS /
14 MADRs PASS / 128 L2 bindings PASS. No validation regressions.

### Open question (no action this session)

The variant-3 fit for multi-ecosystem native-linter L1 rules is
honest but indirect: a future schema-version draft could add a
dedicated `multi-ecosystem-linter-rules` binding variant whose
per-ecosystem item carries a linter rule identifier directly,
parallel to variant 4 for dependency managers. Deferred as a
schema-rides-content candidate for a future milestone; no schema
change made this session (Path A discipline preserved).

### Path A precedent and cooling-off

All M4 Session 2 artifacts at `lifecycle-status: draft`. Per Path A
precedent settled at M1 close, M2 close, and M3 close, stable
promotion is deferred to M4 close consolidation. Per Charter Section
2.4.1 cooling-off rule, attestation will occur in a discrete commit
on a calendar day subsequent to the authoring commits.

---

**M4 Session 1: infrastructure-misconfiguration concern authored at draft.**
First of six specialized concerns in the M4 milestone, targeting
Terraform-complete + web-app-complete substrate coverage. Twelve
rules at draft (5 L1 mechanical, 6 L2 semantic, 1 L3 judgmental)
plus 43 supporting artifacts. No VERSION change at this session;
M4 close consolidation will bump to 0.7.0 alongside the other
five M4-milestone concerns per Path A precedent.

### Added

- **Concern catalog (draft):** `catalogs/concerns/infrastructure-misconfiguration.oscal.yaml`
  with 12 rules (IAC-L1-001 through IAC-L1-005, IAC-L2-001 through
  IAC-L2-006, IAC-L3-001). High-depth concern at the floor of the
  10-15 rule band, matching the structural shape of authorization,
  input-validation, error-handling, supply-chain, and testing-
  strategy concerns. Three concern-boundary notes in the header
  (vs dependency-management, supply-chain, secrets-management);
  cross-references to authorization, logging, and the forthcoming
  data-classification concern.

- **Five L1 static-analysis bindings (draft):**
  `tool-bindings/static-analysis/iac-l1-001-data-resource-encryption-at-rest.yaml`,
  `iac-l1-002-no-unrestricted-ingress.yaml`,
  `iac-l1-003-no-public-access-without-tag.yaml`,
  `iac-l1-004-audit-and-flow-logging-enabled.yaml`,
  `iac-l1-005-iac-sources-version-pinned.yaml`. All variant-3
  registry-reference-with-complementary-tools, composing Semgrep
  registry rules with Checkov, Trivy, terrascan, KICS, and tflint
  (for IAC-L1-005).

- **Six L2 review checklists + one L3 review checklist (draft):**
  `tool-bindings/review-checklist/iac-l2-001-least-privilege-iac-iam.md`
  through `iac-l2-006-governance-tagging.md`, plus
  `iac-l3-001-infrastructure-security-baseline.md`. Each carries
  the substrate-required `review-triggers` frontmatter array; all
  satisfy `review-checklist.schema.json`.

- **Six L2 test templates (draft):**
  `tool-bindings/test-template/iac-l2-001-least-privilege-iac-iam.md`
  through `iac-l2-006-governance-tagging.md`. All
  `framework-agnostic: true`; each enumerates 5-8 test scenarios
  with substrate-recommended cadence and pass criteria.

- **One L3 decision framework (draft):**
  `decision-frameworks/infrastructure-security-baseline.madr.md`.
  Portfolio-of-four-sub-decisions structure (baseline benchmark,
  enforcement model, exception governance, drift cadence) with
  six decision drivers (D1 regulatory regime, D2 multi-account/
  multi-cloud topology, D3 team maturity, D4 preventive vs
  detective trade-off, D5 exception governance, D6 drift cadence).
  Mirrors supply-chain-integrity-strategy MADR precedent.

- **24 paired examples (good + anti-pattern) at**
  `examples/infrastructure-misconfiguration/`, one pair per rule.
  Each example file ~110-180 lines covering Terraform, Kubernetes,
  CloudFormation, and where appropriate Azure/GCP patterns;
  anti-pattern files reference the detection coverage in the
  matched L1 binding.

### Changed

- **Profile updated:** `profiles/production-grade-baseline.oscal.yaml`
  now imports infrastructure-misconfiguration catalog; selects all
  12 rules at catalog-default severity; rule-selection-count
  advanced from 106 to 118; last-modified bumped to 2026-05-31;
  added back-matter resource describing the catalog.

- **Substrate-scope.md amended** to classify infrastructure-
  misconfiguration as a high-depth concern with the 10-15 rule
  target band documented and rule-count justification recorded.

### Validation state at session close

12 catalogs PASS / 1 profile PASS / 52 SA bindings PASS /
13 MADRs PASS / 119 L2 bindings PASS. No validation regressions.

### Path A precedent and cooling-off

All M4 Session 1 artifacts at `lifecycle-status: draft`. Per Path
A precedent settled at M1 close, M2 close, and M3 close, stable
promotion is deferred to M4 close consolidation. Per Charter
Section 2.4.1 cooling-off rule, attestation will occur in a
discrete commit on a calendar day subsequent to the authoring
commits; the substrate-author's attestation event marks the
draft-to-stable transition for the entire concern.

---

**Post-M3-close documentation: usability statement + L1 maturity
disclosure.** Documentation-only update; no lifecycle changes, no
content promotions, no VERSION change. Lands in the open `[Unreleased]`
block per Keep-a-Changelog; folds into the next milestone-close
versioned block (M4 close 0.7.0).

### Added

- HANDOFF Section 4 gains a "Usability statement and project-shape fit
  (as of substrate 0.6.0 / M3 close)" subsection recording the honest
  fit-by-shape assessment: best fit application backends (Shape B);
  partial fit AI/ML (Shape C, mappings exist with coverage-gap records,
  no AI concern catalog until M5); not-yet-fit Terraform/IaC (Shape A,
  M4), data pipelines (Shape D, M4/M5), regulated industries (M7
  profiles); and the L1-enforcement-maturity caveat from the
  registry-ID audit (45/306 references alive; L2/L3 unaffected and the
  strong surface). HANDOFF is substrate-author-local (Section 10
  settled decision 14); this CHANGELOG entry records the conceptual
  addition for the audit trail.
- `governance-commons/FUTURE.md` gains two entries (net 14 -> 16):
  "Usability statement publication (consumer-facing fit assessment)"
  and "L1 enforcement coverage gap is unstated in consumer-facing
  surface." Together with the existing "Registry-ID drift remediation"
  entry these form the substrate's honesty-about-L1-maturity cluster.
  Both propose publication at M6/M7 close or first external exposure,
  whichever comes first.

### Substrate-author notes

The "usable end-to-end" M3 capability claim is true about the
integration system and must not be read as complete content coverage.
This documentation update makes the distinction explicit in the
substrate-author's working record and queues a consumer-facing
distillation as deferred work. No substrate-published normative
content changed; the substrate remains at 0.6.0.



**M3 consolidation phase (Path A): consumer-scaffold + mappings +
schemas stable promotion.** The substrate's major inflection
milestone closes. The 1 M3 spec doc, 4 M3 mappings, and 3 schemas
introduced or refactored during the M3 Sessions 1, 2a, 2b, 3, and 4
authoring arc are promoted from draft to stable under Charter Section
2.4.1 solo-author attestation. The 106 L2 binding files refactored at
M3 Session 4 already carry `lifecycle-status: stable` via
parent-inheritance (Section 10 settled decision 23) and require no
field-level edits at this close; the 3 schemas they validate against
flip from draft to stable in this consolidation per the
schema-rides-content Path A precedent (Section 10 settled decisions
14/17/21/22). M3 closes; M4 (Specialized concerns: Terraform-complete
and web-app-complete) authoring is unblocked.

Per Charter Section 2.4.1, every artifact promoted in this version
honored a cooling-off interval of one calendar day or more between
its authoring date and this attestation date. The latest M3 draft
authoring (L2 binding schemas + refactor, 2026-05-29 M3 Session 4)
satisfies cooling-off against this 2026-05-30 attestation; all
earlier-authored drafts (mappings 2026-05-28 M3 Session 2a; consumer-
scaffold.md 2026-05-27 M3 Session 1) satisfy cooling-off by larger
intervals. Section 2.4 validation criteria applied per artifact:
intent clear, methodology defensible, provenance complete, no
conflict with existing commons content.

M3 introduces no concern catalogs (catalog inventory unchanged at
11; profile rule-selection-count unchanged at 106). M3's contribution
is the system: the substrate now publishes a normative consumer
contract (`spec/consumer-scaffold.md`), four cross-taxonomy mappings
binding external threat models (OWASP LLM Top 10, OWASP Agentic ASI,
MITRE ATLAS, STRIDE) to substrate concern rules, and schema
validation for the L2 review-checklist and test-template binding
files. The substrate is now usable end-to-end per the M3 capability
statement in HANDOFF Section 4.

### Promoted

Spec doc (Section 7 prose flipped from "draft, promotion to stable
deferred" to "stable at substrate-version 0.6.0"; no other content
change):

- `spec/consumer-scaffold.md` (594 lines authored M3 Session 1
  2026-05-27 with Section 5 rewrite by M3 Session 2b 2026-05-28).
  Specifies the five-obligation consumer scaffold contract and adds
  two new normative sections not previously covered at spec depth:
  Section 3 (agent prompt injection patterns; nine prompt slots; the
  agent's required structured output shape; substrate-recommended
  constitution-slicing defaults per consulter type; 30K-50K hard
  context cap per invocation) and Section 4 (CI workflow integration;
  eight-step sequence; substrate-default OpenGrep engine selection).

Cross-taxonomy mappings (mapping.metadata.version 0.1.0 -> 1.0.0;
mapping.metadata.last-modified bumped to 2026-05-30T00:00:00Z;
lifecycle-status draft -> stable; commons-version 0.5.0 -> 0.6.0;
target-catalog.catalog-version 0.5.0 -> 0.6.0; new props
entered-stable-at, reviewer, reviewed, attestation-mechanism added;
ai-assistance value drafted -> drafted-and-reviewed):

- `mappings/owasp-llm-to-concerns.oscal.yaml` (362 lines; 22
  relations + 3 coverage-gap records; M3 Session 2a authored
  2026-05-28; UUID `8de2278f-897a-437c-b761-6ad8466e8a13`)
- `mappings/owasp-asi-to-concerns.oscal.yaml` (298 lines; 18
  relations + 3 coverage-gap records; M3 Session 2a authored
  2026-05-28; UUID `04a9a3b2-db32-4362-a427-8ae1cf90d6ae`)
- `mappings/mitre-atlas-to-concerns.oscal.yaml` (334 lines; 19
  relations + 3 coverage-gap records; M3 Session 2a authored
  2026-05-28; UUID `27fe6fea-e4f3-4189-ab82-b455836d16cb`)
- `mappings/stride-to-concerns.oscal.yaml` (321 lines; 26 relations
  + 2 coverage-gap records; M3 Session 2a authored 2026-05-28;
  UUID `03af42a3-a735-477a-ac8e-b7c3ce4ae0fc`)

Schemas (x-governance-commons.lifecycle-status draft -> stable;
x-governance-commons.commons-version bumped to 0.6.0; new x-
governance-commons properties entered-stable-at, reviewer, reviewed,
attestation-mechanism added; ai-assistance note updated to record
the M3 close consolidation; schema-version remains 0.1.0 across all
three, the promotion is lifecycle status only with no schema content
change):

- `schemas/mapping.schema.json` (validates the 4 mapping files
  above; first stable consumers are the 4 mappings themselves). The
  schema was authored at M0 and remained at draft pending real-
  mapping validation; the M3 Session 2a authoring exercised the
  schema, and M3 close promotes it alongside the validated content
  per the Path A schema-rides-content precedent established at M1
  close and reinforced at M2 close.
- `schemas/review-checklist.schema.json` (validates the YAML
  frontmatter of 59 review-checklist L2 binding files; first stable
  consumers are the 59 refactored bindings, all at lifecycle-status
  stable via parent-inheritance per Section 10 settled decision 23).
  Authored M3 Session 4 2026-05-29.
- `schemas/test-template.schema.json` (validates the YAML
  frontmatter of 47 test-template L2 binding files; first stable
  consumers are the 47 refactored bindings, all at lifecycle-status
  stable via parent-inheritance per Section 10 settled decision 23).
  Authored M3 Session 4 2026-05-29.

### Changed

- `VERSION` 0.5.0 -> 0.6.0. Minor bump per `spec/rule-lifecycle.md`
  stable-promotion guidance: M3 close consolidation covers 1 spec
  doc + 4 mappings + 3 schema lifecycle promotions all reaching
  stable in one consolidation event; the minor bump groups them
  atomically per the Path A precedent established at M1 close and
  reinforced at M2 close.

### Unchanged at M3 close

- The 11 concern catalogs from M0/M1/M2 (authentication, secrets-
  management, dependency-management, logging, observability,
  cost-model-selection, authorization, input-validation, error-
  handling, testing-strategy, supply-chain) remain at stable
  lifecycle. No catalog content changed in M3. Catalog inventory
  remains at 11.
- The 12 decision-framework MADRs remain at stable lifecycle. No
  MADR content changed in M3.
- The 47 L1 static-analysis bindings remain at stable lifecycle.
  No L1 binding content changed in M3.
- The 106 L2 bindings (59 review-checklist + 47 test-template)
  refactored at M3 Session 4 already carry lifecycle-status stable
  via parent-inheritance per Section 10 settled decision 23; no
  field-level edits at M3 close.
- `static-analysis-binding.schema.json` remains at lifecycle-status
  stable (promoted to stable at M2 close); no schema content change
  in M3.
- `profiles/production-grade-baseline.oscal.yaml` rule-selection-
  count remains 106; no profile selection change in M3 (M3
  introduces no concerns).
- Substrate-internal reference scaffold under
  `governance-commons/reference/` (1 manifest + 3 agent prompts +
  1 CI workflow + 1 pre-commit hook + 1 sample allowlist + 1
  coverage-matrix template) and substrate-published audit
  documentation under `governance-commons/docs/`
  (registry-id-audit-2026-05.md) carry no lifecycle metadata per
  Section 10 settled decision 24; substrate-author Article VII
  compatibility-with-consumers obligation governs change discipline.

### M3 milestone closure note

M3 (Consumer scaffold + integrity, the major inflection) closes
with this consolidation. The M3 authoring arc (Sessions 1, 2a, 2b,
3, 4) produced the system that consumes the catalogs M1 and M2
produced: a normative consumer contract, a substrate-internal
reference implementation of all five contract obligations, four
threat-catalog mappings, the L2 binding format refactor + schema
validation, a substrate write-isolation pre-commit hook, and the
substrate's first registry-id honesty audit. Combined with the M1
universal floor (5 catalogs) and M2 common coverage (5 catalogs)
and the M0 authentication catalog, the substrate now covers 11
concerns at stable lifecycle AND publishes a complete reference
implementation of the consumer scaffold contract. The M3 capability
statement is now realized at commitment grade: **substrate is
usable end-to-end**.

Per HANDOFF Section 4, M4 (Specialized concerns: Terraform-complete
and web-app-complete) is the next milestone. M4 introduces 6
specialized concerns (infrastructure-misconfiguration,
code-organization, reliability, performance-database,
performance-caching, data-classification). M4 work starts at
substrate version 0.6.0 and will land at draft until M4's own
consolidation phase bumps to 0.7.0.

### Open Questions closed by this version

- **No M3-tagged open questions required closing at this version.**
  Open Questions 21 (M3 spec-doc candidates) and 23 (M3
  substrate-scope.md amendment sequencing) were resolved at M3
  Session 1 open. Open Question 22 (variant 6 sub-splitting
  threshold) remains open as a forward-looking design question;
  decision deferred until the second attestation-type cluster
  surfaces. Open Question 25 (EU CRA regulatory drift watch
  through 2027-12-11) remains open as a tracking item; quarterly
  recheck cadence in effect per Section 12.

## [0.6.0] - 2026-05-30

**M3: consumer scaffold and integrity inflection (mappings, L2 binding
refactor to MADR-pattern frontmatter, registry-ID audit, reference
scaffold). Authored across M3 Sessions 1 through 4 and released at the
M3 close on 2026-05-30. The session detail follows.**

## M3 Session 4 (released in [0.6.0])

**M3 Session 4: L2 binding format refactor (schemas + validator +
106 bindings).** Largest structural transformation of the substrate
since the M0 schema landing. All 59 review-checklist files and 47
test-template files migrated from markdown-wrapped-YAML to MADR-pattern
YAML frontmatter + markdown body. Two new schemas (review-checklist
and test-template) enter at lifecycle-status draft; one new validator
script `scripts/validate-l2-bindings.sh` joins the substrate's
validation surface; `scripts/validate-all.sh` updated to invoke the
new validator. The L2 binding format gap is closed at structural-
metadata level; the L2 metadata-to-content drift gap (FUTURE.md
deferred entry) remains open as a future validator candidate.

The refactor is information-preserving. All 106 binding files inherit
lifecycle-status `stable` from their parent catalog rules per Section
10 settled decision 23 (parent-inheritance). Schema lifecycle
promotion is deferred to M3 Session 5 close consolidation per the
schema-rides-content M1 / M2 close precedent (Section 10 settled
decisions 14/17/21/22). VERSION remains 0.5.0 (M3 Session 5 close
bumps to 0.6.0 alongside mappings and consumer-scaffold.md
promotions and the two new schemas).

One surfaced authoring artifact: three TEST-L2-* review-checklist
files contained unquoted colons inside review-trigger strings in
the original markdown-wrapped-YAML (e.g.,
`Periodic audits (substrate-recommended: quarterly)`). PyYAML
parses these as single-key mappings rather than strings. The
refactor reconstructs the original string form via a
`coerce_to_string` helper; the new schema validation would have
caught these at authoring time had it been in place. The fix is
information-preserving; no review-question or test-scenario
content is altered.

### Added

Substrate validation infrastructure:

- `governance-commons/schemas/review-checklist.schema.json`
  (220 lines, draft, schema-version 0.1.0, commons-version 0.5.0).
  Validates the YAML frontmatter of L2 review-checklist binding
  files. Required fields: `binding-id`, `title`, `substrate-rule`,
  `substrate-rule-href`, `layer`, `lifecycle-status`,
  `commons-version`, `binding-version`, `author`, `authored`,
  `review-triggers`. Optional structured fields: `reviewer`,
  `reviewed`, `entered-status-at`, `attestation-mechanism`,
  `ai-assistance`, `authoritative-sources`, `layer-tags`,
  `related-bindings`, `reviews-what`, `reviews-where`,
  `superseded-by`, `deprecation-window-ends`. Conditional
  requirement: `reviewer` + `reviewed` required when
  lifecycle-status is `stable`; `superseded-by` +
  `deprecation-window-ends` required when lifecycle-status is
  `deprecated`. The `binding-id` pattern is
  `^review-checklists\.[a-z][a-z0-9-]*$` matching the MADR-pattern
  prefix convention (cf. `decision-frameworks.<name>` in
  decision-framework.schema.json). Markdown body validation is
  deferred per the schema's own validation-notes; the L2
  metadata-to-content drift check is a future validator candidate.

- `governance-commons/schemas/test-template.schema.json`
  (200 lines, draft, schema-version 0.1.0, commons-version 0.5.0).
  Validates the YAML frontmatter of L2 test-template binding
  files. Same shape as review-checklist schema with two
  divergences: `layer` enum restricted to `L2` only (test
  templates are L2-only per substrate convention; L3 judgmental
  rules pair with review-checklist bindings reviewing the
  consumer's ADR document, not with test templates exercising
  code), and `framework-agnostic` (optional boolean) replaces
  `review-triggers`/`reviews-what`/`reviews-where`. The
  `binding-id` pattern is `^test-templates\.[a-z][a-z0-9-]*$`
  matching the MADR-pattern prefix convention.

- `scripts/validate-l2-bindings.sh` (227 lines, bash 3.2 portable,
  executable). Discovers and validates L2 binding files in both
  `tool-bindings/review-checklist/` and `tool-bindings/test-template/`
  directories, dispatching to the appropriate schema based on file
  parent directory. Same shape as `validate-decision-frameworks.sh`
  with a directory-based schema-dispatch step. README.md files are
  skipped. Supports invocation with explicit file arguments for
  pre-commit integration.

### Changed

- `scripts/validate-all.sh` adds `validate-l2-bindings.sh` to the
  VALIDATORS array (position 5, dependency-heavier-than-frameworks
  but parent-validators run first). VALIDATORS array comment block
  updated.

- All 59 files in `governance-commons/tool-bindings/review-checklist/`
  refactored from markdown-wrapped-YAML to MADR-pattern YAML
  frontmatter + markdown body. Information-preserving. New
  frontmatter fields: `binding-id` (with `review-checklists.`
  prefix), `title` (normalized from H1), `layer` (L2 or L3 derived
  from substrate-rule), `lifecycle-status: stable` (parent-inherited
  per Section 10 settled decision 23), `commons-version` (preserved
  from old `substrate-version`), `binding-version: 1.0.0` (bumped
  to stable convention from old 0.1.0), `author: myoung`,
  `authored` (preserved from old `last-modified`), `last-modified`:
  2026-05-29 (Session 4 refactor date), `reviewer:
  myoung-self-attested`, `reviewed`/`entered-status-at` (parent
  rule's attestation date: 2026-05-20 for AUTH-* per M0; 2026-05-22
  for SECRETS-*/DEPS-*/LOG-*/OBS-*/COST-* per M1 close; 2026-05-26
  for AUTHZ-*/INPUT-*/ERR-*/TEST-*/SUPPLY-* per M2 close),
  `attestation-mechanism` (cites Charter Section 2.4.1 + Section 10
  settled decision 23), `ai-assistance` (refactor disclosure plus
  preserved original-authoring AI disclosure). Preserved type-
  specific fields: `review-triggers` (array), `reviews-what`,
  `reviews-where` (the latter two only on the 5 of 12 L3 review
  checklists that carried them).

- All 47 files in `governance-commons/tool-bindings/test-template/`
  refactored similarly. Per-type differences from review-checklist:
  `binding-id` uses `test-templates.` prefix; `framework-agnostic`
  (preserved from old `binding.spec.framework-agnostic`) replaces
  `review-triggers`; no `reviews-what`/`reviews-where` (test
  templates are L2-only).

- `governance-commons/FUTURE.md` "L2 binding format lacks schema
  validation" entry marked CLOSED 2026-05-29 with the original
  problem statement preserved as historical record. The companion
  "L2 binding metadata can drift from markdown content" entry
  remains open as a forward-looking validator candidate. No other
  FUTURE.md content changed.

### Migration

Consumers integrating L2 review-checklist or test-template bindings
into their workflows (pre-commit hooks, CI gates, agent-prompt
attachments) should update their consumption patterns:

- The YAML metadata is no longer in a `binding:` envelope inside a
  markdown fenced code block. Consumers parse the YAML frontmatter
  delimited by `---` at the top of each file.
- The `binding.metadata.name` field is replaced by `binding-id`
  with the `review-checklists.` or `test-templates.` prefix.
- The `binding.metadata.substrate-version` field is renamed to
  `commons-version` (matching the MADR-pattern convention).
- The `binding.metadata.last-modified` field semantics changed:
  `last-modified` in the new frontmatter is the date of the most
  recent edit (Session 4 date for refactored files); `authored`
  is the date the binding's content was originally authored
  (preserved from the old `last-modified` value).
- `binding-version` bumped to 1.0.0 across all bindings (was 0.1.0
  in the markdown-wrapped-YAML form); the stable-lifecycle
  convention is now explicit.

Consumers who parsed the markdown body for review questions or test
scenarios have no migration concern; the body content is preserved
verbatim. The H1 is normalized to a substrate-recommended form
(`<RULE-ID> review checklist: <description>` / `<RULE-ID> test
template: <description>`) but this is editorial; consumers parsing
H2 (`## Scenario N`, `## 1. Coverage`) section headers see no
change.

The frontmatter SPDX placement follows Section 10 settled decision
15 (YAML comments inside frontmatter on lines 2 and 3, immediately
after the opening `---`); the new schema-validation discipline
relies on this placement.

## M3 Session 3 (released in [0.6.0])

**M3 Session 3: pre-commit hook, registry-ID audit, coverage-matrix
template, FUTURE.md catch-up.** Four bundled deliverables for the
smaller M3 items per HANDOFF Section 4 milestone roadmap. None
individually justified a session; the bundle is the appropriate
granularity. All four deliverables land under
`governance-commons/` per Section 10 settled decision 24
(substrate-internal location for all reference content). No
catalog, MADR, profile, or schema content changed in this session;
the substrate's stable lifecycle inventory at commons-version 0.5.0
is unaffected.

### Added

Substrate-internal reference content (illustrative; no lifecycle
metadata; substrate-author Article VII compatibility-with-consumers
obligation governs change discipline):

- `governance-commons/reference/hooks/pre-commit` (188 lines, bash
  3.2 portable, executable). Reference pre-commit hook implementing
  substrate write-isolation per Charter Article II. Rejects commits
  that touch any path under `governance-commons/` unless the
  committer is in the consumer-maintained `.substrate-authors`
  allowlist file or the `SUBSTRATE_AUTHOR_OVERRIDE=1` environment
  override is set. Identity matching is exact-line against
  `git config user.email` and `git config user.name`. The hook
  emits a multi-line error to stderr explaining which substrate
  paths are affected and how to authorize the commit. Consumers
  copy this file out of `governance-commons/reference/hooks/` to
  their own `.githooks/pre-commit` (or install via the pre-commit
  framework) and author their own `.substrate-authors` file.

- `governance-commons/reference/hooks/substrate-authors.example`
  (an illustrative allowlist file). Documents the
  `.substrate-authors` format the hook expects: one identity per
  line (email or git user.name), blank lines and `#` comments
  ignored. Consumers copy this to their repo root as
  `.substrate-authors` and edit to list authorized identities.

Substrate-internal reference template:

- `governance-commons/reference/templates/substrate-coverage-matrix.md`
  (256 lines). Reference template for the consumer-side
  substrate-coverage matrix artifact. Demonstrates the three-section
  structure (feature header, per-rule matrix, per-L3 ADR list)
  consumers use to map "this feature's in-scope substrate rules"
  to "this feature's implementation tasks and review obligations."
  Includes a worked example for a sample feature
  ("password-reset-via-email-otp") covering 12 substrate rules
  across 7 catalogs with 1 L3 ADR. The substrate's contract is on
  the information captured; consumers select Markdown, CSV, or
  issue-tracker-backed forms.

Substrate-published audit documentation:

- `governance-commons/docs/registry-id-audit-2026-05.md` (575
  lines). First systematic audit of the substrate's L1 binding
  registry references against the live `semgrep/semgrep-rules`
  upstream tree. Audited substrate version 0.5.0 against upstream
  develop branch at SHA `d04ae90ca63c7719a4a679485b2adce9b34599b5`
  (2026-05-20). Method: substrate-internal Python tooling that
  parses each binding's `referenced-rules` list, fetches the
  upstream tree via the GitHub git-trees API in one request,
  resolves candidate paths from each registry-id, fetches the
  resolved file via `raw.githubusercontent.com` to verify the
  expected rule id is present, and reports per-binding and
  per-language alive/mismatch/dead/dead-declared counts. Headline
  finding: of the substrate's 306 registry references, 45 (15%)
  are verifiably alive, 7 (2%) have file-lives-but-rule-id-absent
  mismatches, 247 (81%) are dead, 7 (2%) are dead-declared. 23 of
  the 47 bindings have zero live references. Concern-level
  pattern: secrets-management and authentication achieve
  reasonable upstream coverage; authorization, logging,
  observability, cost-model-selection, testing-strategy, and
  several supply-chain bindings have minimal upstream community-
  rule coverage at L1. The audit publishes four remediation tiers
  (drift-driven binding updates, aspirational-binding rewrites,
  secret-detection coverage expansion, Section 8 authoring-
  convention amendment) plus a fifth tier (quarterly audit cadence
  with substrate-published tooling scheduled for M8). Substrate
  L2 review checklists and L3 decision frameworks are unaffected
  by the audit; they remain at full stable lifecycle.

### Changed

- `governance-commons/FUTURE.md` catch-up. Four entries closed,
  three new entries added; net file grows from 484 to 620 lines.
  Closed entries: SAST tool selection (OpenGrep substrate-default
  per Section 10 settled decision 19); L1 binding schema (static-
  analysis-binding schema 0.3.0 stable since M2 close per Section
  10 settled decision 22); Pre-commit hook for substrate write-
  isolation (landed in this session); Substrate validation wrapper
  script (`scripts/validate-all.sh` shipped since M1 close).
  Added entries: AI safety / agentic AI concern catalog (strongest
  signal from M3 Session 2a coverage-gap records; candidate M5
  scope amendment for the planned `responsible-ai` concern's depth
  upgrade to high and possible split into adjacent `agentic-
  systems` concern); Registry-ID drift remediation (four-tier
  follow-up surfaced by the audit; Tier 1 mechanical fix half-
  session, Tier 2 aspirational-binding rewrites 2-6 sessions,
  Tier 3 secret-detection coverage expansion one focused session,
  Tier 4 authoring-convention amendment bundled); Registry-ID
  audit tooling skeleton (publish the Python extractor-and-
  verifier pattern as substrate-maintained tooling at M8 per the
  Tier D folder structure plan).

### Substrate-author notes

This session is the smallest in the M3 milestone arc by content
weight (the substrate's catalog/MADR/profile/schema inventory is
unchanged) but produces two artifacts with substantive substrate-
external impact: the pre-commit hook makes Charter Article II
enforceable at the consumer's commit boundary, and the registry-ID
audit document is the substrate's first formal honesty audit of
its own L1 enforcement claims. The audit specifically declines to
remediate the bindings in this session; remediation is downstream
substrate-author work scheduled at the substrate-author's
discretion across one or more later sessions.

The coverage-matrix template completes the substrate's reference
scaffold surface. Combined with the M3 Session 2b reference manifest
+ 3 agent prompts + CI workflow, the substrate now publishes a
complete reference implementation of the five-obligation consumer
scaffold contract specified in `spec/consumer-scaffold.md`.

Section 7 discipline rule 17 (COMMIT-GUIDE shell discipline) is
honored in the M3 Session 3 COMMIT-GUIDE: every command block
resolving a substrate-relative path opens with `cd "$REPO_ROOT"`
on its own line; no bare `python3 -c "import <third-party>"`
invocations; preference for existing validators and
schema-specific `check-jsonschema` calls over bespoke inline
checks.

Remaining M3 work: Session 4 (L2 binding format refactor across all
11 concerns; markdown-wrapped-YAML to MADR-pattern YAML frontmatter
+ markdown body); Session 5 (M3 close consolidation; all M3 draft
content promoted to stable; VERSION 0.5.0 -> 0.6.0).

## M3 Session 2b (released in [0.6.0])

**M3 Session 2b: substrate-internal reference scaffold + structural
refactor.** Two coupled deliverables in a single session:

1. **Substrate-internal location for all reference files.** The
   Session 1 reference manifest moves from the repository root into
   the substrate at `governance-commons/reference/manifest/`. The
   four reference files from this session (3 agent prompts + 1 CI
   workflow) are authored directly at
   `governance-commons/reference/agents/` and
   `governance-commons/reference/workflows/` rather than at the
   consumer-side locations (`.specify/templates/agents/` and
   `.github/workflows/`) that Session 1's `consumer-scaffold.md`
   Section 5 had proposed.

2. **Reference scaffold completed.** With the 3 reference agent
   prompts and 1 reference CI workflow now landed (alongside the
   reference manifest), the consumer-scaffold contract authored
   in Session 1 now has demonstrable reference implementations
   across all five obligations.

The structural refactor reflects the substrate's isolation
invariant: everything inside `governance-commons/` is substrate-
published content (whether schema-validated rules, MADRs, mappings,
or illustrative references); everything outside is the consumer's
own integration surface. Reference files are illustrative substrate
content, so they live inside the substrate. Consumers integrate by
copying out of `governance-commons/reference/` into their own
integration locations (substrate-recommended: repo root for the
manifest, `.specify/templates/agents/` for prompts, `.github/
workflows/` for the CI workflow); the substrate does not place
files at consumer-side locations on the consumer's behalf.

### Added

Substrate-internal reference scaffold (under
`governance-commons/reference/`; illustrative; no lifecycle
metadata; substrate-author Article VII compatibility-with-consumers
obligation governs change discipline):

- `governance-commons/reference/manifest/governance-manifest.yaml`
  (moved from repository root, where M3 Session 1 originally
  placed it). Validates clean against
  `governance-commons/schemas/manifest.schema.json` at new
  location. Content unchanged from Session 1.

- `governance-commons/reference/agents/threat-modeling-agent.md`
  (~225 lines). Reference template for the post-spec-drafting
  checkpoint. Demonstrates all 9 substrate-published agent prompt
  slots from consumer-scaffold.md Section 3.2. Specifies the
  consultation-events fenced-block output discipline. Honest-
  coverage-gap discipline reminder referencing specific gap entries
  in the 4 M3 Session 2a mappings (LLM01, LLM06, LLM09 in
  owasp-llm; ASI01, ASI06, ASI09 in owasp-asi; AML.T0043,
  AML.T0054, AML.T0059 in mitre-atlas; STRIDE-R, STRIDE-D in
  stride). Constitution slice per substrate-recommended default
  for threat-modeling-agent: Articles V, VI.

- `governance-commons/reference/agents/implementation-planning-agent.md`
  (~200 lines). Reference for the post-design checkpoint. Same
  9-slot pattern. Specifies cross-concern dependency awareness
  (one implementation choice frequently satisfies rules across
  multiple concerns; events should record all satisfactions).
  Constitution slice: Articles II, V, VI.

- `governance-commons/reference/agents/code-review-agent.md`
  (~200 lines). Reference for the post-implementation checkpoint.
  Same 9-slot pattern. Specifies verification triad of per-concern
  L2 + plan-commitment + threat-model coverage. Specifies
  closure-claim discipline (FAIL findings do not auto-close in the
  agent's own output; closure happens via subsequent
  consultation). Constitution slice: Articles II, V, VI.

- `governance-commons/reference/workflows/governance-commons-gate.yml`
  (~295 lines). Reference GitHub Actions workflow implementing the
  8-step CI contract from consumer-scaffold.md Section 4.3. Three
  jobs: manifest-validation (Steps 1-3), static-analysis (Step 4,
  OpenGrep as substrate-default engine per HANDOFF Section 10
  settled decision 19), evidence-validation (Steps 5-8, JSONL
  events + manifest cross-check via inline Python). Workflow
  consults the consumer's active manifest at repo root (where the
  consumer copies the reference manifest to); the workflow itself
  is the substrate's reference example, consumers copy it to their
  own `.github/workflows/` (or CI-equivalent path) and adapt.

### Removed

- `governance-manifest.yaml` at the repository root (the Session 1
  reference manifest, now relocated to
  `governance-commons/reference/manifest/governance-manifest.yaml`).
  The substrate no longer places reference files at consumer-side
  locations.

### Changed

- `governance-commons/spec/consumer-scaffold.md` Section 5 rewritten
  to document the substrate-internal reference location convention.
  The section now explains that reference files live inside the
  substrate at `governance-commons/reference/` and that consumers
  copy them out to their own integration locations. Sections 1-4
  (the substrate-published contracts) are unchanged. The spec
  document remains at lifecycle-status draft; promotion to stable
  scheduled for M3 close consolidation per Path A.

### Substrate-author notes

The structural refactor was identified mid-session as a substrate-
isolation correctness issue: M3 Session 1's choice to place the
reference manifest at repo root and the (not-yet-landed) plan to
place agent prompts and CI workflow at `.specify/templates/agents/`
and `.github/workflows/` created a substrate-boundary ambiguity.
Resolving the ambiguity by moving all reference content inside
`governance-commons/reference/` sharpens the substrate isolation
invariant: every substrate-published file is now under
`governance-commons/`, full stop.

The decision is recorded as a Section 10 settled decision in
HANDOFF (substrate-internal reference location convention) and is
the authoritative pattern for any future substrate-published
reference content (e.g., a future reference pre-commit hook will
land at `governance-commons/reference/hooks/pre-commit`, not at
`.githooks/pre-commit`).

With Sessions 1, 2a, and 2b now landed (and the M3 Session 1
choice retroactively corrected by the refactor here), M3 has
delivered the substrate-published contract, the substrate-side
cross-taxonomy bridges, and the substrate-internal reference
implementations. Remaining M3 work: Session 3 (pre-commit hook +
registry-ID audit + substrate-coverage matrix template +
FUTURE.md catch-up), Session 4 (L2 binding format refactor across
all 11 concerns), Session 5 (M3 close consolidation: all M3 draft
content promoted to stable; VERSION 0.5.0 -> 0.6.0).

## M3 Session 2a (released in [0.6.0])

**M3 Session 2a: threat catalog mappings (substrate-side).** Scope-
split delivery of the original M3 Session 2 plan after three prior
sessions ran out of context-window budget before bundling. Session
2a delivers only the substrate-side, schema-validated content: 4
threat-catalog mappings under `governance-commons/mappings/`. The
consumer-side reference files (3 agent prompts + 1 CI workflow)
defer to Session 2b.

All M3 Session 2a artifacts enter at lifecycle-status draft;
promotion to stable deferred to M3 close per the Path A precedent
established at M1 close and M2 close (Section 10 settled decision
21).

The 4 mappings exercise the mapping schema for the first time
since its M0 authoring; the schema accommodated all 4 mappings
without amendment per pre-flight Step 4 (verified in prior session
turns that had access to the live schema). One structural pattern
applied uniformly: the `target-catalog` field requires a single
`catalog-id` string, so threat-to-concerns mappings spanning all
11 concern catalogs use the collective `catalog-id: "concerns"`
with the methodology field recording the umbrella scope, and
qualified rule IDs in `target-rule` (e.g.,
`authorization.AUTHZ-L1-001`) provide specific cross-catalog
references.

### Added

Substrate-side threat catalog mappings (lifecycle-status draft;
commons-version 0.5.0; under `governance-commons/mappings/`):

- `mappings/owasp-llm-to-concerns.oscal.yaml` (362 lines; 22
  relations + 3 coverage-gap records). Maps OWASP LLM Top 10
  risks LLM01-LLM10 to substrate concern rules across input-
  validation, authorization, logging, secrets-management,
  observability, supply-chain, dependency-management, error-
  handling, testing-strategy, and cost-model-selection.
  Coverage-gap records flag LLM01 (LLM-specific prompt
  injection), LLM06 (excessive agency), and LLM09 (misinformation)
  as partial coverage pending future AI safety concern catalog.
  UUID: `8de2278f-897a-437c-b761-6ad8466e8a13`.

- `mappings/owasp-asi-to-concerns.oscal.yaml` (298 lines; 18
  relations + 3 coverage-gap records). Maps OWASP Agentic ASI
  2026 risks ASI01-ASI10 to substrate concern rules. Coverage-
  gap records flag ASI01 (goal hijacking), ASI06 (rogue agents),
  and ASI09 (inadequate human oversight) as partial coverage
  pending future agentic AI concern catalog. UUID:
  `04a9a3b2-db32-4362-a427-8ae1cf90d6ae`.

- `mappings/mitre-atlas-to-concerns.oscal.yaml` (334 lines; 19
  relations + 3 coverage-gap records). Maps 10 selected MITRE
  ATLAS techniques (AML.T0040, T0043, T0048, T0051, T0052,
  T0053, T0054, T0055, T0057, T0059) to substrate concern rules.
  Coverage-gap records flag T0043 (adversarial data crafting),
  T0054 (LLM jailbreak), and T0059 (erode ML model integrity)
  as partial coverage. UUID:
  `27fe6fea-e4f3-4189-ab82-b455836d16cb`.

- `mappings/stride-to-concerns.oscal.yaml` (321 lines; 26
  relations + 2 coverage-gap records). Maps all 6 STRIDE
  categories (Spoofing, Tampering, Repudiation, Information
  Disclosure, Denial of Service, Elevation of Privilege) to
  substrate concern rules. Strongest coverage of the 4 mappings:
  STRIDE categories correspond closely to security architectural
  concerns the substrate has at full depth. Coverage-gap records
  flag STRIDE-R (log integrity) and STRIDE-D (rate limiting /
  circuit breaking) as partial coverage. UUID:
  `03af42a3-a735-477a-ac8e-b7c3ce4ae0fc`.

### Substrate-author notes

A recurring theme across the coverage-gaps: substrate addresses
architectural fundamentals (input validation, authorization,
logging, supply chain integrity) but lacks LLM-specific, agentic-
specific, and AI-safety-specific rules. The substrate-author can
either accept this as the substrate's intentional scope boundary
(the current concerns are general-purpose) or treat it as a signal
for a future AI safety / responsible AI / agentic AI concern
catalog in M4 or later. The signal is now recorded across 11
coverage-gap entries across the 4 mappings; the recommended-action
fields consistently point to a future agentic / AI safety concern
catalog.

Session 2b will land the 3 reference agent prompts (under
`.specify/templates/agents/`) and the reference CI workflow (under
`.github/workflows/`), which collectively exercise the consumer-
scaffold.md Section 3 (agent prompt injection contract) and
Section 4 (CI workflow contract) end-to-end. Session 2b is bounded
to consumer-side reference content only; the substrate-side
mapping content lands with this Session 2a commit.

### Validation note

The 4 mapping files were authored against the structure validated
in prior session turns where the live mapping schema was
accessible: `check-jsonschema --schemafile
governance-commons/schemas/mapping.schema.json
governance-commons/mappings/*.oscal.yaml` produced
`ok -- validation done` for each file. The substrate-author should
re-run that validation on apply per the COMMIT-GUIDE pre-flight
section before committing.

## M3 Session 1 (released in [0.6.0])

**M3 Session 1: consumer scaffold contract.** First M3-phase content
addition. M3 (Consumer scaffold + integrity, the major inflection
per HANDOFF Section 4) authors the substrate-published normative
contract for end-to-end consumer integration. This session lands
the unifying spec doc that brings together the previously-isolated
manifest, evidence, and consumption-contract pieces, plus the two
topics not previously covered at spec depth: agent prompt
injection patterns and CI workflow integration. The session also
lands the substrate's first complete reference manifest instance,
demonstrating all 47 L1 substrate rules across a four-checkpoint
build-time AI coding framework integration.

All M3 Session 1 artifacts enter at lifecycle-status draft;
promotion to stable is deferred to M3 close per the Path A
precedent established at M1 close and reinforced at M2 close
(Section 10 settled decision 21).

Pre-session-0 substrate-scope.md amendment (Q23 resolution at
session open per substrate-recommended path b, M2 Session 5
precedent): `consumer-scaffold.md` added to Cross-references
section, registering it as a Tier 1 spec doc. No Tier 1 listing
change required (Tier 1 already includes `spec/*.md` generically);
no Categorically-outside change required.

### Added

Substrate spec doc (lifecycle-status draft; commons-version 0.5.0):

- `spec/consumer-scaffold.md` (594 lines, 8 sections + preamble).
  Section 1 enumerates the five obligations a consumer scaffold
  satisfies (manifest, agent prompts, constitution slicing,
  evidence emission, closure verification). Section 2 maps each
  obligation to its existing substrate spec doc, identifying that
  three obligations (manifest, evidence, closure) already had
  spec coverage and two obligations (agent prompts, CI workflow
  integration) did not. Section 3 specifies the agent prompt
  injection contract: the eight prompt slots (`commons-version`,
  `profile`, `checkpoint-name`, `consults-catalogs`,
  `consults-rules`, `consults-mappings`,
  `consults-decision-frameworks`, `constitution-articles`,
  `artifact-under-review`), the agent's required structured
  output shape (consultation-event JSON conforming to
  `consultation-event.schema.json`), the substrate-recommended
  constitution-slicing defaults per consulter type (threat-
  modeling-agent, code-review-agent, implementation-planning-
  agent, architecture-review-agent, policy-decision-point), and
  the substrate-recommended 30K-50K hard context cap per
  invocation. Section 4 specifies the CI workflow integration
  contract: the eight-step sequence (discover manifest, validate
  manifest, pin commons version, run static-analysis bindings
  for in-scope checkpoints, collect consultation events,
  validate consultation events, cross-check events against
  manifest contract, block or pass), the substrate-default
  static-analysis engine (OpenGrep per Section 10 decision 19),
  pre-commit hook integration scope (L1 mechanical only at
  pre-commit; L2/L3 at workflow checkpoints), and what the
  section does not specify (CI provider, branching strategy,
  authentication mechanism, event routing, performance
  characteristics). Section 5 documents reference implementation
  pointers (governance-manifest.yaml at repo root in this
  session; agent prompt patterns and CI workflow example
  deferred to M3 Session 2). Section 6 bounds the document (not
  a runbook, not a tutorial, not an implementation, no
  duplication of existing spec docs). Sections 7 and 8 cover
  versioning and cross-references.

Reference manifest (lifecycle inherited from manifest schema
which is at first-stable; the manifest instance does not carry its
own lifecycle-status field):

- `governance-manifest.yaml` at repository root. Validates clean
  against `governance-commons/schemas/manifest.schema.json`.
  Pinned to commons-version 0.5.0 and profile
  production-grade-baseline. Demonstrates four checkpoints:
  - **post-spec-drafting** consulter `threat-modeling-agent`:
    consults 3 threat catalogs (LLM Top 10, Agentic ASI,
    STRIDE) + 4 concern catalogs (authentication, authorization,
    input-validation, supply-chain) + 4 L3 MADRs. Blocking,
    report-and-block findings.
  - **post-design** consulter `implementation-planning-agent`:
    consults 11 concern catalogs (full M1+M2 set) + 6 L3 MADRs.
    Non-blocking, report-only findings.
  - **post-implementation** consulter `code-review-agent`:
    consults 10 concern catalogs (excluding cost-model-selection
    which is design-phase). Blocking, report-and-block findings.
  - **pre-commit** consulter `opengrep-static-analysis`:
    consults all 47 L1 substrate rules by ID across 11 concerns.
    Blocking, report-and-block findings.
  - Each AI-agent checkpoint carries an
    `x-constitution-articles` consumer extension demonstrating
    the constitution-slicing slot from consumer-scaffold.md
    Section 3.4.
  - Evidence medium: jsonl-append-only at
    `.governance-commons/consultation-events.jsonl` with
    append-only-filesystem integrity.

### Changed

- `spec/substrate-scope.md` Cross-references section: added
  `../spec/consumer-scaffold.md` reference registering the new
  spec doc as a Tier 1 substrate artifact. Editorial amendment
  per spec-doc versioning convention; no material change to
  substrate-scope.md's content scoping decisions.

### Open Questions resolved at session open

- **Open Question 21:** M3 spec-doc candidates. RESOLVED via
  substrate-author confirmation at M3 Session 1 open. Path:
  author `consumer-scaffold.md` as new spec doc unifying
  manifest-format.md, consultation-evidence.md, and consumption-
  contract.md, plus adding agent prompt patterns (Section 3)
  and CI workflow integration (Section 4) as new normative
  content. Existing spec docs not amended in this session;
  cross-references in `consumer-scaffold.md` Section 8 point to
  them.
- **Open Question 23:** M3 substrate-scope.md amendment
  sequencing. RESOLVED via substrate-author confirmation at M3
  Session 1 open. Path (b) selected per M2 Session 5 precedent:
  amendment landed as pre-session-0 step within M3 Session 1,
  not as a discrete pre-session amendment commit. The amendment
  added `consumer-scaffold.md` to substrate-scope.md Cross-
  references; no other substrate-scope.md sections required
  change.

### Validation

All four substrate validators clean post-authoring:

- `bash scripts/validate-catalogs.sh`: 11 passed
- `bash scripts/validate-profiles.sh`: 1 passed
- `bash scripts/validate-static-analysis-bindings.sh`: 47 passed
- `bash scripts/validate-decision-frameworks.sh`: 12 passed
- Reference manifest validates clean against manifest.schema.json:
  `check-jsonschema --schemafile governance-commons/schemas/manifest.schema.json governance-manifest.yaml`
  produces `ok -- validation done`

### Substrate-author notes

This is the first M3 authoring session. The Path A discipline
applies: artifacts land at draft within the session and consolidate
to stable at M3 close after cooling-off. The two new normative
sections (agent prompt injection in Section 3 of
consumer-scaffold.md, CI workflow integration in Section 4)
exercise the substrate-published-contract surface in a way no
prior substrate session has. The substrate-author should validate
the contracts against M3 Session 2 reference agent prompt and CI
workflow authoring before treating the contracts as fully exercised.

## [0.5.0] - 2026-05-26

**M2 consolidation phase (Path A): common-coverage stable promotion.**
All 5 M2 draft catalogs and their paired MADRs promoted from draft to
stable under Charter Section 2.4.1 solo-author attestation. Static-
analysis-binding schema promoted from draft (0.3.0) to stable
alongside its consuming bindings per the Path A schema-rides-content
precedent established at M1 close. M2 closes; M3 (consumer scaffold +
integrity inflection) authoring is unblocked.

Per Charter Section 2.4.1, every artifact promoted in this version
honored a cooling-off interval of one calendar day or more between
its authoring date and this attestation date. The latest M2 draft
authoring (testing-strategy, 2026-05-25) satisfies cooling-off
against this 2026-05-26 attestation; all earlier-authored drafts
satisfy cooling-off by larger intervals. Section 2.4 validation
criteria applied per artifact: rule intent clear, examples
demonstrate the rule, severity and layer assignments defensible,
provenance complete, no conflict with existing commons content.

### Promoted

Concern catalogs (lifecycle-status draft -> stable; catalog-status
in-development -> feature-complete; version 0.1.0 -> 1.0.0; per-rule
lifecycle-status: draft -> stable on every rule; entered-stable-at
added on every rule; catalog-attestation prop added with Charter
Section 2.4.1 remarks; substrate-version 0.4.0 -> 0.5.0):

- `catalogs/concerns/authorization.oscal.yaml` (12 rules; draft
  authored 2026-05-22 M2 Session 1)
- `catalogs/concerns/input-validation.oscal.yaml` (12 rules; draft
  authored 2026-05-23 M2 Session 2)
- `catalogs/concerns/error-handling.oscal.yaml` (10 rules; draft
  authored 2026-05-24 M2 Session 3)
- `catalogs/concerns/testing-strategy.oscal.yaml` (8 rules; draft
  authored 2026-05-25 M2 Session 4)
- `catalogs/concerns/supply-chain.oscal.yaml` (12 rules; draft
  authored 2026-05-23 M2 Session 5)

Decision-framework MADRs (frontmatter lifecycle-status draft ->
stable; reviewer: myoung-self-attested; reviewed: 2026-05-26;
attestation-mechanism block added per M1 precedent; commons-version
0.4.0 -> 0.5.0; framework-version 0.1.0 -> 1.0.0):

- `decision-frameworks/authorization-model-selection.madr.md`
- `decision-frameworks/input-validation-strategy.madr.md`
- `decision-frameworks/error-handling-strategy.madr.md`
- `decision-frameworks/testing-strategy.madr.md`
- `decision-frameworks/supply-chain-integrity-strategy.madr.md`

Schema (x-governance-commons.lifecycle-status draft -> stable;
commons-version 0.4.0 -> 0.5.0; last-modified bumped to 2026-05-26;
ai-assistance note appended documenting the M2 close consolidation;
schema-version remains 0.3.0, the promotion is lifecycle status only
with no schema content change):

- `schemas/static-analysis-binding.schema.json` (variant 6
  `attestation-orchestration` promoted to stable alongside content
  per the Path A schema-rides-content M1 close precedent; the
  promotion is exercised by SUPPLY-L1-002 SLSA provenance
  verification and SUPPLY-L1-003 signature verification, the first
  substrate consumers of variant 6)

### Changed

- `VERSION` 0.4.0 -> 0.5.0. Minor bump per `spec/rule-lifecycle.md`
  stable-promotion guidance: M2 close consolidation covers 5 catalogs
  + 5 paired MADRs + 1 schema variant promotion + 1 schema lifecycle
  promotion all reaching stable in one consolidation event; the
  minor bump groups them atomically.
- `profiles/production-grade-baseline.oscal.yaml` last-modified
  bumped to 2026-05-26T00:00:00Z. No selection changes; the
  rule-selection-count of 106 from M2 Session 5 already reflects all
  M2 concerns; commons-version remains 1.0.0 (first-stable from M1
  close); only the timestamp reflects the M2 close attestation event.
- Tool-bindings (47 static-analysis bindings, 59 review checklists,
  47 test templates) inherit lifecycle status from their parent
  catalog rules per substrate convention; no field-level edits to
  binding files were required for M2 close (resolves Open Question
  26 below).

### M2 milestone closure note

M2 (Common substrate coverage) closes with this consolidation. The
M2 common-coverage authoring (Sessions 1 through 5) produced 5
concern catalogs covering authorization, input-validation, error-
handling, testing-strategy, and supply-chain. Combined with the
M1 universal floor (5 catalogs) and the M0 authentication catalog,
the substrate now covers 11 concerns at stable lifecycle. The M2
capability statement is now realized at commitment grade: the
substrate covers concerns most production projects need (web apps,
infrastructure, AI/ML systems) and the content is stable per
Charter Article IV immutability semantics.

Per HANDOFF Section 4, M3 (Consumer scaffold + integrity) is the
next milestone and the major inflection: M3 produces the system
that consumes the catalogs M1 and M2 produced. M3 scope covers a
consumer-side governance manifest, agent prompt patterns, a CI
workflow example invoking OpenGrep with substrate bindings, threat
catalog mappings (OWASP LLM Top 10, OWASP Agentic ASI, MITRE
ATLAS, STRIDE -> concerns), an L2 binding format refactor across
all 11 concerns, and a pre-commit hook for substrate write-
isolation. M3 work starts at substrate version 0.5.0 and will
land at draft until M3's own consolidation phase bumps to 0.6.0.

### Open Questions closed by this version

- **Open Question 24:** Variant 6 schema promotion at M2 close
  (Path A scope confirmation). Closed by promoting schema 0.3.0
  draft -> stable in this consolidation, alongside the 5 catalog
  promotions, per the M1 close Path A precedent. Variant 6
  attestation-orchestration is now stable; SUPPLY-L1-002 and
  SUPPLY-L1-003 are the consuming bindings.
- **Open Question 26:** Promotion semantics for review checklists
  and test templates at M2 close. Closed by confirming parent-
  concern promotion is sufficient: the 59 review checklists and
  47 test templates inherit lifecycle-status from their parent
  catalog rules without field-level edits. No checklist or test-
  template files are modified in this consolidation commit.

## M2 Session 5 (released in [0.5.0])

**M2 Session 5: supply-chain concern authoring.** Fifth M2-phase
content addition; follows M2 Session 1 (authorization, 2026-05-22),
M2 Session 2 (input-validation, 2026-05-23), M2 Session 3 (error-
handling, 2026-05-24), and M2 Session 4 (testing-strategy,
2026-05-25). The supply-chain concern is the substrate's eleventh
concern, anchored to SLSA v1.1 (build-track levels and threat
overview), NIST SP 800-218 SSDF v1.1 (Secure Software Development
Framework), NIST SP 800-161r1 (Cybersecurity Supply Chain Risk
Management Practices), OWASP ASVS v5.0.0 Chapter 14 (Configuration),
OWASP Top 10 CI/CD Security Risks (2022), EU Cyber Resilience Act
(Regulation 2024/2847), in-toto attestation framework, Sigstore
(cosign, Fulcio, Rekor), and the CycloneDX 1.6 and SPDX 2.3
SBOM specifications. All artifacts enter at lifecycle-status
draft; promotion to stable is deferred to M2 close per the
Path A precedent.

Regulatory currency note: EO 14028 remains in force (EO 14306 of
June 2025 amended EO 14144 without rescinding EO 14028). OMB
M-26-05 of February 2026 rescinded M-22-18 and M-23-16, ending
the universal federal SSDF self-attestation collection mandate;
federal agencies retain risk-based discretion and NIST SSDF
remains a substrate-recommended technical framework. EU CRA
Regulation 2024/2847 is the active enforceable regulatory driver:
reporting obligations activate 2026-09-11, full enforcement
2027-12-11. The substrate's L3 ADR template surfaces CRA
in-scope determination as a Section 1 (Context) requirement.

Schema 0.3.0 variant 6 attestation-orchestration: this session
added a sixth `binding-type` variant to the static-analysis-
binding schema to model attestation-verification semantics
(provenance verification, signature verification, transparency-
log lookup). The variant is structurally distinct from variant 5
scanner-orchestration: verifiers consume signed attestations and
emit pass/fail plus a policy-evaluation record; scanners consume
advisory databases and emit graded findings. SUPPLY-L1-002
(SLSA provenance verification) and SUPPLY-L1-003 (signature
verification) are the first substrate consumers of variant 6.
The schema was bumped from 0.2.0 to 0.3.0 with lifecycle-status
draft per Path A precedent (M2 Session 1's variant 4 addition,
M2 Session 2's variant 5 addition).

Supply-chain is a high-depth concern per spec/substrate-scope.md
(10 to 15 rules target). This authoring lands mid-band (12 rules:
5 L1 + 6 L2 + 1 L3), matching the substrate-author's instruction
recorded at session opening.

### Added

Concern catalog (12 rules; lifecycle-status draft; catalog-status
in-development; version 0.1.0):

- `catalogs/concerns/supply-chain.oscal.yaml` (5 L1 mechanical,
  6 L2 semantic, 1 L3 judgmental):
  - SUPPLY-L1-001 digest-pinned-artifacts (severity: high)
  - SUPPLY-L1-002 slsa-provenance-verification (severity:
    critical; first variant-6 binding consumer)
  - SUPPLY-L1-003 signature-verification (severity: critical;
    second variant-6 binding consumer)
  - SUPPLY-L1-004 sbom-presence-and-validity (severity: high)
  - SUPPLY-L1-005 no-remote-execution-in-build (severity:
    critical)
  - SUPPLY-L2-001 dependency-vetting (severity: high)
  - SUPPLY-L2-002 vulnerability-disclosure-response (severity:
    high; EU CRA 24-hour ENISA path)
  - SUPPLY-L2-003 critical-dependency-audit (severity: medium;
    tier-1 quarterly, tier-2 semi-annual, tier-3 annual)
  - SUPPLY-L2-004 signed-commit-and-protected-branch (severity:
    high)
  - SUPPLY-L2-005 build-environment-isolation (severity: high)
  - SUPPLY-L2-006 attestation-and-sbom-retention (severity:
    medium; baseline 3yr / strict 7yr / loose 1yr)
  - SUPPLY-L3-001 supply-chain-integrity-strategy (severity:
    high; pairs with MADR)

Tool bindings (19 paired with the catalog rules):

- `tool-bindings/static-analysis/` — 5 L1 bindings:
  - `supply-l1-001-digest-pinned-artifacts.yaml` (variant 4
    multi-ecosystem-orchestration; 12 ecosystem-detections
    covering docker images, kubernetes manifests, github
    actions, terraform providers and modules, helm charts,
    npm, pypi, go modules, maven, cargo, gem, oci registries)
  - `supply-l1-002-slsa-provenance-verification.yaml` (variant 6
    attestation-orchestration; first substrate demonstration)
  - `supply-l1-003-signature-verification.yaml` (variant 6
    attestation-orchestration)
  - `supply-l1-004-sbom-presence-and-validity.yaml` (variant 3
    registry-reference-with-complementary-tools; syft as
    substrate-default generator, cyclonedx-cli and spdx-tools
    as validators, Dependency-Track as substrate-recommended
    retention surface)
  - `supply-l1-005-no-remote-execution-in-build.yaml` (variant 1
    static-analysis with semgrep-pattern-v1; covers curl-pipe-
    shell, eval-of-fetched-payload, wget-pipe-shell, irm-pipe-
    iex, python exec-of-fetched-code, nodejs eval-of-fetched-
    payload patterns across bash, dockerfile, yaml CI workflows,
    powershell, python, javascript)

- `tool-bindings/review-checklist/` — 7 review checklists (6 L2
  plus 1 L3, 7-10 review questions each, following the
  test-l2-* / test-l3-001 precedent from M2 Session 4):
  - `supply-l2-001-dependency-vetting.md`
  - `supply-l2-002-vulnerability-disclosure-response.md`
  - `supply-l2-003-critical-dependency-audit.md`
  - `supply-l2-004-signed-commit-and-protected-branch.md`
  - `supply-l2-005-build-environment-isolation.md`
  - `supply-l2-006-attestation-and-sbom-retention.md`
  - `supply-l3-001-supply-chain-integrity-strategy.md`

- `tool-bindings/test-template/` — 6 L2 test templates
  (framework-agnostic verification scenarios; CI gate shape):
  - `supply-l2-001-dependency-vetting.md`
  - `supply-l2-002-vulnerability-disclosure-response.md`
  - `supply-l2-003-critical-dependency-audit.md`
  - `supply-l2-004-signed-commit-and-protected-branch.md`
  - `supply-l2-005-build-environment-isolation.md`
  - `supply-l2-006-attestation-and-sbom-retention.md`

Decision framework (1 paired with SUPPLY-L3-001):

- `decision-frameworks/supply-chain-integrity-strategy.madr.md`
  — Portfolio-of-decisions structure (8 sub-decisions, not
  single option pick), departing from the single-option
  precedent of authorization-model-selection and matching the
  multi-decision shape of testing-strategy.madr.md. Eight
  sub-decisions analyzed: (1) SLSA Build Level target with
  options L1/L2/L3 keyed to profile; (2) attestation scope and
  predicate-type policy with first-party-only / first-party-
  plus-tier-1 / all-production-artifacts options; (3) SBOM
  cadence, format (CycloneDX 1.6 default, SPDX 2.3 accepted),
  and storage (OCI referrers default, Dependency-Track and
  S3-versioned as substrate-recommended additional surfaces);
  (4) signing identity policy with OIDC-bound keyless (default),
  long-lived key with rotation, and enterprise PKI options;
  (5) transparency log selection (public-good Rekor default,
  self-hosted, substrate-accepted equivalents); (6) retention
  horizon (3yr baseline / 7yr strict / 1yr loose / indefinite);
  (7) exemption discipline (time-bounded with quarterly review
  default); (8) review cadence (annual default plus
  regulatory-change, profile-transition, and post-incident
  triggers, including explicit CRA full-enforcement trigger
  2027-12-11). Nine decision drivers (consumer threat model,
  regulatory exposure, engineering investment tolerance,
  upstream ecosystem reality, downstream commitments, build-
  platform sovereignty, incident-response capability,
  transition discipline maturity). Anti-patterns the substrate
  rejects: strategy without documented sub-decisions; ADR
  inconsistent with operational reality; indefinite exemption
  discipline; absent regulatory analysis.

Examples (24 files, 12 paired good/anti-pattern pairs):

- `examples/supply-chain/` — paired good/anti-pattern examples
  for all 12 substrate rules. Each pair illustrates the
  substrate-aligned pattern (good) and the substrate-rejected
  forms (anti-pattern). L1 examples concrete code patterns
  (Dockerfile FROM with digest pin, GitHub Actions verification
  gate with slsa-verifier, cosign verification with explicit
  signer identity, multi-stage Dockerfile with SBOM in final
  image, checksum-verified binary download alternative to
  curl-pipe-shell). L2 examples concrete artifacts (vetting
  artifact at adoption, vulnerability-response runbook with
  EU CRA section, tiered dependency inventory, GitHub branch
  protection configuration, hermetic-build GitHub Actions
  workflow, OCI registry referrers-attached retention with
  Dependency-Track query surface). L3 example concrete ADR
  with all 8 sub-decisions documented.

Profile updates:

- `profiles/production-grade-baseline.oscal.yaml`:
  - `last-modified`: `2026-05-25T00:00:00Z` → `2026-05-23T00:00:00Z`
  - `rule-selection-count`: 94 → 106
  - Header comment updated to include supply-chain in the M2
    inventory and to note the M2 Session 5 addition.
  - 12 imports added for supply-chain rules.
  - 12 alters added for supply-chain rules with
    `profile-selection-rationale`, `profile-severity-override`
    (matching catalog defaults), and `profile-ai-assistance`
    properties.
  - Back-matter resource added for the supply-chain catalog
    (UUID `d0e1f2a3-b4c5-6d7e-8f9a-0b1c2d3e4f5b`).

### Changed

Schema and spec updates supporting the supply-chain authoring:

- `schemas/static-analysis-binding.schema.json`:
  - `schema-version`: 0.2.0 → 0.3.0
  - `lifecycle-status`: stable → draft (Path A pattern)
  - Added variant 6 `attestation-orchestration` to the spec
    oneOf with required fields `[binding-type, description,
    primary-verifiers, license-attribution]` and allowed fields
    including `ecosystem-specific-verifiers`,
    `transparency-log-sources`, `attestation-policy-defaults`,
    `verification-output-handling`, and `exemption-handling`.

- `spec/substrate-scope.md`:
  - Supply-chain added to the High depth tier listing (10-15
    rules) with adjacency clarification distinguishing it from
    the dependency-management concern (vetting and pinning vs
    artifact provenance, signing, SBOM, build-environment
    integrity).
  - Tier 2 enforcement-engine guidance updated to clarify the
    OpenGrep migration: substrate-default engine is OpenGrep
    (Semgrep CE fork); the substrate adopts Semgrep pattern
    format (semgrep-pattern-v1) because OpenGrep did not adopt
    a distinct format of its own; format is stable across both
    engines. Four references to OpenGrep added; zero stale
    "Semgrep YAML rules" references remain.

### Validation

- All 11 catalogs validate against OSCAL v1.1.2 schema.
- All 47 static-analysis tool bindings validate against the
  binding schema (42 from prior sessions plus 5 new supply-chain
  L1 bindings). The variant-6 schema additions validate against
  the bumped 0.3.0 schema.
- All 12 decision-framework MADRs validate.
- Profile validates against the OSCAL profile schema.

### Cross-references

The supply-chain concern interacts with the substrate's other
concerns in specific ways recorded in the catalog and the MADR:

- **dependency-management**: supply-chain and dependency-management
  share the upstream-trust surface; dependency-management governs
  manifest-lockfile pinning, vetting before adoption, and
  vulnerability scanning, while supply-chain governs artifact
  provenance, signing, SBOM discipline, and build-environment
  integrity. SUPPLY-L2-001 (dependency vetting at adoption) pairs
  with the dependency-vetting-policy.madr.md decision framework.
  SUPPLY-L2-003 (critical dependency audit) references the
  upstream-ecosystem signals tracked through the
  dependency-management discipline.
- **secrets-management**: SECRETS governs build-time credential
  handling; supply-chain documents the signing-identity policy
  that SECRETS provisions. SUPPLY-L2-005 build-environment
  isolation cross-references SECRETS-* for build-time secret
  discipline.
- **logging**: LOG-L2-002 (tamper-evident log integrity)
  cross-references with SUPPLY-L2-006 (attestation and SBOM
  retention with audit trail). The retention surface inherits
  integrity properties from the logging concern.
- **authorization**: AUTHZ-L2-002 (least-privilege role design)
  governs the principals authorized to write to the supply-chain
  retention surface, modify policy files, and approve exemptions.
- **testing-strategy**: TEST-L2-002 (critical-path coverage)
  references SUPPLY-L1-* as part of the substrate L1 surface
  that critical paths exercise. Supply-chain CI gates are
  themselves substrate-required to be tested per the testing-
  strategy ADR.

The variant-6 schema introduction is recorded in this session's
schema changelog. SUPPLY-L1-002 and SUPPLY-L1-003 serve as the
reference implementations of variant 6 attestation-orchestration
for future supply-chain rules at finer attestation granularities
(license-attestation verification, vuln-scan attestation
verification, threat-model attestation verification).

---

## M2 Session 4 (released in [0.5.0])

**M2 Session 4: testing-strategy concern authoring.** Fourth
M2-phase content addition; follows M2 Session 1 (authorization,
2026-05-22), M2 Session 2 (input-validation, 2026-05-23), and
M2 Session 3 (error-handling, 2026-05-24). The testing-strategy
concern is the substrate's tenth concern, anchored to OWASP
ASVS v5.0.0 (V14 Configuration / test discipline references),
ISO/IEC/IEEE 29119 (Software Testing Standards),
the ISTQB Foundation Level syllabus, Martin Fowler's "Practical
Test Pyramid" and related testing-non-determinism essays, and
Google's Engineering Practices for testing. All artifacts enter
at lifecycle-status draft; promotion to stable is deferred to
M2 close per the Path A precedent.

The substrate's L1 mechanical surface covers the highest-impact
test-discipline antipatterns (skip without rationale, empty or
assertion-free test bodies, fixed-time sleeps for
synchronization, and test framework imports in production
paths). The L2 semantic surface covers the structural decisions
(pyramid composition consistency with documented strategy,
critical-path coverage including security probes aligned with
substrate L1 rules from adjacent concerns, and deterministic
execution under randomization and parallelism). The L3
judgmental rule pairs with a MADR analyzing pyramid shape
choice (classic, trophy, diamond, or documented alternative),
per-tier coverage targets, CI gate composition, flake handling
policy, environment management, performance budgets, mutation
testing inclusion, property-based testing inclusion, and
determinism enforcement.

Testing-strategy is a medium-depth concern per
spec/substrate-scope.md (7 to 10 rules target). This authoring
lands at the mid-band (8 rules: 4 L1 + 3 L2 + 1 L3), reflecting
the substrate-author's instruction to "go with proposed"
4+3+1 split.

### Added

Concern catalog (8 rules; lifecycle-status draft; catalog-
status in-development; version 0.1.0):

- `catalogs/concerns/testing-strategy.oscal.yaml` (4 L1
  mechanical, 3 L2 semantic, 1 L3 judgmental):
  - TEST-L1-001 skip-requires-reason (severity: medium)
  - TEST-L1-002 no-empty-test-body (severity: high)
  - TEST-L1-003 no-flaky-sleep (severity: medium)
  - TEST-L1-004 no-test-framework-in-production (severity:
    high)
  - TEST-L2-001 test-pyramid-composition (severity: high)
  - TEST-L2-002 critical-path-coverage (severity: high)
  - TEST-L2-003 deterministic-execution (severity: high)
  - TEST-L3-001 testing-strategy (severity: high)

Tool bindings (11 paired with the catalog rules):

- `tool-bindings/static-analysis/` — 4 L1 bindings using the
  variant-3 (registry-reference-with-complementary-tools)
  pattern established by the L1 surface in M0/M1/M2 Sessions
  1-3:
  - `test-l1-001-skip-requires-reason.yaml`
  - `test-l1-002-no-empty-test-body.yaml`
  - `test-l1-003-no-flaky-sleep.yaml`
  - `test-l1-004-no-test-framework-in-production.yaml`

- `tool-bindings/review-checklist/` — 4 review checklists
  (3 L2 + 1 L3, 8 review questions each, following the
  err-l2-* / err-l3-001 precedent):
  - `test-l2-001-test-pyramid-composition.md`
  - `test-l2-002-critical-path-coverage.md`
  - `test-l2-003-deterministic-execution.md`
  - `test-l3-001-testing-strategy.md`

- `tool-bindings/test-template/` — 3 L2 test templates
  (framework-agnostic verification scenarios):
  - `test-l2-001-test-pyramid-composition.md`
  - `test-l2-002-critical-path-coverage.md`
  - `test-l2-003-deterministic-execution.md`

Decision framework (1 paired with TEST-L3-001):

- `decision-frameworks/testing-strategy.madr.md` — Six options
  surveyed (classic pyramid as substrate-preferred default;
  trophy for frontend-heavy applications; diamond/honeycomb
  for integration-heavy systems; ice cream cone substrate-
  discouraged; unit-only substrate-discouraged; ad-hoc
  substrate-rejected). Seven application-context drivers
  (architecture, integration topology, risk profile, CI
  budget, team capacity, regulatory context, observability
  surface) and nine concrete decisions (pyramid shape,
  per-tier targets, CI gate, flakiness policy, environment,
  performance budget, mutation inclusion, property-based
  inclusion, determinism enforcement). MADR includes consumer
  ADR documentation requirements and review-cadence guidance.

Examples (16 files, 8 paired good/anti-pattern pairs):

- `examples/testing-strategy/` — paired good/anti-pattern
  examples for all 8 substrate rules. Each pair illustrates
  the substrate-aligned pattern (good) and the substrate-
  rejected forms (anti-pattern), with multi-language coverage
  (Python, JavaScript, Java, Go, Ruby as appropriate per
  rule).

Profile updates:

- `profiles/production-grade-baseline.oscal.yaml`:
  - `last-modified`: `2026-05-24T00:00:00Z` → `2026-05-25T00:00:00Z`
  - `rule-selection-count`: 86 → 94
  - Header comment updated to include testing-strategy in the
    M2 inventory and to note the M2 Session 4 addition.
  - 8 imports added for testing-strategy rules.
  - 8 alters added for testing-strategy rules with
    `profile-selection-rationale`, `profile-severity-override`
    (matching catalog defaults), and `profile-ai-assistance`
    properties.
  - Back-matter resource added for the testing-strategy
    catalog (UUID `d0e1f2a3-b4c5-6d7e-8f9a-0b1c2d3e4f5a`).

### Validation

- All 10 catalogs validate against OSCAL v1.1.2 schema.
- All 42 static-analysis tool bindings validate against the
  binding schema.
- All 11 decision-framework MADRs validate.
- Profile validates against the OSCAL profile schema.

### Cross-references

The testing-strategy concern's critical-path coverage
explicitly exercises substrate L1 rules from adjacent concerns:
AUTH-L1-* (authentication), AUTHZ-L1-* (authorization),
INPUT-L1-* (input-validation), ERR-L1-* (error-handling), and
LOG-L1-* (logging). The substrate's compositional discipline
is preserved: TEST-L2-002 (critical-path-coverage) does not
duplicate those rules; it requires that they are exercised
through the testing strategy.

The OBS-L3-001 (observability-slo-policy) ADR is referenced
as the source of truth for what failure modes must be visible;
the testing strategy commits to exercising the instrumentation
that delivers that visibility.

The substrate-author's instruction to "go with proposed"
4+3+1 medium-depth scoping is recorded in the framework MADR
and in the catalog-status notes.

---

## M2 Session 3 (released in [0.5.0])

**M2 Session 3: error-handling concern authoring.** Third
M2-phase content addition; follows M2 Session 1 (authorization,
2026-05-22) and M2 Session 2 (input-validation, 2026-05-23).
The error-handling concern is the substrate's ninth concern,
anchored to OWASP ASVS v5.0.0 Chapter 7 (Error Handling and
Logging), OWASP Top 10 2021 A05:2021 Security Misconfiguration
and A09:2021 Security Logging and Monitoring Failures, RFC 7807
(superseded by RFC 9457) Problem Details for HTTP APIs, and the
AWS Builders' Library on timeouts, retries, and backoff with
jitter. All artifacts enter at lifecycle-status draft;
promotion to stable is deferred to M2 close per the Path A
precedent.

The substrate's L1 mechanical surface covers the highest-
impact error-handling antipatterns (bare exception catches,
exception swallowing without log, stack-trace leakage in
responses, hardcoded success status codes on error paths, and
resource acquisition without language-native finalization).
The L2 semantic surface covers the structural decisions
(error response contract consistency, typed domain vs
infrastructure error classification, bounded retry with
circuit-breaker protection, observable response discrepancy
avoidance for enumeration resistance). The L3 judgmental rule
pairs with a MADR analyzing error response contract choice,
typed hierarchy organization, retry and circuit-breaker
policy per dependency, fail-fast versus graceful-degradation
defaults, and error logging policy.

Error-handling is a high-depth concern per
spec/substrate-scope.md (10 to 15 rules target). This
authoring lands at the floor (10 rules: 5 L1 + 4 L2 + 1 L3),
matching the logging concern's structural precedent.

### Added

Concern catalog (10 rules; lifecycle-status draft; catalog-
status in-development; version 0.1.0):

- `catalogs/concerns/error-handling.oscal.yaml` (5 L1
  mechanical, 4 L2 semantic, 1 L3 judgmental):
  - ERR-L1-001 no-bare-except (severity: high)
  - ERR-L1-002 no-exception-swallow (severity: high)
  - ERR-L1-003 no-stack-trace-in-response (severity: critical)
  - ERR-L1-004 error-status-code (severity: high)
  - ERR-L1-005 resource-finalization (severity: high)
  - ERR-L2-001 error-response-contract (severity: high)
  - ERR-L2-002 typed-error-classification (severity: high)
  - ERR-L2-003 retry-and-circuit-breaker (severity: high)
  - ERR-L2-004 observable-response-discrepancy (severity:
    critical)
  - ERR-L3-001 error-handling-strategy (severity: high)

Tool bindings (all 14 paired with the catalog rules):

- 5 L1 static-analysis bindings (semgrep-based pattern
  detection with complementary linter coverage):
  - `tool-bindings/static-analysis/err-l1-001-no-bare-except.yaml`
  - `tool-bindings/static-analysis/err-l1-002-no-exception-swallow.yaml`
  - `tool-bindings/static-analysis/err-l1-003-no-stack-trace-in-response.yaml`
  - `tool-bindings/static-analysis/err-l1-004-error-status-code.yaml`
  - `tool-bindings/static-analysis/err-l1-005-resource-finalization.yaml`
- 5 review-checklist bindings (one per L2 rule plus L3):
  - `tool-bindings/review-checklist/err-l2-001-error-response-contract.md`
  - `tool-bindings/review-checklist/err-l2-002-typed-error-classification.md`
  - `tool-bindings/review-checklist/err-l2-003-retry-and-circuit-breaker.md`
  - `tool-bindings/review-checklist/err-l2-004-observable-response-discrepancy.md`
  - `tool-bindings/review-checklist/err-l3-001-error-handling-strategy.md`
- 4 test-template bindings (one per L2 rule):
  - `tool-bindings/test-template/err-l2-001-error-response-contract.md`
  - `tool-bindings/test-template/err-l2-002-typed-error-classification.md`
  - `tool-bindings/test-template/err-l2-003-retry-and-circuit-breaker.md`
  - `tool-bindings/test-template/err-l2-004-observable-response-discrepancy.md`

Decision framework (lifecycle-status draft):

- `decision-frameworks/error-handling-strategy.madr.md`
  (paired with ERR-L3-001; 9 decision drivers; 5 considered
  options; substrate-recommended retry library defaults
  across Python, JavaScript/TypeScript, Java, .NET, Go,
  Ruby; references logging-architecture and observability-
  slo-policy MADRs without duplication)

Examples (20 paired good/anti-pattern files under
`examples/error-handling/`):

- no-bare-except-{good,anti-pattern}.md
- no-exception-swallow-{good,anti-pattern}.md
- no-stack-trace-in-response-{good,anti-pattern}.md
- error-status-code-{good,anti-pattern}.md
- resource-finalization-{good,anti-pattern}.md
- error-response-contract-{good,anti-pattern}.md
- typed-error-classification-{good,anti-pattern}.md
- retry-and-circuit-breaker-{good,anti-pattern}.md
- observable-response-discrepancy-{good,anti-pattern}.md
- error-handling-strategy-{good,anti-pattern}.md (consumer
  ADR examples)

### Changed

- `profiles/production-grade-baseline.oscal.yaml`: imports the
  error-handling catalog with all 10 rules selected; adds 10
  modify.alters blocks (one per ERR rule) with profile-
  selection-rationale, profile-severity-override (catalog
  defaults preserved), and profile-ai-assistance properties;
  adds back-matter resource entry for the error-handling
  catalog. Rule-selection-count updated 76 -> 86.
  Last-modified updated to 2026-05-24.

- `catalogs/concerns/input-validation.oscal.yaml`: editorial
  cleanup of catalog-metadata-level lifecycle-status and
  entered-draft-at properties to align indentation with the
  authorization catalog precedent. Cleanup 0a from the M2
  Session 3 pre-flight; no semantic change. (See
  COMMIT-GUIDE-M2-SESSION-3.md commit 0.)

**M2 Session 2: input-validation concern authoring.** Second
M2-phase content addition; follows M2 Session 1 (authorization)
authored 2026-05-22. The input-validation concern is the
substrate's eighth concern, anchored to OWASP ASVS v5.0.0 Chapter
5 (Validation, Sanitization and Encoding) and OWASP Top 10
A03:2021 Injection plus A10:2021 SSRF. All artifacts enter at
lifecycle-status draft; promotion to stable is deferred to M2
close per the Path A precedent.

The substrate's L1 mechanical surface covers the highest-impact
injection categories (string-built SQL, shell-interpreted
subprocess invocation, unsafe deserialization, output-encoding
opt-outs, path traversal). The L2 semantic surface covers the
design-pattern layer (schema-at-boundary, canonical encoding,
type narrowing, file uploads, SSRF, safe loaders for configuration
and ML models). The L3 judgmental rule pairs with a MADR
analyzing schema-first vs imperative placement, library choice
per language, and canonical-form policy.

### Added

Concern catalog (12 rules; lifecycle-status draft; catalog-status
in-development; version 0.1.0):

- `catalogs/concerns/input-validation.oscal.yaml` (5 L1 mechanical,
  6 L2 semantic, 1 L3 judgmental):
  - INPUT-L1-001 parameterized-queries (severity: critical)
  - INPUT-L1-002 no-shell-injection-from-user-input (severity:
    critical)
  - INPUT-L1-003 no-unsafe-deserialization (severity: critical)
  - INPUT-L1-004 contextual-output-encoding (severity: high)
  - INPUT-L1-005 path-traversal-prevention (severity: high)
  - INPUT-L2-001 schema-validation-at-boundary (severity: high)
  - INPUT-L2-002 canonical-encoding-before-validation (severity:
    high)
  - INPUT-L2-003 type-narrowing-at-boundary (severity: high)
  - INPUT-L2-004 file-upload-validation (severity: high)
  - INPUT-L2-005 ssrf-prevention (severity: critical)
  - INPUT-L2-006 deserialization-safe-loaders (severity: high)
  - INPUT-L3-001 input-validation-strategy (severity: critical)

Tool bindings (all 19 paired with the catalog rules):

- 5 L1 static-analysis bindings (semgrep-based pattern detection):
  - `tool-bindings/static-analysis/input-l1-001-parameterized-queries.yaml`
  - `tool-bindings/static-analysis/input-l1-002-no-shell-injection.yaml`
  - `tool-bindings/static-analysis/input-l1-003-no-unsafe-deserialization.yaml`
  - `tool-bindings/static-analysis/input-l1-004-contextual-output-encoding.yaml`
  - `tool-bindings/static-analysis/input-l1-005-path-traversal-prevention.yaml`
- 7 review-checklist bindings (one per L2 rule plus L3):
  - `tool-bindings/review-checklist/input-l2-001-schema-validation-at-boundary.md`
  - `tool-bindings/review-checklist/input-l2-002-canonical-encoding-before-validation.md`
  - `tool-bindings/review-checklist/input-l2-003-type-narrowing-at-boundary.md`
  - `tool-bindings/review-checklist/input-l2-004-file-upload-validation.md`
  - `tool-bindings/review-checklist/input-l2-005-ssrf-prevention.md`
  - `tool-bindings/review-checklist/input-l2-006-deserialization-safe-loaders.md`
  - `tool-bindings/review-checklist/input-l3-001-input-validation-strategy.md`
- 6 test-template bindings (one per L2 rule):
  - `tool-bindings/test-template/input-l2-001-schema-validation-at-boundary.md`
  - `tool-bindings/test-template/input-l2-002-canonical-encoding-before-validation.md`
  - `tool-bindings/test-template/input-l2-003-type-narrowing-at-boundary.md`
  - `tool-bindings/test-template/input-l2-004-file-upload-validation.md`
  - `tool-bindings/test-template/input-l2-005-ssrf-prevention.md`
  - `tool-bindings/test-template/input-l2-006-deserialization-safe-loaders.md`

Decision framework (lifecycle-status draft):

- `decision-frameworks/input-validation-strategy.madr.md` (paired
  with INPUT-L3-001; 9 decision drivers; 5 considered options;
  substrate-recommended library defaults across Python, JavaScript,
  Java, Go, Ruby, PHP)

Examples (24 paired good/anti-pattern files under
`examples/input-validation/`):

- parameterized-queries-{good,anti-pattern}.md
- no-shell-injection-{good,anti-pattern}.md
- no-unsafe-deserialization-{good,anti-pattern}.md
- contextual-output-encoding-{good,anti-pattern}.md
- path-traversal-prevention-{good,anti-pattern}.md
- schema-validation-at-boundary-{good,anti-pattern}.md
- canonical-encoding-before-validation-{good,anti-pattern}.md
- type-narrowing-at-boundary-{good,anti-pattern}.md
- file-upload-validation-{good,anti-pattern}.md
- ssrf-prevention-{good,anti-pattern}.md
- deserialization-safe-loaders-{good,anti-pattern}.md
- input-validation-strategy-{good,anti-pattern}.md (consumer ADR
  examples)

### Changed

- `profiles/production-grade-baseline.oscal.yaml`: imports the
  input-validation catalog with all 12 rules selected; adds 12
  modify.alters blocks (one per INPUT rule) with profile-
  selection-rationale, profile-severity-override (catalog defaults
  preserved), and profile-ai-assistance properties; adds back-
  matter resource entry. Rule-selection-count updated 64 -> 76.
  Last-modified updated to 2026-05-23.

**M2 Session 1: authorization concern authoring.** First M2-phase
content addition; pairs with the M1 Path A consolidation that
closed substrate version 0.4.0. The authorization concern is the
substrate's seventh universal-floor concern and the first M2
addition. All artifacts enter at lifecycle-status draft per the
substrate's draft-first authoring convention; promotion to stable
is deferred to M2 close per the Path A precedent established at
M1 close (2026-05-22).

The authorization concern was selected for M2 Session 1 per the
substrate-author roadmap recorded in HANDOFF Section 11. The
substrate's seven L2 OWASP-aligned categories (BOLA, BOPLA, BFLA,
SSRF-via-authz, mass-assignment, deny-by-default, audit) are
distributed across 6 L2 rules with a single L3 model-selection
rule pairing with the corresponding MADR framework.

### Added

Concern catalog (12 rules; lifecycle-status draft; catalog-status
in-development; version 0.1.0):

- `catalogs/concerns/authorization.oscal.yaml` (5 L1 mechanical,
  6 L2 semantic, 1 L3 judgmental):
  - AUTHZ-L1-001 protected-route-declares-authz (severity:
    critical)
  - AUTHZ-L1-002 authz-before-resource-access (severity:
    critical)
  - AUTHZ-L1-003 no-hardcoded-role-strings (severity: high)
  - AUTHZ-L1-004 no-client-side-only-authz (severity: high)
  - AUTHZ-L1-005 mass-assignment-allowlist (severity: high)
  - AUTHZ-L2-001 object-level-authorization (severity: critical)
  - AUTHZ-L2-002 least-privilege-role-design (severity: high)
  - AUTHZ-L2-003 step-up-and-audit-for-privilege-changes
    (severity: high)
  - AUTHZ-L2-004 multi-tenant-data-layer-isolation (severity:
    critical)
  - AUTHZ-L2-005 centralized-deny-by-default-policy (severity:
    high)
  - AUTHZ-L2-006 audit-events-on-decisions (severity: high)
  - AUTHZ-L3-001 authorization-model-selection (severity:
    critical)

Tool bindings (all 24 paired with the catalog rules):

- 5 L1 static-analysis bindings (semgrep-based pattern detection):
  - `tool-bindings/static-analysis/authz-l1-001-protected-route-declares-authz.yaml`
  - `tool-bindings/static-analysis/authz-l1-002-authz-before-resource-access.yaml`
  - `tool-bindings/static-analysis/authz-l1-003-no-hardcoded-role-strings.yaml`
  - `tool-bindings/static-analysis/authz-l1-004-no-client-side-only-authz.yaml`
  - `tool-bindings/static-analysis/authz-l1-005-mass-assignment-allowlist.yaml`
- 7 review-checklist bindings (one per L2 rule plus L3):
  - `tool-bindings/review-checklist/authz-l2-001-object-level-authorization.md`
  - `tool-bindings/review-checklist/authz-l2-002-least-privilege-role-design.md`
  - `tool-bindings/review-checklist/authz-l2-003-step-up-and-audit-for-privilege-changes.md`
  - `tool-bindings/review-checklist/authz-l2-004-multi-tenant-data-layer-isolation.md`
  - `tool-bindings/review-checklist/authz-l2-005-centralized-deny-by-default-policy.md`
  - `tool-bindings/review-checklist/authz-l2-006-audit-events-on-decisions.md`
  - `tool-bindings/review-checklist/authz-l3-001-authorization-model-selection.md`
- 6 test-template bindings (one per L2 rule; substrate-format
  scenario lists with framework-agnostic scaffolding):
  - `tool-bindings/test-template/authz-l2-001-object-level-authorization.md`
  - `tool-bindings/test-template/authz-l2-002-least-privilege-role-design.md`
  - `tool-bindings/test-template/authz-l2-003-step-up-and-audit-for-privilege-changes.md`
  - `tool-bindings/test-template/authz-l2-004-multi-tenant-data-layer-isolation.md`
  - `tool-bindings/test-template/authz-l2-005-centralized-deny-by-default-policy.md`
  - `tool-bindings/test-template/authz-l2-006-audit-events-on-decisions.md`

Decision framework MADR (lifecycle-status draft; commons-version
0.4.0; framework-version 0.1.0):

- `decision-frameworks/authorization-model-selection.madr.md`
  pairs with AUTHZ-L3-001; mirrors the auth-strategy.madr.md
  precedent for L3-as-pre-build-gate; covers 9 decision drivers
  and 5 considered options (RBAC, ABAC, ReBAC, Hybrid, Minimal)

Examples (24 paired files, 12 good and 12 anti-pattern, one pair
per substrate rule), all under `examples/authorization/`:

- 5 L1 pairs: protected-route-declares-authz, authz-before-
  resource-access, no-hardcoded-role-strings, no-client-side-
  only-authz, mass-assignment-allowlist
- 6 L2 pairs: object-level-authorization, least-privilege-role-
  design, step-up-and-audit-for-privilege-changes, multi-
  tenant-data-layer-isolation, centralized-deny-by-default-
  policy, audit-events-on-decisions
- 1 L3 pair: authorization-model-selection (good example shows
  a filled-in consumer ADR; anti-pattern shows six failing-ADR
  shapes)

### Changed

Profile modifications:

- `profiles/production-grade-baseline.oscal.yaml`:
  - Added `imports` block referencing authorization catalog with
    all 12 rule IDs selected
  - Added 12 `modify.alters` blocks with profile-selection-
    rationale, profile-severity-override, and profile-ai-
    assistance properties for each authorization rule
  - Added back-matter resource for the authorization catalog
  - Updated rule-selection-count from 52 to 64
  - Updated imports header comment to reflect authorization
    addition

### Rationale

Authorization is the substrate's seventh universal-floor concern
and the natural successor to authentication in the M2 sequence.
The substrate's seven L2 OWASP-aligned categories (BOLA, BOPLA,
BFLA, SSRF-via-authz, mass-assignment, deny-by-default, audit)
mapped to 6 L2 rules per the substrate's coverage-by-design
philosophy: BOLA -> L2-001 object-level, BOPLA -> L1-005 mass-
assignment (promoted to L1 because the input boundary is
mechanically detectable), BFLA -> L2-002 least-privilege role
design, multi-tenant isolation -> L2-004 (substrate's
substrate-original concern, not OWASP-listed but substrate-
considered essential for B2B SaaS), deny-by-default -> L2-005,
audit -> L2-006, step-up-and-audit-for-privilege-changes ->
L2-003.

The L3-001 model selection rule mirrors AUTH-L3-001's structure:
substrate-required ADR before substantive implementation; paired
MADR provides the analysis framework; the consumer's ADR
satisfies the rule by adapting the framework to application
context.

### Substrate-author notes

- All artifacts at lifecycle-status draft per Path A precedent
  established at M1 close (M1 sessions authored at draft;
  consolidated to stable at M1 close after cooling-off interval)
- No VERSION bump in this session; the version bump will happen
  at M2 close or upon stable promotion of the authorization
  concern
- No em-dashes or en-dashes per substrate writing convention
- All YAML frontmatter and validators clean (28 static-analysis
  bindings PASS, 8 decision-frameworks PASS, 7 catalogs PASS,
  1 profile PASS, overall PASS)

## [0.4.0] - 2026-05-22

**M1 consolidation phase (Path A): universal-floor stable promotion.**
All 5 M1 draft catalogs and their paired MADRs promoted from draft
to stable under Charter Section 2.4.1 solo-author attestation.
Profile and static-analysis-binding schema also promoted to stable.
SPDX backfill bundled. M1 closes; M2 authoring is unblocked.

Per Charter Section 2.4.1, every artifact promoted in this version
honored a cooling-off interval of one calendar day or more between
its authoring date and this attestation date. Section 2.4 validation
criteria applied per artifact: rule intent clear, examples
demonstrate the rule, severity and layer assignments defensible,
provenance complete, no conflict with existing commons content.

### Promoted

Concern catalogs (lifecycle-status draft -> stable; catalog-status
in-development -> feature-complete; version 0.1.0 -> 1.0.0; per-rule
lifecycle-status: draft -> stable on every rule; entered-stable-at
added on every rule; catalog-attestation prop added with Charter
Section 2.4.1 remarks):

- `catalogs/concerns/secrets-management.oscal.yaml` (8 rules; draft
  authored 2026-05-20 M1 Session 1)
- `catalogs/concerns/dependency-management.oscal.yaml` (5 rules;
  draft authored 2026-05-20 M1 Session 1)
- `catalogs/concerns/logging.oscal.yaml` (10 rules; draft authored
  2026-05-20 M1 Session 2a)
- `catalogs/concerns/observability.oscal.yaml` (8 rules; draft
  authored 2026-05-21 M1 Session 2b)
- `catalogs/concerns/cost-model-selection.oscal.yaml` (5 rules;
  draft authored 2026-05-21 M1 Session 2c)

Decision-framework MADRs (frontmatter lifecycle-status draft ->
stable; reviewer: myoung-self-attested; reviewed:
2026-05-22; attestation-mechanism block added per auth-strategy
precedent; commons-version 0.2.0/0.3.0 -> 0.4.0; framework-version
0.1.0 -> 1.0.0):

- `decision-frameworks/secrets-management-platform.madr.md`
- `decision-frameworks/dependency-vetting-policy.madr.md`
- `decision-frameworks/logging-architecture.madr.md`
- `decision-frameworks/observability-slo-policy.madr.md`
- `decision-frameworks/cost-model-selection-policy.madr.md`

Schema (x-governance-commons.lifecycle-status draft -> stable;
last-modified bumped):

- `schemas/static-analysis-binding.schema.json` (schema-version
  remains 0.2.0; promotion is lifecycle status only, no schema
  content change)

Profile (prop lifecycle-status draft -> stable;
commons-version 0.1.0 -> 1.0.0; version 0.1.0 -> 1.0.0;
last-modified bumped):

- `profiles/production-grade-baseline.oscal.yaml`

### Changed

- `VERSION` 0.3.0 -> 0.4.0. Minor bump per `spec/rule-lifecycle.md`
  guidance: "Increment substrate version per semantic versioning
  (typically minor for first-time stable promotion of a draft)."
  Bumping at consolidation rather than per-artifact keeps the
  consolidation phase atomic.
- SPDX-License-Identifier headers backfilled on 4 decision-framework
  MADRs that lacked them. The 2 already-stable MADRs (auth-strategy,
  mfa-factor-selection) receive the SPDX block as editorial
  correction per Charter Article IV Section 4.2 (non-material, no
  artifact-version bump). The 2 previously-draft MADRs
  (secrets-management-platform, dependency-vetting-policy) receive
  the SPDX block bundled with their lifecycle promotion. All 7 MADRs
  now carry the SPDX header inside their YAML frontmatter per Section
  10 settled decision 15 (HANDOFF.md).
- `scripts/validate-all.sh` added (convenience wrapper that runs all
  four substrate validators in sequence with unified summary; not
  authoritative, the four individual validators remain authoritative).
- `scripts/apply-license-headers.sh` added (idempotent SPDX header
  injector for substantive substrate files; intentionally excludes
  third-party content under `.specify/` and `.claude/skills/speckit-*`;
  does NOT cover the decision-frameworks/ directory, so MADR SPDX
  backfill is handled by direct edit during the same consolidation
  phase).

### Retired

- Legacy session-specific verify scripts: `verify-m1-session-1.sh`,
  `verify-m1-session-2.sh`, `verify-m1-session-2-recovery.sh`,
  `verify-m1-session-3.sh`. Per Section 7 Rule 16 (settled M1
  Session 2b close, HANDOFF.md), the substrate publishes 4
  general-purpose validators only; session-specific verify scripts
  are not authored from Session 2c forward. The four legacy scripts
  served their per-session purposes during M1 authoring; their
  retirement here closes HANDOFF Open Question 18.

### M1 milestone closure note

M1 (Universal substrate floor) closes with this consolidation. The
M1 universal-floor authoring (Sessions 1, 2a, 2b, 2c) produced 5
concern catalogs covering the universal floor of concerns every
project shape needs (secrets-management, dependency-management,
logging, observability, cost-model-selection). The M1 capability
statement is now realized at commitment grade: the substrate covers
those concerns and the content is stable per Charter Article IV
immutability semantics. Authentication is the 6th stable catalog,
inherited from M0.

Per HANDOFF Section 4, M2 (Common substrate coverage) is the next
milestone, targeting 5 common concerns (supply-chain,
input-validation, error-handling, testing-strategy, authorization)
at full depth. M2 work starts at substrate version 0.4.0 and will
land at draft until M2's own consolidation phase bumps to 0.5.0.

### Open Questions closed by this version

- **Open Question 16:** SPDX backfill on 4 MADRs. Closed by bundling
  the backfill into the consolidation phase as described above.
- **Open Question 17:** Schema 0.2.0 promotion to stable. Closed by
  bundling the schema's lifecycle-status flip into the consolidation
  phase as described above.
- **Open Question 18:** Legacy verify-m1-session-*.sh retirement.
  Closed by retiring the four scripts (executed in the working tree
  prior to this consolidation phase; documented here).

## M1 authoring sessions (released in [0.4.0])


### Added

**M1 Session 2c deliverables (2026-05-21):** cost-model-selection
concern catalog authored at lifecycle-status draft, with supporting
artifacts and profile integration. This is the fifth and final
concern catalog of the M1 universal-floor authoring sequence
(authentication, secrets-management, dependency-management,
logging, observability, cost-model-selection). The substrate's
low-depth tier classification for cost-model-selection (per
`spec/substrate-scope.md`) is realized at 5 rules, mirroring the
dependency-management precedent (2 L1 mechanical + 2 L2 semantic
+ 1 L3 judgmental).

Session 2c also caught and resolved a depth-classification drift
at the Section 11 step 1 depth-confirmation gate: HANDOFF Section 4
and Section 11 had described cost-model-selection as medium depth
(6-10 rules) citing substrate-scope.md, but substrate-scope.md
itself classifies cost-model-selection as low depth (3-6 rules)
alongside dependency-management. Path A (author at low depth per
substrate-scope.md as authoritative) was confirmed; HANDOFF drift
patches accompany this session. The depth gate continues to work
as designed.

Concern catalog (at `draft`):

- `catalogs/concerns/cost-model-selection.oscal.yaml` (5 rules:
  2 L1 mechanical COST-L1-001 cost-attribution-tags-present and
  COST-L1-002 workload-resource-limits-set,
  2 L2 semantic COST-L2-001 cost-emission-pipeline-discipline and
  COST-L2-002 cost-anomaly-alerting-configured,
  1 L3 judgmental COST-L3-001 cost-model-selection-policy)

Decision framework (MADR-format, validates clean against
`schemas/decision-framework.schema.json`; SPDX header placed
as YAML comments inside frontmatter per Section 10 settled
decision 15):

- `decision-frameworks/cost-model-selection-policy.madr.md`
  (substrate analysis of cost SLI selection options A1 through A4,
  cost SLO target shape options B1 through B3, budget computation
  method options D1 through D2, over-budget response policy options
  E1 through E4; 7 substrate-recognized decision drivers; substrate-
  recommended composite position for typical unit-economics-driven
  services; related-frameworks reference to observability-slo-policy
  recording the cost-vs-reliability trade-off pairing)

Tool bindings (static-analysis L1, both variant 3 registry-
reference-with-complementary-tools per the obs-l1-001 precedent;
no schema bump required at variant 3; schema fitness check
confirmed at Section 11 step 3):

- `tool-bindings/static-analysis/cost-l1-001-cost-attribution-tags.yaml`
- `tool-bindings/static-analysis/cost-l1-002-workload-resource-limits.yaml`

Tool bindings (review-checklist L2 and L3):

- `tool-bindings/review-checklist/cost-l2-001-cost-emission-pipeline.md`
- `tool-bindings/review-checklist/cost-l2-002-cost-anomaly-alerting.md`
- `tool-bindings/review-checklist/cost-l3-001-cost-model-selection-policy.md`

Tool bindings (test-template L2):

- `tool-bindings/test-template/cost-l2-001-cost-emission-pipeline.md`
- `tool-bindings/test-template/cost-l2-002-cost-anomaly-alerting.md`

Examples (10 files, paired good and anti-pattern per rule):

- `examples/cost-model-selection/cost-attribution-tags-good.md`
- `examples/cost-model-selection/cost-attribution-tags-anti-pattern.md`
- `examples/cost-model-selection/workload-resource-limits-good.md`
- `examples/cost-model-selection/workload-resource-limits-anti-pattern.md`
- `examples/cost-model-selection/cost-emission-pipeline-good.md`
- `examples/cost-model-selection/cost-emission-pipeline-anti-pattern.md`
- `examples/cost-model-selection/cost-anomaly-alerting-good.md`
- `examples/cost-model-selection/cost-anomaly-alerting-anti-pattern.md`
- `examples/cost-model-selection/cost-model-selection-policy-good.md`
  (complete consumer ADR example adapting the substrate framework)
- `examples/cost-model-selection/cost-model-selection-policy-anti-pattern.md`

### Changed

- `profiles/production-grade-baseline.oscal.yaml` updated to import
  the cost-model-selection catalog and select all 5 rules. Profile
  rule-selection-count 47 -> 52. Back-matter resources updated with
  the new catalog reference. The profile's last-modified date
  unchanged at 2026-05-21 (Session 2b modification date) since
  the Session 2c update lands on the same calendar day.

### Validation status

All four validators clean against the Session 2c deliverables:

- validate-catalogs: 6 passed (authentication, cost-model-selection,
  dependency-management, logging, observability, secrets-management)
- validate-static-analysis-bindings: 23 passed (2 new
  cost-model-selection bindings added in variant 3, no schema bump
  required; schema fitness check confirmed at Section 11 step 3)
- validate-decision-frameworks: 7 passed (auth-strategy,
  cost-model-selection-policy, dependency-vetting-policy,
  logging-architecture, mfa-factor-selection,
  observability-slo-policy, secrets-management-platform)
- validate-profiles: 1 passed

### M1 universal-floor closeout

M1 Session 2c concludes the universal-floor authoring sequence.
All five M1 universal-floor concerns now exist at lifecycle-status
draft (authentication 16 rules, secrets-management 8 rules,
dependency-management 5 rules, logging 10 rules, observability
8 rules, cost-model-selection 5 rules; 52 rules total across
6 catalogs). The next M1 milestone is the consolidation phase:
promotion of all draft catalogs to stable lifecycle (requires
Charter Section 2.4.1 cooling-off attestation commits on
subsequent calendar days, one per concern, per Section 11 of
HANDOFF.md). Optional consolidation work surfaces in the
HANDOFF Section 11 closeout direction: mappings/ cross-taxonomy
authoring; SPDX backfills across older artifacts; Rule 16 legacy
verify-m1-session-*.sh cleanup.

**M1 Session 2b deliverables (2026-05-21):** observability concern
catalog authored at lifecycle-status draft, with supporting
artifacts and profile integration. This is the fourth concern
catalog; the substrate's medium-depth tier classification for
observability (per `spec/substrate-scope.md`) is realized at
8 rules. Per substrate-author guidance recorded 2026-05-21,
OBS-L2-002 (high-cardinality metric label avoidance) is the
explicit L1 promotion candidate; the rule lives at L2 with
semantic review until consumer project usage confirms the
mechanical pattern holds across ecosystems.

Concern catalog (at `draft`):

- `catalogs/concerns/observability.oscal.yaml` (8 rules:
  3 L1 mechanical OBS-L1-001 through OBS-L1-003,
  4 L2 semantic OBS-L2-001 through OBS-L2-004,
  1 L3 judgmental OBS-L3-001)

Decision framework (MADR-format, validates clean against
`schemas/decision-framework.schema.json`; SPDX header placed
as YAML comments inside frontmatter per Section 10 settled
decision 15):

- `decision-frameworks/observability-slo-policy.madr.md`
  (substrate analysis of SLI selection options A1 through A4,
  SLO target shapes B1 through B3, measurement window options
  C1 through C3, error budget computation D1 through D2,
  burndown response policies E1 through E3; 7 substrate-
  recognized decision drivers; substrate-recommended composite
  position for typical request-driven services)

Tool bindings (static-analysis L1, all variant 3 registry-
reference-with-complementary-tools):

- `tool-bindings/static-analysis/obs-l1-001-no-sensitive-data-in-telemetry.yaml`
- `tool-bindings/static-analysis/obs-l1-002-trace-context-propagation.yaml`
- `tool-bindings/static-analysis/obs-l1-003-metric-naming-convention.yaml`

Tool bindings (review-checklist L2 and L3):

- `tool-bindings/review-checklist/obs-l2-001-semantic-convention-coverage.md`
- `tool-bindings/review-checklist/obs-l2-002-cardinality-discipline.md`
  (carries `l1-promotion-candidate: true` flag and
  L1-promotion contribution log section)
- `tool-bindings/review-checklist/obs-l2-003-alerting-discipline.md`
- `tool-bindings/review-checklist/obs-l2-004-dashboard-discipline.md`
- `tool-bindings/review-checklist/obs-l3-001-slo-policy.md`

Tool bindings (test-template L2):

- `tool-bindings/test-template/obs-l2-001-semantic-convention-coverage.md`
- `tool-bindings/test-template/obs-l2-002-cardinality-discipline.md`
  (carries L1-promotion contribution log section)
- `tool-bindings/test-template/obs-l2-003-alerting-discipline.md`
- `tool-bindings/test-template/obs-l2-004-dashboard-discipline.md`

Examples (16 files, paired good and anti-pattern per rule):

- `examples/observability/no-sensitive-data-in-telemetry-good.md`
- `examples/observability/no-sensitive-data-in-telemetry-anti-pattern.md`
- `examples/observability/trace-context-propagation-good.md`
- `examples/observability/trace-context-propagation-anti-pattern.md`
- `examples/observability/metric-naming-convention-good.md`
- `examples/observability/metric-naming-convention-anti-pattern.md`
- `examples/observability/semantic-convention-coverage-good.md`
- `examples/observability/semantic-convention-coverage-anti-pattern.md`
- `examples/observability/cardinality-discipline-good.md`
- `examples/observability/cardinality-discipline-anti-pattern.md`
- `examples/observability/alerting-discipline-good.md`
- `examples/observability/alerting-discipline-anti-pattern.md`
- `examples/observability/dashboard-discipline-good.md`
- `examples/observability/dashboard-discipline-anti-pattern.md`
- `examples/observability/slo-policy-good.md` (complete
  consumer ADR example adapting the substrate framework)
- `examples/observability/slo-policy-anti-pattern.md`

### Changed

- `profiles/production-grade-baseline.oscal.yaml` updated to
  import the observability catalog and select all 8 rules.
  Profile rule-selection-count 39 -> 47. Back-matter resources
  updated with the new catalog reference. The profile's
  last-modified bumped to 2026-05-21.

### Validation status

All four validators clean against the Session 2b deliverables:

- validate-catalogs: 5 passed (authentication, dependency-
  management, logging, observability, secrets-management)
- validate-static-analysis-bindings: 21 passed (3 new
  observability bindings added in variant 3, no schema bump
  required; schema fitness check confirmed at Section 11 step 3)
- validate-decision-frameworks: 6 passed (auth-strategy,
  dependency-vetting-policy, logging-architecture,
  mfa-factor-selection, observability-slo-policy,
  secrets-management-platform)
- validate-profiles: 1 passed

**M1 Session 2a deliverables (2026-05-20):** logging concern
catalog authored at lifecycle-status draft, with supporting
artifacts and profile integration. This is the third concern
catalog (after secrets-management and dependency-management);
the substrate's high-depth tier classification for logging
(per `spec/substrate-scope.md`) is realized at 10 rules.

Concern catalog (at `draft`):

- `catalogs/concerns/logging.oscal.yaml` (10 rules:
  5 L1 mechanical LOG-L1-001 through LOG-L1-005,
  4 L2 semantic LOG-L2-001 through LOG-L2-004,
  1 L3 judgmental LOG-L3-001)

Decision framework (MADR-format, validates clean against
`schemas/decision-framework.schema.json`):

- `decision-frameworks/logging-architecture.madr.md`
  (5 substrate-recognized options spanning cloud-native
  managed, self-hosted open-source, commercial SaaS, hybrid,
  and transport sub-decision; 7 substrate-required decision
  drivers; no-deliberate-architecture option explicitly
  discouraged)

Tool bindings (static-analysis L1):

- `tool-bindings/static-analysis/log-l1-001-structured-format.yaml`
- `tool-bindings/static-analysis/log-l1-002-no-sensitive-data-in-logs.yaml`
- `tool-bindings/static-analysis/log-l1-003-correlation-ids.yaml`
- `tool-bindings/static-analysis/log-l1-004-severity-levels.yaml`
- `tool-bindings/static-analysis/log-l1-005-log-injection.yaml`

All five log-l1-* bindings carry `binding-type:
registry-reference-with-complementary-tools` (variant 3 per
`schemas/static-analysis-binding.schema.json` v0.2.0), following
the AUTH-L1-008 precedent. The variant pairs Semgrep registry
rules with substrate-recommended complementary tooling
(OpenTelemetry auto-instrumentation, project-side language
linters, framework correlation libraries, observability platform
redaction).

Schema (Session 2a recovery, 2026-05-21):

- `schemas/static-analysis-binding.schema.json` updated from
  `schema-version` 0.1.0 to 0.2.0
- Variant 4 added: `binding-type:
  multi-ecosystem-orchestration`. Carries a required
  `ecosystem-detections` array (one element per package manager,
  each with manifest-file, lockfile-files, strict and permissive
  install commands, and an optional substitute-mechanism for
  ecosystems without a native lockfile such as java-maven). Also
  permits `complementary-tools`, `consumer-script-illustrative`
  at top level, and the standard consumer-invocation /
  coverage-notes / detection-gap-disclosure blocks
- Variant 5 added: `binding-type: scanner-orchestration`.
  Carries a required `primary-scanners` array plus optional
  `ecosystem-specific-scanners`, `complementary-services`,
  `sarif-integration` (with description and
  example-github-actions-snippet), `threshold-policy-defaults`
  (profile-keyed policy with block-at-or-above, warn-at,
  rationale), and `exemption-handling` (with description and
  example-exemption-file-format)
- `engine-guidance-ref` property added to variants 2 and 3 (it
  was already permitted on variant 1 at 0.1.0); aligns the
  substrate-internal reference convention across all variants
- `commons-version` updated 0.2.0 → 0.3.0; `last-modified` set
  to 2026-05-21; `x-governance-commons.validation-notes` and
  `x-governance-commons.ai-assistance` updated to document the
  five-variant model and the engine-guidance-ref alignment

The schema increment was forced by the validator failure that
errored Commit 2 of the original Session 2a sequence. The 5
log-l1-* bindings originally staged carried a hybrid
variant-1/variant-3 shape (rule-format plus rule-sources plus
complementary-tools) that no 0.1.0 variant accepted. Schema 0.2.0
formalizes the multi-tool pattern (variant 3 unchanged for the
log/secrets bindings) and adds variants 4 and 5 for the
ecosystem-orchestration and scanner-orchestration patterns that
the Session 1 deps-l1-* bindings had carried as latent failures.

Session 1 binding refactors (Session 2a recovery, 2026-05-21):

Five Session 1 bindings were refactored against schema 0.2.0
during the Session 2a recovery. The files were originally added
in Session 1 with structurally-failing shapes that the substrate
validator did not catch at Session 1 apply time. The Session 2a
catalog-then-binding apply hit the validator with strict mode,
surfacing the five latent failures alongside the five
log-l1-* shape failures. All bindings remain at lifecycle-status
draft; binding-version bumps from 0.1.0 to 0.2.0:

- `tool-bindings/static-analysis/secrets-l1-001-no-secrets-in-source.yaml`
  refactored to variant 3 (`registry-reference-with-complementary-tools`)
- `tool-bindings/static-analysis/secrets-l1-002-sensitive-files-gitignored.yaml`
  refactored to variant 3, with `recommended-gitignore-entries`
  and `consumer-script-illustrative` nested inside a
  `gitignore-audit` block per AUTH-L1-008 precedent
- `tool-bindings/static-analysis/secrets-l1-003-no-secrets-in-logs.yaml`
  refactored to variant 3
- `tool-bindings/static-analysis/deps-l1-001-pinned-versions.yaml`
  migrated to variant 4 (`multi-ecosystem-orchestration`); the
  14-element `ecosystem-detections` array is now first-class
  rather than top-level extra properties
- `tool-bindings/static-analysis/deps-l1-002-vulnerable-dependencies.yaml`
  migrated to variant 5 (`scanner-orchestration`);
  `primary-scanners`, `ecosystem-specific-scanners`,
  `complementary-services`, `sarif-integration`,
  `threshold-policy-defaults`, and `exemption-handling` are now
  first-class rather than top-level extra properties

Information was preserved across all five refactors (no rule
content removed; the structural shape changed, the substantive
content did not).

Validator outcome after refactor: 18 static-analysis bindings
(8 AUTH-L1 plus 10 in this session) pass against schema v0.2.0.
Backward compatibility verified against the 8 AUTH-L1 bindings;
no 0.1.0-valid binding becomes invalid under 0.2.0.

Review checklists for all L2 and L3 rules (5 total):

- 4 logging L2 checklists (LOG-L2-001 through LOG-L2-004)
- 1 logging L3 checklist (LOG-L3-001)

Test templates for all L2 rules (4 total):

- 4 logging L2 test templates (LOG-L2-001 through LOG-L2-004)

Examples (good and anti-pattern, 20 files total):

- 20 logging examples (10 good, 10 anti-pattern across the
  10 rules)

### Changed (Session 2a)

Schema `schemas/static-analysis-binding.schema.json`:

- `schema-version` updated from `0.1.0` to `0.2.0` (additive
  changes; no 0.1.0-valid binding becomes invalid under 0.2.0).
  Two new binding-type variants (`multi-ecosystem-orchestration`,
  `scanner-orchestration`) and `engine-guidance-ref` permitted
  on variants 2 and 3. See the Schema subsection under Added
  (Session 2a recovery) for details.

Profile `profiles/production-grade-baseline.oscal.yaml`:

- `imports` extended with `logging.oscal.yaml` (10 rules)
- `modify.alters` extended with 10 new blocks recording
  profile selection rationale, severity confirmation, and
  AI-assistance metadata per Charter Article V Section 5.6
- `rule-selection-count` updated from `29` to `39`
- `back-matter.resources` extended with logging catalog
  resource entry
- `last-modified` updated to `2026-05-20T22:00:00Z`

### Authoring notes (Session 2a)

- The logging concern's depth was classified per
  `spec/substrate-scope.md` (high depth, 10 rules);
  HANDOFF.md Section 11 Path A line had said "medium depth,
  7-8 rules". The substrate-scope.md classification is
  authoritative (HANDOFF.md is a working document; the
  substrate's own spec governs). HANDOFF.md Section 11
  amended to match. Tracked as Open Question 14.
- M1 Session 2 was scoped to 2-3 concerns (logging,
  observability, cost-model-selection). At full depth
  per the secrets-management precedent, one concern
  saturates a single chat turn's output budget. Session
  was rescoped to 2a (logging only); observability becomes
  Session 2b in a follow-up chat; cost-model-selection
  defers further. Tracked as Open Question 15.
- The static-analysis-binding schema increment from 0.1.0
  to 0.2.0 was forced by validator failure during the
  Commit 2 apply step of the original Session 2a sequence
  (cp of the 5 log-l1-* bindings followed by
  `validate-static-analysis-bindings.sh` reported 10
  failures: 5 from log-l1-* shape mismatch, 5 from latent
  Session 1 secrets-l1-* and deps-l1-* shapes never
  exercised by the original validator). The recovery
  authored two new schema variants and refactored all 10
  bindings to validate cleanly. The recovery is recorded
  as additional Session 2a authoring; cooling-off applies
  only to attestation commits per Section 2.4.1. Future
  sessions run all four validators iteratively during
  authoring to catch latent schema-vs-binding drift before
  apply time. Lesson added to HANDOFF.md Section 11.

All artifacts in this entry follow the substrate discipline
invariants documented in HANDOFF.md and CHARTER.md Article
III: SPDX-License-Identifier headers, no em-dashes or
en-dashes, one-way reference direction (substrate references
no consumer concepts), date format YYYY-MM-DD, author
identity `myoung`.

---

### Added

**M1 Session 1 deliverables (2026-05-19 through 2026-05-20):**
secrets-management and dependency-management concern catalogs
authored at lifecycle-status draft, with supporting artifacts and
profile integration.

Concern catalogs (both at `draft`):

- `catalogs/concerns/secrets-management.oscal.yaml` (8 rules:
  3 L1 mechanical SECRETS-L1-001 through SECRETS-L1-003,
  4 L2 semantic SECRETS-L2-001 through SECRETS-L2-004,
  1 L3 judgmental SECRETS-L3-001)
- `catalogs/concerns/dependency-management.oscal.yaml` (5 rules:
  2 L1 mechanical DEPS-L1-001 through DEPS-L1-002,
  2 L2 semantic DEPS-L2-001 through DEPS-L2-002,
  1 L3 judgmental DEPS-L3-001)

Decision frameworks (MADR-format, validate clean against
`schemas/decision-framework.schema.json`):

- `decision-frameworks/secrets-management-platform.madr.md`
  (5 options spanning single-cloud native, Vault self-managed,
  hybrid, Kubernetes-native operator, and deployment-platform-
  discouraged; 7 substrate-required decision drivers)
- `decision-frameworks/dependency-vetting-policy.madr.md`
  (4 options spanning strict allowlist, criteria-based gate,
  lightweight gate, and no-policy-discouraged; 7 substrate-
  required decision drivers)

Tool bindings:

- `tool-bindings/static-analysis/secrets-l1-001-no-secrets-in-source.yaml`
- `tool-bindings/static-analysis/secrets-l1-002-sensitive-files-gitignored.yaml`
- `tool-bindings/static-analysis/secrets-l1-003-no-secrets-in-logs.yaml`
- `tool-bindings/static-analysis/deps-l1-001-pinned-versions.yaml`
- `tool-bindings/static-analysis/deps-l1-002-vulnerable-dependencies.yaml`

Review checklists for all L2 and L3 rules:

- 4 secrets-management L2 checklists (SECRETS-L2-001 through L2-004)
- 1 secrets-management L3 checklist (SECRETS-L3-001)
- 2 dependency-management L2 checklists (DEPS-L2-001, L2-002)
- 1 dependency-management L3 checklist (DEPS-L3-001)

Test templates for all L2 rules (6 total):

- 4 secrets-management L2 test templates
- 2 dependency-management L2 test templates

Examples (good and anti-pattern, 26 files total):

- 16 secrets-management examples (8 good, 8 anti-pattern across
  the 8 rules)
- 10 dependency-management examples (5 good, 5 anti-pattern across
  the 5 rules)

### Changed

Profile `profiles/production-grade-baseline.oscal.yaml`:

- `imports` extended with `secrets-management.oscal.yaml`
  (8 rules) and `dependency-management.oscal.yaml` (5 rules)
- `modify.alters` extended with 13 new blocks recording profile
  selection rationale, severity confirmation, and AI-assistance
  metadata per Charter Article V Section 5.6
- `rule-selection-count` updated from `16` to `29`
- `back-matter.resources` extended with two new catalog
  resource entries
- `last-modified` updated to `2026-05-20T18:00:00Z`

Substrate version target: 0.2.0 → 0.3.0 (corresponds to the
secrets-management + dependency-management additions).

### Migration

No migration required for consumers currently inheriting from
`production-grade-baseline`. The 13 new rules engage as their
profile selections take effect; consumers with strict tilt
requirements may override severity or applicability in their
own inheriting profiles per Charter Article V Section 5.6.

The two new L3 rules (SECRETS-L3-001, DEPS-L3-001) require
consumers to author ADRs. Consumers entering production at
substrate version 0.3.0 should plan ADR authoring per the paired
MADR decision frameworks; consumers grandfathered from earlier
substrate versions may treat the L3 ADRs as a documented gap
with a remediation timeline.

Schema migration for static-analysis-binding 0.1.0 → 0.2.0
(Session 2a recovery): no consumer-side migration required.
All 0.1.0-valid bindings remain valid under 0.2.0; the schema
added two new binding-type values
(`multi-ecosystem-orchestration`, `scanner-orchestration`) and
permitted `engine-guidance-ref` on variants 2 and 3. Consumers
who author their own static-analysis bindings do not need to
modify existing bindings; new bindings may opt into the new
variants where appropriate.

### Authoring notes

All artifacts in this entry follow the substrate discipline
invariants documented in HANDOFF.md and CHARTER.md Article III:
SPDX-License-Identifier headers, no em-dashes or en-dashes,
one-way reference direction (substrate references no consumer
concepts), date format YYYY-MM-DD, author identity `myoung`.

---

**Prior Unreleased content (M0 structural work):**

Structural directories with READMEs to support catalog authoring,
profile authoring, mapping authoring, tool binding, decision
framework authoring, example collection, schema publication, and
substrate tooling. Directories are present but content is mostly
empty; subsequent commits populate them with format specifications,
schemas, the default profile, and the first concern catalog.

New directories:

- `catalogs/concerns/` for concern catalog content
- `catalogs/design-patterns/` for software design pattern catalogs
- `profiles/` for substrate-level tailoring profiles
- `mappings/` for cross-taxonomy relations
- `tool-bindings/` for Layer 1 mechanical enforcement bindings
  - `tool-bindings/semgrep/` for Semgrep YAML bindings
  - `tool-bindings/cedar/` for Cedar policy fragments
  - `tool-bindings/lint-configs/` for per-language lint config
    templates
  - `tool-bindings/benchmark-suites/` for performance budget
    benchmark templates
- `decision-frameworks/` for MADR-format Layer 3 decision support
- `examples/` for Layer 2 review support examples
- `schemas/` for JSON Schema validation
- `tooling/` for substrate-native utilities

This CHANGELOG.md itself is also added under this entry per Charter
Article VIII Section 8.1.

## [0.1.0] - 2026-05-17

Initial pre-stable release of the substrate's constitutional layer.

### Added

- `CHARTER.md` (substrate's supreme authority document, nine
  Articles in Article/Section format, covering nature
  and authority, authoring discipline, AI's role, catalog identity
  and immutability, profiles and tailoring, consultation evidence
  contract, compatibility with consumers, lifecycle and versioning,
  and amendments)
- `spec/consultation-evidence.md` (Article VI operationalized:
  semantic contract for what consumers must record when AI consults
  substrate content; medium-agnostic; consumers map required fields
  to their own audit medium)
- `spec/consumption-contract.md` (Article VII operationalized:
  bidirectional checklist of substrate obligations to consumers
  and consumer obligations to substrate)
- `spec/extension-contract.md` (Article V operationalized:
  procedures for tailoring without forking, profile authoring,
  custom catalog authoring, substrate contribution paths,
  composition across organizational altitudes)
- `spec/rule-lifecycle.md` (Article VIII operationalized: state
  machine for draft/stable/deprecated/retired transitions with
  entry criteria, transition procedures, version-bump rules,
  deprecation timing, and mechanical artifacts)

### Pre-existing content

The substrate inherited the following from prior development phases
before the Charter was authored. These remain in place under the
new authority structure:

- `spec/principles.md` (P1-P12 governance principles)
- `spec/architecture-rationale.md`
- `spec/audit-envelope.md`
- `spec/data-classification.md`
- `spec/identity-model.md`
- `spec/oscal-model.md`
- `spec/policy-dsl-choice.md`
- `catalogs/threats/` (OWASP LLM Top 10, OWASP Agentic ASI, MITRE
  ATLAS, STRIDE in custom YAML format)
- `catalogs/compliance/` (NIST 800-53, NIST CSF v2, NIST 800-171,
  NIST 800-218, NIST AI RMF, EU AI Act, plus ai-security-baseline
  and federal-bridge profiles, all in OSCAL format via Trestle)
- `policies/` (Cedar policies for runtime authorization)
- `playbooks/` (incident response playbooks)
- `attestation/` (SLSA, in-toto, cosign specifications)
- `lib-context/` (library-specific AI assistance context)
- `VERSION`, `README.md`, `PORTABILITY.md`, `MAINTENANCE.md`

This pre-existing content is treated as authored under the Charter's
authority retroactively. Future modifications follow Charter
discipline.

## Version notes

Pre-1.0 status: the substrate is in pre-stable development. Charter
Article IX Section 9.5 notes that expectations of stability during
pre-stable status are lower than they will be once the commons
reaches 1.0. Breaking changes during 0.x versions follow standard
deprecation procedures where feasible but may occur with shorter
windows when the substrate's authoring discipline matures.

Consumers integrating against pre-1.0 substrate accept this risk.
The substrate aims for 1.0 once the constitutional layer, structural
directories, format specifications, schemas, default profile, and
at least one concern catalog (authentication) have stabilized
end-to-end.
