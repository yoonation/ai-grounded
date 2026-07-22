<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.data-classification-policy data-classification policy (anti-pattern)

Substrate-original illustration.

```text
There is no data-classification policy ADR. Classification grew per feature:

- Team A labels customer records "PII" and encrypts them.
- Team B labels the same kind of data "sensitive" and does not encrypt the
  reporting replica.
- The infrastructure tags use "confidential" for the same data, so the code
  labels and the data-sensitivity tags do not match.
- No one recorded which classes may be cached or exported, so a nightly job
  ships restricted records to an analytics bucket with public-read.
```

## Why this violates the rule

With no recorded policy, the decisions do not cohere: three vocabularies name
the same data (PII, sensitive, confidential), the same class is encrypted in
one store and not another, the code labels and infrastructure tags disagree,
and an export sends restricted data to a destination that cannot protect it
because no propagation rule was written. A policy ADR covering the six
sub-decisions, with one vocabulary bound to both the labels and the tags,
makes these interactions visible and owned before they become an exposure.
