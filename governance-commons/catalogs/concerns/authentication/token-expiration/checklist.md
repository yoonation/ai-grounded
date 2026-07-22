---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: authentication.token-expiration
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  A JWT issued without an expiry is sast-detectable, but confirming that every
  token type the application issues (session, OAuth access and refresh, reset,
  verification) carries an explicit expiry set at issuance requires reviewing the
  issuance paths, which a static tool cannot fully resolve.
review-triggers:
  - A new token type is issued by the application
  - Changes to token issuance, signing, or session creation code
  - Changes to token lifetime configuration
---

# Review checklist: issued tokens carry an explicit expiry

## Review questions

- Does every token the application issues (session, JWT, OAuth access and refresh,
  password reset, email verification) carry an explicit expiration set at
  issuance?
- Are the lifetimes bounded and appropriate to the token's purpose (short for
  access and reset, longer but finite for refresh)?
- Is the expiry enforced on validation, not only set at issuance?
- For stateless tokens, is the expiry part of the signed payload so it cannot be
  altered by the holder?

## Mechanical assist

The sast gate can flag a JWT created without an exp claim. Treat a clean run as
necessary, not sufficient; the cross-token-type coverage is review work.
