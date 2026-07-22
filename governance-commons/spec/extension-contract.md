<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Extension Contract

This document specifies the procedures for tailoring Governance
Commons to organizational, industry, project, or use-case needs. The
contract is referenced by Article V of `CHARTER.md` and binds
consumers who modify substrate behavior or extend substrate content.

This document is the **operational procedures** for the principles
in Article V. Where the Charter says "consumers may tailor via
profiles" in principle, this document says how, with concrete steps,
constraints, and submission paths.

## Why this contract exists

The substrate is opinionated by default. No two organizations have
identical engineering values. The tension between substrate opinion
and organizational reality is resolved through tailoring.

Three failure modes the contract prevents:

- **In-place modification of substrate content.** A consumer that
  edits substrate files directly forks silently and accumulates
  drift. The substrate's portability is broken; the consumer no
  longer benefits from substrate updates.
- **Profile sprawl.** A consumer that creates dozens of profiles for
  small variations loses the benefit of profile inheritance and
  obscures their actual stance. The substrate becomes harder to
  reason about, not easier.
- **Custom-catalog isolation.** A consumer authors a custom catalog
  that solves a real problem but never proposes it back. Other
  consumers reinvent the same content. The substrate fails to
  capture community knowledge.

The contract resolves these by specifying clear procedures for each
tailoring action, by setting limits on what tailoring can do, and by
providing a path from consumer-side innovation back to substrate
adoption.

## The contract in one sentence

Tailoring occurs through profiles that select and modify substrate
content, custom catalogs that namespace consumer-specific content,
and a substrate contribution path that promotes generally-useful
consumer-side content into the substrate.

## Tailoring mechanisms

The substrate supports four tailoring mechanisms, in order of
preference. Use the lightest mechanism that solves the consumer's
problem.

### Mechanism 1: Profile selection (no authoring)

A consumer whose values match an existing profile selects that
profile directly. No authoring required.

The substrate ships:

- `production-grade-baseline` (the opinionated default)
- Industry profiles for common tilts (financial services, healthcare,
  regulated AI, etc.)
- Use-case profiles for common scenarios

Most consumers can find a profile that fits. Adoption is one
declaration in the consumer's manifest or constitution.

### Mechanism 2: Consumer-side profile inheritance

A consumer whose values partially match an existing profile inherits
from it and modifies. Modifications are scoped to what Charter
Article IV Section 4.3 permits as tailorable: severity assignments,
applicability scope, parameters, enforcement bindings.

The consumer authors a profile consumer-side, declares which
substrate profile it inherits from, and records modifications with
rationale per Charter Article V Section 5.5.

This is the mechanism most enterprise consumers use.

### Mechanism 3: Custom catalogs (consumer-side, namespaced)

A consumer with concerns the substrate does not cover authors a
custom catalog consumer-side. The catalog follows substrate format
conventions but uses a consumer namespace for identifiers to avoid
collision with substrate content.

Custom catalogs may be referenced by consumer-side profiles
alongside substrate catalogs. The consumer's audit medium records
consultation of custom catalogs the same way it records substrate
catalogs.

Custom catalogs that achieve general utility may be proposed for
substrate inclusion per Mechanism 4.

### Mechanism 4: Substrate contribution

A consumer with content of general utility proposes it for inclusion
in the substrate. The proposal goes through Charter Article II
authoring procedures. If accepted, the content becomes substrate
content and is subject to substrate authority and lifecycle.

Substrate contribution converts consumer-side innovation into
substrate value for all consumers. It is the path through which the
substrate grows.

## Profile authoring procedures

### Selecting a parent profile

Every consumer-side profile inherits from at least one substrate
profile. The parent is declared explicitly. The substrate supports
single inheritance (one parent profile) as the default; multiple
inheritance is permitted but requires more careful merge handling
and is recommended only when single inheritance does not capture the
desired baseline.

Parent profile selection criteria:

- Choose the parent closest to the consumer's desired stance
- Prefer industry profiles over the default profile when the
  consumer's industry has a published profile
- Prefer specific over general (a healthcare consumer inherits from
  `healthcare`, not from `production-grade-baseline`, because the
  healthcare profile already inherits from the default)

### Permitted modifications

A consumer-side profile may modify:

- **Control selection**: which rules from substrate catalogs are
  active for this consumer. The profile may include rules the parent
  excludes, or exclude rules the parent includes.
- **Severity assignment**: profile-specific severity per rule. A
  consumer may set a substrate rule to P1 in their context where
  the parent profile sets it to P2, or vice versa.
- **Applicability scope**: which features, languages, environments
  this rule applies to in the consumer's context. Narrowing scope is
  weakening (requires rationale per Charter Article V Section 5.5);
  broadening scope is strengthening (no rationale required per
  Section 5.6).
- **Parameters**: rule parameters the substrate defines as
  configurable. Specific thresholds, timeouts, sizes, counts.
- **Enforcement bindings**: which specific tool enforces a
  mechanical rule for this consumer's stack. The substrate provides
  default bindings; consumers may override per their toolchain.

### Forbidden modifications

A consumer-side profile may not:

- **Change rule identity or intent** (Charter Article IV Sections
  4.1 and 4.2 forbid this; profile modifications are tailoring, not
  reauthoring)
- **Remove rules from substrate catalogs** (profiles may exclude
  rules via non-selection; they cannot delete rules from the
  substrate)
- **Reference consumer-side content from substrate-side profiles**
  (only consumer-side profiles may reference custom catalogs; this
  prevents portability rule violations)
- **Bypass the audit medium** (a profile that disables consultation
  evidence recording is not satisfying Charter Article VI)

### Rationale recording for weakening

Charter Article V Section 5.5 requires rationale when a profile
weakens defaults. Acceptable rationale forms:

- A statement in the profile's metadata referencing the consumer's
  ADR that justifies the weakening
- An inline rationale field on the modification itself
- A reference to a documented organizational decision (compliance
  finding, audit recommendation, regulatory requirement, risk
  acceptance) that motivates the weakening

What counts as weakening:

- Lowering severity (P1 to P2, P2 to P3)
- Narrowing applicability (the rule now applies to fewer features,
  languages, or environments)
- Excluding a rule the parent profile includes
- Relaxing parameters (longer timeout, larger threshold, looser
  validation)
- Replacing an enforcement binding with a less strict tool

What does not count as weakening (no rationale required):

- Adding rules the parent profile does not include
- Raising severity (P3 to P2, P2 to P1)
- Broadening applicability
- Tightening parameters
- Replacing an enforcement binding with a stricter tool
- Authoring a custom catalog that adds new rules

## Custom catalog authoring procedures

### Naming and namespacing

Custom catalog identifiers must namespace the consumer to avoid
collision with substrate content. Recommended pattern:

```
<consumer-namespace>.<catalog-name>
```

Examples:

- `acme-corp.internal-auth-patterns`
- `bigbank.regulatory-reporting`
- `clinicalapp.fhir-compliance`

The consumer-namespace prefix is the consumer's choice. The
substrate reserves no specific prefix; consumers ensure their
namespace is unique within their integration scope.

Rule identifiers within a custom catalog follow the substrate
convention (a kebab-case rule slug; the rule's layer lives in
`rule.yaml`, not in the identifier) but inherit the catalog's
namespace prefix:

```
acme-corp.internal-auth-patterns.sso-token-lifetime
```

This ensures consumer rule IDs never collide with substrate rule IDs
even if the substrate later adds rules in a similar domain.

### Catalog format

Custom catalogs follow the catalog format specified in
`spec/catalog-format.md`. The format is consumer-agnostic; substrate
and consumer catalogs use the same structure.

Custom catalogs that fail to follow the catalog format may not be
referenced by manifests that satisfy the consultation evidence
contract. Consumers that author custom catalogs without following the
format have lighter integration; they cannot mechanically validate
their catalogs against substrate schemas.

### Catalog quality

Charter Article II authoring discipline applies to substrate content.
The substrate does not enforce it on consumer-side custom catalogs.
However, consumers who do not apply the discipline to their own
catalogs reproduce the failure modes the discipline prevents:

- Sloppy rules create confident wrong behavior in consumer workflows
- Missing provenance makes consumer audit trails incomplete
- Absence of review introduces consumer-specific defects

The substrate recommends consumers apply Charter Article II to
custom catalogs even though the substrate cannot enforce it. This is
discipline, not contract; consumers are free to set their own bar.

### Custom catalog scope

Custom catalogs cover concerns the substrate does not cover. They
should not duplicate substrate content.

Two failure modes to avoid:

- **Reinvention**: a custom catalog that re-encodes content already
  in the substrate. Use the substrate version; if the substrate
  version is wrong or incomplete, propose a substrate change rather
  than maintaining a parallel local version.
- **Override**: a custom catalog whose rules contradict substrate
  rules. If substrate rule X says Y and a custom rule says not-Y,
  the consumer has a conflict. Resolve by profile exclusion of X
  with rationale, not by competing rules.

## Custom profile authoring procedures

Custom profiles are profiles consumers author themselves
(distinguished from custom catalogs above, which are rule
collections).

### Single-organization profiles

The common case. An organization tailors substrate profiles to its
specific stance. The organization's profile inherits from a substrate
profile (industry or default), applies organization-specific
modifications, and may select from custom catalogs the organization
also authors.

Single-organization profiles are organization-internal. They are
versioned by the organization. The substrate makes no claim on them.

### Multi-project profiles

An organization may author multiple profiles for different project
types (consumer-facing services, internal tools, infrastructure,
data pipelines). Each profile inherits from a substrate profile and
applies project-type-specific modifications.

Per-project profiles are recommended over per-team or per-engineer
profiles. Granularity should match real engineering distinctions, not
organizational politics.

### Per-feature profiles

Generally not recommended. A profile per feature creates profile
sprawl that obscures the consumer's actual stance. Per-feature
tailoring is better expressed as feature-specific applicability
within a profile, or as feature-specific ADRs that record exceptions
to the profile.

When per-feature profiles are unavoidable (e.g., a single feature
has wildly different governance needs than the rest of the project),
the substrate permits them but considers them an integration smell
worth periodic review.

## Submission back to the substrate

Consumer-side content of general utility may be proposed for
substrate inclusion. This section describes the submission procedure.

### What is appropriate for substrate inclusion

Substrate-suitable content has these characteristics:

- **General applicability**: useful to more than one organization,
  more than one industry, more than one project type
- **Not organization-specific**: free of references to a specific
  organization's internal tooling, terminology, or processes
- **Defensible content**: meets Charter Article II quality bar
  (citations, examples, severity rationale, layer rationale)
- **Compatible with substrate authority**: respects rule
  immutability, the AI-authoring rule, the portability rule

### What is not appropriate for substrate inclusion

The following stay consumer-side:

- Organization-internal patterns specific to one organization
- Content that violates the portability rule (references to specific
  consumer architectures or tools the substrate does not adopt)
- Content that contradicts existing substrate content without
  reconciliation
- Speculative content not yet validated against real codebases
- Content under licenses incompatible with the substrate's license
  (currently Apache 2.0)

### Submission procedure

In the current pre-1.0 substrate, submission is informal:

1. Open a discussion (issue, email, equivalent) with the substrate
   maintainer
2. Describe the content, its rationale, and why it has general
   utility
3. Attach the content in substrate-compatible format
4. Respond to substrate maintainer review feedback
5. Iterate until the content meets Article II discipline or is
   declined

As the substrate matures, submission procedures formalize. Future
versions of this document will describe the formal procedure when it
exists. For now, the procedure is dialogue with the substrate
maintainer of record (see `MAINTENANCE.md`).

### What happens after submission

If accepted:

- The content enters the substrate in draft status per Charter
  Article VIII Section 8.2
- The original consumer is credited in provenance per Article II
  Section 2.2
- The substrate version bumps per semantic versioning rules
- The content migrates to stable status after Article II Section 2.4
  review

If declined:

- The substrate maintainer provides reasoning
- The consumer may rework and resubmit, accept the decline and keep
  the content consumer-side, or pursue alternative resolution
  through Charter Article IX procedures

The substrate maintainer's decline is not a value judgment on the
content's correctness; it reflects the content's fit with the
substrate's scope and direction.

### Substrate-promoted content vs consumer-retained content

After substrate promotion, the consumer's local copy of the content
becomes redundant. The consumer migrates to the substrate version:

1. Adjust consumer-side profile to select the substrate version
2. Remove the consumer-side custom version
3. Verify the consumer's audit medium shows references to the
   substrate identifier going forward

The consumer-side version may remain in repository history for
audit. The active reference moves to the substrate.

## Tailoring at multiple altitudes

Tailoring occurs at multiple levels of organizational granularity.
This section describes how they compose.

### Organization-level tailoring

An organization adopts a substrate profile or authors a top-level
organization profile that inherits from a substrate profile. This
sets the organization's baseline stance.

Example chain:

```
substrate.production-grade-baseline
  -> substrate.financial-services
    -> bigbank.banking-baseline
```

The organization's baseline inherits from an industry profile,
which inherits from the substrate default. Modifications at each
level layer additively.

### Project-level tailoring

Projects within an organization may inherit from the organization
profile and apply project-specific modifications.

Example chain:

```
bigbank.banking-baseline
  -> bigbank.consumer-mobile-app
  -> bigbank.fraud-detection-pipeline
  -> bigbank.regulatory-reporting-service
```

Each project profile applies project-specific modifications. Common
project tailorings: language-specific binding choices, project-scoped
parameters, project-specific applicability.

### Feature-level tailoring

Generally not recommended as profiles. Feature-specific exceptions
to a project profile are better recorded as feature-specific ADRs
that document the exception with rationale, rather than as separate
profiles.

When feature-level profiles are necessary, they follow the same
authoring procedures as project-level profiles.

### Resolving profile composition

When multiple profiles compose (substrate -> industry -> org -> project),
the substrate's profile resolver (in `tooling/`) produces a flat
effective profile for runtime consultation. The flat profile contains
the union of selections with modifications applied per inheritance
order: later profiles override earlier profiles.

Conflicts in composition (one profile selects a rule, another
excludes it) are resolved by the later profile in inheritance order.
The flat profile records resolution decisions for audit visibility.

## Boundary cases

### A consumer wants to disable a default-profile rule organization-wide

The consumer authors an organization profile that inherits from the
default profile and excludes the rule with rationale per Charter
Article V Section 5.5. The exclusion is recorded in the profile
itself; no substrate change is needed.

### A consumer wants a custom severity for a substrate rule

The consumer's profile sets the severity per profile per Section
4.3. This is permitted tailoring, not modification of substrate
content. No rationale required if strengthening; rationale required
if weakening.

### A consumer wants to add a rule to a substrate catalog

The consumer cannot add rules to substrate catalogs directly. Two
paths:

- If the rule has general utility, propose it for substrate inclusion
  via the submission procedure above
- If the rule is consumer-specific, author it in a custom catalog
  with consumer namespace

The consumer's profile may then select from both substrate and
custom catalogs.

### A consumer wants to deprecate a substrate rule

Consumers cannot deprecate substrate rules. Substrate rules are
deprecated by the substrate per Charter Article VIII Section 8.3.

If the consumer believes a rule should be deprecated, they:

- Open a discussion with the substrate maintainer recommending
  deprecation
- In the interim, exclude the rule via profile per Article V
  Section 5.5 with rationale

The substrate decides deprecation independently. The consumer's
recommendation is input, not authority.

### A consumer has conflicting requirements from multiple compliance regimes

The substrate provides mappings between compliance regimes
(`mappings/`) so consumers can see which substrate rules satisfy
which compliance controls.

When compliance regimes conflict (one requires data retention, one
requires data minimization), the consumer authors organization-level
ADRs that document how the conflict is resolved in their context.
The profile reflects the resolution; the substrate provides the
mappings to verify both regimes are addressed where they agree.

The substrate does not adjudicate between compliance regimes; it
provides the mapping data so consumers can.

### A consumer integrates the substrate without manifests

The substrate's manifest format is provided for consumers that adopt
manifest-driven workflows. Consumers with other workflow styles
(direct invocation, hard-coded integration, policy-as-code without
manifests) may use the substrate without a manifest.

Such consumers still satisfy the consultation evidence contract per
Charter Article VI when their workflow involves AI consultation of
commons content. The manifest mechanism is a convenience for
manifest-driven consumers; it is not a substrate requirement.

### A consumer wants to swap the enforcement binding for an L1 rule

Permitted tailoring per Article IV Section 4.3. The consumer's
profile overrides the enforcement binding. Example: substrate binds
an auth-middleware-presence rule to Semgrep by default; a consumer
using a different SAST tool overrides the binding to that tool.

The consumer ensures their tool's behavior matches the rule's intent.
The substrate's rule identity stays stable; only the binding
changes.

## Substrate evolution and consumer profiles

When the substrate evolves, consumer profiles may need adjustment.

### Substrate adds new rules

Consumer profiles that inherit from substrate profiles automatically
inherit new rules added to those parent profiles. Consumers may
exclude new rules via profile modification if needed.

Substrate addition of rules is non-breaking per Charter Article VIII
Section 7.5. Consumers receive new defaults without integration
changes.

### Substrate deprecates rules

Deprecated substrate rules remain consultable for at least one major
version cycle. Consumer profiles continue functioning during the
deprecation window. Consumers migrate to the superseding rules per
substrate migration guidance before retirement.

### Substrate retires rules

Retired rules are removed from the substrate. Consumer profiles
that referenced retired rule IDs encounter resolution errors at
profile resolution time. Consumers must remove retired rule
references from their profiles.

The substrate provides one major version of warning before retiring
any rule, so consumers have time to migrate.

### Substrate amendments

Charter amendments (per Article IX) may change tailoring
permissions. Consumer profiles authored under prior amendment
versions remain valid for as long as Charter compatibility allows.
The substrate provides migration guidance when amendments require
profile adjustments.

## Versioning of this contract

This contract is versioned with the commons. Changes follow Charter
Article VIII versioning discipline.

Current contract version: **0.1.0** (matches commons version)

### Breaking changes

The following changes are breaking under semver:

- Removing a permitted modification
- Adding a forbidden modification that was previously permitted
- Changing the meaning of a tailoring procedure

### Non-breaking changes

The following are non-breaking:

- Adding a new permitted modification
- Removing a forbidden modification
- Clarifying procedures without changing meaning
- Adding boundary cases or examples

## What this contract is not

To clarify boundaries:

- This contract is not a profile template. Profile examples live in
  `governance-commons/profiles/` and are illustrative.
- This contract is not a custom-catalog template. Catalog format is
  specified in `spec/catalog-format.md`; this document references
  the format but does not duplicate it.
- This contract is not a substrate contribution agreement. Substrate
  contribution legal terms are governed by the repository's `LICENSE`
  and any contributor agreements the substrate adopts in the future.
- This contract is not a governance maturity model. Consumers
  progress from light tailoring to heavy tailoring as their needs
  evolve. The contract describes mechanisms, not progression.

## Closing

Tailoring is the mechanism by which substrate opinion becomes
consumer reality. The substrate ships opinions; consumers configure
them; the configuration is auditable; community contributions flow
back to the substrate when general utility is recognized.

The contract exists so that tailoring is a structured activity, not
a silent compromise of substrate integrity. Profile authoring is
explicit. Custom catalogs are namespaced. Modifications are
rationalized. Submissions are open. Forks are permitted as
last-resort divergence.

When the contract feels constraining, the resolution is amendment
under Charter Article IX, not silent bypass. The substrate exists
because constraints applied consistently produce better software
than constraints applied selectively under pressure.
