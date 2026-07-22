<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.log-injection log injection prevention (good patterns)

## Pattern A: Parameterized structured logger call (Python)

```python
log.info("user_action", user_id=user.id, action=request.form['action'])
```

Why this satisfies logging.log-injection: user input (request.form['action'])
is passed as a structured field value. The structured logger
serializes the value with proper JSON escaping; embedded
newlines, control characters, and quotes are escaped
automatically.

## Pattern B: Structured fields with logging library escaping (Node.js)

```javascript
log.info({
    user_id: user.id,
    user_agent: req.headers['user-agent'],
    referer: req.headers['referer']
}, 'request received');
```

Why this satisfies logging.log-injection: the request headers (user-
tainted) flow into structured fields. pino's JSON
serialization handles escaping; an attacker-controlled
referer cannot inject a newline that breaks the log record.

## Pattern C: Go zerolog typed fields

```go
log.Info().
    Str("user_id", userID).
    Str("user_input", r.FormValue("comment")).
    Msg("user submitted comment")
```

Why this satisfies logging.log-injection: user input is bound as a typed
string field. zerolog's serialization handles escaping; the
record remains a valid single-line JSON object regardless of
the input's content.

## Pattern D: Validator before logger

```python
def safe_user_input(value: str) -> str:
    """Strip control characters and normalize."""
    return ''.join(c for c in value if c.isprintable())

log.info("user_search",
    query=safe_user_input(request.args.get('q', '')),
    user_id=user.id)
```

Why this satisfies logging.log-injection: input is sanitized before
logging. While the structured logger would already handle
escaping, the defense-in-depth pattern strips control
characters at the boundary, eliminating the class entirely.

## Pattern E: Logger plugin that escapes control characters

```python
import structlog

def escape_control_characters(_, __, event_dict):
    """Replace control characters in any string field."""
    for k, v in event_dict.items():
        if isinstance(v, str):
            event_dict[k] = ''.join(
                c if c.isprintable() or c == ' ' else f'\\u{ord(c):04x}'
                for c in v
            )
    return event_dict

structlog.configure(
    processors=[
        escape_control_characters,
        structlog.processors.JSONRenderer(),
    ]
)
```

Why this satisfies logging.log-injection: a logger processor escapes
control characters in every string field before
serialization. Even if a call site passes user input
directly, the processor catches the injection class.

## Pattern F: Java slf4j parameterized placeholders

```java
log.info("user_search query={} user_id={}", userQuery, userId);
```

Why this satisfies logging.log-injection: slf4j's parameterized
placeholders are not string format; they are message-template
substitution that occurs after the slf4j framework's logging
filters. The structured appender (logstash encoder) treats
the substituted values as field values, not as fragments of
the message.

## Cross-reference

- Anti-patterns: examples/logging/log-injection-anti-pattern.md
- Substrate rule: logging.log-injection
- L1 binding: binding.yaml
