<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.test-pyramid-composition documented pyramid composition

Substrate-original good patterns. Adapt to your stack.

## Pattern A: ADR-declared shape with directory organization

The application's testing-strategy.testing-strategy ADR declares:

> Shape: classic pyramid. Targets: 70% unit, 20% integration,
> 10% end-to-end. Tolerance: ±20 percentage points before CI
> fail.

The test suite mirrors the declaration in directory layout:

```
tests/
├── unit/                  # in-process, no I/O, no containers
│   ├── test_orders.py
│   ├── test_pricing.py
│   └── ...                # 487 tests
├── integration/           # testcontainers, real database
│   ├── test_order_repo.py
│   ├── test_payment_gateway.py
│   └── ...                # 142 tests
└── e2e/                   # deployed environment, full stack
    ├── test_checkout_flow.py
    └── ...                # 71 tests
```

Per-tier counts: 487 / 142 / 71 = ratios 69.5% / 20.3% / 10.1%.
Within the ADR-declared tolerance.

## Pattern B: pytest markers as the per-tier signal

```python
# conftest.py
import pytest

def pytest_collection_modifyitems(config, items):
    for item in items:
        if "tests/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "tests/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "tests/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
  "unit: unit tier (in-process, no I/O)",
  "integration: integration tier (testcontainers OK)",
  "e2e: end-to-end tier (deployed environment)",
]
```

The CI gate counts tests per marker:

```yaml
# .github/workflows/test.yml
- name: count tests per tier
  run: |
    UNIT=$(pytest tests/ --collect-only -q -m unit | tail -1 | awk '{print $1}')
    INT=$(pytest tests/ --collect-only -q -m integration | tail -1 | awk '{print $1}')
    E2E=$(pytest tests/ --collect-only -q -m e2e | tail -1 | awk '{print $1}')
    python ci/check_pyramid_ratios.py --unit $UNIT --int $INT --e2e $E2E
```

`check_pyramid_ratios.py` reads the ADR targets and the
substrate-acceptable tolerance, computes the actual ratios,
and fails the build when drift exceeds tolerance.

## Pattern C: Jest projects configuration

```javascript
// jest.config.js
export default {
  projects: [
    {
      displayName: "unit",
      testMatch: ["<rootDir>/src/**/*.test.ts"],
      testEnvironment: "node",
      setupFiles: ["<rootDir>/test-setup/block-network.ts"],
    },
    {
      displayName: "integration",
      testMatch: ["<rootDir>/tests/integration/**/*.test.ts"],
      testEnvironment: "node",
      globalSetup: "<rootDir>/test-setup/start-containers.ts",
    },
    {
      displayName: "e2e",
      testMatch: ["<rootDir>/tests/e2e/**/*.test.ts"],
      testEnvironment: "node",
      maxWorkers: 1,
    },
  ],
};
```

Per-tier projects produce per-tier results in the Jest report.
The CI gate parses the per-project counts and applies the same
ratio check.

## Pattern D: per-tier execution budget documented and enforced

The ADR declares:

> Per-tier execution budgets:
> - Unit: < 60s on CI with 4 workers
> - Integration: < 5min on CI
> - E2E: < 15min on CI
>
> Budget exceedance: warn at the budget, fail at 1.5x the budget.

```python
# ci/check_tier_budgets.py
TIER_BUDGETS = {"unit": 60, "integration": 300, "e2e": 900}

def check_tier_duration(tier, actual_seconds):
    budget = TIER_BUDGETS[tier]
    if actual_seconds > budget * 1.5:
        sys.exit(f"FAIL: {tier} took {actual_seconds}s, budget {budget}s")
    if actual_seconds > budget:
        print(f"WARN: {tier} took {actual_seconds}s, budget {budget}s")
```

## Pattern E: drift report published weekly

```python
# ci/publish_drift_report.py
def publish_pyramid_metrics(counts):
    metrics_backend.gauge("test.tier.count.unit", counts["unit"])
    metrics_backend.gauge("test.tier.count.integration", counts["integration"])
    metrics_backend.gauge("test.tier.count.e2e", counts["e2e"])

    weekly_change = compute_weekly_change(counts)
    if weekly_change["e2e"] > weekly_change["unit"] * 2:
        post_to_team_channel(
            f"e2e tier growing 2x faster than unit tier this week; "
            f"unit:+{weekly_change['unit']}, e2e:+{weekly_change['e2e']}"
        )
```

The trend is visible in a dashboard the team consults; drift
events post to the team channel for early review.
