<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.dependency-direction-layering dependency direction (anti-pattern)

Substrate-original illustration. A domain entity imports the ORM session
and an HTTP request object directly, welding the business core to the
most volatile parts of the system.

## Python: domain reaching outward into infrastructure

```python
# domain/orders.py  (supposedly the stable core)
from sqlalchemy.orm import Session      # <-- imports the ORM
from flask import request               # <-- imports the web framework

class Order:
    def confirm(self, session: Session):
        if not self.lines:
            raise EmptyOrder(self.id)
        self.status = "confirmed"
        actor = request.headers.get("X-Actor")   # web concern in domain
        session.add(AuditRow(order=self.id, actor=actor))
        session.commit()                          # persistence in domain
```

Why this is a finding: the arrow points outward (domain -> infrastructure
and domain -> web framework). confirm() cannot be tested without a live
SQLAlchemy session and a Flask request context, so the core's tests are
slow and brittle, and swapping the ORM or the web framework forces edits
to business logic. Detected by an import-linter or ArchUnit rule that the
domain layer may not depend on infrastructure or framework packages.

Remediation: invert the dependencies as in the good-pattern example.
Define a repository port and an audit port in the domain, implement them
in adapters, and pass the actor in as a plain argument rather than reading
the web request inside the domain.
