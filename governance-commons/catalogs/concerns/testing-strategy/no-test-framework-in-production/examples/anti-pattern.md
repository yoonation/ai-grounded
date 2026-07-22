<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.no-test-framework-in-production test framework imports in production paths

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: pytest imported from production module

```python
# src/my_project/validation.py
import pytest  # imported in production code

def validate_age(value):
    try:
        age = int(value)
    except ValueError:
        pytest.fail(f"invalid age: {value}")  # using test API in production
    if age < 0:
        pytest.fail("age must be non-negative")
    return age
```

`pytest.fail` is a test-framework API. Calling it from production
code means the production deployment must import pytest at
runtime; if pytest is not installed, the import fails. If
pytest is installed in production, the test framework is in the
production bundle, bloating the artifact.

## Anti-pattern B: Mockito imported from production Java

```java
// src/main/java/com/example/PaymentService.java
package com.example;

import org.mockito.Mockito;  // test framework in production

public class PaymentService {
    private final PaymentGateway gateway;

    public PaymentService() {
        this.gateway = Mockito.mock(PaymentGateway.class);  // mock in prod!
    }

    public Receipt charge(Amount amount) {
        return gateway.process(amount);
    }
}
```

The production `PaymentService` constructs a Mockito mock. The
production deployment now runs against a mock gateway that
returns null for every call. This is a real bug pattern: a
copy-paste from a test fixture into production code accidentally
ships the mock to production.

## Anti-pattern C: Jest devDependency referenced from production

```javascript
// src/orders.ts
import { jest } from "@jest/globals";  // jest in production import

export function processOrder(order) {
  const clock = jest.fn().mockReturnValue(new Date());  // test stub in prod
  return new OrderProcessor(clock).process(order);
}
```

```json
// package.json
{
  "dependencies": {
    "@jest/globals": "^29.7.0"   // moved from devDependencies to dependencies
  }
}
```

The `@jest/globals` package is in production `dependencies`
rather than `devDependencies`. The production bundle includes
Jest at runtime. The bundle size grows; the supply-chain surface
includes the test framework's transitive dependencies.

## Anti-pattern D: Go testing package imported from non-_test.go

```go
// orders.go (NOT orders_test.go)
package main

import (
    "testing"  // production import of testing package
    "time"
)

func setupTestUser(t *testing.T) *User {
    return &User{Name: "Test"}
}

// the function is exposed in production builds because the file is not _test.go
```

The `testing` package import in a non-`_test.go` file means the
production binary includes the testing package. The Go compiler
flags this in strict configurations, but the substrate-aligned
L1 rule catches it at the binding layer.

## Anti-pattern E: RSpec helper required from production lib

```ruby
# lib/account_helpers.rb
require 'rspec'  # test framework in production lib/
require 'rspec/mocks'

module AccountHelpers
  def self.build_test_account
    double("Account", balance: 100)  # using rspec-mocks in production
  end
end
```

The `lib/` directory ships in the Ruby gem; the gem now depends
on rspec and rspec-mocks at runtime. Consumers of the gem
inherit those dependencies.

## Anti-pattern F: dynamic import of test framework

```python
# src/my_project/config.py
import importlib

def get_test_helper():
    if env.is_test_mode():
        pytest = importlib.import_module("pytest")  # dynamic import
        return pytest.MonkeyPatch()
    return RealConfig()
```

The dynamic import bypasses static import analysis. The
production code branches on a runtime flag; if the test mode
flag is ever enabled in production (configuration drift,
environment variable leak), the production deployment crashes
on the import.

## Why these forms appear

- Copy-paste from a test fixture into production code without
  removing the test-framework dependency.
- Misunderstanding of "shared test utilities" leading to placing
  the utility in a production module.
- Build system misconfiguration (devDependency moved to
  dependency, test scope omitted, _test.go convention violated).
- Dynamic imports added as a "clever" optimization that ships
  test code conditionally.

## Substrate-aligned remediation

In each case, the remediation is the same shape: move the test-
framework-dependent code out of the production module; if the
production code needs a fake or stub for runtime configuration,
introduce a production-grade interface and inject the test
implementation only from test code.
