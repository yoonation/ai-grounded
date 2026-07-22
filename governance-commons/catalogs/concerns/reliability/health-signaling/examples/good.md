<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.health-signaling health signaling (good pattern)

Substrate-original illustration. Liveness and readiness are distinct.
Liveness checks only that the process is responsive; readiness gates on
the critical dependency and recovers automatically.

```python
@app.get("/healthz")            # liveness: process responsiveness only
async def healthz() -> Response:
    # No dependency calls. A downstream outage must not restart us.
    return Response(status_code=200)

@app.get("/readyz")             # readiness: ability to serve traffic
async def readyz() -> Response:
    # Gates on the critical dependency only (per the criticality
    # classification); recovers on its own when the dependency returns.
    if not await db.can_connect(timeout=0.2):
        return Response(status_code=503)   # route traffic away
    return Response(status_code=200)
```

```yaml
# Slow startup signaled distinctly from failure.
startupProbe:   { httpGet: { path: /readyz }, failureThreshold: 30, periodSeconds: 2 }
livenessProbe:  { httpGet: { path: /healthz }, periodSeconds: 10 }
readinessProbe: { httpGet: { path: /readyz }, periodSeconds: 5 }
```

Why this satisfies the rule: liveness cannot be tripped by a dependency
outage (no restart storm), readiness routes traffic away from an instance
that cannot serve its critical dependency and recovers without a restart,
and slow startup is handled by a startup probe rather than mistaken for a
crash.
