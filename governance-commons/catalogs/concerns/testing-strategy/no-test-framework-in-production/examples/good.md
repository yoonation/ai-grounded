<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.no-test-framework-in-production clean test/production separation

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python with src/tests layout

```
my_project/
├── pyproject.toml
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── orders.py           # no pytest import
│       └── clock.py            # production Clock interface
└── tests/
    ├── conftest.py
    ├── test_orders.py          # imports pytest, my_project.orders
    └── fakes/
        └── fake_clock.py       # test-only fake implementation
```

```python
# src/my_project/clock.py - production interface
from typing import Protocol
from datetime import datetime

class Clock(Protocol):
    def now(self) -> datetime: ...

class SystemClock:
    def now(self) -> datetime:
        return datetime.utcnow()
```

```python
# tests/fakes/fake_clock.py - test-only implementation
from datetime import datetime, timedelta
from my_project.clock import Clock

class FakeClock:
    def __init__(self, initial: datetime):
        self._now = initial
    def now(self) -> datetime:
        return self._now
    def advance(self, delta: timedelta):
        self._now += delta
```

```toml
# pyproject.toml
[project.optional-dependencies]
test = ["pytest>=8.0", "freezegun>=1.5"]

[project]
dependencies = []   # production dependencies only
```

Production code imports the `Clock` protocol; tests inject a
`FakeClock`. The test framework lives in optional-dependencies;
production builds exclude it.

## Pattern B: JavaScript with src/__tests__ layout

```
my-app/
├── package.json
├── src/
│   ├── orders.ts                # no jest import
│   ├── clock.ts                 # production Clock
│   └── __tests__/               # co-located tests
│       └── orders.test.ts       # imports jest, ../orders
└── ...
```

```typescript
// src/clock.ts - production
export interface Clock {
  now(): Date;
}

export const systemClock: Clock = {
  now: () => new Date(),
};
```

```json
// package.json
{
  "dependencies": {},
  "devDependencies": {
    "jest": "^29.7.0",
    "@types/jest": "^29.5.0"
  }
}
```

Webpack / Vite / esbuild excludes `__tests__/` directories from
the production bundle via the build configuration. Jest lives
in `devDependencies`.

## Pattern C: Java with src/main and src/test

```
my-service/
├── pom.xml
├── src/
│   ├── main/
│   │   └── java/com/example/
│   │       ├── OrderService.java    # no junit import
│   │       └── Clock.java           # production interface
│   └── test/
│       └── java/com/example/
│           ├── OrderServiceTest.java  # imports junit, mockito
│           └── FakeClock.java         # test-only fake
└── ...
```

```xml
<!-- pom.xml -->
<dependencies>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>          <!-- test scope only -->
  </dependency>
  <dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.7.0</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

Maven's test scope ensures JUnit and Mockito do not ship to the
production JAR. The directory layout (src/main/java vs
src/test/java) enforces the separation mechanically.

## Pattern D: Go with _test.go convention

```
my-tool/
├── go.mod
├── orders.go                    # production
├── orders_test.go               # tests; uses "testing" package
├── clock.go                     # production Clock interface
└── clock_test.go                # imports testify
```

```go
// clock.go - production
package main

import "time"

type Clock interface {
    Now() time.Time
}

type systemClock struct{}

func (systemClock) Now() time.Time { return time.Now() }
```

```go
// clock_test.go - test only
package main

import (
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
)

type fakeClock struct {
    now time.Time
}

func (f *fakeClock) Now() time.Time { return f.now }
```

The Go compiler automatically excludes `_test.go` files from
production builds; the `testing` import in production code (a
non-`_test.go` file) is forbidden by the testing-strategy.no-test-framework-in-production binding.

## Why this matters

Production code that depends on test framework imports either
ships those dependencies to production (bloating the artifact,
increasing supply-chain surface, occasionally exposing debug
surfaces) or fails to import them at runtime (crashing the
production deployment). The clean separation makes the
dependency direction one-way: tests depend on production code;
production code does not depend on tests.
