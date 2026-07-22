<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.no-placeholder-documentation no placeholder documentation (anti-patterns)

Substrate-original anti-pattern examples for documentation.no-placeholder-documentation. A placeholder ships
as though the content were finished.

## A reference page that is a stub

```markdown
## Authentication

TODO: write this section.
```

## A doc comment with a fill-in placeholder

```python
def settle_invoice(invoice_id: str, amount_cents: int) -> SettlementResult:
    """TBD: describe what this does."""
    ...
```

The page and the doc comment present as documentation and contain none. A
reader spends time on an empty section and loses trust. Replace with real
content, or record the gap with a visible known-gap notice.
