<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.retry-and-circuit-breaker unbounded retry, missing timeouts, no circuit-breaker

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Unbounded while True retry

```python
def fetch_user_profile(user_id):
    while True:
        try:
            return http_client.get(f"/users/{user_id}").json()
        except httpx.TimeoutException:
            continue
```

The loop never terminates. A persistent downstream failure
holds the caller forever; the caller's own deadline is
violated; the caller's own thread or connection is consumed
indefinitely. Under load, every caller blocks on the same
unhealthy downstream and the application stops processing
unrelated work.

## Antipattern B: No timeout on HTTP call

```python
def fetch_user_profile(user_id):
    return http_client.get(f"/users/{user_id}").json()
```

The default HTTP client may have no timeout (Python `requests`
default is no timeout; `httpx` default is 5s; Java
`HttpClient` default is no timeout). A slow downstream holds
the caller indefinitely. Combined with concurrent request
handling, the application's thread or async-task pool
fills with stuck requests.

## Antipattern C: Constant-interval retry (no backoff)

```python
import time

def fetch_with_retry(user_id):
    for attempt in range(10):
        try:
            return http_client.get(
                f"/users/{user_id}",
                timeout=0.5,
            ).json()
        except httpx.TimeoutException:
            time.sleep(1)
    raise DownstreamTimeout()
```

10 attempts with 1-second sleep between each. Under a
synchronized failure (all callers hit the downstream at the
same time), the retry storm hits every second; downstream
load is amplified by 10x with no spreading. Combined with no
jitter, every caller retries at the same instant.

## Antipattern D: Excessive retry count

```python
@retry(stop=stop_after_attempt(50), wait=wait_fixed(0.1))
def fetch_data():
    return downstream.call()
```

50 attempts. Even with bounded total time (50 × 100ms = 5s),
the retry amplification is 50x. A downstream operating at
50% failure rate sees 25x successful retry traffic; a
downstream that returns to 100% failure sees 50x load with
no recovery window.

## Antipattern E: Retry on every error type indiscriminately

```python
@retry(stop=stop_after_attempt(3))
def authorize_user(token):
    return auth_service.verify(token)
```

The retry decorator does not specify which exception types
are retriable. `InvalidTokenError` (the user's token is bad;
not retriable) is retried 3 times; downstream receives 3
authorization attempts with the same bad token; the downstream
may rate-limit or lock the account.

## Antipattern F: Non-idempotent operation retried without contract

```python
@retry(stop=stop_after_attempt(3))
def authorize_payment(amount, payment_method):
    return payment_gateway.authorize(
        amount=amount,
        payment_method=payment_method,
        # NO idempotency_key parameter
    )
```

A payment authorization that times out on the network layer
may have succeeded on the gateway side. Retry without an
idempotency key produces a duplicate charge. The user is
charged twice; reconciliation requires manual intervention.

## Antipattern G: No circuit-breaker on degradation-prone dependency

```python
def get_recommendation(user_id):
    return third_party_recommender.suggest(
        user_id,
        timeout=5,
    )
```

The third-party recommender has documented rate limits and
historical degradation events. With no circuit-breaker, every
caller hits the downstream during outage; the upstream's
SLO is consumed by the unhealthy downstream's latency. A
breaker would open after consecutive failures and let the
upstream return a degraded (cached, default) response.

## Antipattern H: Timeout longer than the caller's deadline

```python
# Caller has a 1-second total deadline
def handle_request(request):
    profile = fetch_profile(request.user_id)  # timeout=5
    orders = fetch_orders(request.user_id)    # timeout=5
    return Response(profile, orders)
```

Each downstream call's timeout (5 seconds) exceeds the
caller's total deadline (1 second). On a slow downstream,
the caller exits via its own deadline, but the downstream
call is still running, consuming a connection. With
sufficient concurrent slow requests, the connection pool
exhausts.

## Antipattern I: Circuit-breaker that never opens

```python
breaker = CircuitBreaker(failure_threshold=10000, reset_timeout=60)
```

The threshold (10000 failures) effectively means the breaker
never opens. The breaker exists in code but is configured to
provide no protection. Reviewers approving the change need
to verify thresholds are appropriate; defaults from copy-paste
of an unrelated service are common antipatterns.

## Remediation

For each antipattern above:

1. Add an explicit per-call timeout shorter than the caller's
   deadline.

2. Bound retry: max 3 attempts for idempotent calls (1 for
   non-idempotent without idempotency keys); explicit total
   time budget.

3. Apply exponential backoff with jitter between attempts.

4. Classify the call as idempotent or non-idempotent. Apply
   idempotency keys for non-idempotent operations the
   downstream supports; do not retry without the contract.

5. Add a circuit-breaker around degradation-prone
   dependencies. Configure thresholds per the dependency's
   known capacity and recovery characteristics; document the
   configuration in the error-handling.error-handling-strategy ADR.

6. Compute the worst-case retry-amplified load and verify it
   stays within the downstream's documented capacity and
   within the application's SLO budget per observability.slo-policy.

7. Test the resilience layer per the
   `error-handling.retry-and-circuit-breaker-retry-and-circuit-breaker.md` test template;
   confirm the breaker opens and recovers under simulated
   failure.
