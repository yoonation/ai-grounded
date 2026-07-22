<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.mfa-factor-selection MFA factor selection MADR (good)

A substrate-original example of a well-formed MFA factor
selection MADR. The application described is fictional (same
fictional ExampleApp used in the authentication.authentication-strategy good example, for
continuity). The MADR demonstrates the substrate's quality
requirements.

---

```markdown
# ADR-008: MFA Factor Selection

## Status

Accepted

Date: 2026-04-22
Deciders: J. Park (CTO), M. Singh (Security Lead), R. Chen (Eng Lead)
Consulted: UX research; customer support lead; compliance counsel
Informed: All engineering; product management

## Context and Problem Statement

This ADR follows ADR-007 (authentication strategy: hybrid
passkey-primary with federated alternative). The hybrid strategy
requires MFA factor selection for users who cannot use the
passkey path (older devices, accessibility considerations). The
federated path inherits the IdP's authenticator choice; this
ADR covers only the application-managed factors.

Target AAL: AAL2 per NIST SP 800-63B-4. Rationale: ExampleApp
aggregates personal financial data including account numbers
(last 4 digits) and transaction history. While not directly
processing money movement, the data sensitivity meets the AAL2
threshold per substrate-author's interpretation of GLBA Safeguards
Rule "appropriate authentication" and PCI DSS adjacency
considerations. Compliance counsel concurs.

User device profile: 80% mobile (modern iOS 16+ and Android 9+,
which support platform authenticators); 18% desktop browser
(modern); 2% legacy or unsupported. Mobile users are the primary
passkey enrollers per ADR-007.

Phishing threat model: in scope. Financial aggregation
applications are documented phishing targets. The application-
managed factor must be phishing-resistant or the trade-off must
be acknowledged.

Recovery flow tolerance: low to moderate. ExampleApp's user
population churns when locked out for hours. Recovery via
backup codes is the substrate-required mechanism; recovery via
the federated path is the second mechanism (the user logs in via
Sign in with Apple or Sign in with Google, which authenticates
via that IdP's factor).

## Decision Drivers

D1. Target AAL2 per NIST SP 800-63B-4 limits factor choices.
SMS OOB is not permitted at AAL2+ as of 2024 revision.

D2. Mobile-first user population means platform authenticators
(WebAuthn) are widely available. Hardware tokens are unnecessary
for the consumer use case.

D3. Phishing is in scope (D6 from ADR-007). Phishing-resistant
factors strongly preferred for the primary factor.

D4. Recovery cost must be low. Backup codes (authentication.mfa-enrollment) are
the substrate-required mechanism. Federated identity from
ADR-007 provides a second recovery path.

D5. GLBA Safeguards Rule and PCI DSS adjacency require
"appropriate authentication"; AAL2 is the substrate-author's
interpretation. Substrate guidance on financial data
applications excludes SMS as primary; aligns with our analysis.

D6. Procurement cost: minimal. The application-managed factor
is software-based; no hardware tokens are issued. Backup codes
are generated server-side at no incremental cost.

D7. Accessibility: 2% of the user population on legacy or
unsupported devices needs a fallback. Substrate-acceptable
fallback within AAL2: TOTP via authenticator app.

## Considered Options

1. WebAuthn / passkeys (primary, for users on supported devices)
2. TOTP via authenticator app (secondary, for users on
   unsupported devices)
3. Push with number matching (rejected; see Pros and Cons)
4. SMS-based codes (rejected; see Pros and Cons)
5. Phone-call OTP (rejected; see Pros and Cons)

## Decision Outcome

Chosen mix:
- **Primary: WebAuthn / passkeys**, for users on supported
  devices. Aligns with ADR-007 (passkey-primary strategy).
- **Secondary: TOTP via authenticator app**, for the ~2% of users
  on devices that do not support platform authenticators.
- **Recovery: backup codes per authentication.mfa-enrollment**, mandatory for both
  factor types.

### Substrate alignment

- Substrate-preferred factors for AAL2 consumer application:
  Options 1 (WebAuthn) and 2 (push with number matching) per the
  substrate analysis in decision-frameworks/mfa-factor-selection.madr.md
- This decision: Option 1 (WebAuthn) as primary; Option 3 (TOTP)
  as secondary
- Alignment status: Aligned. Substrate-preferred primary chosen.
  Substrate-acceptable secondary (TOTP) chosen over substrate-
  preferred Option 2 (push) because we do not currently deploy
  an authenticator app and pushing a vendor's app adoption is
  out of scope for this implementation phase.
- Future review: if user adoption of the secondary factor is
  material (>5% of authentications), reconsider push as primary
  to gain the number-matching anti-fatigue benefit.

## Consequences

### Positive consequences

- Phishing resistance achieved on the primary path
- AAL2 requirement satisfied
- Mobile user experience optimal
- No SMS attack surface (no SIM-swap or SS7 risk for our auth)
- Recovery via backup codes plus federated path keeps support
  load low

### Negative consequences

- TOTP fallback is phishable; the ~2% of users on the secondary
  path are vulnerable to phishing. Mitigation: user education;
  consider hard-requiring passkey upgrade as the device profile
  evolves
- Backup code generation and storage adds operational complexity
  (authentication.mfa-enrollment enrollment hardening rule applies)
- Multiple factor paths increase the operational and review
  surface

### Required follow-up work

Substrate rules in scope given this decision:

- authentication.mfa-on-privileged-operations (MFA on privileged operations) applies to both
  factor paths
- authentication.mfa-enrollment (MFA enrollment hardening) applies to enrollment
  for both factors and to backup code generation
- authentication.timing-safe-comparison (timing-safe comparison) applies to backup code
  verification
- authentication.password-hashing (password storage hashing) applies to backup code
  storage (codes are hashed with Argon2id per the substrate's
  password-grade hashing standard)
- authentication.rate-limiting (rate limiting) applies to MFA challenge endpoints

## Pros and Cons of the Options

### Option 1: WebAuthn / passkeys

- Good, because phishing-resistant (D3)
- Good, because supports AAL2 with appropriate enrollment (D1)
- Good, because platform authenticator available to 98% of user
  population (D2)
- Bad, because 2% of users cannot use this option (need fallback)
- Bad, because recovery requires backup codes + identity proof

### Option 2: TOTP via authenticator app

- Good, because supports AAL2
- Good, because no carrier dependency
- Good, because widely supported via free apps (Google
  Authenticator, Authy, 1Password)
- Bad, because phishable (D3 partially unsatisfied)
- Bad, because user must install and configure an app

### Option 3: Push with number matching (REJECTED)

- Good, because substrate-preferred at AAL2
- Bad, because requires vendor authenticator app deployment
- Bad, because operational complexity to manage app vendor
  relationship
- Reason for rejection: we do not currently deploy an
  authenticator app; adopting one is out of scope for this
  implementation phase. Re-evaluate in next annual review.

### Option 4: SMS-based codes (REJECTED)

- Good, because lowest user friction
- Bad, because SIM-swap and SS7 risks (D5)
- Bad, because NIST SP 800-63B-4 does not permit SMS OOB at
  AAL2+ (D1)
- Reason for rejection: AAL2 target rules SMS out per regulatory
  guidance. Substrate guidance also discourages SMS for financial
  applications.

### Option 5: Phone-call OTP (REJECTED)

- Good, because accessible to users without smartphones
- Bad, because subject to SIM-swap and SS7 risks similar to SMS
- Bad, because higher operational cost per authentication
- Reason for rejection: user population is 100% smartphone-
  capable per onboarding requirements; accessibility is handled
  via the TOTP secondary path (TOTP apps support accessibility
  features on iOS and Android). Re-evaluate if user population
  changes.

## References

- authentication.mfa-factor-selection (substrate rule)
- ADR-007 (predecessor: authentication strategy)
- decision-frameworks.auth-strategy (substrate framework
  referenced by ADR-007)
- decision-frameworks.mfa-factor-selection (substrate framework
  referenced by this ADR)
- authentication.mfa-on-privileged-operations, authentication.mfa-enrollment, authentication.timing-safe-comparison, authentication.password-hashing,
  authentication.rate-limiting (substrate rules in scope)
- NIST SP 800-63B-4 (2024 revision)
- GLBA Safeguards Rule (16 CFR Part 314)

## Decision review schedule

- Next scheduled review: 2027-04-22 (annual)
- Triggers that force earlier review:
  - NIST SP 800-63B revision affecting AAL2 factor permissions
  - Material change in user device profile (e.g., new platform
    authenticator availability or deprecation)
  - User adoption of TOTP fallback exceeds 5% of authentications
    (re-evaluate push as primary)
  - Security incident affecting any factor type in use
  - Regulatory change affecting financial-data authentication
```

---

## Why this example is substrate-compliant

- MADR exists and is in standard location
- authentication.mfa-factor-selection applicability confirmed (references ADR-007 and
  the hybrid strategy that requires a separate factor)
- Target AAL stated (AAL2) with regulatory basis (GLBA, PCI DSS
  adjacency)
- User device profile assessed (80% mobile, 18% desktop, 2%
  legacy)
- Phishing threat model addressed (in scope, addressed by
  passkey primary)
- Substrate-preferred factors considered (Options 1 and 2
  analyzed; Option 3 explicitly evaluated and rejected with
  reasoning)
- SMS rejected with explicit reference to AAL2 and substrate
  guidance
- Substrate alignment explicit (Aligned with reasoning for
  Option 3 vs Option 2 choice)
- Backup codes covered (authentication.mfa-enrollment referenced)
- Multiple-factor mix enumerated (primary + secondary +
  recovery)
- Review schedule includes factor-evolution triggers (NIST
  revision, device profile change, user adoption telemetry)

## Cross-reference

- Substrate rule: authentication.mfa-factor-selection in catalogs/concerns/authentication.oscal.yaml
- Decision framework MADR: decision-frameworks/mfa-factor-selection.madr.md
- Review binding: checklist.md
- Anti-pattern: examples/authentication/mfa-factor-selection-anti-pattern.md
