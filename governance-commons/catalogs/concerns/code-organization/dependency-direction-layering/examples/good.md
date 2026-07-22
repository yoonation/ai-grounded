<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.dependency-direction-layering dependency direction (good pattern)

Substrate-original illustration. The domain core defines a repository
interface; the persistence adapter implements it. The dependency is
inverted, so the core depends on nothing volatile and can be tested
without a database.

## Python: domain owns the port, infrastructure implements it

```python
# domain/orders.py  (stable; imports nothing from infrastructure)
from typing import Protocol

class OrderRepository(Protocol):
    def get(self, order_id: str) -> "Order": ...
    def save(self, order: "Order") -> None: ...

class Order:
    def confirm(self) -> None:
        if not self.lines:
            raise EmptyOrder(self.id)
        self.status = "confirmed"


# infrastructure/sql_orders.py  (volatile; depends on the domain)
from domain.orders import OrderRepository, Order

class SqlOrderRepository(OrderRepository):
    def __init__(self, session):
        self._session = session
    def get(self, order_id): ...
    def save(self, order): ...
```

Dependency direction: infrastructure -> domain. The arrow points inward
toward the stable core. The domain's confirm() logic is unit-testable
with an in-memory fake of OrderRepository, no SQL needed. An import-linter
layers contract (domain may not import infrastructure) holds this in CI.
