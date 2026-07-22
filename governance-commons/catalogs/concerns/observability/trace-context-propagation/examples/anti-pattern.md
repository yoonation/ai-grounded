<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.trace-context-propagation trace context propagation (anti-patterns)

Substrate-original anti-pattern examples for observability.trace-context-propagation.

## Anti-pattern A: Raw HTTP client without instrumentation (Python)

```python
import requests


def call_downstream(payload):
    return requests.post(
        "https://downstream.internal/api/v1/process",
        json=payload,
        timeout=10,
    )
```

Why this violates observability.trace-context-propagation: requests is used without
opentelemetry-instrumentation-requests being installed and
called at application startup. The outbound call goes out
without a traceparent header. The downstream service receives
no trace context and starts a new trace. Operators investigating
slow requests through the call path cannot connect the
originating request to the downstream activity.

Remediation: install opentelemetry-instrumentation-requests
and configure it at startup. The good-pattern example shows
the minimal configuration.

## Anti-pattern B: Manual header construction without inject (Python)

```python
def send_custom_transport(url, payload):
    headers = {
        "Content-Type": "application/json",
        "X-Tenant-Id": current_tenant_id(),
    }
    custom_transport.post(url, payload, headers=headers)
```

Why this violates observability.trace-context-propagation: the headers dict is constructed
manually for a non-instrumented transport, but no
propagate.inject call adds the traceparent. The header dict
is the consumer's full control surface for outbound headers
on this transport; the omission is the propagation break.

Remediation: call propagate.inject(headers) before sending.
The good-pattern example shows the minimal injection.

## Anti-pattern C: gRPC client without OpenTelemetry interceptor (Go)

```go
func newClient(target string) (*grpc.ClientConn, error) {
    return grpc.Dial(target)
}
```

Why this violates observability.trace-context-propagation: no OpenTelemetry interceptor is
attached to the gRPC channel. Outbound gRPC calls through this
channel propagate no trace context. The downstream gRPC server
starts a new trace. Cross-service trace investigation fails
at this hop.

Remediation: attach otelgrpc.UnaryClientInterceptor and
otelgrpc.StreamClientInterceptor when constructing the
channel.

## Anti-pattern D: Untraced call without documented exemption (Python)

```python
def call_internal_api():
    return requests.get("https://internal.example.com/data")
```

Why this violates observability.trace-context-propagation: even if the consumer has
decided this call is deliberately untraced, the substrate
discipline requires the exemption be documented at the call
site with the substrate-recognized exemption comment. Without
the comment, the call is indistinguishable from an oversight.

Remediation: add the exemption comment with a rationale
pointing to the ADR; OR install instrumentation and let
propagation happen (the substrate-default).

## Anti-pattern E: Instrumentation imported but not configured (Node.js)

```javascript
import '@opentelemetry/instrumentation-fetch';
import { fetch } from 'undici';

async function callDownstream(payload) {
  return await fetch('https://downstream.internal/api/v1/process', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
```

Why this violates observability.trace-context-propagation at runtime: importing the
instrumentation module is not enough; the module must be
registered (typically via the OpenTelemetry SDK setup) before
the first fetch call. The static analysis sees the import and
may pass; the runtime propagation health check catches the
case (no traceparent on the outbound fetch).

Remediation: register the instrumentation in the application's
OpenTelemetry SDK initialization, before any user code makes
outbound calls. The good-pattern example for the Python
equivalent (RequestsInstrumentor().instrument()) shows the
explicit registration pattern; Node.js requires the same
explicit registration step.

## Anti-pattern F: Subprocess shellout for HTTP

```python
def fetch_via_curl(url):
    result = subprocess.run(
        ["curl", "-sS", url],
        capture_output=True,
        text=True,
    )
    return result.stdout
```

Why this violates observability.trace-context-propagation: subprocess invocations of curl
do not participate in the parent process's OpenTelemetry
context. The outbound call from curl carries no traceparent.
There is no auto-instrumentation for subprocess shellout.

Remediation: replace with an in-process HTTP client that is
auto-instrumented. If subprocess is operationally necessary
(an existing tool the consumer must invoke), explicitly pass
the traceparent header on the curl command line: curl
-H "traceparent: ..." ...

## Cross-reference

- Substrate rule: observability.trace-context-propagation in catalogs/concerns/observability.oscal.yaml
- L1 binding: checklist.md
- Good-pattern examples: examples/observability/trace-context-propagation-good.md
- Related: logging.correlation-ids (correlation IDs in logs depend on trace context being propagated)
