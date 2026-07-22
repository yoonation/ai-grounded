<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.health-signaling health signaling (anti-pattern)

Substrate-original illustration. A single endpoint serves both probes and
calls every dependency, so a downstream outage triggers a fleet-wide
restart storm and removes capacity exactly when it is needed.

```python
@app.get("/health")    # used as BOTH liveness and readiness
async def health() -> Response:
    # Liveness should never depend on downstreams. Here a slow or down
    # database makes every instance report unhealthy, so the
    # orchestrator restarts the whole fleet during a DB blip.
    await db.ping()
    await cache.ping()          # non-critical, yet gates liveness
    await recs_client.ping()    # optional, yet gates liveness
    return Response(status_code=200)
```

```yaml
livenessProbe:  { httpGet: { path: /health } }   # restarts on DB outage
readinessProbe: { httpGet: { path: /health } }   # same endpoint
```

Why this fails the rule: liveness and readiness are conflated, and the
single check calls critical, degradable, and optional dependencies
alike. A transient outage of any of them, including an optional one,
restarts healthy instances, turning a minor dependency blip into a
self-inflicted outage. The fix is to separate the signals and strip
dependencies out of liveness, as in the good example.
