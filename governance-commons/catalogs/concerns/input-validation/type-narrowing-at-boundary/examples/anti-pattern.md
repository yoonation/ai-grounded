<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.type-narrowing-at-boundary type narrowing at boundary (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Schema declares fields as str

```python
# FORBIDDEN: structured fields declared as primitive str.
# Handlers re-parse and re-validate at use sites.
class CreateInvoiceRequest(BaseModel):
    customer_id: str       # should be UUID
    contact_email: str     # should be EmailStr
    website: str           # should be HttpUrl
    amount: str            # should be Decimal with constraints
    due_date: str          # should be datetime.date
```

Why this violates input-validation.type-narrowing-at-boundary:
- Downstream code receives str, has no guarantee of validity
- Each consumer must re-parse and re-validate
- Type-checker cannot enforce correctness at call sites
- "Parse, don't validate" inversion: validation produces a str,
  not a domain type

## Anti-pattern B: Handler re-parses inside the body

```python
# FORBIDDEN: handler accepts str and re-parses to UUID.
# The schema's job is to produce the UUID; doing it here is
# duplicate work and the validation form differs from any
# other parser site.
def transfer_funds_BAD(req: TransferRequestStr):
    try:
        source = UUID(req.source)
    except ValueError:
        raise HTTPException(400, "invalid source UUID")
    try:
        amount = Decimal(req.amount)
    except (InvalidOperation, ValueError):
        raise HTTPException(400, "invalid amount")
    # ... handler continues with parsed values ...
```

## Anti-pattern C: Repository accepts str instead of domain type

```python
# FORBIDDEN: repository signature accepts str. The caller
# must convert; the type system does not enforce it.
class UserRepositoryBAD:
    def get(self, user_id: str) -> User | None:
        try:
            uuid_obj = UUID(user_id)
        except ValueError:
            return None
        # ... query with str(uuid_obj) ...
```

## Anti-pattern D: Lenient constructor that produces invalid instances

```python
# FORBIDDEN: constructor accepts any string and produces a
# Money instance whose validity must be checked separately.
class MoneyBAD:
    def __init__(self, value: str):
        # No validation; downstream code must check.
        self.value = value

    def is_valid(self) -> bool:
        try:
            Decimal(self.value)
            return True
        except InvalidOperation:
            return False

# Now every consumer must call money.is_valid() to be safe.
```

## Anti-pattern E: Cross-module passage strips the type

```python
# FORBIDDEN: handler has the UUID; service layer accepts str;
# repository converts back. The type degrades across module
# boundaries and is reconstructed at each layer.
def handler(req: TransferRequest):
    return service.transfer(
        source=str(req.source),
        destination=str(req.destination),
        amount=str(req.amount),
    )

class Service:
    def transfer(self, source: str, destination: str, amount: str):
        # Re-parse here...
        ...
```

## Anti-pattern F: Defensive re-validation throughout the codebase

```python
# FORBIDDEN: same validation repeated at every use site.
def display_amount_BAD(amount_str: str) -> str:
    if not re.match(r"^\d+\.\d{2}$", amount_str):
        return "invalid amount"
    return f"${amount_str}"

def calculate_tax_BAD(amount_str: str) -> str:
    if not re.match(r"^\d+\.\d{2}$", amount_str):
        raise ValueError("invalid amount")
    return str(Decimal(amount_str) * Decimal("0.08"))

# The same regex check appears in dozens of files.
```

## Why review identifies these

The input-validation.type-narrowing-at-boundary review checklist's six questions flag:
- Structured fields declared as primitive types
- Handler signatures show str where domain types are expected
- Constructors do not reject malformed input
- Cross-module passage strips the type
- Tests pass strings; handlers re-parse
- No domain type abstraction for project-specific fields
