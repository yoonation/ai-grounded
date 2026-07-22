<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.classification-correctness classification correctness (anti-pattern)

Substrate-original illustration.

```python
# An aggregate labeled internal that re-exposes restricted source fields.
def build_account_report(profile, transactions):
    # transactions are restricted (financial)
    report = AccountReport(rows=summarize(profile, transactions))
    report.data_classification = "internal"   # under-classified
    return report
```

## Why this violates the rule

The report is built from restricted financial transactions but is labeled
internal, so it is handled far below the level its contents require: it may be
cached in a shared tier, accessed by a broad role, and logged, all of which
the restricted source data forbids. The derived artifact must inherit the
most restrictive class of its inputs; labeling it internal silently
under-protects the data it re-exposes.
