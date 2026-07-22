<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.duplication-and-abstraction duplication and abstraction (anti-pattern)

Substrate-original illustration. Two superficially similar handlers are
merged behind a flag-parameterized abstraction. They looked alike but
encode different decisions, so the abstraction grows a tangle of
conditionals as they diverge.

## Python: premature abstraction over coincidental similarity

```python
def process(kind, payload):
    record = load(payload.id)
    if kind == "order":
        record.total = sum(payload.lines)
        if payload.region == "EU":
            record.total *= 1.20          # VAT, order-only
    elif kind == "refund":
        record.total = -sum(payload.lines)
        if payload.approved_by is None:   # approval, refund-only
            raise NeedsApproval(payload.id)
    record.kind = kind
    if kind == "order":
        notify_customer(record)
    else:
        notify_finance(record)            # different path again
    save(record)
```

Why this is a finding: orders and refunds shared a rough shape (load,
compute, notify, save) but not a concept; the merged process() now
branches on kind at every step and will keep accreting flags as the two
diverge. The shared abstraction couples two things that change for
different reasons.

Remediation: reverse the premature abstraction (the un-DRY remediation).
Split into process_order and process_refund, each straight-line and
readable, and share only what is genuinely one concept (the load/save
persistence helpers), as judged against code-organization.module-boundary-cohesion cohesion.
