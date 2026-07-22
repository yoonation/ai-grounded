---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.input-validation.type-narrowing-at-boundary-type-narrowing-at-boundary"
title: "input-validation.type-narrowing-at-boundary test template: type narrowing at boundary"
substrate-rule: "input-validation.type-narrowing-at-boundary"
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

# input-validation.type-narrowing-at-boundary test template: type narrowing at boundary

## How to use this binding

This binding describes test scenarios verifying that domain
values are parsed into domain types at input boundaries rather
than carried as primitive strings. The tests combine integration
scenarios against the boundary and static checks against the
handler signatures.

## Scenario 1: Malformed UUID rejected at boundary

**Preconditions**
- An endpoint accepts a UUID parameter (path, query, body)
- The endpoint's schema declares the field as a UUID type

**Action**
- Submit a malformed UUID ("not-a-uuid", a 35-character string,
  a string with invalid characters)

**Expected**
- HTTP 400 with a structured error identifying the UUID field
  and "invalid UUID format" or equivalent
- The handler does not execute
- No database lookup with the malformed value is attempted

## Scenario 2: Malformed email rejected at boundary

**Preconditions**
- An endpoint accepts an email parameter
- The schema declares the field as an email-validating type

**Action**
- Submit a malformed email ("not-an-email", a string missing
  the @ symbol, a string with invalid characters in the local
  or domain part)

**Expected**
- HTTP 400 with a structured error identifying the email field
- The handler does not execute
- No downstream email-sending or registration logic runs

## Scenario 3: Domain type appears in handler signature

**Preconditions**
- A handler exists for an endpoint accepting a domain-typed
  field

**Action**
- Inspect the handler's function signature (static check or
  introspection)

**Expected**
- The signature shows the domain type (uuid.UUID, EmailStr,
  Money, etc.), not str
- The IDE or type checker accepts the signature without
  complaint
- An attempt to pass a raw string at a call site produces a
  type-checker error

## Scenario 4: Handler unit test uses domain-type fixture

**Preconditions**
- A handler accepts a domain-typed argument
- A unit test exists for the handler

**Action**
- Inspect the unit test

**Expected**
- The test constructs a domain-type instance directly (e.g.,
  uuid.UUID("...")) rather than passing a string the handler
  re-parses
- The test does not duplicate parsing logic
- Parsing failures are exercised in a separate test of the
  schema's constructor

## Scenario 5: Cross-module passage preserves the type

**Preconditions**
- An endpoint handler passes a domain-typed value to a
  service-layer function, which passes it to a repository-
  layer function

**Action**
- Inspect the type signatures along the call chain

**Expected**
- The domain type is preserved at each layer's interface
- No intermediate function strips the type to str and
  reconstructs it
- The storage-layer conversion (domain type to database
  representation) is isolated in a dedicated adapter

## Scenario 6: Negative-value rejected for non-negative domain types

**Preconditions**
- An endpoint accepts a Money or non-negative quantity field
- The domain type's constructor rejects negative values

**Action**
- Submit a negative value in the field

**Expected**
- HTTP 400 at the schema layer (not at the handler-body level)
- The constructor's validation message is surfaced in the error
  response

## Scenario 7: Negative test for type-narrowing absence

**Preconditions**
- A new endpoint is being added with a UUID parameter
- The reviewer wants to verify the substrate's discipline is
  applied

**Action**
- Inspect the schema and handler

**Expected**
- The schema declares UUID type, not str
- The handler signature uses UUID, not str
- No defensive re-parsing exists in the handler body
- If any of these conditions fail, input-validation.type-narrowing-at-boundary review checklist
  produces NEEDS FOLLOW-UP
