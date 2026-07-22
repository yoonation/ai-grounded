---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: authentication.mfa-factor-selection
title: "MFA Factor Selection"
lifecycle-status: stable
commons-version: "0.2.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-19"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
ai-assistance: "AI drafted from substrate-author intent. Second decision framework authored; uses the L3 MADR format proven by auth-strategy.madr.md and validated via scripts/validate-decision-frameworks.sh."
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention."
authoritative-sources:
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md"
  - "https://pages.nist.gov/800-63-4/sp800-63b.html"
  - "https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html"
  - "https://fidoalliance.org/passkeys/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.auth-strategy
---

# MFA Factor Selection

This decision framework provides the substrate's analysis of MFA
factor options. Consumers reference this framework when authoring
their own ADR documenting their application's MFA factor selection
(substrate-recommended location for the consumer's ADR:
`/docs/decisions/ADR-XXX-mfa-factor-selection.md`).

The framework is referenced by substrate rule authentication.mfa-factor-selection, which
requires applications to have an explicit, documented MFA factor
decision before MFA-related code is implemented. This rule applies
when the authentication.authentication-strategy strategy decision results in a strategy that
requires a separate MFA factor (passwords-plus-MFA, federated-with-
step-up, hybrid). The rule does NOT apply when the strategy is
passkey-primary because passkeys are themselves the factor.

## Context

MFA factor selection determines the authenticator assurance level
(AAL) achievable by the authenticated session. Different factor
types provide different phishing resistance, different recovery
flow complexity, different regulatory acceptability, and different
operational overhead.

The most common substrate failure mode is defaulting to SMS-based
codes because they are familiar and easy to implement. SMS suffers
from SIM-swap attacks (the attacker transfers the victim's phone
number to a controlled SIM), telco SS7 protocol vulnerabilities,
and inherent carrier dependency. NIST SP 800-63B-4 explicitly does
NOT permit SMS OOB authentication for AAL2 or higher as of the
2024 revision; applications subject to AAL2 requirements cannot
defensibly use SMS as their primary second factor.

This framework forces the choice to be deliberate. The substrate
analyzes each factor option; consumers select based on their
context and document the rationale in their ADR.

## Decision Drivers

The substrate identifies the following drivers that should inform
MFA factor selection. Consumers may add application-specific
drivers but should address each substrate driver in their ADR.

- **D1. Target authenticator assurance level (AAL).** NIST SP
  800-63B-4 defines AAL1, AAL2, and AAL3. Regulated industries
  often have a target AAL (e.g., banking is typically AAL2).
  The factor choice must support the target AAL.

- **D2. User population's device capability.** Are users on
  devices with platform authenticators (FaceID, TouchID, Windows
  Hello)? Do users have hardware security keys? Can users
  install authenticator apps? Geographic distribution affects
  device profile and authenticator availability.

- **D3. Phishing threat model.** Is phishing in the application's
  threat model? Financial services, identity providers, and
  high-value content applications almost universally have
  phishing in scope. Phishing-resistant factors (WebAuthn,
  passkeys, FIDO2) defeat the most common attack vector.

- **D4. Recovery flow tolerance.** Different factors have
  different recovery costs. Hardware tokens lost in the field
  are expensive to replace and time-consuming to re-enroll.
  TOTP apps lost with the user's phone require recovery flows
  that themselves are attack surface.

- **D5. Regulatory context.** PCI DSS, HIPAA, FedRAMP, and
  industry frameworks have specific authenticator requirements.
  The factor choice must satisfy applicable regulations.
  Documented compliance argument is part of the MADR.

- **D6. Operational and procurement cost.** Hardware tokens
  have unit cost; TOTP and push are software-based and free.
  Support burden for factor enrollment and recovery varies by
  factor.

- **D7. Accessibility.** Some factors are inaccessible to some
  users (visual impairment with TOTP apps; motor impairment
  with hardware tokens). The factor mix must accommodate the
  user population's accessibility needs.

## Considered Options

### Option 1: WebAuthn / passkeys / FIDO2 hardware tokens

**Substrate preference:** Substrate-preferred for new
applications whose user population can use modern authenticators.

**Pros:**
- Phishing-resistant by design (the authenticator only releases
  the assertion to the legitimate origin)
- Supports NIST AAL3 with hardware-bound credentials
- Aligned with FIDO Alliance and W3C Web Authentication standards
- Increasingly familiar to users; OS-level support on iOS, Android,
  Windows, macOS

**Cons:**
- Enrollment friction; users unfamiliar with passkeys may struggle
- Recovery complexity when user loses all enrolled passkeys
- Older devices and browsers may be unsupported
- Hardware tokens have procurement cost ($25-$60 per token typical)

### Option 2: Push notifications with number matching

**Substrate preference:** Substrate-acceptable. Increasing
substrate preference as number-matching becomes the default in
major implementations.

**Pros:**
- Better user experience than typing codes
- Resists push fatigue attacks (user must match a number shown
  on the login screen to numbers shown in the push)
- Can include context (location, IP, requesting application)
- AAL2 acceptable per NIST SP 800-63B-4 when implemented correctly

**Cons:**
- Requires authenticator app installed on user's device
- Requires internet connectivity on the user's device at login time
- Push fatigue attacks succeed against implementations without
  number matching
- Dependency on app vendor (Duo, Microsoft Authenticator, Okta
  Verify, etc.)

### Option 3: TOTP apps

**Substrate preference:** Substrate-acceptable as a second factor
for AAL2.

**Pros:**
- Widely supported by free authenticator apps (Google
  Authenticator, Authy, 1Password, Aegis, Microsoft Authenticator)
- Works offline once enrolled (no internet required at login)
- No carrier dependency
- AAL2 acceptable per NIST SP 800-63B-4

**Cons:**
- Phishable: user can be tricked into typing the code on a
  fake site, and the attacker can replay the code within the
  30-second window
- Device loss requires recovery flow; the TOTP secret is on
  the user's device
- Shared secret model: the secret is on both the server and
  the user's device, both of which can be compromised

### Option 4: Phone-call OTP

**Substrate preference:** Substrate-acceptable for accessibility
cases where other factors are impractical.

**Pros:**
- Works for users without smartphones
- Accessible to users with visual impairments (audio delivery)
- Familiar interaction model

**Cons:**
- Subject to the same SIM-swap and SS7 risks as SMS
- Higher operational cost per authentication than digital factors
- AAL constraint: NIST SP 800-63B-4 permits phone-call OOB only
  as a single-factor authenticator at AAL1; as a second factor
  it is permitted at AAL2 with restrictions

### Option 5: SMS-based codes

**Substrate preference:** Substrate-discouraged. Permitted only
under documented constraints.

**Pros:**
- Works on any phone including non-smart phones
- Well-understood by users
- Lowest implementation friction

**Cons:**
- SIM-swap attacks (very common in financial services attacks)
- Telco SS7 vulnerabilities (interception of SMS in transit)
- Carrier dependency (deliverability, regional availability)
- **NIST SP 800-63B-4 does NOT permit SMS OOB authenticator for
  AAL2 or higher as of the 2024 revision.** Applications subject
  to AAL2 requirements cannot use SMS as a compliant second
  factor.

Substrate permits this option only when:
- The application's required AAL is AAL1 (low assurance)
- The threat model documents that SIM-swap and SS7 attacks are
  out of scope (rare for production-grade applications)
- A stronger factor is impractical for the user population
- Justification is documented in the MADR

### Option 6: Email-based codes

**Substrate preference:** Substrate-discouraged except as
last-resort recovery.

**Pros:**
- No carrier dependency
- Works for users without smartphones

**Cons:**
- Email is often the recovery channel for everything else; using
  it as a primary MFA factor creates a single point of failure
  (attacker who compromises email gets MFA for free)
- Email is phishable
- Email deliverability variance affects login reliability
- Not permitted as a primary OOB authenticator at AAL2 per NIST
  SP 800-63B-4

### Substrate-preferred order for new applications

1. **Option 1 (WebAuthn/passkeys)** for any user population that
   can support it
2. **Option 2 (push with number matching)** for enterprise
   contexts where a managed authenticator app is already
   deployed
3. **Option 3 (TOTP)** as a second-factor when 1 and 2 are
   impractical
4. **Option 4 (phone-call)** as an accessibility fallback
5. **Option 5 (SMS)** only under documented AAL1 + threat-model
   constraints
6. **Option 6 (email)** only as last-resort recovery

Backup codes per authentication.mfa-enrollment are required regardless of primary
factor choice as the break-glass recovery mechanism.

## Decision Outcome

Consumers select their MFA factor mix based on their context.
The decision must:

- State the chosen factor(s) explicitly
- State the target AAL and justify how the factor mix satisfies it
- Address phishing resistance in the application's threat model
- Document recovery flow design (typically: backup codes per
  authentication.mfa-enrollment plus support-channel verification)
- For deviations from substrate preference (especially SMS-as-
  primary), provide explicit justification

Choices that deviate from substrate preference for a given
context must be explicitly justified in the consumer's ADR
(see Documentation Required section).

## Pros and Cons of the Options

Detailed analysis per option is provided in the Considered
Options section above. Consumers should adapt this analysis to
their specific application context. Per-option comparison
matters when multiple options are plausible candidates; consumers
should explicitly compare the top candidates rather than
defaulting to the first one considered.

## Documentation Required

Consumers using this framework satisfy authentication.mfa-factor-selection by producing
an ADR in their application that addresses each of the following.
The consumer's ADR location is substrate-recommended at
`/docs/decisions/ADR-XXX-mfa-factor-selection.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: application-specific context
  covering target AAL, user device profile, phishing threat
  model, regulatory context, and accessibility considerations
- **Decision Drivers**: the substrate's drivers (D1-D7 above)
  adapted to the application's specific context, plus any
  application-specific drivers the substrate cannot anticipate
- **Considered Options**: the substrate factor options that are
  plausibly applicable; consumers may exclude options with brief
  reasoning
- **Decision Outcome**: the chosen factor mix with reasoning that
  references the decision drivers; for multi-factor applications
  (offering multiple MFA options to users) the ADR specifies
  the full mix
- **Substrate Alignment**: explicit statement of whether the
  choice aligns with substrate-preferred factors for the
  application context; deviations (especially SMS-as-primary)
  must be justified with explicit reference to applicable AAL
  and threat model
- **Consequences**: positive consequences (which threats are
  mitigated, what assurance level is achieved), negative
  consequences (operational overhead, user friction, recovery
  cost), and required follow-up work (inventory of substrate
  rules in scope, especially authentication.mfa-on-privileged-operations fresh-MFA-on-privileged-
  ops, authentication.mfa-enrollment enrollment hardening)
- **Pros and Cons of Each Option**: option-comparative analysis
- **References**: authentication.mfa-factor-selection substrate rule, authentication.authentication-strategy
  strategy decision (this MADR builds on that one), related
  substrate rules, application-specific references
- **Decision Review Schedule**: next scheduled review date and
  triggers that force earlier review (NIST guidance change
  affecting permitted factors, regulatory change, security
  incident affecting MFA factor type in use)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR.

## More Information

This framework is referenced by:

- **authentication.mfa-factor-selection** (substrate rule): the rule that requires this
  MADR
- **authentication.authentication-strategy** (substrate rule, related framework): the
  strategy decision. The MFA factor selection follows from the
  strategy choice; passkey-primary strategies do not need a
  separate factor selection
- **authentication.mfa-on-privileged-operations** (fresh MFA on privileged operations): applies
  to the chosen factor
- **authentication.mfa-enrollment** (MFA enrollment hardening): applies to the
  enrollment flow for the chosen factor
- **authentication.timing-safe-comparison** (timing-safe comparison): applies to factor
  verification (TOTP codes, backup codes, etc.)

This framework relates to:

- `decision-frameworks.auth-strategy`: the predecessor decision;
  whether authentication.mfa-factor-selection applies at all depends on the authentication.authentication-strategy
  outcome

External references:

- OWASP ASVS v5.0.0 V6 (Authentication):
  https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V6-Authentication.md
- NIST SP 800-63B-4 (Digital Identity Guidelines):
  https://pages.nist.gov/800-63-4/sp800-63b.html
- OWASP Multifactor Authentication Cheat Sheet:
  https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html
- FIDO Alliance Passkey deployment guidance:
  https://fidoalliance.org/passkeys/
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
