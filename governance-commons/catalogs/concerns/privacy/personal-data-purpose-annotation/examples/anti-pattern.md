<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.personal-data-purpose-annotation personal-data purpose and basis annotation (anti-pattern)

Substrate-original illustration.

```python
# Personal fields persisted with no purpose and no lawful basis declared.
class CustomerContact(Base):
    email = Column(String)          # personal, no purpose, no basis
    marketing_opt_in = Column(Boolean)
```

## Why this violates the rule

The personal fields are persisted with no processing purpose and no lawful basis
recorded, so the system holds personal data whose lawful use was never declared.
There is nothing for the per-purpose basis check (privacy.lawful-basis-and-consent) or the
minimization check (privacy.purpose-limitation-and-minimization) to anchor to. Adding a structured purpose and
basis annotation alongside the classification label is the fix.
