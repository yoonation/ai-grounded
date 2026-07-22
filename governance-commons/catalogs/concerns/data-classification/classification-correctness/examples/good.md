<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.classification-correctness classification correctness (good pattern)

Substrate-original illustration.

```python
# A derived report inherits the most restrictive class of its inputs.
def build_account_report(profile, transactions):
    # profile is confidential; transactions are restricted (financial)
    report = AccountReport(rows=summarize(profile, transactions))
    report.data_classification = most_restrictive(
        profile.data_classification,
        transactions.data_classification,
    )   # resolves to restricted
    return report
```

## Why this satisfies the rule

The derived report carries the most restrictive class among its inputs
(restricted, from the financial transactions), so the derived artifact is
protected to the level its most sensitive source requires. The
most-restrictive-wins rule prevents an aggregate from silently
under-classifying the data it re-exposes.
