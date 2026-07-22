<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.type-narrowing-at-boundary type narrowing at boundary

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Pydantic with library-provided domain types

```python
from decimal import Decimal
from uuid import UUID
from datetime import date
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Annotated

Money = Annotated[Decimal, Field(ge=0, decimal_places=2)]

class CreateInvoiceRequest(BaseModel):
    customer_id: UUID         # not str
    contact_email: EmailStr   # not str
    website: HttpUrl          # not str
    amount: Money             # Decimal with constraints
    due_date: date            # not str

def create_invoice(req: CreateInvoiceRequest):
    # req.customer_id IS a uuid.UUID; no re-parsing.
    # req.amount IS a Decimal with the constraints applied.
    # No defensive isinstance checks here.
    customer = customer_repo.get(req.customer_id)
    return InvoiceService.create(customer, req)
```

## Pattern B: Custom domain types with strict constructors

```python
import re
from typing import NewType

class OrgCode(str):
    """Organization code: 3-10 uppercase letters + digits."""
    PATTERN = re.compile(r"^[A-Z0-9]{3,10}$")

    def __new__(cls, value: str):
        if not isinstance(value, str):
            raise TypeError("OrgCode requires str")
        if not cls.PATTERN.match(value):
            raise ValueError(
                f"invalid org code: must match {cls.PATTERN.pattern}"
            )
        return super().__new__(cls, value)

# Used as a Pydantic type via __get_validators__ or BaseModel
# config; downstream handlers receive OrgCode, not str.
```

## Pattern C: Handler signature consumes domain types

```python
def transfer_funds(
    source: UUID,
    destination: UUID,
    amount: Decimal,
    actor: UserId,
) -> TransferReceipt:
    # All parameters are domain types; the caller cannot pass
    # arbitrary strings. The type checker enforces correctness
    # at call sites application-wide.
    ...
```

## Pattern D: Repository layer preserves the type

```python
class UserRepository:
    def get(self, user_id: UUID) -> User | None:
        # user_id IS a UUID; storage conversion to str happens
        # at the SQL parameter step, isolated here.
        with self.conn.cursor() as cur:
            cur.execute("SELECT ... FROM users WHERE id = %s", (str(user_id),))
            row = cur.fetchone()
            return User.from_row(row) if row else None

# Service layer:
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def lookup(self, user_id: UUID) -> User | None:
        return self.repo.get(user_id)  # UUID flows through
```

## Pattern E: Zod with TypeScript inference

```typescript
import { z } from 'zod';

const TransferRequestSchema = z.object({
  source: z.string().uuid().transform(v => v as UUID),
  destination: z.string().uuid().transform(v => v as UUID),
  amount: z.string().regex(/^\d+\.\d{2}$/).transform(v => new Decimal(v)),
}).strict();

type TransferRequest = z.infer<typeof TransferRequestSchema>;
//   ^ { source: UUID; destination: UUID; amount: Decimal }

async function transferFunds(req: TransferRequest): Promise<Receipt> {
  // req.source is UUID, not string.
  // req.amount is Decimal, not string or number.
  return await transferService.process(req);
}
```

## Pattern F: Handler unit test uses domain-type fixtures directly

```python
def test_transfer_funds():
    # Construct domain-type instances directly; the test
    # does not exercise parsing.
    source = UUID("11111111-1111-1111-1111-111111111111")
    destination = UUID("22222222-2222-2222-2222-222222222222")
    amount = Decimal("100.00")
    actor = UserId(UUID("33333333-3333-3333-3333-333333333333"))

    receipt = transfer_funds(source, destination, amount, actor)
    assert receipt.status == "completed"
```
