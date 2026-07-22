<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.no-stack-trace-in-response stack trace in response

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Flask debug mode in production

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
```

`debug=True` produces a detailed error page with the full
stack trace, local variables, an interactive Python debugger
console, and an interactive evaluation form. In production
this is direct remote code execution. The Semgrep registry
rule `python.flask.security.audit.debug-enabled` flags this.

## Antipattern B: Django DEBUG=True in production

```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
```

Django's DEBUG mode produces a yellow error page with stack
trace, environment variables, settings module contents, and
SQL queries that ran. Combined with ALLOWED_HOSTS = ['*'], the
configuration is exploitable from any origin.

## Antipattern C: Returning traceback in JSON response

```python
import traceback

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({
        "error": str(e),
        "trace": traceback.format_exc(),
    }), 500
```

The handler explicitly serializes the full traceback into the
response body. Every framework internal, every file path, and
every variable name visible in the trace becomes attacker
input.

## Antipattern D: Express development error handler in production

```javascript
const errorhandler = require('errorhandler');
app.use(errorhandler());
```

The `errorhandler` package's middleware produces a detailed
HTML error page with stack trace. Per the package's own
documentation it is for development only; using it in
production is a substrate violation.

## Antipattern E: Spring whitelabel error page with trace

`application.properties`:
```
server.error.include-stacktrace=always
server.error.include-message=always
server.error.include-exception=true
```

Spring Boot's whitelabel error page includes the stack trace
and exception class when these properties are set. The
Semgrep registry rule
`java.spring.security.audit.spring-actuator-trace-exposed`
flags this.

## Antipattern F: Java printStackTrace into response

```java
} catch (Exception e) {
    response.setStatus(500);
    e.printStackTrace(response.getWriter());
    return;
}
```

`printStackTrace` writes the trace into the response body
character stream. The client receives the trace; the operator
log may not even capture it (if printStackTrace writes only
to the response).

## Antipattern G: Echoing internal exception class names

```javascript
} catch (err) {
  res.status(500).json({
    error: `${err.constructor.name}: ${err.message}`,
  });
}
```

While shorter than a full stack trace, the constructor name
leaks the application's exception class hierarchy. Combined
with err.message, the response may leak internal paths,
SQL fragments, or library-specific error patterns.

## Antipattern H: Rails consider_all_requests_local

```ruby
# config/environments/production.rb
config.consider_all_requests_local = true
```

This setting causes Rails to treat every request as if it
came from a local developer, producing the full error page
with backtrace, environment, parameters, and session detail.
The Semgrep registry rule
`ruby.rails.security.audit.consider-all-requests-local`
flags this.

## Antipattern I: Custom serializer with all fields

```python
@dataclass
class ApplicationError(Exception):
    message: str
    code: str
    internal_state: dict
    cause: Optional[Exception] = None

@app.errorhandler(ApplicationError)
def handle_app_error(e):
    return jsonify(dataclasses.asdict(e)), 500
```

`dataclasses.asdict` serializes every field including
`internal_state` (which may contain credentials, internal
IDs, debug context) and `cause` (which carries the original
exception's full state). The substrate-preferred pattern is
explicit allowlisting: declare which fields are client-facing
on the exception class and serialize only those.

## Remediation

For each antipattern above:

1. Disable framework debug mode in production (env vars,
   config files, settings modules).

2. Route error responses through a centralized handler that
   constructs Problem Details (or the application's documented
   alternative) by explicit field allowlist.

3. Log the full exception detail server-side per error-handling.no-exception-swallow;
   the client receives the controlled response, the operator
   receives the diagnostic.

4. Configure infrastructure (Spring Boot properties, Django
   settings, Rails config, Flask env vars) to suppress
   framework-default disclosure surfaces.

5. Verify via Checkov, kube-linter, or per-framework
   configuration scanners that deployment configurations do
   not re-enable debug surfaces.
