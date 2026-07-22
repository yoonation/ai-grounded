---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.authentication.session-regeneration-session-fixation"
title: "authentication.session-regeneration test template: session fixation prevention"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# authentication.session-regeneration test template: session fixation prevention

## Scenario 1: Session ID changes on login completion

**Preconditions**
- Fresh browser session (no existing cookies)

**Action**
- Make an unauthenticated request to the application; capture
  the session cookie value (call it SID1)
- Submit a successful login with that same session cookie
- Capture the post-login session cookie (call it SID2)

**Expected**
- SID1 differs from SID2
- A subsequent request presenting SID1 is unauthenticated
- A subsequent request presenting SID2 is authenticated as the
  logged-in user

## Scenario 2: Pre-auth session ID is invalidated after login

**Preconditions**
- Capture pre-auth session ID SID1

**Action**
- Complete login (issuing SID2)
- Make a request presenting SID1

**Expected**
- The SID1 request is unauthenticated
- If the application uses session storage, SID1 is not present
  in the storage (or is marked invalidated)

## Scenario 3: Session ID changes on MFA completion

**Preconditions**
- User logged in with primary credentials (SID2)
- MFA challenge pending

**Action**
- Complete MFA challenge
- Capture session ID after MFA completion (call it SID3)

**Expected**
- SID3 differs from SID2
- Request presenting SID2 is no longer considered fully
  authenticated (or fails per the application's policy)

## Scenario 4: Session ID changes on OAuth callback

**Preconditions**
- User in OAuth authorization code flow with the application

**Action**
- Capture session ID before OAuth callback (SID1)
- Complete OAuth callback; capture post-callback session ID
  (SID2)

**Expected**
- SID1 differs from SID2

## Scenario 5: Cookie attributes correct on rotated session

**Preconditions**
- Application uses cookie-based sessions

**Action**
- Trigger a session rotation event (login or other)
- Inspect the Set-Cookie header on the response

**Expected**
- The cookie carries httpOnly attribute
- The cookie carries Secure attribute
- The cookie carries SameSite=Lax or SameSite=Strict
- The cookie value differs from the pre-rotation value

## Scenario 6: Session rotation on privilege boundary (if applicable)

**Preconditions**
- Application has privilege boundaries (admin role acquisition,
  sensitive area entry)

**Action**
- User logged in at standard privilege; capture SID2
- User elevates to admin privilege (via admin login,
  sudo-style flow, or other elevation)
- Capture post-elevation session ID (SID3)

**Expected**
- SID3 differs from SID2

Skip this scenario if the application has no privilege boundaries.

## Scenario 7: JWT-equivalent token rotation

**Preconditions**
- Application uses JWT-based authentication

**Action**
- Capture pre-auth token (if any) or initial-state token (JWT1)
- Complete authentication; capture new token (JWT2)

**Expected**
- JWT1 (if present) differs from JWT2
- A request presenting JWT1 is rejected (token revoked, jti
  list updated, or other invalidation mechanism)

## Cross-reference

- Substrate rule: authentication.session-regeneration in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Good examples: examples/authentication/session-fixation-good.md
- Anti-patterns: examples/authentication/session-fixation-anti-pattern.md
