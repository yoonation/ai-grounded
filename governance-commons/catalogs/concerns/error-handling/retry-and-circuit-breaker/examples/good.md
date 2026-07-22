<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.retry-and-circuit-breaker retry and circuit-breaker

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python tenacity with backoff and jitter

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential_jitter,
    retry_if_exception_type, before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=0.1, max=2.0, jitter=0.2),
    retry=retry_if_exception_type(DownstreamTimeout),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def fetch_user_profile(user_id: str) -> Profile:
    try:
        response = http_client.get(
            f"/users/{user_id}",
            timeout=0.2,  # per-call timeout shorter than total budget
        )
        response.raise_for_status()
        return Profile.from_json(response.json())
    except httpx.TimeoutException as e:
        raise DownstreamTimeout("fetch_user_profile", e) from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (502, 503, 504):
            raise DownstreamTimeout("fetch_user_profile", e) from e
        raise
```

Bounded retry (max 3 attempts), exponential backoff with
jitter (100ms initial doubling to 2s cap), retry only on
typed `DownstreamTimeout` (the retriable class), per-call
timeout. Non-retriable errors (4xx) propagate immediately.

## Pattern B: Java resilience4j with retry and circuit-breaker

```java
@Configuration
public class ResilienceConfig {
    @Bean
    public Retry profileFetchRetry() {
        return Retry.of("profile-fetch", RetryConfig.custom()
            .maxAttempts(3)
            .waitDuration(Duration.ofMillis(100))
            .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(100, 2.0))
            .retryOnException(e -> e instanceof DownstreamTimeoutException)
            .build());
    }

    @Bean
    public CircuitBreaker profileServiceBreaker() {
        return CircuitBreaker.of("profile-service", CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .slidingWindowSize(20)
            .minimumNumberOfCalls(10)
            .waitDurationInOpenState(Duration.ofSeconds(60))
            .permittedNumberOfCallsInHalfOpenState(3)
            .build());
    }
}

@Service
public class ProfileService {
    private final Retry retry;
    private final CircuitBreaker breaker;

    public Profile fetchProfile(String userId) {
        Supplier<Profile> decorated = CircuitBreaker.decorateSupplier(
            breaker,
            Retry.decorateSupplier(retry, () -> callProfileService(userId)));
        return decorated.get();
    }
}
```

resilience4j composes Retry and CircuitBreaker decorators.
The breaker opens on 50% failure rate in a 20-call window,
half-opens after 60 seconds, and admits 3 trial calls.

## Pattern C: Go gobreaker with exponential backoff

```go
package downstream

import (
    "context"
    "time"
    "github.com/sony/gobreaker"
    "github.com/cenkalti/backoff/v4"
)

var profileBreaker = gobreaker.NewCircuitBreaker(gobreaker.Settings{
    Name:        "profile-service",
    MaxRequests: 3,
    Interval:    30 * time.Second,
    Timeout:     60 * time.Second,
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        failRate := float64(counts.TotalFailures) / float64(counts.Requests)
        return counts.Requests >= 10 && failRate >= 0.5
    },
})

func FetchProfile(ctx context.Context, userID string) (*Profile, error) {
    result, err := profileBreaker.Execute(func() (interface{}, error) {
        var profile *Profile
        op := func() error {
            ctx, cancel := context.WithTimeout(ctx, 200*time.Millisecond)
            defer cancel()
            p, err := callProfileService(ctx, userID)
            if err != nil {
                return classifyForRetry(err)
            }
            profile = p
            return nil
        }
        b := backoff.NewExponentialBackOff()
        b.InitialInterval = 100 * time.Millisecond
        b.MaxElapsedTime = 1 * time.Second
        b.RandomizationFactor = 0.2
        return profile, backoff.Retry(op, backoff.WithMaxRetries(b, 2))
    })
    if err != nil {
        return nil, err
    }
    return result.(*Profile), nil
}

func classifyForRetry(err error) error {
    var to *TimeoutError
    if errors.As(err, &to) {
        return err // retriable
    }
    return backoff.Permanent(err) // not retriable
}
```

gobreaker wraps the call; cenkalti/backoff applies bounded
retry with exponential backoff and jitter. The classifier
function marks non-retriable errors as Permanent so backoff
stops immediately.

## Pattern D: .NET Polly composed policies

```csharp
public class ProfileServiceClient
{
    private readonly IAsyncPolicy<Profile> _resilientPolicy;

    public ProfileServiceClient(IHttpClientFactory factory)
    {
        var retry = Policy<Profile>
            .Handle<HttpRequestException>()
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: attempt =>
                    TimeSpan.FromMilliseconds(100 * Math.Pow(2, attempt))
                    + TimeSpan.FromMilliseconds(Random.Shared.Next(0, 100)),
                onRetry: (outcome, delay, attempt, ctx) =>
                    _logger.LogWarning("Retry {Attempt} after {Delay}",
                        attempt, delay));

        var breaker = Policy<Profile>
            .Handle<HttpRequestException>()
            .CircuitBreakerAsync(
                exceptionsAllowedBeforeBreaking: 5,
                durationOfBreak: TimeSpan.FromSeconds(60));

        _resilientPolicy = Policy.WrapAsync(breaker, retry);
    }

    public Task<Profile> FetchAsync(string userId)
        => _resilientPolicy.ExecuteAsync(() => CallProfileServiceAsync(userId));
}
```

Polly composes circuit-breaker and retry. The outer breaker
sees the result after retry exhausts; the inner retry runs
within the breaker's closed state.

## Pattern E: Idempotency-key contract for non-idempotent calls

```python
from uuid import uuid4

def authorize_payment(amount: int, payment_method_id: str) -> AuthorizationResult:
    idempotency_key = str(uuid4())  # generated per logical operation
    try:
        return payment_gateway.authorize(
            amount=amount,
            payment_method=payment_method_id,
            idempotency_key=idempotency_key,
            timeout=2.0,
        )
    except GatewayTimeout:
        # Safe to retry because the gateway deduplicates by key
        return payment_gateway.authorize(
            amount=amount,
            payment_method=payment_method_id,
            idempotency_key=idempotency_key,  # same key
            timeout=2.0,
        )
```

The non-idempotent payment authorization uses an idempotency
key the gateway honors. Retry is safe because the gateway
deduplicates by key (a duplicate request returns the original
response). The substrate accepts retry of non-idempotent
operations only with this contract.

## Pattern F: SLO-aligned configuration documented in the ADR

From the error-handling.error-handling-strategy ADR for the application:

> Per observability.slo-policy, the application's SLO budget is 99.9%
> success rate over a 30-day window (error budget: 43m
> downtime per month).
>
> Retry configuration: max 3 attempts on idempotent calls;
> exponential backoff base 100ms with equal jitter; max
> elapsed retry time 1s.
>
> Under sustained downstream failure, retry amplifies load on
> the downstream by up to 3x. At our peak request volume of
> 100 RPS, the worst-case downstream load is 300 RPS. The
> downstream's documented capacity is 500 RPS; our amplified
> load stays within their headroom.
>
> Circuit-breaker thresholds: open at 50% failure rate in a
> 30-second window with minimum 10 calls; half-open after 60
> seconds; close on 3 consecutive successes.

The configuration is justified against the SLO budget and the
downstream's documented capacity. Reviewers can verify the
math.
