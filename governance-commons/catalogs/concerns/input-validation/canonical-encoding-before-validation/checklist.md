---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.canonical-encoding-before-validation-canonical-encoding-before-validation"
title: "input-validation.canonical-encoding-before-validation review checklist: canonical encoding before validation"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add input fields with text content (names, identifiers, free-text)"
  - "Code changes that compare two strings for equality (lookups, matches)"
  - "Code changes that decode URL parameters, base64 fields, or other encoded inputs"
  - "Periodic input-validation self-assessment"
---

# input-validation.canonical-encoding-before-validation review checklist: canonical encoding before validation

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.

This checklist enforces the "canonicalize before validate"
ordering: input is normalized to a single canonical form before
any validator or comparison operates on it. Without this discipline,
validators that operate on raw input can be tricked by alternative
encodings (URL-encoded, double-encoded, Unicode-normalized
differently). The chosen canonical forms (NFC vs NFKC for Unicode,
case-folding policy, whitespace handling) are documented in the
input-validation-strategy ADR per input-validation.input-validation-strategy.

## Review questions

### 1. Unicode normalization: is the canonical form documented and applied?

Confirm that the application has chosen a Unicode normalization
form (NFC or NFKC) and applies it to text fields at the input
boundary. The choice is documented in the input-validation-
strategy ADR.

What good looks like: text fields are normalized via
unicodedata.normalize("NFC", value) (Python) or the equivalent
in the application's language at the schema-validation step; the
choice between NFC and NFKC is justified in the ADR (NFC preserves
visual equivalence; NFKC additionally collapses compatibility
variants like fullwidth/halfwidth).

What needs follow-up: text fields are not normalized; identical-
looking strings with different code-point sequences compare
unequal at lookup; the ADR does not state the chosen form.

### 2. URL decoding: how many times is request data decoded?

Confirm that URL-encoded request data (path parameters, query
string, form-urlencoded bodies) is decoded exactly once at the
boundary. The framework typically does this; downstream code must
not re-decode the already-decoded values.

What good looks like: the handler operates on decoded values
(spaces are spaces, not %20); downstream code does not call
urllib.parse.unquote or decodeURIComponent on already-decoded
values; double-encoded input (%2520) appears as the once-decoded
form (%20), not as the twice-decoded form (a space).

What needs follow-up: the handler re-decodes parameters that the
framework already decoded; double-encoded probes bypass validators
that operate on the once-decoded form; the application's decoding
behavior depends on which middleware processed the request.

### 3. Case folding: are case-insensitive comparisons locale-safe?

Confirm that case-insensitive comparisons (email addresses,
usernames, lookup keys) use locale-independent case folding
rather than language-specific case conversion. The Turkish-i
problem and similar locale variations produce inconsistent
comparison results when language-specific conversion is used.

What good looks like: comparisons use casefold() in Python,
toLocaleLowerCase("en-US") or toUpperCase("und") in JavaScript, or
the language's locale-independent case-folding equivalent;
identifier columns in the database are case-folded at write time.

What needs follow-up: comparisons use str.lower() with a
language-specific locale; the same username compares as different
strings depending on the JVM locale or system locale; the database
stores both cases for the same logical identifier.

### 4. Path canonicalization: do path operations canonicalize before checking?

Confirm that path operations canonicalize the candidate path
(resolving .. and symbolic links) BEFORE the containment check
(input-validation.path-traversal-prevention pattern). The check operates on the canonical form,
not the user-supplied form.

What good looks like: the call sequence is resolve-then-check;
the check uses a separator-aware prefix comparison; symbolic
link policy is documented (resolve through symlinks vs reject
symlinks).

What needs follow-up: the check operates on the user-supplied
path and is bypassed by encoded traversal; symbolic links create
unexpected containment behavior; the policy is not documented.

### 5. Whitespace and invisible characters: are identifier fields normalized?

Confirm that identifier fields (usernames, email addresses, IDs)
have leading and trailing whitespace stripped, zero-width
characters rejected or stripped, and bidirectional override
characters rejected. These characters are visually invisible
and produce identifiers that look identical but compare unequal.

What good looks like: the schema's identifier-type validators
strip whitespace and reject invisible characters; the email-
validation library handles RFC 5322 dotted-atom canonicalization;
duplicate registration attempts with whitespace-padded usernames
are rejected as conflicts.

What needs follow-up: identifier fields preserve leading and
trailing whitespace; visually identical usernames produce
different account records; zero-width joiners create
indistinguishable identifiers.

### 6. Test coverage: are canonicalization paths tested?

Confirm that the application's test suite includes specific cases
for canonical-form bypass: URL-encoded payloads do not bypass
validators; Unicode-normalized variants of the same string compare
equal; case-insensitive lookups treat locale-variant cases as
equal; whitespace and invisible characters do not create distinct
identifiers.

What good looks like: a dedicated canonicalization test module
exercises each canonical-form behavior with positive and negative
cases; new input fields are added to the test module when
introduced.

What needs follow-up: canonicalization is not tested directly;
regressions in normalization behavior are caught only by users
or by adjacent test cases.

## Output

Each question receives GOOD, NEEDS FOLLOW-UP, or NOT APPLICABLE
per the standard checklist output convention.
