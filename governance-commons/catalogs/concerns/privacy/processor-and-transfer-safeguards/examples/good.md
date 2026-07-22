<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.processor-and-transfer-safeguards processor agreement and transfer mechanism recorded (good pattern)

Substrate-original illustration.

```yaml
# Each processor is bound by a DPA and each transfer names a mechanism.
processors:
  - name: email-delivery-vendor
    dpa: signed                 # instruction-only use, security and sub-processor terms
    sub_processors: flowed-down
    region: eu
  - name: analytics-vendor
    dpa: signed
    region: us
    cross_border_transfer:
      mechanism: standard-contractual-clauses
      supplementary_measures: assessed
```

## Why this satisfies the rule

Each processor that touches personal data is bound by a data-processing agreement
to instruction-only use with sub-processor flow-down, and the cross-border
transfer names a recognized mechanism assessed for the destination. The
contractual and jurisdictional instruments exist rather than being assumed from
where a service happens to be hosted. This rule is review-only and has no test
template because the obligation is contractual.
