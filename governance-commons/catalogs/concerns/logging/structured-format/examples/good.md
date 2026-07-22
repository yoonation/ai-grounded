<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.structured-format structured logging format (good patterns)

Substrate-original good-pattern examples for logging.structured-format.

## Pattern A: Python structlog with JSON renderer

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)

log = structlog.get_logger()
log.info("user_login", user_id=user.id, source_ip=request.remote_addr)
```

Why this satisfies logging.structured-format: structlog with the JSONRenderer
produces structured records. Each call site passes data as
key-value arguments; the renderer handles serialization. No
prose interpolation appears at any call site.

## Pattern B: Node.js pino logger

```javascript
const pino = require('pino')();

pino.info({
    event: 'user_login',
    user_id: user.id,
    source_ip: req.ip
}, 'user logged in');
```

Why this satisfies logging.structured-format: pino emits JSON by default.
Structured fields appear as the first argument object; the
trailing message string is a stable event label, not an
interpolation target.

## Pattern C: Go zerolog with structured fields

```go
import "github.com/rs/zerolog/log"

log.Info().
    Str("event", "user_login").
    Str("user_id", user.ID).
    Str("source_ip", r.RemoteAddr).
    Msg("user logged in")
```

Why this satisfies logging.structured-format: zerolog's fluent API enforces
structured field-by-field log construction. The Msg() call
takes a fixed string; user-controlled values arrive as typed
field values.

## Pattern D: Java slf4j with logstash encoder

```java
logger.info("user_login",
    StructuredArguments.kv("user_id", user.getId()),
    StructuredArguments.kv("source_ip", request.getRemoteAddr()));
```

Why this satisfies logging.structured-format: slf4j with the logstash encoder
produces JSON. The StructuredArguments helpers ensure values
appear as structured fields, not interpolated into the message.

## Pattern E: Ruby semantic_logger

```ruby
SemanticLogger.add_appender(io: $stdout, formatter: :json)
logger = SemanticLogger['Application']

logger.info('user_login',
    user_id: user.id,
    source_ip: request.remote_ip)
```

Why this satisfies logging.structured-format: semantic_logger with the JSON
formatter produces structured records. Named arguments map
directly to JSON fields.

## Pattern F: .NET Serilog with JSON formatter

```csharp
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console(new JsonFormatter())
    .CreateLogger();

Log.Information("user_login {UserId} {SourceIp}",
    user.Id, request.RemoteIpAddress);
```

Why this satisfies logging.structured-format: Serilog with JsonFormatter
emits structured output. Message-template placeholders
({UserId}) map to typed parameters; the underlying record is
a structured object, not a formatted string.

## Pattern G: Test exemption via directory exclusion

```python
# scripts/local-dev-helper.py is excluded from L1-001
# enforcement via the project's pyproject.toml configuration:
#
# [tool.ruff]
# extend-exclude = ["scripts/", "tests/", ".dev/"]

print("Local helper script: bootstrapping dev env")
```

Why this satisfies logging.structured-format: the file is in a directory
the substrate-recommended exemption pattern covers. The
exemption is configured at the linter level so the rule
applies to production source paths only.

## Cross-reference

- Anti-patterns: examples/logging/structured-format-anti-pattern.md
- Substrate rule: logging.structured-format
- L1 binding: binding.yaml
