---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.input-validation.canonical-encoding-before-validation-canonical-encoding-before-validation"
title: "input-validation.canonical-encoding-before-validation test template: canonical encoding before validation"
substrate-rule: "input-validation.canonical-encoding-before-validation"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# input-validation.canonical-encoding-before-validation test template: canonical encoding before validation

## How to use this binding

This binding describes test scenarios for canonical-encoding
behavior at input boundaries. These are integration tests against
the boundary's parsing-and-validation layer; they verify that
alternative encodings are normalized before validation operates
on the input.

## Scenario 1: URL-encoded payload does not bypass validators

**Preconditions**
- An endpoint accepts a parameter with a denylisted value
  (e.g., a path that includes "../")
- A direct submission of the denylisted value is rejected

**Action**
- Submit the same logical value URL-encoded (e.g., "%2e%2e%2f"
  for "../")

**Expected**
- The URL-encoded submission is rejected at the same point as
  the unencoded submission
- The boundary decodes the parameter exactly once, validates the
  decoded form, and rejects

## Scenario 2: Double-URL-encoded payload behaves predictably

**Preconditions**
- The application's framework decodes URL parameters exactly
  once at the boundary
- A double-encoded payload (e.g., "%252e%252e%252f") is
  constructed

**Action**
- Submit the double-encoded payload

**Expected**
- The boundary decodes once to "%2e%2e%2f" (NOT to "../")
- The validator sees the once-decoded form and either:
  (a) rejects it because the literal "%2e" characters appear
  (substrate-recommended), or
  (b) accepts it because the value is treated as the literal
  "%2e%2e%2f" string and the application is documented not to
  re-decode downstream

## Scenario 3: Unicode-normalized variants compare equal

**Preconditions**
- An endpoint accepts a text field used for identifier lookup
  (a username, an email address)
- Two visually identical strings exist: one in NFC form
  (precomposed characters), one in NFD form (decomposed
  characters that combine visually to the same glyphs)

**Action**
- Register or create an identifier using the NFC form
- Attempt a second registration or lookup using the NFD form

**Expected**
- The lookup with the NFD form matches the NFC form record
- A second registration attempt fails as a duplicate; the
  application normalizes both forms to the canonical form
  declared in the ADR (typically NFC)

## Scenario 4: Case-insensitive lookups are locale-independent

**Preconditions**
- An endpoint performs case-insensitive lookup on a text field
  (email address, username)
- The test environment can run with multiple locale settings
  (en_US.UTF-8, tr_TR.UTF-8)

**Action**
- Create an identifier with a character that has locale-
  dependent case conversion (Turkish-i: 'İ' uppercase to 'i'
  lowercase in en_US but to 'I' in tr_TR)
- Look up the identifier under each locale

**Expected**
- The lookup produces the same record regardless of locale
- The application uses locale-independent case folding
  (str.casefold in Python, toLocaleLowerCase("und") or similar)

## Scenario 5: Whitespace-padded identifiers do not create duplicates

**Preconditions**
- An endpoint accepts an identifier (username, email)
- A canonical identifier exists (e.g., "alice")

**Action**
- Attempt to register or look up the same logical identifier
  with leading or trailing whitespace ("  alice  ") or with
  invisible characters (zero-width joiner inserted)

**Expected**
- The whitespace-padded attempt is treated as equivalent to
  the canonical form: registration fails as duplicate; lookup
  matches the canonical record
- Invisible characters are either stripped (substrate-
  recommended for identifier fields) or rejected with a
  structured error

## Scenario 6: Path canonicalization happens before containment check

**Preconditions**
- An endpoint accepts a path component for a file operation
- The base directory is documented (e.g., /var/app/uploads)

**Action**
- Submit a path containing traversal characters in encoded form
  (e.g., "%2e%2e%2fetc%2fpasswd") and in decoded form
  ("../etc/passwd")

**Expected**
- Both forms are rejected at the containment check
- The check operates on the resolved canonical path, not on the
  user-supplied string
- A path within the base directory submitted in encoded form
  ("subdir%2Ffile.txt") is correctly resolved and accepted

## Scenario 7: Multi-decode protection

**Preconditions**
- The application has a documented decode policy (typically
  "decode once at the boundary, do not re-decode")

**Action**
- Audit downstream code for additional urllib.parse.unquote,
  decodeURIComponent, or URLDecoder.decode invocations on
  already-decoded values

**Expected**
- No downstream re-decoding occurs
- If re-decoding is required by a specific integration, the
  re-decoding is documented and tested separately
