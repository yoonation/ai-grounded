<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Rule Lifecycle

This document specifies the lifecycle of artifacts within Governance
Commons: how content enters the substrate, advances through states,
exits via deprecation, and is eventually retired. The lifecycle is
referenced by Article VIII of `CHARTER.md` and binds substrate
authoring discipline.

This document is the **operational state machine** for the lifecycle
principles in Article VIII. Where the Charter names the four states
(draft, stable, deprecated, retired) in principle, this document
specifies entry criteria, transition procedures, version-bump rules,
deprecation timing, and the mechanical artifacts that record each
transition.

## Why this contract exists

Governance content has a shelf life. Authoritative standards evolve
(NIST publishes new versions, OWASP rotates its top-10 every few
years, design patterns mature, new failure modes appear). The
substrate must evolve with them while maintaining the stability
consumers depend on.

Three failure modes the lifecycle prevents:

- **Premature stability**: content marked stable before it has been
  validated against real codebases produces confident wrong behavior
  at scale
- **Eternal draft**: content stuck in draft never reaches the
  consumers that need it, while consumers either work without it or
  build consumer-side equivalents that drift over time
- **Silent retirement**: content removed without warning breaks
  consumer integrations and consumer audit trails that referenced
  the retired identifiers

The lifecycle resolves these by specifying entry criteria, transition
procedures, and deprecation windows that protect consumers while
allowing the substrate to evolve.

## The lifecycle in one diagram

```
                      Charter Article II discipline
                                  │
                                  v
                            [PROPOSED]  (consumer or substrate
                                  │      contributor proposes
                                  │      content; not yet in
                                  │      substrate)
                                  │
                            Article II
                            review + accept
                                  │
                                  v
                            [DRAFT]     (in substrate;
                                  │      identifier reserved;
                                  │      not yet validated)
                                  │
                            validation +
                            two-human review
                                  │
                                  v
                            [STABLE]    (consumers may
                                  │      reference with
                                  │      stability guarantee)
                                  │
                            superseded by
                            new content
                                  │
                                  v
                            [DEPRECATED] (still consultable;
                                  │       consumers migrating)
                                  │
                            deprecation
                            window expires
                                  │
                                  v
                            [RETIRED]   (removed from active
                                         substrate; identifier
                                         reserved forever)
```

Transitions are one-directional. Reversal is not permitted. Content
that needs to return from a later state to an earlier state is
authored as new content with a new identifier.

## State definitions

### Proposed

Not yet substrate content. A proposal exists in the substrate's
contribution channel (issue, email, discussion, pull request) for
the substrate maintainer to evaluate.

A proposal includes:

- The intended catalog or extension to existing catalog
- The proposed rule identifier (or request for identifier assignment)
- The proposed intent statement
- Layer assignment (mechanical, semantic, judgmental) with rationale
- Severity assignment with rationale
- Three or more concrete examples per Charter Article II Section 2.3
- Authoritative source citation or original rationale
- Anti-pattern alongside the pattern where applicable

The substrate maintainer evaluates against Article II authoring
discipline. The proposal is either:

- **Accepted**: content enters draft state with assigned identifier
- **Returned**: proposer receives feedback for revision
- **Declined**: substrate maintainer explains why and the proposal
  closes; the proposer may pursue alternative resolution via
  Charter Article IX

Proposed content is not yet substrate content. It has no identifier
reservation, no consumer guarantees, no portability obligations.
The proposal lives in the contribution channel, not in the
substrate itself.

### Draft

Substrate content in early authoring. The identifier is reserved.
The content is present in the substrate but marked draft.

Properties of draft content:

- **Identifier**: assigned and reserved. Even if the draft never
  reaches stable, the identifier is not reused
- **Visibility**: present in substrate; consumers may consult but
  should not depend on stability
- **Default profile selection**: draft content may not be selected
  by the default profile or any substrate-shipped industry profile.
  Charter Article VIII Section 8.2 forbids draft content in
  default-profile content
- **Consumer-side selection**: consumers may select draft content in
  consumer-side profiles, accepting the integration risk
- **Modification**: draft content may be modified freely, including
  changes to intent text. Article IV's immutability rule applies
  only to stable content
- **Retirement of draft content**: a draft may be abandoned. The
  abandonment is recorded in `CHANGELOG.md`. The identifier remains
  reserved per Article VIII Section 8.2 (never reused)

### Stable

Substrate content that has met Article II quality bar and Charter
Article II Section 2.4 review discipline. Consumers depend on
stable content with the guarantees in Article IV (identifier
immutability, intent immutability).

Properties of stable content:

- **Identifier**: immutable per Article IV Section 4.1
- **Intent statement**: immutable per Article IV Section 4.2
- **Tailorable properties**: severity, applicability, parameters,
  enforcement binding per Article IV Section 4.3 (consumers tailor
  via profiles)
- **Default profile selection**: stable content may be selected by
  default profile, industry profiles, and consumer-side profiles
- **Modification**: editorial corrections permitted per Article IV
  Section 4.2 (typos, formatting, clarifying phrasing that does not
  change meaning). Material changes require retirement and new
  content
- **Deprecation procedure**: stable content moves to deprecated
  when superseded by other content or when its underlying
  authoritative source is updated. Deprecation is procedural, not
  automatic

### Deprecated

Substrate content that is being phased out. Still consultable,
still has all stable-status guarantees during the deprecation
window, but consumers are notified to migrate.

Properties of deprecated content:

- **Identifier and intent**: still immutable
- **Tailorable properties**: still tailorable
- **Default profile selection**: typically removed from default
  profile selection in the same release that deprecates the
  content; the superseding content is added to default profile
- **Industry profile selection**: depends on the industry profile
  maintainer's choice; deprecated content may remain selected in
  industry profiles during deprecation window
- **Modification**: editorial only, same as stable
- **Superseding reference**: deprecated content includes a reference
  to the superseding content's identifier, so consumers know what
  to migrate to
- **Deprecation window**: minimum one major version cycle per
  Charter Article VIII Section 8.3
- **Pre-retirement signal**: the substrate issues a signal in
  `CHANGELOG.md` and `MAINTENANCE.md` at the start of the major
  version cycle that retires the content

### Retired

Content removed from active substrate. The identifier is reserved
forever and never reused. Historical references remain interpretable
via `CHANGELOG.md`.

Properties of retired content:

- **Identifier**: reserved, never reused
- **Intent statement**: preserved in `CHANGELOG.md` for historical
  reference
- **Active substrate presence**: removed from substrate files. The
  retired content is not consultable at runtime
- **Profile references**: any substrate profile that referenced the
  retired identifier is updated in the same version as retirement
  to remove the reference
- **Consumer-side references**: consumer profiles that still
  reference retired identifiers encounter resolution errors at
  profile resolution time. The substrate documented the impending
  retirement during the deprecation window; consumer migration is
  the consumer's responsibility per Charter Article VII

## State transition procedures

### Proposed -> Draft (acceptance)

Triggered by:

- Substrate maintainer accepts the proposal per Article II review

Required actions:

- Assign the artifact identifier (substrate maintainer or proposer
  proposes; maintainer confirms)
- Write the artifact in substrate-appropriate location
  (catalogs/concerns/, profiles/, mappings/, decision-frameworks/,
  examples/)
- Mark lifecycle status as `draft` in the artifact's metadata
- Record provenance per Article II Section 2.2 (author of record,
  date authored, AI assistance acknowledged, authoritative source
  if any)
- Add an entry to `CHANGELOG.md` describing the new draft and its
  identifier
- Increment substrate version per semantic versioning (typically
  minor or patch increment for draft additions)
- Commit the change with a commit message that references the
  proposal and the substrate maintainer's acceptance

Required artifact metadata:

```yaml
lifecycle:
  status: draft
  entered_status_at: 2026-05-17
  identifier_reserved: true
provenance:
  author: <human identity>
  authored: <date>
  authoritative_source: <URL or canonical reference; null if original>
  ai_assistance: <none | proposed | drafted | validated; or specific
                  description>
```

### Draft -> Stable (promotion)

Triggered by:

- Article II Section 2.4 review by a human distinct from the author
- The review confirms the rule's intent is clearly stated, examples
  demonstrate the rule, severity and layer assignments are
  defensible, provenance is complete, and the content does not
  conflict with existing substrate content
- Validation against at least one real codebase confirms the rule
  behaves as intended (per Article II Section 2.3 "validation
  against real codebases before stable promotion")

Required actions:

- Update artifact metadata `lifecycle.status` from `draft` to
  `stable`
- Update `lifecycle.entered_status_at` to the stable promotion date
- Record reviewer identity in `provenance.reviewer` and review date
  in `provenance.reviewed_at` per Article II Section 2.2
- Add an entry to `CHANGELOG.md` describing the promotion
- Increment substrate version per semantic versioning (typically
  minor for first-time stable promotion of a draft)
- If the artifact is suitable for default profile selection, the
  default profile is updated in the same version to include it
  (when appropriate; not all stable content goes in default
  profile)

Required artifact metadata after promotion:

```yaml
lifecycle:
  status: stable
  entered_draft_at: 2026-05-17
  entered_stable_at: 2026-06-15
  identifier_reserved: true
provenance:
  author: <human identity>
  authored: <date>
  authoritative_source: <URL or null>
  ai_assistance: <description>
  reviewer: <distinct human identity>
  reviewed: <review date>
```

Stable promotion is the most consequential transition in the
lifecycle. It is the moment Article IV immutability begins to apply.
Errors caught after stable promotion cannot be silently corrected;
they require either editorial correction (per Article IV Section
4.2) for non-material issues, or deprecation and replacement for
material issues.

### Stable -> Deprecated (supersession)

Triggered by:

- The substrate authors superseding content with a new identifier
  that captures the corrected intent, broader applicability, or
  updated authoritative source
- OR the substrate determines that the rule is no longer reflective
  of current best practice (e.g., the practice it encodes has been
  superseded industry-wide)

Required actions:

- Update artifact metadata `lifecycle.status` from `stable` to
  `deprecated`
- Update `lifecycle.entered_deprecated_at` to the deprecation date
- Set `lifecycle.superseded_by` to the identifier of the superseding
  content (if applicable; may be null if deprecation is due to
  obsolescence without replacement)
- Set `lifecycle.deprecation_window_ends` to the projected
  retirement date (at least one major version cycle away per
  Article VIII Section 8.3)
- Update the default profile (and substrate-shipped industry
  profiles) to swap the deprecated identifier for the superseding
  identifier where applicable
- Add an entry to `CHANGELOG.md` describing the deprecation,
  referencing the superseding content, and stating the retirement
  schedule
- Update `MAINTENANCE.md` to list the deprecated artifact in the
  deprecation tracking section
- Increment substrate version per semantic versioning (deprecation
  is non-breaking; minor version increment is sufficient unless the
  deprecation accompanies other breaking changes)

Required artifact metadata after deprecation:

```yaml
lifecycle:
  status: deprecated
  entered_draft_at: 2026-05-17
  entered_stable_at: 2026-06-15
  entered_deprecated_at: 2027-03-01
  superseded_by: <new artifact identifier or null>
  deprecation_window_ends: 2028-03-01
  identifier_reserved: true
```

### Deprecated -> Retired (removal)

Triggered by:

- The deprecation window has elapsed per Article VIII Section 8.3
- The substrate maintainer confirms the retirement is appropriate

Required actions:

- Remove the artifact file from active substrate location
- Add the retirement record to `CHANGELOG.md` including the
  artifact's identifier, intent statement (preserved for historical
  reference), retirement date, and superseding identifier if any
- Update `MAINTENANCE.md` to move the entry from deprecation
  tracking to retirement record
- Update any substrate profiles that still referenced the retired
  identifier to remove the reference
- Increment substrate version per semantic versioning. Retirement
  is breaking (Article VIII Section 7.5 lists retirement as a
  breaking change) and requires major version increment
- Issue migration guidance in `CHANGELOG.md` for consumers that
  may still be referencing the retired identifier

Once retired, the artifact's identifier remains reserved. The
substrate never reuses the identifier. Future content with similar
intent gets a new identifier per Article IV Section 4.2.

Historical record in `CHANGELOG.md`:

```
[2.0.0] - 2028-03-15
### Retired
- authentication.generic-failure-responses (was: "Auth tokens never appear in URLs")
  Retired after deprecation since 1.4.0 (2027-03-01).
  Superseded by authentication.no-hardcoded-credentials ("Sensitive identifiers never in URLs;
  applies to tokens, session IDs, and PII").
  Identifier authentication.generic-failure-responses remains reserved.
```

### Draft -> Retired (abandonment)

Triggered by:

- Draft content is determined to be inappropriate for the substrate
- Or the proposer withdraws the proposal during draft authoring
- Or the content fails validation and is not salvageable

Required actions:

- Remove the draft artifact from substrate
- Add an abandonment entry to `CHANGELOG.md` including the
  identifier and reason for abandonment
- The identifier remains reserved per Article VIII Section 8.2
- Increment substrate version per semantic versioning (draft
  abandonment is typically a minor or patch increment since
  consumers should not have been depending on draft content)

Draft abandonment does not require a deprecation window because
draft content does not carry stability guarantees. Consumers that
chose to integrate against draft content accepted the risk.

### Forbidden transitions

The following transitions are not permitted:

- **Stable -> Draft**: stable content does not revert to draft. If
  stable content has issues, it is either corrected editorially
  (Article IV Section 4.2) or deprecated and replaced
- **Deprecated -> Stable**: deprecated content does not become
  stable again. If a deprecated rule should remain in use, the
  deprecation is reversed only by issuing a new artifact with a new
  identifier that captures the rule (and the deprecated artifact
  proceeds to retirement on its schedule)
- **Retired -> any other state**: retired content is permanently
  retired. New content with similar intent gets a new identifier
- **Skip states**: content does not move directly from stable to
  retired without passing through deprecated; consumers receive the
  deprecation window protection per Article VIII Section 8.3

## Version bump rules

The substrate version (in `governance-commons/VERSION`) follows
semantic versioning per Charter Article VIII Section 8.1. Lifecycle
transitions trigger version bumps as follows.

| Transition | Substrate version bump | Reasoning |
|---|---|---|
| Proposed -> Draft | PATCH or MINOR | Addition of new content, non-breaking |
| Draft -> Stable | MINOR | Promotion adds functionality; non-breaking |
| Stable -> Deprecated | MINOR | Deprecation is announcement; rule still works |
| Deprecated -> Retired | MAJOR | Retirement removes content; breaking |
| Draft -> Retired | PATCH or MINOR | Draft was not depended upon; non-breaking |
| Editorial correction (any state) | PATCH | Non-material change |
| New profile addition | MINOR | New tailoring option |
| Profile default change (e.g., new rule added to default profile) | MINOR | Consumer profiles inheriting will pick up; non-breaking |
| Profile default removal (rule excluded from default profile that was previously included) | MINOR | Consumers may need to add the rule explicitly if they want it; documented as non-breaking but worth noting |
| Schema change (additive) | MINOR | New optional fields |
| Schema change (breaking) | MAJOR | Required field changes |

Multiple transitions may occur in a single version. The highest-tier
transition determines the version bump. A MINOR version may include
PATCH-level changes; a MAJOR version may include MINOR and PATCH
changes alongside the breaking transition that motivates it.

## Deprecation timing

Charter Article VIII Section 8.3 requires at least one major version
cycle of deprecation before retirement. This section operationalizes
the timing.

### Standard deprecation window

For most stable content, the deprecation window is one full major
version cycle.

Example timeline:

```
Substrate version 1.x.x → content stable
Substrate version 2.0.0 → content deprecated; superseding content added
Substrate version 3.0.0 → deprecated content retired
```

In this example, content is consultable across all of 2.x.x. Consumer
migration is expected during the 2.x.x cycle.

### Extended deprecation window

Some content warrants a longer deprecation window:

- Content widely adopted across the consumer ecosystem
- Content that maps to compliance regimes still in effect
- Content whose superseding rule requires significant consumer
  refactoring

The substrate maintainer may extend the deprecation window for such
content. Extension is recorded in `MAINTENANCE.md` with rationale.

Consumers receive notice of extensions through the same `CHANGELOG.md`
mechanism as standard deprecations.

### Shortened deprecation window

In exceptional circumstances, the substrate may shorten a deprecation
window:

- The deprecated content is causing security harm (a rule that
  inadvertently encodes a vulnerability)
- The deprecated content references an external standard that has
  been withdrawn or revised in ways that make the deprecated content
  actively misleading

Shortening requires substrate maintainer authority and a recorded
rationale in `MAINTENANCE.md`. The minimum window even under
shortening is one minor version cycle, so consumers always have at
least one release to react.

### Indefinite deprecation

Some content may be deprecated without a scheduled retirement date.
This is appropriate when:

- The content is still useful for some consumers but no longer
  reflects the substrate's recommended approach
- The substrate maintainer wants to signal "do not select this in
  new profiles" without removing the content from existing consumer
  profiles

Indefinite deprecation is recorded in `MAINTENANCE.md` with rationale.
The content remains in the substrate at deprecated status.

## Mechanical artifacts

The lifecycle generates several mechanical artifacts that consumers
and substrate maintainers depend on.

### CHANGELOG.md

The substrate's authoritative record of state transitions. Every
transition produces an entry. Entries follow Keep a Changelog format
(keepachangelog.com) with substrate-specific sections:

- **Added**: new draft or stable content
- **Promoted**: draft -> stable transitions
- **Deprecated**: stable -> deprecated transitions
- **Retired**: deprecated -> retired transitions
- **Abandoned**: draft -> retired transitions
- **Changed**: editorial corrections, profile modifications
- **Migration**: guidance for consumers reacting to lifecycle
  changes

Each entry includes the affected artifact identifier, the
transition date, references to superseding content if applicable,
and any migration guidance.

### MAINTENANCE.md

The substrate's operational tracking document. Lifecycle-related
sections include:

- **Deprecation tracking**: all currently deprecated artifacts with
  superseding identifiers, deprecation dates, and projected
  retirement dates
- **Indefinite deprecations**: artifacts deprecated without
  retirement schedule, with rationale
- **Extended windows**: artifacts with extended deprecation windows,
  with rationale
- **Retirement record**: artifacts retired, with identifier reservation
  preserved and superseding identifier recorded

### Artifact metadata

Every substrate artifact includes a `lifecycle` metadata block
documenting its current state, transition dates, and (when
applicable) superseding identifier. The metadata block is
machine-parseable so tooling can compute deprecation windows,
generate consumer migration reports, and validate lifecycle
discipline.

### Substrate version

The `governance-commons/VERSION` file is the substrate's
authoritative version. Every lifecycle transition that triggers a
version bump updates the VERSION file in the same commit.

## Consumer responsibilities

Consumers track substrate lifecycle to maintain integration
integrity. Consumer responsibilities per Charter Article VII:

### Pinning substrate version

Consumers reference specific substrate versions per the consumption
contract. Pinning protects consumers from unexpected lifecycle
transitions during their own development cycles.

### Tracking deprecation announcements

Consumers monitor `CHANGELOG.md` (or substrate release announcements)
to learn of deprecations affecting their profile selections.

### Migrating during deprecation windows

Consumers update their profiles to select superseding content during
the deprecation window. Migration before retirement avoids resolution
errors at the consumer's profile resolution.

### Handling retirements

Consumer profiles that still reference retired identifiers after the
retirement version encounter resolution errors. Consumers either:

- Migrate to the superseding identifier (the substrate's recommended
  path)
- Pin to the pre-retirement substrate version, accepting that they
  will not benefit from substrate evolution beyond that version
- Author consumer-side rules with the retired intent and
  consumer-namespaced identifiers, accepting maintenance burden

The substrate provides the deprecation window so consumers have
time to choose deliberately. Retirement without prior deprecation
is a substrate defect; consumer surprise at retirement after the
window is a consumer integration defect.

## Boundary cases

### A stable rule is found to be incorrect

Editorial correction (Article IV Section 4.2) applies only to typos,
formatting, or clarifying phrasing that does not change meaning.

If the rule's intent is incorrect (the rule says X but should say Y,
where X and Y are different meanings), correction requires:

1. Author a new artifact with a corrected identifier and intent
2. Deprecate the incorrect artifact with reference to the new one
3. The new artifact follows draft -> stable promotion

The incorrect rule is not silently rewritten. Consumers that adopted
the incorrect rule see the deprecation and migrate to the corrected
version.

### A draft rule needs urgent stable promotion

The substrate may accelerate promotion when consumer demand or
substrate strategy warrant. Acceleration does not bypass Article II
Section 2.4 review discipline; it shortens the time to review and
validation.

The minimum acceleration: same-day promotion if reviewer is
available, validation example exists, and the content is genuinely
ready. Faster promotion increases the risk of post-promotion
discovery of issues. The substrate maintainer weighs the trade-off.

### A deprecated rule reveals new relevance

If a deprecated rule turns out to still be needed (e.g., the
superseding rule is found to miss a case the deprecated rule
covered):

1. Author a new stable artifact that captures the case (do not
   un-deprecate the original; Forbidden transitions section above)
2. Deprecate the superseding rule if appropriate, or extend it via
   a new artifact

The deprecated rule continues its retirement schedule. The
"recovered" case is handled by new content.

### A consumer-side custom rule should become substrate

The consumer proposes via the contribution path. The proposal enters
the proposed state and follows the standard lifecycle from there.

The original consumer-side identifier (consumer-namespaced) and the
substrate identifier are different artifacts. The consumer's
original artifact remains at consumer-side; the substrate version
is a separate artifact with substrate-assigned identifier.

After substrate acceptance, the consumer migrates their profile to
reference the substrate identifier and deprecates their own
consumer-side version per their own discipline.

### A profile is deprecated

Profiles follow the same lifecycle as catalog content. A deprecated
profile is still consultable; consumers using it migrate to a
superseding profile during the deprecation window.

### An entire catalog is deprecated

A catalog deprecation deprecates all rules in the catalog. The
superseding catalog (if any) is referenced. Consumers using rules
from the deprecated catalog migrate to corresponding rules in the
superseding catalog.

Wholesale catalog deprecation is rare. It typically reflects a
substantial reorganization of a concern area.

### Schema versioning

Schemas in `governance-commons/schemas/` are themselves lifecycled
artifacts. Schema versions follow the same state machine. Schema
deprecation gives consumers a window to migrate their integration
to the new schema.

## Versioning of this contract

This contract is versioned with the commons. Changes follow Charter
Article VIII versioning discipline.

Current contract version: **0.1.0** (matches commons version)

### Breaking changes to this contract

The following are breaking under semver:

- Changing required actions for any transition
- Adding new required fields to artifact metadata
- Shortening the standard deprecation window
- Adding a forbidden transition that was previously permitted

### Non-breaking changes to this contract

The following are non-breaking:

- Adding optional fields to artifact metadata
- Clarifying procedures without changing meaning
- Adding boundary cases or examples
- Extending the deprecation window
- Adding new permitted transitions

## What this contract is not

To clarify boundaries:

- This contract is not a release management process for consumer
  projects. Consumers manage their own releases independently of
  substrate releases.
- This contract is not a compliance regime for the substrate itself.
  The substrate is not certified against any compliance framework;
  it provides content to help consumers achieve compliance.
- This contract is not a deprecation policy for consumer-side
  artifacts. Consumers manage consumer-side artifact lifecycle per
  their own discipline.
- This contract is not a migration tool. Tooling that helps
  consumers migrate from deprecated content lives in
  `governance-commons/tooling/`; this document specifies the
  semantics tooling supports.

## Closing

The lifecycle exists so that the substrate can evolve while
consumers can depend on it. Evolution without lifecycle discipline
produces silent breakage. Stability without evolution produces
substrate stagnation. The lifecycle is the structured middle path.

The four states are not bureaucratic ceremony; they are the
mechanism by which consumers know what they can depend on, what
they should migrate from, and what is permanently gone. Each state
transition is recorded mechanically so the substrate's history is
itself auditable.

When the lifecycle feels constraining, the resolution is amendment
under Charter Article IX, not silent shortcut. The substrate's
value comes from consumers trusting its stability. That trust is
built one disciplined transition at a time.
