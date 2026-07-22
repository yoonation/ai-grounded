<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.duplication-and-abstraction duplication and abstraction (good pattern)

Substrate-original illustration. Three genuine copies of one validation
rule are consolidated into a single named function on the third
occurrence, because they encode the same piece of knowledge.

## Python: true duplication consolidated on the rule of three

```python
# Before: the same e.164 phone check appears in three places, all of
# which would have to change together if the rule changed.

# After: one authoritative representation.
# validation/phone.py
import re

_E164 = re.compile(r"^\+[1-9]\d{1,14}$")

def is_valid_phone(value: str) -> bool:
    """The single source of truth for phone validity (E.164)."""
    return bool(_E164.match(value))


# callers now share the one rule
from validation.phone import is_valid_phone

def register_user(form):
    if not is_valid_phone(form.phone):
        raise InvalidInput("phone")

def update_contact(form):
    if not is_valid_phone(form.phone):
        raise InvalidInput("phone")
```

Why this passes: the three copies encoded one decision (what a valid
phone number is), confirmed by the third occurrence, so consolidating
into is_valid_phone means a future change to the rule is a single edit.
This is DRY applied to knowledge, not to incidental text.
