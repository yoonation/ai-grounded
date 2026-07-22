---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authentication.session-regeneration-session-fixation"
title: "authentication.session-regeneration review checklist: session fixation prevention"
substrate-rule: "authentication.session-regeneration"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.1.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-18"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-20"
entered-status-at: "2026-05-20"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes to authentication completion paths (login, MFA, OAuth callback, magic link)"
  - "Code changes to session middleware or cookie handling"
  - "Code changes to privilege elevation logic"
---

# authentication.session-regeneration review checklist: session fixation prevention

## Review questions

### 1. Session regenerate called at authentication

Does the authentication completion handler call the framework's
session-regenerate primitive (or equivalent for JWT-based systems)
after successful authentication?

What good looks like: framework session-regenerate appears
immediately after authentication validation succeeds and before
any response carrying the new authenticated state is sent.

What needs follow-up: the pre-auth session is preserved across
authentication; the same session ID maps both pre-auth and post-
auth state.

### 2. All authentication paths covered

If the application has multiple authentication paths (login,
MFA completion, OAuth callback, magic link, SSO), is session
regeneration applied to all of them?

What good looks like: every path that transitions an unauthenticated
session to authenticated calls session-regenerate; common helper
or middleware encapsulates the pattern.

What needs follow-up: only the primary login path rotates; OAuth
callback or MFA completion leaves the session ID unchanged.

### 3. Privilege boundary rotation

Are session identifiers also rotated at privilege boundary
crossings (admin role acquisition, sensitive area entry)?

What good looks like: privilege elevation triggers a session
rotation in addition to the authentication.mfa-on-privileged-operations MFA freshness check.

What needs follow-up: privilege elevation is silent at the session
layer; the user's session ID is unchanged across privilege boundary.

### 4. Cookie attributes appropriate

For cookie-based sessions: are the cookie attributes correct
(httpOnly, Secure, SameSite=Lax or Strict)?

What good looks like: cookie attributes are set on the
session-regenerate path; httpOnly prevents JavaScript access;
Secure enforces HTTPS-only transmission; SameSite mitigates
CSRF.

What needs follow-up: cookie attributes are missing or weak;
httpOnly omitted; SameSite=None without explicit reason.

### 5. JWT-equivalent rotation

For JWT-based systems: does authentication issue a new token AND
invalidate the previous one?

What good looks like: a token-revocation list or jti tracking
mechanism marks the pre-auth token as invalid when the new token
issues.

What needs follow-up: the pre-auth token (if any) is left valid
until natural expiration; replay of the pre-auth token still
authenticates.

### 6. Response ordering correct

Is the session-regenerate call placed BEFORE any response that
carries authenticated state?

What good looks like: regenerate, then issue response with new
cookie or token; the user's first authenticated request uses the
new identifier.

What needs follow-up: regenerate happens after the response is
sent; the first authenticated request still uses the pre-auth
identifier.

## Reviewer attestation

```
authentication.session-regeneration review checklist: complete
- Session regenerate at authentication: PASS / FOLLOW-UP / EXEMPT
- All authentication paths covered: PASS / FOLLOW-UP / EXEMPT
- Privilege boundary rotation: PASS / FOLLOW-UP / EXEMPT
- Cookie attributes appropriate: PASS / FOLLOW-UP / EXEMPT
- JWT-equivalent rotation: PASS / FOLLOW-UP / EXEMPT
- Response ordering correct: PASS / FOLLOW-UP / EXEMPT
```

## Cross-reference

- Substrate rule: authentication.session-regeneration in catalogs/concerns/authentication.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/authentication/session-fixation-good.md
- Anti-patterns: examples/authentication/session-fixation-anti-pattern.md
