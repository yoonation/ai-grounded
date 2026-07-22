<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.log-injection log injection

## Anti-pattern A: f-string interpolation with user input

```python
@app.route('/search')
def search():
    q = request.args.get('q', '')
    log.info(f"user searched for {q}")
    return run_search(q)
```

Why this violates logging.log-injection: q is user-controlled. An
attacker passing q="anything\n2026-05-20 09:00:00 INFO admin
deleted record 12345" produces what looks like a second log
record. Forensic analysis cannot distinguish injected entries
from real ones.

## Anti-pattern B: Template literal with user input

```javascript
app.get('/search', (req, res) => {
    const q = req.query.q;
    console.log(`user searched for ${q}`);
    runSearch(q);
});
```

Why this violates logging.log-injection: template literal interpolation
of req.query.q produces the same forged-entry vulnerability.
Embedded newlines in q split a single log line into multiple.

## Anti-pattern C: String concatenation in Java logger

```java
String userInput = request.getParameter("name");
log.info("processing input: " + userInput);
```

Why this violates logging.log-injection: string concatenation builds
the full message at the call site. If userInput contains
control characters or newlines, the log line is corrupted.
slf4j's parameterized placeholder approach is the substrate-
preferred alternative.

## Anti-pattern D: fmt.Sprintf passed to logger

```go
userInput := r.FormValue("name")
log.Println(fmt.Sprintf("user submitted: %s", userInput))
```

Why this violates logging.log-injection: fmt.Sprintf builds the message
including untrusted input; log.Println treats the result as
prose. The injection class is fully open.

## Anti-pattern E: CRLF injection through HTTP header

```python
agent = request.headers.get('User-Agent', 'unknown')
log.info(f"request from agent {agent}")
```

Why this violates logging.log-injection: a malicious User-Agent header
containing "\r\n" can split the log record. The header value
is user-controlled at the HTTP layer; this is a documented
CRLF injection vector (CWE-93).

## Anti-pattern F: Exception str with user input

```python
def validate_input(value):
    if not value.isdigit():
        raise ValueError(f"invalid input: {value}")

try:
    validate_input(request.args['n'])
except ValueError as e:
    log.error(f"validation failed: {e}")
```

Why this violates logging.log-injection: the exception message includes
user input via f-string. log.error then re-interpolates the
exception. The control characters reach the log unescaped.

## Anti-pattern G: Direct user input as logger argument with prose formatter

```python
LOGGING = {
    'formatters': {
        'simple': {'format': '%(asctime)s %(levelname)s %(message)s'}
    }
}

log.info(request.args['msg'])
```

Why this violates logging.log-injection: user input is the message
directly. The prose formatter does no escaping; control
characters reach the output. The substrate's mechanical rule
applies even here: structured logging (JSON formatter)
would have caught the issue at the field-serialization
layer.

## Cross-reference

- Good patterns: examples/logging/log-injection-good.md
- Substrate rule: logging.log-injection
- Authoritative: CWE-117 Improper Output Neutralization for Logs, CWE-93 CRLF Injection
