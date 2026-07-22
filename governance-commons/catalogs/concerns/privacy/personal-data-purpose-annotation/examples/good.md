<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.personal-data-purpose-annotation personal-data purpose and basis annotation (good pattern)

Substrate-original illustration.

```python
# Each personal field declares its processing purpose and lawful basis,
# on top of the data-classification.model-classification-label sensitivity label.
class CustomerContact(Base):
    # classification: confidential (data-classification.model-classification-label label)
    email = PersonalField(
        purpose="transactional-notifications",
        lawful_basis="contract",
    )
    marketing_opt_in = PersonalField(
        purpose="marketing",
        lawful_basis="consent",
    )
```

## Why this satisfies the rule

Every personal field names a processing purpose and a lawful basis alongside the
classification label, so the field's lawful use is declared rather than assumed.
The static check (privacy.personal-data-purpose-annotation) can see the annotation is present; whether the
basis is valid for that purpose is the privacy.lawful-basis-and-consent review.
