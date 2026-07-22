<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.mfa-factor-selection MFA factor selection MADR (forbidden)

Five patterns of substrate-non-compliant MFA factor decisions.
Do not produce MADRs that look like these.

## Anti-pattern A: No MADR; SMS shipped by default

The team implements MFA by adding "send SMS code" because Twilio
is easy to integrate. SMS becomes the only MFA factor. No MADR
exists; the choice was made implicitly because it was the path
of least resistance during sprint planning.

Why this violates authentication.mfa-factor-selection:
- No documented decision
- SMS as primary at undefined AAL with no analysis of whether
  SIM-swap is in the threat model
- If the application's required AAL is AAL2 or higher, the
  choice fails NIST SP 800-63B-4 compliance
- The substrate's discouragement of SMS is not addressed

This is the most common substrate failure mode for MFA. The
substrate's L3-002 rule exists specifically to prevent this
pattern.

## Anti-pattern B: MADR exists but selects SMS without justification

```markdown
# ADR-008: MFA Factor

## Status
Accepted

## Context
We need MFA for the login flow.

## Decision
We will use SMS codes sent via Twilio.

## Substrate alignment
Deviation.
```

Why this violates authentication.mfa-factor-selection:
- "Deviation" without explanation
- No analysis of phishing threat model
- No statement of target AAL
- No consideration of why SMS over other options
- No acknowledgment of NIST SP 800-63B-4 limitations on SMS
- No discussion of SIM-swap risk in the threat model
- No backup code mention (authentication.mfa-enrollment)
- Decision-driver-free

A reviewer applying the substrate's checklist marks every
applicable question FOLLOW-UP.

## Anti-pattern C: MADR exists but is post-hoc rationalization

```markdown
# ADR-008: MFA Factor Selection

## Status
Accepted

## Context
The application requires MFA.

## Considered Options
1. TOTP (chosen)

## Decision Outcome
We chose TOTP because Google Authenticator is widely available.

## Substrate alignment
Aligned.

## Consequences
Users install Google Authenticator and scan a QR code.
```

Why this violates authentication.mfa-factor-selection:
- "Considered Options" lists only the chosen option
- WebAuthn and push (substrate-preferred for the likely AAL2
  context) are not even mentioned
- "Substrate alignment: Aligned" is unsupported (TOTP is
  substrate-acceptable but not substrate-preferred when WebAuthn
  is available; the MADR does not address the deviation from
  preference)
- No decision drivers
- No discussion of phishing threat model
- No target AAL stated
- No backup code mention
- No multi-factor mix discussion (what if users cannot use TOTP?)

## Anti-pattern D: MADR conflates strategy and factor

The team writes one combined ADR mixing authentication.authentication-strategy strategy
content and authentication.mfa-factor-selection factor content. The factor analysis is
buried in the strategy MADR.

Why this violates authentication.mfa-factor-selection:
- The two decisions have different review schedules, different
  decision drivers, different consequence inventories. Combining
  them obscures both decisions.
- When the factor needs revision (e.g., NIST 2024 revision
  deprecating SMS for AAL2+), revising "the MFA section of the
  strategy MADR" is awkward and error-prone
- Substrate review tooling expects them as separate frameworks;
  the conflated MADR breaks the validation pattern
- Future AUTH-L3 frameworks (other concerns; e.g., authorization
  decision frameworks) follow the per-decision pattern;
  conflating breaks the precedent

Remediation: split into two separate ADRs (one for strategy, one
for factor) referencing each other. The authentication.authentication-strategy good example
and authentication.mfa-factor-selection good example show the proper separation.

## Anti-pattern E: Stale MADR; NIST guidance changed since authoring

The application authored an MFA MADR in 2023 selecting SMS for
its AAL2 target. The MADR was valid at the time (older NIST
revisions did permit SMS at AAL2 with restrictions). NIST SP
800-63B-4 (2024) does NOT permit SMS at AAL2+. The application's
MADR has not been reviewed; SMS is still the production factor.

Why this violates authentication.mfa-factor-selection:
- The MADR is stale; the basis (NIST guidance permitting SMS)
  has changed
- The application's running implementation no longer meets the
  stated AAL2 target
- Substrate review-schedule triggers should have caught this
  (NIST revision affecting permitted factors is a substrate-
  recommended trigger)
- Even if the MADR had no factor-evolution triggers, annual
  review (also substrate-recommended) would have surfaced the
  issue

Remediation: review the MADR against current NIST guidance;
either migrate to a compliant factor (WebAuthn, push, or TOTP)
and update the MADR, or supersede the MADR with one that
documents the current (compliant) factor choice. Do not leave
the gap open.

## Anti-pattern F: MADR for an application using passkey-primary strategy

The team authored an MFA factor MADR for an application whose
authentication.authentication-strategy strategy is passkey-primary. The MADR analyzes TOTP,
SMS, etc. but the application does not use those factors because
passkeys ARE the factor.

Why this is wrong (but mildly):
- authentication.mfa-factor-selection conditionally applies; passkey-primary strategies
  do not require a separate factor decision
- The MADR is unnecessary work; reviewer time spent reviewing
  it is wasted
- If the MADR documents factors as "available" but unused, the
  application may inadvertently enable a weaker factor path
  later without going through the decision process

Remediation: the MADR can be left in place as documentation
(harmless), OR explicitly marked "Not applicable; authentication.authentication-strategy
strategy is passkey-primary; this framework does not apply per
its applicability condition." The latter is the substrate-
recommended pattern.

## Common failure mode across most anti-patterns

The team treats MFA as a checkbox: "we have MFA" rather than
"we have a deliberately-selected, AAL-appropriate, phishing-
threat-model-aware MFA factor mix that the substrate guidance
endorses." The substrate's L3-002 rule forces the deliberate
selection to happen and be documented.

## Cross-reference

- Substrate rule: authentication.mfa-factor-selection in catalogs/concerns/authentication.oscal.yaml
- Decision framework MADR: decision-frameworks/mfa-factor-selection.madr.md
- Review binding: checklist.md
- Good example: examples/authentication/mfa-factor-selection-good.md
