<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.test-pyramid-composition undocumented or inverted pyramid

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: no documented shape, mixed organization

```
tests/
├── test_orders_basic.py      # actually a unit test
├── test_orders_with_db.py    # actually integration
├── test_user_e2e.py          # actually e2e
├── test_pricing.py           # mix of unit and integration
├── test_checkout.py          # all e2e despite the name
└── ...                       # no tier-classification convention
```

Tests are distinguished only by filename, and filenames do not
follow a convention. The CI runner executes all tests in one
pass; per-tier counts are not observable; ratios cannot be
computed; the ADR (if it exists) cannot be verified against the
running suite.

## Anti-pattern B: ice cream cone shape unmonitored

The team has historically added tests at whatever tier was
convenient. Six months in, the per-tier counts are:

```
unit:        42 tests
integration: 78 tests
e2e:        301 tests
```

The PR feedback loop takes 25 minutes. Flake rate is 8%. Each
red CI run triggers retry-until-green culture. The team's
"productivity hack" of writing e2e tests instead of unit tests
felt fast at the time and is now technical debt.

The substrate-rejected pattern (inverted pyramid) compounds: as
the e2e tier grows, each new test adds to the slow, flaky tier;
the unit tier shrinks proportionally; the cost-to-confidence
ratio inverts.

## Anti-pattern C: ADR declared but suite ignores it

The testing-strategy.testing-strategy ADR declares 70/20/10 unit/integration/e2e. The
actual suite has 50/30/20. No CI gate exists to detect drift.
The ADR exists as a paper artifact disconnected from the running
code.

The substrate's L2 review checklist question 8 (drift detection)
catches this state: the ADR is documented but there is no
ratchet to prevent the pyramid from inverting silently.

## Anti-pattern D: tier names without tier semantics

```python
# tests/unit/test_orders.py
def test_order_processing():
    db = create_real_postgres_connection()  # this is integration!
    order_service = OrderService(db)
    db.execute("INSERT INTO users ...")
    result = order_service.process(order_data)
    assert result.status == "ok"
```

The file is in `tests/unit/` but the test spins up a real
PostgreSQL connection. The substrate's L2 review catches this as
"tier-appropriate coverage" failure: unit tests should not
exercise real I/O. Misclassified tests pollute the unit-tier
counts and produce misleading per-tier observability.

## Anti-pattern E: ratios computed but never enforced

The CI emits per-tier counts in the build log. No one looks at
them. There is no automated alert when ratios drift; there is
no PR gate when a contributor adds 20 e2e tests with no unit
counterpart.

```yaml
# .github/workflows/test.yml
- name: print test counts
  run: |
    echo "Unit: $(find tests/unit -name '*.py' | wc -l)"
    echo "Integration: $(find tests/integration -name '*.py' | wc -l)"
    echo "E2E: $(find tests/e2e -name '*.py' | wc -l)"
    # no further action; ratios printed but not checked
```

Observability without enforcement is not protection. The
substrate-acceptable form (Pattern B in the companion good
example) acts on the counts.

## Anti-pattern F: per-tier budgets exceeded without consequence

The ADR declares 5-minute integration budget. The actual
integration suite has grown to 17 minutes. The team accepts the
slow CI because "the tests are valuable." Six months later, the
PR feedback loop is too slow to support trunk-based development;
the team adopts feature branches; the long-lived branches
accumulate merge conflicts.

The substrate-aligned response: when the budget is consistently
exceeded, either optimize the slow tier, reclassify slow tests
into a tier with a larger budget, or revise the ADR budget with
documented rationale.

## Anti-pattern G: trophy declared for backend service

The team adopts the testing trophy shape because they read about
it in a blog post. The application is a backend REST API with
no UI rendering layer. The trophy emphasizes component /
integration tests, which for a backend means slow integration
tests dominate the suite. The team gets the worst of both
shapes: slow PR feedback like the trophy, but no UI-component
benefit because there is no UI.

The substrate-acceptable shape is informed by application
architecture (D1 driver in the framework MADR). Choosing a shape
that does not match the architecture is the substrate-rejected
case the L2 review and L3 ADR review surface.

## Why these forms accumulate

Test pyramid drift is structural: every individual test addition
is reasonable; no single PR introduces the inverted shape;
across hundreds of PRs over a year, the suite drifts. Without a
ratchet, the drift is invisible until the feedback loop becomes
intolerably slow.
