---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: authentication.authentication-strategy
title: "Authentication Strategy Selection"
lifecycle-status: stable
commons-version: "0.2.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-19"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
ai-assistance: "AI drafted from substrate-author intent. First decision framework authored end-to-end; exercises the MADR-format decision framework pattern and the decision-framework.schema.json for the first time. Frontmatter validates clean against schema at lifecycle-status stable under Charter Section 2.4.1 solo-author attestation."
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
authoritative-sources:
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md"
  - "https://pages.nist.gov/800-63-4/sp800-63b.html"
  - "https://fidoalliance.org/passkeys/"
  - "https://adr.github.io/madr/"
---

# Authentication Strategy Selection

This decision framework provides the substrate's analysis of
authentication strategy options. Consumers reference this
framework when authoring their own ADR documenting their
application's authentication strategy choice (substrate-
recommended location for the consumer's ADR:
`/docs/decisions/ADR-XXX-authentication-strategy.md`).

The framework is referenced by substrate rule authentication.authentication-strategy, which
requires applications to have an explicit, documented strategy
decision before authentication implementation begins. Consumers
satisfy authentication.authentication-strategy by authoring an ADR that adapts the analysis
in this framework to their application context.

## Context

Authentication strategy is the foundational choice that determines
which substrate rules apply, how hard each rule is to satisfy, and
what additional concerns the application inherits. The choice has
implications across the entire authentication surface and cannot
be compensated for downstream by perfect implementation of
individual L1 or L2 rules.

Password-based authentication inherits the full AUTH-L1 plus
AUTH-L2 rule set including password policy, rate limiting, breach
corpus screening, account lockout, and MFA enrollment hardening.
Passkey-based authentication eliminates several of those rules but
adds enrollment-flow and recovery-flow complexity. Federated
authentication delegates most of the auth surface to an identity
provider but introduces dependency management and identity-
lifecycle concerns.

Making this choice without explicit analysis is the most common
substrate failure mode. Teams default to password-based
authentication because it is familiar; they then implement it
incompletely because the rule surface is larger than they
anticipated. This framework forces the choice to be deliberate.

The substrate provides analysis of each viable option but does
not prescribe a single choice. Consumers select based on their
context. The substrate requires the choice to be documented and
reasoned; it does not require consumers to choose the substrate-
preferred option.

## Decision Drivers

The substrate identifies the following drivers that should inform
the strategy choice. Consumers may add application-specific
drivers but should address each substrate driver in their ADR.

- **D1. User population's capability with modern auth methods.**
  Are users on devices that support platform authenticators
  (WebAuthn-compatible)? Is the population technical enough to
  enroll passkeys or use MFA apps? Geographic distribution
  affects device profile.

- **D2. Regulatory context.** GLBA (US financial services), GDPR
  (EU personal data), HIPAA (US healthcare), PCI DSS (payment
  cards), SOX (US public companies), and industry-specific
  frameworks each have authentication implications. NIST SP
  800-63B-4 Authenticator Assurance Levels (AAL1, AAL2, AAL3)
  inform what is acceptable for which data sensitivity.

- **D3. Existing identity infrastructure.** Is there an
  established IdP relationship (corporate SSO, Okta, Azure AD,
  Auth0)? Greenfield applications have more freedom; applications
  integrating with existing identity have constraints.

- **D4. Operational maturity.** Security team size, on-call
  coverage, incident response readiness. Some strategies have
  larger operational surface than others. Password-based
  authentication has the largest rule surface and the most
  operational overhead.

- **D5. Recovery flow tolerance.** How disruptive can identity
  recovery be for legitimate users? High-churn segments (consumer
  applications) cannot tolerate hours-long lockouts. Enterprise
  B2B applications can absorb more recovery friction.

- **D6. Phishing resistance requirements.** Is the application a
  high-value phishing target (financial services, identity
  providers, content with attached real-world consequence)?
  Phishing-resistant strategies (passkeys) are substantially
  stronger.

- **D7. Time to market.** Some strategies have shorter
  implementation paths than others. Password-based requires the
  full L1+L2 rule surface and is the longest path.

## Considered Options

### Option 1: Passkeys (WebAuthn) as primary, passwords as fallback

**Substrate preference:** Substrate-preferred for consumer
applications whose user population can use WebAuthn.

**Applicable when:** User population can use modern browsers
with platform authenticators or hardware security keys
(typical: iOS 16+, Android 9+, modern desktop browsers).

**Pros:**
- Phishing-resistant per FIDO Alliance specification
- Aligned with NIST SP 800-63B-4 modern authenticator guidance
- Eliminates the password rule surface (authentication.password-hashing not in scope;
  authentication.password-policy password policy not in scope) where passkeys are
  the only path; partial elimination where passwords are recovery
  factor
- Better mobile user experience than password+MFA

**Cons:**
- Enrollment friction for first-time users unfamiliar with passkeys
- Recovery complexity when user loses all enrolled passkeys
- Older devices and browsers may be unsupported
- Operational learning curve for support staff

### Option 2: Passwords plus mandatory MFA

**Substrate preference:** Substrate-acceptable.

**Applicable when:** Passkey support is impractical due to legacy
client constraints, regulated environments specifying password-
based auth, or user population that cannot enroll modern
authenticators.

**Pros:**
- Operationally well-understood; mature tooling
- Maximally compatible across devices and clients
- No dependency on third-party identity providers
- Substrate rules are comprehensive (the AUTH-L1+L2 rule set
  exists precisely because this option is well-traveled)

**Cons:**
- Largest rule surface to satisfy correctly (all AUTH-L1 plus
  authentication.rate-limiting, authentication.mfa-on-privileged-operations, authentication.account-lockout, authentication.password-policy, authentication.mfa-enrollment)
- User friction from password requirements and MFA challenges
- Password policy and breach corpus screening have operational
  overhead (authentication.password-policy)
- Phishable unless MFA is phishing-resistant (TOTP is not)

### Option 3: Federated identity via OIDC

**Substrate preference:** Substrate-preferred for B2B applications
with established IdP relationships.

**Applicable when:** B2B application where the customer or user
population has an established identity provider relationship
(corporate SSO, Okta, Azure AD, Workspace, Auth0).

**Pros:**
- Delegates authentication surface to specialists
- Consistent identity for users across many applications
- Inherits the IdP's authentication strength (often AAL2 or higher)
- Reduced operational burden on the application

**Cons:**
- Hard dependency on IdP availability and security
- Identity-lifecycle management requires coordination with the
  federation layer (provisioning, deprovisioning, role changes)
- Vendor lock-in considerations; multi-IdP support multiplies
  implementation cost
- B2C applications rarely have an established IdP context

### Option 4: Magic links or email-based passwordless

**Substrate preference:** Substrate-acceptable for low-risk
applications only.

**Applicable when:** Low-risk applications with personal data
that is not financial, medical, or otherwise regulated.

**Pros:**
- Low user friction at login
- No password rule surface
- Simple to implement

**Cons:**
- Authentication strength is tied to email account security,
  which is often the weakest link in attack chains
- Email deliverability and inbox-handling concerns affect login
  reliability
- Substrate does NOT recommend for applications handling personal
  financial data, medical records, or regulated content

### Option 5: Hybrid (multiple primary strategies offered)

**Substrate preference:** Substrate-acceptable with caveats.

**Applicable when:** Consumer wants to offer multiple
authentication paths to address edge cases (e.g., passkeys
primary with federated alternative for users on unsupported
devices or as a recovery path).

**Pros:**
- Combines benefits of multiple strategies
- Can address edge cases without forcing fallback to a weaker
  primary option
- Improves accessibility for users with diverse device profiles

**Cons:**
- Each path independently must satisfy all applicable substrate
  rules; operational and review surface multiplied by path count
- More complex user experience (which path do users take?)
- More attack surface to defend

## Decision Outcome

The substrate's preferred order of consideration for new
applications:

1. **Option 1 (passkeys)** first, for consumer applications with
   user populations capable of using modern authenticators
2. **Option 3 (federated)** for B2B applications with established
   IdP relationships
3. **Option 2 (password + MFA)** as fallback where Option 1 is
   impractical
4. **Option 5 (hybrid)** when the application has genuine
   multi-path requirements and accepts the operational cost
5. **Option 4 (magic links)** only for low-risk applications

Consumers may choose any option that fits their context. Choices
that deviate from substrate preference for a given context must
be explicitly justified in the consumer's ADR (see Documentation
Required section).

## Pros and Cons of the Options

Detailed analysis is provided per option in the Considered Options
section above. Consumers should adapt this analysis to their
specific application context, adding application-specific pros
and cons that the substrate cannot anticipate.

When the application context aligns clearly with a substrate-
preferred option (e.g., consumer app with modern user population
clearly fits Option 1), the consumer's ADR can be relatively
short, citing the substrate analysis and adding application-
specific details. When the application context creates tension
(e.g., regulated industry that nominally fits Option 2 but the
consumer wants to use Option 1 anyway), the ADR must address the
tension explicitly and reason through the trade-off.

## Documentation Required

Consumers using this framework satisfy authentication.authentication-strategy by producing
an ADR in their application that addresses each of the following.
The consumer's ADR location is substrate-recommended at
`/docs/decisions/ADR-XXX-authentication-strategy.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: application-specific
  context covering user population, risk profile, identity
  infrastructure, operational maturity, and recovery tolerance
- **Decision Drivers**: the substrate's drivers (D1-D7 above)
  adapted to the application's specific context, plus any
  application-specific drivers the substrate cannot anticipate
- **Considered Options**: at least the substrate options that
  are plausibly applicable to the application; consumers may
  exclude options with brief reasoning (e.g., "Option 4 (magic
  links) excluded: application handles financial data")
- **Decision Outcome**: the chosen option with reasoning that
  references the decision drivers
- **Substrate Alignment**: explicit statement of whether the
  choice aligns with substrate-preferred options for the
  application context; deviations must be justified
- **Consequences**: positive consequences (which threats are
  mitigated), negative consequences (operational overhead,
  user friction, dependency risk), and required follow-up work
  (inventory of substrate rules in scope given the chosen
  strategy)
- **Pros and Cons of Each Option**: option-comparative analysis
  showing why the chosen option was preferred over the rejected
  options
- **References**: authentication.authentication-strategy substrate rule, related substrate
  rules in scope, application-specific references (threat models,
  regulatory documentation, prior ADRs)
- **Decision Review Schedule**: next scheduled review date
  (substrate-recommended annually) and triggers that force
  earlier review (regulatory change, material change in user
  population, security incident)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR. Consumers can self-review against the checklist
before submitting their ADR for acceptance.

## More Information

This framework is referenced by:

- **authentication.authentication-strategy** (substrate rule): the rule that requires
  consumers to author an authentication strategy ADR.
- **authentication.rate-limiting through authentication.mfa-enrollment** (semantic rules): apply to
  most authentication strategies; the consumer's ADR enumerates
  which apply given the chosen strategy.
- the authentication mechanical (L1) rules (mechanical rules): apply
  to password-based strategies; not in scope for pure passkey or
  federated-only strategies.

This framework relates to (but is independent of):

- **authentication.mfa-factor-selection** (MFA factor selection, future framework): once
  the strategy has been chosen, MFA factor selection is a
  separate decision. authentication.mfa-factor-selection will be authored as a follow-on
  framework with its own MADR file.

The substrate's substrate-scope.md and Charter (specifically
Article V on opinionated defaults) inform how the substrate
expresses preference without prescribing.

External references:

- OWASP ASVS v5.0.0 V6 (Authentication):
  https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md
- NIST SP 800-63B-4 (Digital Identity Guidelines):
  https://pages.nist.gov/800-63-4/sp800-63b.html
- FIDO Alliance Passkey deployment guidance:
  https://fidoalliance.org/passkeys/
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
