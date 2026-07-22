<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.input-validation-strategy consumer ADR (filled-in)

A substrate-original example of a consumer ADR that adapts the
substrate's input-validation-strategy framework to a concrete
application context. The consumer's ADR satisfies input-validation.input-validation-strategy
by addressing each decision driver and naming the chosen options.

The example below is for a hypothetical "OrderingService"
application: a Python FastAPI service exposing public HTTP APIs
with both internal and partner clients.

---

# ADR-0007: Input validation strategy

- **Status:** Accepted
- **Date:** 2026-04-15
- **Deciders:** API Platform team (Alice, Bob), Security Engineering (Carol)
- **References:**
  - Substrate framework MADR: governance-commons/decision-frameworks/input-validation-strategy.madr.md
  - Substrate rule: input-validation.input-validation-strategy
  - Related ADRs: ADR-0003 authentication strategy, ADR-0006 authorization model

## Context and Problem Statement

OrderingService is a Python 3.12 FastAPI service exposing a
public HTTP API consumed by an internal web client and four
partner integrations. The service handles order submissions,
inventory queries, and webhook deliveries. We need a documented
input-validation strategy before the public API expansion in
Q3-2026 that adds four more partner endpoints.

## Decision Drivers

Adapted from the substrate framework's D1-D9. Application-
specific context noted where relevant.

- **D1 Placement:** All endpoints are FastAPI; framework
  supports schema-first natively via Pydantic dependency
  injection.
- **D2 Library:** Python 3.12 + FastAPI; Pydantic is already
  vendored.
- **D3 Canonical encoding:** Partner identifiers carry mixed
  Unicode (international addresses); NFC needed.
- **D4 Error shape:** Partners requested RFC 7807 alignment
  for forward compatibility with their tooling.
- **D5 Unknown-field handling:** Partner integrations are
  rate-of-change moderate; new optional fields appear roughly
  quarterly. Strict rejection would break partner forward-
  compatibility unless we coordinate releases.
- **D6 Versioning:** We have a /v1/ namespace and intend to
  introduce /v2/ at the Q3 expansion. URL versioning.
- **D7 Type-narrowing depth:** UUID, EmailAddr, Money are
  in-scope; we already have a project-internal OrderId type.
- **D8 Logging:** WARN for validation failures from partner
  endpoints (signals integration issue); INFO for client form
  submission failures.
- **D9 Performance:** Highest-traffic endpoint is /orders at
  ~2k req/s peak; Pydantic v2 (Rust core) handles this with
  margin.

## Considered Options

- **Option 1: Schema-first with Pydantic v2 (substrate-preferred)**
- **Option 2: Schema-first with JSON Schema + jsonschema library**
- **Option 3: Imperative with FastAPI helpers**
- **Option 4: Validation at the domain boundary (DDD style)**

Option 5 (minimal validation) excluded: incompatible with our
public-API posture.

## Decision Outcome

**Chosen: Option 1 (schema-first with Pydantic v2).**

Pydantic v2 is the substrate-preferred library for Python; it
integrates natively with FastAPI; the team is fluent in it; the
Rust core handles our throughput requirement comfortably.

For the other dimensions:

- **D3 Canonical encoding:** NFC at the schema layer via
  `before` validators on text fields; locale-independent
  case folding for identifier fields.
- **D4 Error shape:** RFC 7807 Problem Details (application/
  problem+json content type) for HTTP errors.
- **D5 Unknown-field handling:** Lenient (strip) for partner
  endpoints (forward-compatibility); strict (reject) for
  internal endpoints. The mix is documented and applied via
  endpoint-class base models (PartnerRequest base allows extra,
  InternalRequest base forbids extra).
- **D6 Versioning:** URL versioning (/v1/, /v2/); breaking
  changes only across major versions; six-month deprecation
  window on /v1/ after /v2/ ships.
- **D7 Type-narrowing depth:** UUID, EmailStr, HttpUrl, date,
  Decimal-Money type, and project-internal OrgCode and
  OrderId types. All present in schema; no primitive strings
  for these.

**Substrate Alignment:** Aligned with substrate preferences
except D5 (we chose lenient for partner endpoints; substrate
prefers strict). Justification: partner forward-compatibility
requires accepting unknown fields without coordinated releases.

## Consequences

Positive:
- Single validation library; team fluency; type system aligned
- Generated OpenAPI documentation matches enforced schemas
- RFC 7807 error format aligns with partner tooling
- the input-validation mechanical (L1) rules mechanical detection
  applies directly

Negative:
- Partner endpoints accept unknown fields silently (lenient);
  malicious payload smuggling possible until field-level
  scrutiny catches it. Compensation: partner endpoints have
  bounded total payload size (10 KB) and bounded field counts.
- Pydantic v2 migration cost (~3 weeks) for the existing v1
  call sites.

Follow-up:
- Migrate remaining endpoints from v1 to v2 by 2026-06-30
- Add Pydantic-driven OpenAPI generation to the CI pipeline
- Add INPUT-L1 Semgrep rules to pre-commit hooks
- Quarterly review of the partner endpoint lenient policy

## Pros and Cons of Each Option

(omitted for brevity; the substrate framework's analysis applies)

## Decision Review Schedule

Next review: 2027-04-15. Earlier review triggered by: addition
of a new client class beyond internal/partner; regulatory
change requiring stricter validation; security incident
affecting validation.
