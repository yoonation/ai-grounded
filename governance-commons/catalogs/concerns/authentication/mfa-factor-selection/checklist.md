---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.mfa-factor-selection-mfa-factor-selection"
title: "authentication.mfa-factor-selection review checklist: MFA factor selection"
substrate-rule: "authentication.mfa-factor-selection"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.1.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-19"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New application before MFA-related code is implemented (pre-build gate)"
  - "Existing application adding or changing MFA factor types"
  - "Periodic review of the existing MFA factor ADR (annually)"
reviews-what: "the consumer's filled-in MFA factor selection ADR"
reviews-where: "typically /docs/decisions/ADR-XXX-mfa-factor-selection.md"
---

# authentication.mfa-factor-selection review checklist: MFA factor selection

## How to use this binding

L3 review reviews a DOCUMENT (the consumer's filled-in MADR),
not code. Same pattern as authentication.authentication-strategy's review checklist. The
questions below verify that the MADR satisfies the substrate's
quality requirements specific to MFA factor selection.

The MADR is a pre-build gate per authentication.mfa-factor-selection. Reviewers must
complete this checklist before MFA-related implementation
proceeds.

## Review questions

### 1. MADR exists and is in the standard location

Is there a MADR document for MFA factor selection in the
application's decision-records location?

What good looks like: a document at `/docs/decisions/ADR-XXX-
mfa-factor-selection.md` (or the consumer's adapted location);
linked from the application's architectural documentation.

What needs follow-up: no MADR exists; the MADR for authentication.authentication-strategy
(strategy) was authored but no separate MFA factor MADR exists
even though the strategy choice requires one.

### 2. authentication.mfa-factor-selection applicability is confirmed

Does the MADR confirm that authentication.mfa-factor-selection applies to this
application given the authentication.authentication-strategy strategy decision?

What good looks like: the MADR's Context section references the
authentication.authentication-strategy decision and confirms that the chosen strategy
requires a separate MFA factor (i.e., the strategy was not
pure passkey-primary).

What needs follow-up: the MADR was authored unnecessarily
(strategy was passkey-primary, no MFA factor selection needed);
or the MADR was NOT authored but the strategy requires one.

### 3. Target AAL is stated

Does the MADR explicitly state the target authenticator
assurance level (AAL1, AAL2, AAL3) and the basis for the
target?

What good looks like: target AAL is named explicitly; basis
references regulatory requirements (PCI DSS, HIPAA, FedRAMP,
industry framework) or threat-model analysis.

What needs follow-up: target AAL is not stated; "we want strong
auth" without specifying AAL; AAL stated but no basis given.

### 4. User device profile assessed

Does the MADR address the user population's device capability?

What good looks like: explicit statement of what platform
authenticators are available to the user population (iOS
TouchID/FaceID, Android Biometric Prompt, Windows Hello, etc.);
explicit consideration of users without such devices.

What needs follow-up: device profile not assessed; assumption
that all users have modern devices without verification;
inaccessibility-by-design without acknowledgment.

### 5. Phishing threat model addressed

Does the MADR address whether phishing is in the application's
threat model and how the chosen factor addresses it?

What good looks like: phishing is explicitly in or out of scope
with reasoning; if in scope, the chosen factor is phishing-
resistant (WebAuthn, passkeys) or the trade-off is documented.

What needs follow-up: phishing not discussed; phishing
acknowledged but the chosen factor is phishable (TOTP, SMS)
without justification.

### 6. Substrate-preferred factors considered

Does the MADR's Considered Options section include the
substrate-preferred factors that are plausibly applicable
(WebAuthn/passkeys; push-with-number-matching)?

What good looks like: at least Options 1 (WebAuthn) and 2
(push) are addressed even if rejected; rejection reasoning is
explicit.

What needs follow-up: substrate-preferred options not even
mentioned; rejection without analysis ("we don't support
WebAuthn" with no reasoning).

### 7. SMS-as-primary requires explicit justification

If SMS is included as a primary or only factor: is the
justification explicit, and does it reference the application's
required AAL?

What good looks like: SMS is included only when AAL1 is the
target and the threat model documents that SIM-swap and SS7
are out of scope; OR SMS is included only as accessibility
fallback alongside stronger primary factors.

What needs follow-up: SMS is the only factor without analysis;
SMS is included for AAL2+ applications (which NIST SP 800-63B-4
does not permit as of 2024); SMS-as-primary is treated as
default without consideration of alternatives.

### 8. Substrate alignment is explicit

Does the MADR explicitly state whether the choice aligns with
substrate-preferred factors?

What good looks like: a dedicated "Substrate alignment"
subsection states alignment (Aligned | Deviation: justified);
deviations are explicit and reasoned.

What needs follow-up: alignment not addressed; deviation
without reasoning.

### 9. Backup codes covered

Does the MADR reference authentication.mfa-enrollment backup code requirements
as part of the factor design?

What good looks like: explicit acknowledgment that backup codes
per authentication.mfa-enrollment are required as the break-glass recovery
mechanism regardless of primary factor choice.

What needs follow-up: backup codes not mentioned; backup codes
treated as primary factor rather than recovery mechanism;
backup code requirements deferred indefinitely.

### 10. Multiple-factor mix is enumerated

If the application offers users a choice of factors, does the
MADR enumerate all supported factors and address each?

What good looks like: every supported factor has its own
analysis in the MADR; the mix is justified (typically:
strongest factor as default, weaker as accessibility
fallback).

What needs follow-up: the application supports multiple
factors but the MADR addresses only one; the rationale for the
mix is not given.

### 11. Decision review schedule includes factor-evolution triggers

Are review triggers defined that account for the rapidly
evolving authenticator landscape?

What good looks like: review triggers include NIST guidance
change affecting permitted factors (e.g., the 2024 SMS
deprecation for AAL2+ should have triggered review of
SMS-using applications); user-population device adoption
shifts; vendor changes for chosen factor.

What needs follow-up: review schedule is generic; no triggers
specific to authenticator evolution.

## Reviewer attestation

```
authentication.mfa-factor-selection review checklist: complete
- MADR exists and in standard location: PASS / FOLLOW-UP / N/A
- authentication.mfa-factor-selection applicability confirmed: PASS / FOLLOW-UP / N/A
- Target AAL stated: PASS / FOLLOW-UP / EXEMPT
- User device profile assessed: PASS / FOLLOW-UP / EXEMPT
- Phishing threat model addressed: PASS / FOLLOW-UP / EXEMPT
- Substrate-preferred factors considered: PASS / FOLLOW-UP / EXEMPT
- SMS-as-primary justification (if applicable): PASS / FOLLOW-UP / N/A
- Substrate alignment explicit: PASS / FOLLOW-UP / EXEMPT
- Backup codes covered: PASS / FOLLOW-UP / EXEMPT
- Multiple-factor mix enumerated (if applicable): PASS / FOLLOW-UP / N/A
- Review schedule with factor-evolution triggers: PASS / FOLLOW-UP / EXEMPT
```

When all applicable questions pass, the MADR is accepted and the
pre-build gate is cleared. MFA-related implementation proceeds.

## Cross-reference

- Substrate rule: authentication.mfa-factor-selection in catalogs/concerns/authentication.oscal.yaml
- Decision framework MADR: decision-frameworks/mfa-factor-selection.madr.md
- Related framework: decision-frameworks/auth-strategy.madr.md (predecessor decision)
- Good example: examples/authentication/mfa-factor-selection-good.md
- Anti-pattern: examples/authentication/mfa-factor-selection-anti-pattern.md
