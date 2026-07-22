<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.canonical-encoding-before-validation canonical encoding before validation (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Validator operates on raw input, downstream re-decodes

```python
# FORBIDDEN: validator checks the raw value; downstream code
# URL-decodes again.
@app.route("/files/<path:filename>")
def serve_file_BAD(filename):
    # Validator checks the raw string.
    if "../" in filename:
        abort(400)
    # Downstream decoding turns "%2e%2e%2f" into "../", bypassing
    # the check above.
    decoded = urllib.parse.unquote(filename)
    return send_file(os.path.join("/var/app/uploads", decoded))
```

Why this violates input-validation.canonical-encoding-before-validation:
- The check operates on the raw form
- Downstream code decodes, producing a form the check didn't
  see
- Canonical CWE-180 (validate before canonicalize)

## Anti-pattern B: No NFC normalization on identifier fields

```python
# FORBIDDEN: usernames stored verbatim. Two users register
# with visually identical names but different Unicode forms
# (NFC vs NFD); both succeed; lookups become unpredictable.
class User(BaseModel):
    username: str  # no normalization
    email: str

def register_BAD(username: str, email: str):
    db.users.insert({"username": username, "email": email})
```

## Anti-pattern C: Locale-dependent case conversion

```python
# FORBIDDEN: str.lower() is locale-aware in some runtimes.
# Turkish-i: 'İ'.lower() in tr_TR is 'i' but in en_US is 'i̇'
# (with combining dot).
def find_user_BAD(email: str):
    return db.users.find_one({"email": email.lower()})
```

The substrate-recommended replacement is .casefold() or
locale-independent normalization with explicit locale.

## Anti-pattern D: Whitespace and zero-width preserved in identifiers

```python
# FORBIDDEN: identifier fields preserve leading/trailing
# whitespace and zero-width characters. Two registrations
# with "alice" and "alice " (trailing space) succeed as
# distinct accounts.
def register_BAD(username: str):
    if len(username) < 3:
        raise ValueError("too short")
    db.users.insert({"username": username})  # raw
```

## Anti-pattern E: URL decoding more than once

```javascript
// FORBIDDEN: re-decoding undoes any encoded characters the
// client intentionally sent as literals. Combined with a
// validator that checks the once-decoded form, this produces
// a bypass.
app.get('/files/:name', (req, res) => {
  const name = req.params.name;  // already once-decoded
  const decodedAgain = decodeURIComponent(name);  // wrong
  fs.readFile(path.join(UPLOAD_DIR, decodedAgain), ...);
});
```

## Anti-pattern F: Path containment check before realpath

```python
# FORBIDDEN: containment check runs before canonicalization.
# Symlinks and encoded traversal can produce a canonical path
# outside the base that the check missed.
def serve_file_BAD2(filename):
    base = "/var/app/uploads"
    candidate = os.path.join(base, filename)
    if not candidate.startswith(base):  # check BEFORE resolve
        abort(403)
    canonical = os.path.realpath(candidate)
    with open(canonical, "rb") as f:  # canonical may escape base
        return f.read()
```

## Anti-pattern G: Schema validates structure but not canonical form

```python
# FORBIDDEN: schema declares the field as a string with length
# bounds but does not normalize. NFC-vs-NFD duplicates pass
# the schema and produce database inconsistencies.
class UserRegistration(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    # No @field_validator applies normalization or strips
    # invisible characters.
```

## Why review identifies these

The input-validation.canonical-encoding-before-validation review checklist's six questions flag:
- No documented Unicode normalization form
- Downstream URL re-decoding
- Locale-dependent case conversion
- Whitespace and invisible characters preserved in identifiers
- Path operations validate before canonicalize
- Canonicalization paths are not tested directly
