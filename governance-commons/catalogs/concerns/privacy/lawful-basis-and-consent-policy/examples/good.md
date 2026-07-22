<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.lawful-basis-and-consent-policy lawful-basis and consent policy ADR (good pattern)

Substrate-original illustration.

```markdown
# ADR: Privacy lawful-basis and consent policy

## Lawful basis per purpose
- transactional-notifications: contract
- marketing: consent (specific, unbundled, withdrawable)
- fraud-prevention: legitimate interest (balancing assessment recorded)

## Consent model
Requested per purpose, recorded with timestamp, checked before processing,
withdrawal as easy as grant.

## Records of processing
Maintained per purpose: categories, recipients, retention, transfers. Reviewed quarterly.

## DPIA trigger
Required for high-risk processing, large-scale special-category data, or systematic monitoring.

## Special-category data
Processed only under an explicit-consent or other narrow permitted basis.

## Owner and review
Owner: privacy lead. Reviewed quarterly and on any new processing activity.
```

## Why this satisfies the rule

The policy is explicit and recorded as an ADR: a basis per purpose with the
legitimate-interest assessment shown, a valid consent model, the records of
processing, a concrete DPIA trigger, and special-category handling, with an owner
and a review cadence. The L2 rules (privacy.lawful-basis-and-consent, privacy.purpose-limitation-and-minimization) have a standard to
apply rather than improvising per feature.
