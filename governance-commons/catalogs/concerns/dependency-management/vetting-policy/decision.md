---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: dependency-management.vetting-policy
title: "Dependency Vetting Policy Selection"
lifecycle-status: stable
commons-version: "0.4.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-20"
entered-status-at: "2026-05-22"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
ai-assistance: "AI drafted from substrate-author intent following auth-strategy.madr.md and secrets-management-platform.madr.md precedents; third decision framework authored in the substrate. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft."
authoritative-sources:
  - "https://github.com/ossf/wg-best-practices-os-developers/blob/main/docs/Concise-Guide-for-Evaluating-Open-Source-Software.md"
  - "https://www.cisa.gov/sites/default/files/2023-09/CISA-OSS-Action-Plan-508c.pdf"
  - "https://github.com/ossf/scorecard"
  - "https://slsa.dev/spec/v1.0/"
  - "https://owasp.org/www-project-software-component-verification-standard/"
  - "https://adr.github.io/madr/"
---

# Dependency Vetting Policy Selection

This decision framework provides the substrate's analysis of
dependency vetting policy options. Consumers reference this
framework when authoring their own ADR documenting their
project's vetting policy. The substrate-recommended location
for the consumer's ADR is
`/docs/decisions/ADR-XXX-dependency-vetting-policy.md`.

The framework is referenced by substrate rule dependency-management.vetting-policy,
which requires applications to have an explicit, documented
vetting policy before direct dependencies are introduced.
Consumers satisfy dependency-management.vetting-policy by authoring an ADR that
adapts the analysis in this framework to their application
context.

## Context

Dependency vetting is the policy layer above the mechanical
L1 rules. L1 rules (pinned versions, vulnerability blocking)
catch known-bad states; vetting policy decides which
dependencies are admitted in the first place. Without an
explicit vetting policy, decisions about which dependencies
to admit are made implicitly, inconsistently, and often by
the first contributor who needs the dependency.

The choice has implications across the L2 rules. The policy
determines what evidence accompanies a dependency-management.provenance provenance
review (license, maintenance health, supply-chain history),
what cadence dependency-management.update-cadence enforces, and what exceptions are
allowed at each level. A clear policy makes the L2 review
checklists fast to apply; an absent or vague policy makes
them protracted and inconsistent.

Common substrate failure mode: teams have a strong policy on
paper but no intake process to apply it; or have no policy
but a sense of which dependencies are "risky" that varies by
reviewer. The framework forces the policy to be explicit and
operationalized.

The substrate provides analysis of each viable option but
does not prescribe a single choice. Consumers select based
on their context. Smaller teams with less capacity for
dedicated vetting may choose a lightweight option; teams
operating in regulated environments may need a stricter
option.

## Decision Drivers

The substrate identifies the following drivers that should
inform the policy choice. Consumers may add project-specific
drivers but should address each substrate driver in their
ADR.

- **D1. License posture.** Pure permissive (MIT, Apache-2.0,
  BSD only); permissive plus weak copyleft (MPL-2.0, LGPL);
  permissive plus strong copyleft with caveats (GPL allowed
  for internal tools, not for shipped products); or
  proprietary-only with strict allow-list. The license
  posture is upstream of the vetting policy because it
  determines which dependencies are even candidates.

- **D2. Operational capacity for vetting.** A team with a
  dedicated security architect or supply-chain function can
  sustain strict vetting. A team where dependency reviews
  fall on whoever is on-call must lean toward criteria-
  based or lightweight options. Honest assessment of
  capacity is substrate-required because policies that
  outstrip capacity decay into ad-hoc decisions.

- **D3. Regulatory context.** PCI DSS, HIPAA, FedRAMP, ISO
  27001, SOC 2 Type 2, and industry-specific frameworks
  have varying expectations for supply-chain hygiene.
  FedRAMP High and similar regimes typically expect a
  documented vetting policy and evidence of its execution.

- **D4. Transitive footprint tolerance.** Some projects
  accept large transitive graphs (modern JavaScript
  projects routinely have 1000+ transitive dependencies);
  others actively minimize transitives. Policy decisions
  about transitive review depth follow from this driver.

- **D5. Ecosystem maturity.** Different language ecosystems
  have different baseline supply-chain hygiene. Go,
  Rust's first-party crates, Maven Central, and PyPI with
  attestations are relatively mature. npm has a higher
  rate of supply-chain incidents historically. The policy
  may apply different rigor to different ecosystems.

- **D6. Build-time cost tolerance.** Strict vetting can
  delay dependency adoption by days while review proceeds.
  Some projects (research, exploratory, prototype) cannot
  tolerate that delay; others (production financial,
  regulated medical) require it.

- **D7. Team size and contributor distribution.** A small
  team where every contributor reviews dependency PRs
  works differently from a large team with a dedicated
  supply-chain reviewer. The policy reflects who actually
  does the review.

## Considered Options

The substrate-recognized options span a spectrum from strict
allowlist to no policy.

### Option 1: Strict allowlist (every direct dependency requires explicit approval)

**Substrate preference:** Substrate-acceptable for highly-
regulated contexts only.

**Applicable when:** Regulatory regime requires it (FedRAMP
High, certain government and financial contexts);
operational capacity supports the review effort; the
project values strong supply-chain assurance over rapid
dependency adoption.

**Pros:**
- Strongest supply-chain assurance posture
- Forces deliberate decisions about every introduced
  dependency
- Audit-friendly: the allowlist itself is the evidence
- Aligned with regulated-environment expectations

**Cons:**
- High operational cost; review effort scales with
  dependency-addition rate
- Can block legitimate work; produces frustration if
  intake is slow
- Difficult to maintain when team capacity is uneven or
  reviewer attention is intermittent
- Risk of decay into rubber-stamp approvals if the
  process is not respected

### Option 2: Criteria-based gate (dependencies meeting documented criteria auto-approved; others reviewed)

**Substrate preference:** Substrate-PREFERRED for most
production projects.

**Applicable when:** Project has the capacity to define
and maintain objective criteria; the criteria can be
checked mechanically or with light review effort; the
project wants to balance assurance with adoption velocity.

**Pros:**
- Scales: most dependencies auto-approve, freeing reviewer
  time for genuinely novel introductions
- Criteria provide a transparent decision basis
- Compatible with OpenSSF Scorecard, npm trust signals,
  and other automated supply-chain signal sources
- Falsifiable: a reviewer can point to the failing
  criterion when rejecting

**Cons:**
- Criteria definition is itself work; criteria must be
  maintained as the ecosystem evolves
- Auto-approval may admit dependencies that fail the
  spirit of the policy while meeting its letter
- Requires tooling to apply criteria at PR time

### Option 3: Lightweight gate (PR review with informal criteria)

**Substrate preference:** Substrate-acceptable for small
teams and lower-risk projects.

**Applicable when:** Small team where every contributor
sees every PR; the project does not have regulatory
constraints that demand more rigor; the cost of formal
criteria exceeds the benefit at the project's scale.

**Pros:**
- Low operational cost
- Captures reviewer judgment without forcing it into a
  checklist
- Works well when the reviewer pool is small and
  consistent

**Cons:**
- Not auditable: no artifact records the reasoning
- Inconsistent across reviewers and over time
- Decay risk: the implicit criteria shift unpredictably
- Does not satisfy regulated-environment expectations

### Option 4: No policy (ad-hoc decisions per PR)

**Substrate preference:** Substrate-DISCOURAGED as a
deliberate choice. Acceptable only for clearly experimental
or non-production projects.

**Applicable when:** Throwaway prototype, research code
not on a production path, learning project.

**Pros:**
- Zero overhead
- Maximum velocity for early-stage exploration

**Cons:**
- Fails dependency-management.vetting-policy at face value (no documented policy)
- Produces dependency graphs no one understands
- Cannot satisfy any review for compliance, security
  audit, or M&A diligence

## Decision Outcome

The substrate's preferred order of consideration for new
projects:

1. **Option 2 (criteria-based gate)** for any production
   project with the capacity to define criteria
2. **Option 1 (strict allowlist)** for regulated contexts
   where the regulatory regime expects it and the project
   has the operational capacity
3. **Option 3 (lightweight gate)** for small teams with
   small dependency surfaces and no regulatory constraints
4. **Option 4 (no policy)** never for production;
   acceptable for clearly experimental projects with the
   understanding that dependency-management.vetting-policy is explicitly out of
   scope per the consumer's profile

Consumers may choose any option that fits their context.
Choices that deviate from substrate preference for a given
context must be explicitly justified in the consumer's ADR.

## Pros and Cons of the Options

Detailed analysis is provided per option in the Considered
Options section above. Consumers should adapt this analysis
to their specific project context.

When the project context aligns clearly with a substrate-
preferred option (e.g., a small-team production service
clearly fits Option 2 or Option 3 depending on capacity),
the consumer's ADR can be relatively short. When the project
context creates tension (e.g., a small team in a regulated
context that nominally requires Option 1 but lacks the
capacity), the ADR must address the tension explicitly and
reason through the trade-off, possibly committing to capacity
investment or to an interim compromise with a documented
upgrade path.

## Documentation Required

Consumers using this framework satisfy dependency-management.vetting-policy by
producing an ADR in their project that addresses each of
the following. The consumer's ADR location is substrate-
recommended at
`/docs/decisions/ADR-XXX-dependency-vetting-policy.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: project-specific
  context covering language ecosystems in use, dependency
  surface size, team operational capacity, regulatory
  context, and any existing supply-chain incidents that
  inform the policy
- **Decision Drivers**: the substrate's drivers (D1-D7
  above) adapted to the project's specific context, plus
  any project-specific drivers
- **Considered Options**: at least the substrate options
  that are plausibly applicable; consumers may exclude
  options with brief reasoning (e.g., "Option 1 excluded:
  team capacity does not support strict allowlist
  intake")
- **Decision Outcome**: the chosen option with reasoning
  that references the decision drivers
- **Concrete Criteria** (for Option 2): the specific
  criteria that determine auto-approval (license allow-
  list, OpenSSF Scorecard threshold, maintenance recency
  window, CVE history window, transitive footprint
  ceiling)
- **Intake Process**: who reviews, on what SLA, with
  what escalation path
- **Substrate Alignment**: explicit statement of whether
  the choice aligns with substrate-preferred options;
  deviations must be justified
- **Consequences**: positive consequences (which risks
  are managed), negative consequences (overhead,
  acceptable false rejects), and required follow-up work
  (tooling, training, dependency inventory)
- **Pros and Cons of Each Option**: option-comparative
  analysis showing why the chosen option was preferred
  over the rejected options
- **References**: dependency-management.vetting-policy substrate rule, related
  substrate rules in scope, project-specific references
  (regulatory documentation, prior ADRs)
- **Decision Review Schedule**: next scheduled review date
  (substrate-recommended annually) and triggers that force
  earlier review (major incident, regulatory change,
  substrate version increment, team-size or capacity
  change)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR. Consumers can self-review against the
checklist before submitting their ADR for acceptance.

## More Information

This framework is referenced by:

- **dependency-management.vetting-policy** (substrate rule): the rule that requires
  consumers to author a dependency vetting policy ADR
- **dependency-management.provenance** (provenance review): the policy
  determines the evidence required at provenance review
  time
- **dependency-management.update-cadence** (update cadence): the policy informs how
  cadence applies to different dependency classes
- **dependency-management.pinned-versions and dependency-management.vulnerable-dependencies**: the policy operates
  above L1; L1 enforces the mechanical floor regardless
  of policy choice

This framework relates to (but is independent of):

- **Cross-concern boundary with supply-chain**: SBOM
  generation, SLSA attestation, signed-release publishing
  are supply-chain-concern rules. The vetting policy may
  reference supply-chain artifacts (SBOM, attestation) as
  evidence; the policies are coordinated but separately
  scoped.
- **Cross-concern boundary with license-compliance**:
  license allow-listing may live in a separate license-
  compliance concern (not yet scoped); for now, the
  vetting policy is the substrate-recognized home for
  license decisions.

External references:

- OpenSSF Concise Guide for Evaluating Open Source Software:
  https://github.com/ossf/wg-best-practices-os-developers/blob/main/docs/Concise-Guide-for-Evaluating-Open-Source-Software.md
- CISA Open Source Software Security Action Plan:
  https://www.cisa.gov/sites/default/files/2023-09/CISA-OSS-Action-Plan-508c.pdf
- OpenSSF Scorecard:
  https://github.com/ossf/scorecard
- SLSA v1.0 specification:
  https://slsa.dev/spec/v1.0/
- OWASP Software Component Verification Standard (SCVS):
  https://owasp.org/www-project-software-component-verification-standard/
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
