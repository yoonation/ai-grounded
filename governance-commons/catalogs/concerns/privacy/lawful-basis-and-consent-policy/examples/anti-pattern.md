<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.lawful-basis-and-consent-policy lawful-basis and consent policy ADR (anti-pattern)

Substrate-original illustration.

```markdown
# (no privacy policy ADR exists)

Lawful basis is decided ad hoc per feature. Consent is a single "agree to terms"
checkbox. No records of processing. DPIA is done only if someone remembers.
```

## Why this violates the rule

There is no recorded policy: the basis is decided per feature with no coherence,
consent is a single bundled checkbox, no records of processing are kept, and the
DPIA trigger is a matter of whether someone remembers. The L2 rules have nothing
consistent to conform to, so locally reasonable choices fail to cohere. Recording
the basis per purpose, the consent model, the records of processing, and the DPIA
trigger in an ADR is the fix.
