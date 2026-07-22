<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.no-bare-except bare except

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Python bare except

```python
def parse_user_age(raw):
    try:
        return int(raw)
    except:
        return 0
```

The bare `except:` catches everything including KeyboardInterrupt
and SystemExit. The function silently returns 0 on any failure;
programming defects are masked. The substrate detection at
error-handling.no-bare-except flags the `except:` clause.

## Antipattern B: Python except Exception with swallow

```python
def load_config():
    try:
        with open('/etc/app/config.json') as f:
            return json.load(f)
    except Exception:
        return {}
```

`except Exception` is a near-bare catch. File-not-found,
permission-denied, malformed JSON, disk error, and a TypeError
in a misconfigured `json.load` all collapse to "return empty
config." The application boots with no configuration and fails
mysteriously later.

## Antipattern C: Java catch (Exception)

```java
public Order loadOrder(String id) {
    try {
        return jdbcTemplate.queryForObject(SQL, mapper, id);
    } catch (Exception e) {
        return null;
    }
}
```

Catches every checked and unchecked exception including
NullPointerException, ClassCastException, and OutOfMemoryError.
The caller has no way to distinguish "order not found" from
"database unavailable" from "programming defect" from "out of
memory."

## Antipattern D: JavaScript catch without narrowing

```javascript
async function fetchProfile(userId) {
  try {
    return await api.getProfile(userId);
  } catch (err) {
    return null;
  }
}
```

The catch swallows every error type indistinguishably. Network
errors, authorization errors, parsing errors, and bugs all
produce `null`. Downstream code has no signal of failure.

## Antipattern E: Go err discard

```go
order, _ := repo.Load(ctx, id)
return order
```

The Go-idiomatic equivalent of bare-except: the `_ = err`
assignment discards the error. The caller works with a nil
order without knowing whether it is "no rows" or "connection
failed."

## Antipattern F: Ruby bare rescue

```ruby
def load_user(id)
  User.find(id)
rescue
  nil
end
```

Bare `rescue` (no class) catches StandardError and its
subclasses. Ruby's `rescue Exception => e` is even worse: it
catches SystemExit and Interrupt, making the process
unkillable.

## Antipattern G: catch-then-empty-handler

```python
def send_notification(user, message):
    try:
        email_service.send(user.email, message)
    except SmtpException:
        pass
```

While `SmtpException` is narrow (which would otherwise satisfy
error-handling.no-bare-except), the empty handler body violates error-handling.no-exception-swallow (no
exception swallow). The pattern is the antipattern union: the
exception is suppressed silently and the operator has no
signal that the notification failed.

## Remediation

For each antipattern above, replace the catch with the
typed-catch pattern from the good-example file. When the
intent is "log and continue," restructure to catch the
specific class, log per error-handling.no-exception-swallow, and either propagate or
return a typed result that the caller can branch on.
