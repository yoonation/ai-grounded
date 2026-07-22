<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.canonical-encoding-before-validation canonical encoding before validation

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Pydantic v2 with NFC normalization at the schema layer

```python
import unicodedata
from pydantic import BaseModel, EmailStr, field_validator
from typing import Annotated
from pydantic import StringConstraints

def normalize_nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value).strip()

class UserRegistration(BaseModel):
    username: Annotated[str, StringConstraints(min_length=3, max_length=32)]
    email: EmailStr
    display_name: str

    @field_validator("username", "display_name", mode="before")
    @classmethod
    def normalize_text(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("must be a string")
        normalized = normalize_nfc(v)
        # Reject invisible characters in identifiers.
        for ch in normalized:
            if unicodedata.category(ch).startswith("C"):
                raise ValueError("invisible characters not permitted")
        return normalized
```

NFC normalization runs at the schema's `before` validator so
that downstream constraints (length, pattern) operate on the
canonical form. Invisible-character rejection is explicit.

## Pattern B: Locale-independent case folding (Python)

```python
def canonical_email(email: str) -> str:
    # casefold is locale-independent and stronger than .lower()
    # for some Unicode scripts.
    return unicodedata.normalize("NFC", email).strip().casefold()

# When storing or comparing identifiers:
canonical = canonical_email(user_email)
existing = db.query(User).filter_by(email_canonical=canonical).first()
```

The application stores `email_canonical` alongside the display
form. Lookups use the canonical form.

## Pattern C: Single URL decode at the boundary (Flask)

```python
# Flask decodes URL parameters once; downstream code uses the
# decoded values directly. No re-decoding occurs.
@app.route("/search")
def search():
    # query is already URL-decoded by Werkzeug.
    query = request.args.get("q", "")
    # Do NOT call urllib.parse.unquote(query) here.
    return search_service.find(query)
```

## Pattern D: Path canonicalization before containment check (already covered by input-validation.path-traversal-prevention pattern A)

```python
# Repeated from path-traversal-prevention-good.md for
# completeness: canonicalize, then check.
BASE_DIR = Path("/var/app/uploads").resolve()

def read_upload(filename: str) -> bytes:
    candidate = (BASE_DIR / filename).resolve()  # canonicalize
    if not candidate.is_relative_to(BASE_DIR):    # then check
        raise ValueError("path traversal blocked")
    return candidate.read_bytes()
```

## Pattern E: Username uniqueness with NFC and casefold (database constraint)

```sql
-- Username column stored case-folded and NFC-normalized at
-- application write time; the database constraint enforces
-- uniqueness on the canonical form.
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username_canonical VARCHAR(32) NOT NULL UNIQUE,
    username_display VARCHAR(64) NOT NULL,
    email_canonical VARCHAR(255) NOT NULL UNIQUE,
    email_display VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

```python
def create_user(username_display: str, email_display: str):
    username_canonical = unicodedata.normalize(
        "NFC", username_display
    ).strip().casefold()
    email_canonical = unicodedata.normalize(
        "NFC", email_display
    ).strip().casefold()
    # The UNIQUE constraint catches duplicate-in-canonical-form
    # registrations that differ only in unnormalized form.
    db.execute(...)
```

## Pattern F: Reject confusable characters in identifiers

```python
from confusable_homoglyphs import confusables

def reject_confusables(value: str) -> str:
    # confusable_homoglyphs detects characters that look like
    # ASCII but are non-ASCII (Cyrillic 'а' vs Latin 'a').
    detected = confusables.is_confusable(value, greedy=True)
    if detected:
        raise ValueError("confusable characters not permitted")
    return value
```

For high-trust identifier fields (usernames, organization
names), rejecting visually-confusable characters prevents
account impersonation via lookalike characters.
