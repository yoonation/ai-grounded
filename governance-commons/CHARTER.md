<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Governance Commons Charter

This Charter establishes the supreme rules governing the substrate
known as Governance Commons. It is the highest-precedence document
within `governance-commons/`. Catalogs, profiles, mappings, tool
bindings, decision frameworks, schemas, and tooling all defer to this
Charter.

This Charter is read by every consumer that adopts Governance Commons,
by every human authoring or modifying commons content, and by every AI
agent that proposes, drafts, validates, or applies commons content. Any
deviation from this Charter requires either an amendment under Article
IX or a documented incompatibility recorded by the deviating consumer.

This Charter does not duplicate the engineering principles in
`spec/principles.md`. Those principles define the philosophical values
that motivate the substrate (P1-P12). This Charter defines the
**constitutional** rules for how the substrate functions, how it is
extended, and how consumers interact with it.

## Nature of this document

This Charter is to profiles and tailorings what a written constitution
is to case law. The Charter states substrate principles. Profiles
interpret those principles for specific organizations. Consumer-side
ADRs interpret them for specific projects. Together they form the
governance rule set; none stands alone.

The Charter covers what is stable: how catalogs may be authored, what
AI may and may not do with them, how identity and meaning persist
across versions, how tailoring works, what evidence consumers owe, and
how the substrate evolves. Profiles cover what is contextual: which
controls apply to a financial services organization, which severities
a regulated AI deployment requires, which custom rules a healthcare
provider adds. Consumer-side ADRs cover what is project-specific.

When a Charter provision seems to conflict with reality, exactly one
of three resolutions applies: (a) the situation is foreseen and a
profile records the principled tailoring under Article V, (b) the
situation reveals a gap in the Charter that warrants an amendment per
Article IX, or (c) the situation reveals work that should not proceed
under this Charter's authority. The wrong resolution is to silently
bypass the provision.

The substrate is intentionally **opinionated by default and tailorable
by design**. The default profile encodes production-grade software
development with strong security, performance, reliability, and code
quality. Organizations whose values tilt differently express that tilt
through profiles, not through silent deviation. Article V is the
mechanism; the audit trail is the discipline.

## Article I: Nature and Authority

### Section 1.1 - What this Charter binds

This Charter binds all content within `governance-commons/`. It binds
all humans authoring or modifying that content. It binds all AI agents
that propose, draft, validate, traverse, or apply that content. It
binds all consumers that incorporate the commons into their workflow.

Compliance is the condition of using the substrate. Consumers that
cannot or will not comply with this Charter must fork the substrate
and accept the consequences of divergence.

### Section 1.2 - Reference direction

References between consumers and the commons flow in exactly one
direction. Consumers may reference any commons artifact by path,
identifier, or version. The commons may not reference any consumer,
any specific consuming framework, any consumer-specific format, or
any consumer-specific directory layout. This rule preserves the
substrate's portability and is enforced mechanically by the existing
`PORTABILITY.md` discipline.

A consumer may interpret commons content, layer additional content on
top, or restrict which commons content applies to its workflow. A
consumer may not modify commons content in place. Modifications travel
back to the commons via the procedures in Article II.

### Section 1.3 - Relationship to consumer constitutions

Consumers commonly maintain their own constitutional documents
(project constitutions, framework constitutions, organizational
governance documents). Those documents are authoritative within their
scope. This Charter is authoritative within the substrate's scope.

Where a consumer's constitution and this Charter both apply, the
consumer's constitution governs consumer-specific operational
questions and this Charter governs substrate-specific structural
questions. Conflicts that cannot be resolved by separation of scope
are resolved by (a) the consumer adjusting its constitution, (b) the
consumer raising a Charter amendment under Article IX, or (c) the
consumer forking the substrate.

### Section 1.4 - Supreme authority within the substrate

No commons artifact may contradict this Charter. Catalogs, profiles,
mappings, tool bindings, decision frameworks, schemas, and tooling
that conflict with this Charter are deemed invalid until reconciled
through amendment or correction.

## Article II: Authoring Discipline

### Section 2.1 - Human authorship of commons content

All catalogs, profiles, mappings, decision frameworks, and schemas in
the commons are authored, reviewed, and approved by humans. AI may
propose, draft, validate, summarize, traverse, and apply commons
content per Article III, but no commons content enters the substrate
without explicit human authorship attribution and approval.

Rationale: governance is the codification of an engineering
organization's values. Values are human, not learned. Allowing AI to
unilaterally author commons content would convert the substrate from
human-encoded values into AI-encoded inference, which is the failure
mode this Charter exists to prevent.

### Section 2.2 - Provenance recording

Every catalog rule, profile selection, mapping relation, decision
framework, and schema definition records its provenance. Required
provenance fields:

- Author of record (human identity)
- Date authored
- Authoritative external source if any (URL or canonical reference)
- Reviewer of record (human identity, distinct from author for
  stable-status content; see Section 2.4.1 for the solo-author
  attestation convention when only one maintainer is of record)
- Date reviewed
- AI assistance acknowledged (if AI participated in drafting,
  validation, or proposal)

Provenance is part of the artifact, not metadata about it. An artifact
without provenance is not commons content; it is unverified material.

### Section 2.3 - Quality bar for new content

Content entering the commons meets a quality bar before promotion to
stable status. The bar requires:

- Authoritative source cited where one exists, or original rationale
  recorded where none does
- Three or more concrete examples demonstrating the rule's application
- Severity assignment with explicit reasoning
- Layer assignment (mechanical, semantic, judgmental) with explicit
  reasoning
- Anti-pattern alongside the pattern (what NOT to do, where applicable)
- Validation against real codebases before stable promotion (draft
  status permitted prior)

Rationale: bad catalog content is worse than absent content. A
sloppily-authored rule creates confident wrong behavior with a clean
audit trail. The quality bar exists to prevent the substrate from
becoming a precision instrument pointed in the wrong direction.

### Section 2.4 - Review discipline

Stable content is reviewed by a second human (distinct from author)
who validates:

- The rule's intent is clearly stated
- The examples actually demonstrate the rule
- The severity and layer assignments are defensible
- The provenance is complete
- The content does not conflict with existing commons content

Review is recorded in provenance per Section 2.2.

Draft content may be authored without second-human review but must
state its draft status explicitly and may not be referenced by
profiles in the default profile set.

### Section 2.4.1 - Solo-author attestation (substitute for second-human review)

The substrate's review discipline in Section 2.4 requires a second
human reviewer distinct from the author. This requirement assumes a
multi-maintainer substrate. During the substrate's pre-stable
maintainership phase, the substrate is solo-authored. A literal
reading of Section 2.4 would forbid any content from reaching stable
lifecycle status until a second maintainer is added, which would
either stall the substrate at draft indefinitely or pressure the
substrate-author to recruit a second maintainer prematurely for the
wrong reason.

This Section establishes solo-author attestation as a bounded,
auditable substitute for second-human review. It does not weaken
the quality bar in Section 2.3. It records the substrate's
solo-author phase honestly rather than silently violating Section
2.4.

**Eligibility.** Solo-author attestation applies only when:

- The substrate has exactly one maintainer of record per
  `MAINTENANCE.md`
- The substrate version is in pre-stable status (0.x per Article
  VIII)
- The current maintainer is recorded in `CONTRIBUTORS.md` as the
  sole substrate-author
- The Charter version is at or above 0.2.0 (the version that
  introduced this Section)

When any eligibility condition fails, Section 2.4's literal
requirement governs and Section 2.4.1 is unavailable.

**Mechanism.** A solo-author attestation consists of:

1. A documented cooling-off interval between authoring and
   attestation. The substrate-author may not attest content
   authored in the same calendar day. Minimum interval is one
   calendar day. The interval exists to surface concerns the
   author would have raised had they been a second reviewer; same-
   day attestation is structurally indistinguishable from rubber-
   stamping.
2. A discrete commit recording the attestation. The attestation
   commit is distinct from the authoring commit. The attestation
   commit's message states which artifact is attested, against
   which version of the Charter, and confirms each Section 2.4
   validation criterion was applied.
3. The attested artifact records the attestation in its provenance
   using `reviewer: "myoung-self-attested"` (or the equivalent
   identifier for the maintainer of record, suffixed with
   `-self-attested` to mark the attestation as solo-author rather
   than second-human). The `reviewed` field records the date of
   the attestation commit, not the date of the authoring commit.
4. An entry in `CHANGELOG.md` under the same version that the
   attestation lands in, describing the lifecycle transition.

The four mechanical components together are the attestation. None
is optional. Their combined effect is that the attestation is
visible in commit history, in artifact provenance, and in the
Charter-mandated changelog. An auditor reconstructing the
substrate's history can verify each component independently.

**Sunset clause.** Solo-author attestation expires when any of:

- A second maintainer is added to `MAINTENANCE.md`. From that
  point forward, new stable promotions use Section 2.4 (second-
  human review). Previously self-attested content retains its
  status but new attestations follow Section 2.4.
- The substrate reaches version 1.0.0. Reaching post-stable
  versioning is the substrate's signal that maintainership has
  matured beyond what solo-author attestation is meant to bridge.
- The substrate-author of record changes. Attestations are
  identity-bound; a maintainer change resets the attestation
  baseline.

When the sunset clause fires, content previously promoted under
Section 2.4.1 is not retroactively invalidated, but the section
itself is no longer a valid path for new promotions. The substrate
amends the Charter under Article IX to either remove this Section
or revise its terms based on operational experience.

**Amendment at version 1.0.0, revised 2026-06-05 (under Article IX).**
The version-1.0.0 sunset trigger fired with the 1.0.0 release
(2026-06-07) and was first resolved by closing Section 2.4.1 to new
stable promotions. On review before any external publication of the
substrate, and before any stable promotion had been made under the
closed regime, the substrate-author has elected instead to extend
solo-author attestation through the substrate's remaining
private-development phase. This revised amendment supersedes the prior
close in full and resolves the sunset as follows:

1. **Operative eligibility is re-based on publication, not version.**
   The "pre-stable status (0.x)" eligibility condition above is
   superseded. For the purpose of this Section, the operative
   eligibility condition is that the substrate repository is not yet
   public (it has not been published or open-sourced for external
   consumption). All other eligibility conditions (a single maintainer
   of record, the maintainer recorded in `CONTRIBUTORS.md`, the Charter
   at or above 0.2.0) continue to apply unchanged. Reaching version
   1.0.0 no longer, by itself, makes Section 2.4.1 unavailable.
2. **The sunset trigger is re-based on publication.** The "reaches
   version 1.0.0" sunset trigger in the Sunset clause above is
   superseded by the following trigger: solo-author attestation expires
   when the substrate repository is made public (published or
   open-sourced for external consumption). The other two sunset
   triggers (a second maintainer is added; the maintainer of record
   changes) continue to apply unchanged. The rationale is that the risk
   solo-author attestation manages, an unreviewed change reaching
   external consumers, materializes at publication, not at an internal
   version milestone; the discipline that substitutes for second-human
   review should bridge exactly the private-development phase and end
   when the substrate is first exposed externally.
3. **Corrections are not new promotions.** A correction to existing
   substrate content does not require attestation, does not require the
   cooling-off interval, and is not a new stable promotion for the
   purpose of this Section or Section 2.4. A correction is a change that
   preserves the substance of existing content and adds no new stable
   content: bug fixes; broken cross-reference, href, and identifier
   fixes; malformed-syntax repairs; metadata, typo, and formatting
   fixes; documentation-consistency edits; and portability and hygiene
   cleanup. Authoring new concern, profile, or mapping content, and any
   first-time promotion of draft content to stable, remain new
   promotions: they require solo-author attestation under this Section
   while it is available, or second-human review under Section 2.4.
4. **Retained status.** All content promoted under Section 2.4.1
   through the 1.0.0 release (the 25 concern catalogs, the 5 profiles,
   the 5 mappings, and their paired decision frameworks and L2
   bindings) retains its stable status and is not retroactively
   invalidated.

When the publication-based sunset later fires, content previously
promoted under Section 2.4.1 is not retroactively invalidated, exactly
as the Sunset clause provides, and from that point new stable
promotions require Section 2.4 (second-human review) or a fresh
Article IX amendment.

This revised amendment is discipline-relaxing relative to the
superseded close (it re-opens a solo-author path the close had shut).
Per Article IX Section 9.2 it is therefore a breaking amendment taking
a major Charter version increment (0.2.0 to 1.0.0), recorded in
Section 9.5 and in `CHANGELOG.md` per Article IX Section 9.1.

**What this Section does not do.** Solo-author attestation does
not reduce the quality bar in Section 2.3. It does not exempt
content from the provenance requirements in Section 2.2. It does
not authorize AI to substitute for the second human; AI
participation in the substrate remains governed by Article III.
The attesting human is the substrate-author themselves, reading
their own prior work after the cooling-off interval, applying the
same validation criteria they would apply to another author's
work. The discipline is in the cooling-off, the explicit recording,
and the commit history. The substitute is not equivalence; it is
honest accommodation of the substrate's current maintainership
phase.

### Section 2.5 - No silent deletion

Commons content is never deleted silently. Retirement of a rule,
profile, or other artifact follows the lifecycle procedures in Article
VIII. Removal events are recorded in `CHANGELOG.md`.

Rationale: consumers that reference commons content by identifier need
predictable behavior when content disappears. Silent deletion breaks
consumer audit trails and obscures the substrate's own history.

### Section 2.6 - Cite authoritative sources

When commons content derives from external authoritative sources
(OWASP, NIST, MITRE, ISO, W3C, OpenSSF, industry-recognized
publications), the source is cited explicitly in the artifact. The
substrate does not claim to invent what it curates.

When commons content is genuinely original, that originality is
declared in provenance and the rationale is recorded inline.

## Article III: AI's Role

### Section 3.1 - Permissible AI activities

AI may perform the following activities with respect to commons
content:

- **Propose** new rules, profiles, mappings, or decision frameworks
  for human review
- **Draft** content from human-supplied intent, citations, and
  examples
- **Validate** existing content against schemas, against authoritative
  sources, and against real codebases
- **Summarize** content for consumer agents at runtime
- **Traverse** content following manifest assignments to consult only
  what is required for a given task
- **Apply** content by consulting rules during consumer workflows and
  reporting findings per the consultation evidence contract
- **Detect** drift between commons content and consumer codebases
- **Suggest** corrections to commons content when the AI identifies
  potential errors

### Section 3.2 - Forbidden AI activities

AI may not perform the following activities:

- **Approve** new commons content (human authority required)
- **Merge** proposed content into the commons (human authority
  required)
- **Commit** changes to commons content without recorded human
  signature
- **Retire or deprecate** existing commons content unilaterally
- **Modify rule identity** (rule IDs, intent text per Article IV)
- **Override severity** assignments at runtime in a way that conflicts
  with the applicable profile
- **Disable** rules at runtime without invoking the explicit override
  mechanism documented by the consumer

Rationale: governance content is human-authored values. AI's role is
to assist humans in encoding and applying those values, not to author
or modify them autonomously.

### Section 3.3 - Recording AI assistance

When AI assists with authoring, validating, proposing, or correcting
commons content, the assistance is recorded in the artifact's
provenance per Section 2.2. Recording AI assistance is not optional;
it is part of the artifact's integrity.

AI-proposed content that humans subsequently author still records the
AI assistance. The human reviewer's role is to verify the content;
the AI's role in producing the initial draft is acknowledged.

### Section 3.4 - Human signature requirement

Any change to commons content requires a recorded human signature.
The signature mechanism is implementation-specific (Git commit
authorship, signed commits, recorded approval in a review system),
but the substrate requires that human authorship be cryptographically
or auditably attestable for every change.

### Section 3.5 - AI consultation reporting

When AI agents consult commons content during consumer workflows,
they report what they consulted per the consultation evidence
contract in Article VI. Unreported consultation does not satisfy the
contract. Consumers that cannot or do not require AI agents to report
consultation are not satisfying Article VI and are using the
substrate without governance integrity.

## Article IV: Catalog Identity and Immutability

### Section 4.1 - Rule identity is immutable

Every rule in the commons has a stable identifier (the rule ID). Once
a rule enters stable status, its identifier never changes. Rules are
not renumbered, renamed, or re-keyed.

Rationale: consumers reference rules by identifier in their
manifests, audit trails, and ADRs. Identifier stability is what makes
those references durable across versions. Renaming a rule breaks
every consumer reference to it and cannot be detected mechanically.

### Section 4.2 - Rule intent is immutable

Every rule has an intent statement (the rule's title and short
description). Once a rule enters stable status, its intent statement
is immutable. The rule means what it meant when it was promoted to
stable.

Rationale: a rule whose intent shifts over time produces inconsistent
behavior across versions. authentication.no-credentials-in-urls means the same thing in version
2.3 as it meant in version 2.1. Without this guarantee, mappings,
profiles, and consumer ADRs become unreliable.

Editorial corrections to typos, formatting, or clarifying phrasing
that does not change the rule's meaning are permitted and recorded
in `CHANGELOG.md`. Material changes to intent require retirement of
the existing rule and creation of a new rule with a new identifier.

### Section 4.3 - Tailorable properties

The following rule properties are tailorable by profiles, by
consumers, or by organizations under Article V:

- **Severity assignment** for this organization's context
- **Applicability scope** (which features, languages, environments
  this rule applies to)
- **Parameters** (specific thresholds, timeouts, sizes, counts) where
  the rule defines them
- **Enforcement binding** (which tool enforces a mechanical rule for
  this organization's stack)

Rationale: a rule like "all auth endpoints call auth middleware" has
the same meaning everywhere, but the specific middleware name varies
by stack. Identity stays stable; parameters travel.

### Section 4.4 - Distinction between retirement and non-applicability

A rule that no longer reflects current best practice is **retired**
per Section 8.3. Retirement is a substrate-level decision recorded
in `CHANGELOG.md` and affects all consumers.

A rule that does not apply to a specific consumer's context is
**excluded by profile** per Article V. Exclusion is a
consumer/organization-level decision recorded in the consumer's
profile and the consumer's audit trail. The rule remains in the
substrate; this consumer simply does not select it.

Conflating these two is a recurring failure mode. A consumer that
disagrees with a rule does not retire it from the substrate; the
consumer excludes it from their profile and records why. The rule
remains available for other consumers.

## Article V: Profiles and Tailoring

### Section 5.1 - Profile as the tailoring mechanism

Tailoring the substrate to a specific organization, industry, or
project occurs through the OSCAL profile model and through this
Charter's extension permissions. Profiles select subsets of commons
content, modify parameters, set severities for the organization's
context, and may import other profiles.

Profiles never modify commons content in place. A profile that
selects a rule does not own that rule; it references it.

### Section 5.2 - The default profile is opinionated

The commons ships a default profile (`production-grade-baseline.oscal.yaml`)
that encodes opinionated defaults: production-grade software, high-load
capable, secure, performant, observable, and following established
software design patterns. The default profile is not neutral; it is a
stance.

Organizations whose values match the default adopt it as-is.
Organizations whose values tilt differently inherit from the default
profile and modify it explicitly.

Rationale: a neutral default is a default of "anything goes," which
is not governance. The substrate's value is the stance it takes. The
profile mechanism is what makes the stance configurable without
making it absent.

### Section 5.3 - Industry and use-case profiles

The commons ships additional profiles for common industry tilts
(financial services, healthcare, regulated AI, etc.) and common use
cases. These profiles inherit from the default profile and apply
industry-specific modifications.

Industry profiles are subject to the same authoring discipline as
catalogs (Article II). They are commons content.

### Section 5.4 - Consumer-side profile authoring

Consumers may author their own profiles that inherit from any commons
profile. Consumer-side profiles live consumer-side and are not
governed by this Charter's authoring discipline. They are governed by
the consumer's own discipline.

A consumer-side profile that achieves general utility may be proposed
for inclusion in the commons via Article II authoring procedures. At
that point it becomes commons content and is subject to Charter
authority.

### Section 5.5 - Weakening defaults requires rationale

A profile that disables, weakens, or removes any default control
(lowering severity, narrowing applicability, omitting selection,
relaxing parameters beyond the default) records rationale for the
modification. The rationale is part of the profile artifact.

This requirement applies equally to commons profiles and to
consumer-side profiles. Rationale-less weakening defeats the purpose
of the substrate, even when the substrate cannot enforce the
requirement mechanically on consumer-side profiles.

### Section 5.6 - Strengthening defaults requires no rationale

A profile that strengthens any default control (raising severity,
broadening applicability, tightening parameters, adding additional
controls) requires no rationale. Strength is welcome by default.

### Section 5.7 - Extension via custom catalogs

Consumers may author custom catalogs that extend the commons. Custom
catalogs live consumer-side and are governed by the consumer's
discipline. Profiles may select from custom catalogs alongside
commons catalogs.

A custom catalog that achieves general utility may be proposed for
inclusion in the commons via Article II authoring procedures.

Custom catalogs must follow the catalog format specified in
`spec/catalog-format.md` to be referenced by manifests that satisfy
the consultation evidence contract.

## Article VI: Consultation Evidence Contract

### Section 6.1 - The contract

A consumer that incorporates Governance Commons into a workflow where
AI agents consult commons content must satisfy the consultation
evidence contract specified in `spec/consultation-evidence.md`. The
contract defines the data shape and required fields; consumers map
their runtime architecture to it.

Satisfying the contract is the condition of claiming governance
integrity. A consumer that does not satisfy the contract is using
the substrate without governance, which is permitted but is not
governed AI development.

### Section 6.2 - Required evidence fields

For every AI consultation of commons content during a consumer
workflow, the consumer records at minimum:

- **Consulter identity** (the agent or runtime principal that
  consulted)
- **Timestamp** of consultation
- **Commons version** consulted
- **Profile** active at time of consultation
- **Artifact identifiers** examined (catalog IDs, rule IDs)
- **Findings** produced (with rule references)
- **Closure claim** if applicable (how the finding was addressed)

Consumers may record additional fields. Consumers may not omit
required fields.

### Section 6.3 - Storage is consumer-specified

The contract specifies what must be recorded, not where or how. A
consumer may satisfy the contract via append-only event logs,
OpenTelemetry spans, structured logs, immutable storage systems, or
any other audit-grade mechanism appropriate to the consumer's
architecture.

The substrate makes no assumption about consumer storage. The
substrate's tooling for evidence verification (when built) operates
on the contract's data shape and adapts to consumer storage via
defined adapters.

### Section 6.4 - Evidence integrity

Recorded consultation evidence is append-only and tamper-evident
within the consumer's audit medium. Consumers that cannot guarantee
append-only behavior cannot claim full satisfaction of the contract.

Evidence that is mutable after the fact is not evidence; it is a
narrative.

### Section 6.5 - Verification responsibility

Verification that consultation actually occurred is a consumer
responsibility. The substrate provides specifications and may provide
tooling. Consumers integrate verification into their own workflow.

A consumer that records consultation but does not verify the
recording is creating an audit trail without integrity. Article VI
expects both.

## Article VII: Compatibility with Consumers

### Section 7.1 - What the substrate provides

The substrate provides:

- Stable identifiers for all artifacts
- Schemas for all data formats produced by the substrate
- Documented contracts (consultation evidence, consumption,
  extension) that consumers integrate against
- Versioning per Article VIII with semantic version discipline
- Migration guidance for breaking changes
- An opinionated default profile and tailoring mechanism per
  Article V

### Section 7.2 - What the substrate does not provide

The substrate does not provide:

- Runtime enforcement of commons content (consumer responsibility)
- Storage for consultation evidence (consumer responsibility)
- Workflow integration with any specific consumer architecture
- Guarantees about specific tools' presence or behavior
- Project-level operational rules (consumer-side constitutions
  provide these)
- Authority over consumer codebases, workflows, or decisions

### Section 7.3 - What consumers must provide

A consumer that adopts the commons must provide:

- A mechanism to satisfy the consultation evidence contract (Article
  VI)
- A profile selection (the default profile if no tailoring is needed,
  or a consumer-side profile that inherits from a commons profile)
- A workflow integration that consults the appropriate catalogs at
  appropriate times (the specific mechanism is consumer's choice)
- An audit medium that supports the contract's evidence requirements

### Section 7.4 - What consumers must not assume

A consumer may not assume:

- That commons content remains identical across major versions
  (semver applies)
- That tooling provided by the substrate works in any specific
  runtime environment
- That the substrate's directory layout will remain stable beyond the
  guarantees in Article VIII
- That all consumers use the same profile or interpret commons
  content identically

### Section 7.5 - Breaking change signaling

The commons signals breaking changes via major version increments in
the `VERSION` file. Breaking changes include:

- Retirement of rules (existing identifiers no longer present)
- Change to required fields in the consultation evidence contract
- Change to schemas in `schemas/`
- Removal of default-profile-included rules

Non-breaking changes (rule additions, severity adjustments in
profiles, new profiles, new tool bindings, editorial corrections)
follow minor or patch version increments.

## Article VIII: Lifecycle and Versioning

### Section 8.1 - Commons version

The commons has a single version recorded in `VERSION` at the
substrate root. The version follows semantic versioning. The version
is incremented on any change to commons content per Section 7.5.

The current version is the only authoritative version. Consumers
that reference a specific version are operating against a snapshot;
the snapshot remains stable but the substrate evolves forward.

### Section 8.2 - Artifact lifecycle states

Every artifact in the commons (rule, profile, mapping, decision
framework, schema) exists in one of four lifecycle states:

- **Draft**: under active authoring, not subject to Section 2.4
  review yet, may not be referenced by default-profile content,
  identifier reserved
- **Stable**: meets Article II quality bar, reviewed per Section 2.4,
  may be referenced freely, immutable per Article IV
- **Deprecated**: superseded by other content, remains present and
  consultable, signals to consumers that migration is expected,
  records the superseding artifact's identifier
- **Retired**: removed from active commons content, identifier
  remains reserved (never reused), historical record preserved in
  `CHANGELOG.md`

Lifecycle transitions are one-directional: draft to stable, stable
to deprecated, deprecated to retired. Reversing a transition requires
creating a new artifact (with a new identifier per Section 4.2 if the
original was retired).

### Section 8.3 - Deprecation window

Deprecated artifacts remain consultable for at least one major
version cycle before retirement. Consumers receive a minimum of one
major version of advance notice before any deprecated content is
retired.

Rationale: consumers integrate against commons content with the
expectation of stability. A deprecation window protects consumers
from breaking changes without warning.

### Section 8.4 - Versioning of profiles

Profiles version independently from the commons. A profile's version
reflects changes to its selections, parameters, and modifications,
not changes to the underlying catalog content it references.

Catalog content changes propagate to consumers via the commons
version. Profile changes propagate to consumers via the profile
version.

### Section 8.5 - Versioning of consumer-side artifacts

Consumer-side profiles, custom catalogs, and consumer-side
manifests are versioned by the consumer. This Charter does not
prescribe consumer-side versioning discipline beyond requiring that
consumers be able to identify which commons version their artifacts
target.

## Article IX: Amendments

### Section 9.1 - Charter changes require process

This Charter can be amended. Amendments require:

1. A proposal describing the change and its rationale
2. A migration plan for affected consumers (if applicable)
3. Review by the substrate's maintainer or maintainer group
4. Approval from the substrate's owning authority
5. Update to this document with version increment

The proposal, review, and approval are recorded in commit history
and in `CHANGELOG.md`.

### Section 9.2 - Compatibility of amendments

Amendments that strengthen authoring discipline, expand AI
restrictions, raise quality bars, or improve evidence contracts are
non-breaking and follow minor version increments.

Amendments that weaken authoring discipline, relax AI restrictions,
lower quality bars, or remove evidence requirements are breaking
and follow major version increments. Such amendments require
particular scrutiny because they reduce the substrate's integrity.

### Section 9.3 - Forking is permitted

Consumers that cannot accept this Charter as written or as amended
may fork the substrate. A fork is no longer Governance Commons but
remains free to reuse the Charter's structure under the Charter's
license terms.

Forks are not the failure mode this Charter prevents. Silent
non-compliance is the failure mode. A consumer that openly forks
because their values diverge from the substrate's is exercising
appropriate disagreement.

### Section 9.4 - Substrate owner

The substrate's owning authority is recorded in `MAINTENANCE.md` and
evolves as the substrate matures from single-maintainer to
maintainer group. Amendments approved under Section 9.1 are
approved by the authority of record at the time of amendment.

### Section 9.5 - Version

Current version: **1.0.0**

Version history:

- **1.0.0** (2026-06-05): Section 2.4.1 sunset resolution. The
  version-1.0.0 sunset trigger fired with the substrate's 1.0.0 release
  (2026-06-07). It was first resolved by closing Section 2.4.1 to new
  stable promotions; that close amended the Section text but was not
  recorded here with a Charter version increment as Section 9.1 step 5
  requires (this entry corrects that omission). On review before any
  external publication, and before any stable promotion under the
  closed regime, the close was superseded by the revised Amendment at
  version 1.0.0 (reopen): solo-author attestation is extended through
  the substrate's private-development phase, the eligibility condition
  and sunset trigger are re-based from version 1.0.0 to repository
  publication, and a corrections clause is added (a correction to
  existing content is not a new stable promotion and needs no
  attestation or cooling-off). The reopen is a discipline-relaxing
  amendment per Section 9.2 and therefore takes a major Charter version
  increment (0.2.0 to 1.0.0) and receives the particular scrutiny that
  Section requires.
- **0.2.0** (2026-05-19): Section 2.4.1 added (Solo-author attestation
  as bounded substitute for the second-human review requirement in
  Section 2.4 during the substrate's solo-maintainer phase). Section
  2.2 cross-reference added to point at 2.4.1 from the provenance
  field list. Non-breaking amendment per Section 9.2: clarifies an
  unavailable path (multi-maintainer review) and authorizes a more
  rigorous substitute (cooling-off plus discrete attestation commit
  plus changelog entry) rather than allowing silent violation. Minor
  version increment per semver and Section 9.2.
- **0.1.0** (2026-05-17): Initial publication of this Charter as the
  supreme authority document of Governance Commons.

This Charter is at stable status (1.0.0), consistent with the commons
reaching 1.0. Amendments follow Article IX procedures; discipline-
relaxing amendments take major increments and receive particular
scrutiny per Section 9.2.

## Application across consumers

How consumers honor this Charter:

| Consumer type | Charter obligations |
|---|---|
| Build-time framework (AI code authoring) | All Articles. Catalog consultation occurs at workflow checkpoints; evidence contract satisfied via consumer audit medium. |
| Runtime framework (AI agent enforcement) | All Articles. Catalog consultation occurs at policy decision points; evidence contract satisfied via runtime telemetry. |
| Standalone catalog consumer (no AI workflow) | Articles I, II, IV, V, VII, VIII. Article III applies if AI is used for any authoring; Article VI applies if AI consults catalogs in production. |
| Educational or reference use | Articles I, IV, V. Authoring discipline (II, III) applies if the consumer contributes back. |

This table is illustrative. A consumer that does not match any row
applies the Articles that govern their actual use of the substrate.

## Application across content types

How each commons content type honors this Charter:

| Content type | Primary Articles enforced |
|---|---|
| Concern catalogs | II, IV, VIII |
| Compliance catalogs | II, IV, VIII (provenance from authoritative source) |
| Threat catalogs | II, IV, VIII |
| Design pattern catalogs | II, IV, VIII (provenance recognizing public concepts vs cited sources) |
| Profiles | II, V, VIII |
| Mappings | II, IV, VIII |
| Tool bindings | II, VII |
| Decision frameworks | II, IV (intent immutability), VIII |
| Schemas | II, VII (consumers integrate against them) |
| Tooling | II (authoring), VII (consumers use them) |

All commons content types enforce Articles I (authority), III (AI's
role), and VI (consultation evidence contract).

## Foundational traditions

This Charter draws on established traditions in standards governance
and engineering rule-making. The traditions are the operational
vocabulary for translating Charter principles into substrate
practice.

- **NIST OSCAL governance** (NIST 800-53 baseline maintenance,
  community contribution model) for catalog lifecycle and profile
  tailoring
- **OWASP project governance** (cell-organized contributor model,
  CC-licensed content, version transparency) for community-authored
  catalog content
- **W3C specification process** (working drafts, candidate
  recommendations, proposed recommendations, recommendations) for
  the draft/stable/deprecated/retired lifecycle
- **Semver** (semver.org) for version discipline and breaking change
  signaling
- **Open source license discipline** (Apache 2.0, MIT, CC-BY) for
  how the substrate handles attribution and derivative works
- **NIST documentary discipline** (rationale recording, glossary
  precision, controlled vocabulary) for authoring quality

When humans authoring commons content, or AI agents assisting with
authoring, encounter ambiguity in this Charter, the foundational
traditions inform interpretation. The traditions do not override the
Charter; they fill gaps.

## Closing

This Charter is the supreme rule of Governance Commons. It is
authored by humans, enforced by humans, amended by humans, and
respected by AI. AI's role is to assist humans in applying the
Charter's authority, not to exercise it.

The substrate exists because engineering organizations need durable,
machine-readable, AI-consultable encodings of their values. The
Charter exists because those encodings must remain anchored in
human authority no matter how capable the AI that consults them
becomes.

When in doubt, the Charter favors human authority, audit-trail
integrity, and substrate portability. When those values conflict
with other considerations, the resolution is amendment under
Article IX, not silent compromise.
