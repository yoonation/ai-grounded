<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.accuracy-and-sync accuracy and sync (good pattern)

Substrate-original good-pattern example for documentation.accuracy-and-sync. The documentation
update travels with the behavior change, and the example is executed so
drift fails a check.

## A doc-tested example that stays in sync (illustrative)

```python
def to_cents(amount: str) -> int:
    """Convert a decimal currency string to integer cents.

    >>> to_cents("1.50")
    150
    >>> to_cents("0.01")
    1
    """
    ...
```

The examples in the docstring run as doc-tests in CI. If the behavior of
`to_cents` changes, the doc-test fails, so the documentation cannot silently
fall out of sync: the change either updates the example or breaks the build.
The same change that altered behavior updates the prose that describes it.
