<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.no-exception-swallow no exception swallow

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python logger.exception with context

```python
import logging
logger = logging.getLogger(__name__)

def process_payment(payment_id: str, correlation_id: str):
    try:
        gateway.charge(payment_id)
    except GatewayDeclined as e:
        logger.warning(
            "payment declined",
            extra={
                "payment_id": payment_id,
                "correlation_id": correlation_id,
                "decline_code": e.code,
            },
        )
        raise PaymentDeclined(payment_id, e.code) from e
    except GatewayTimeout as e:
        logger.error(
            "payment gateway timeout",
            extra={
                "payment_id": payment_id,
                "correlation_id": correlation_id,
            },
            exc_info=True,
        )
        raise PaymentGatewayUnavailable(payment_id) from e
```

Every except branch logs with sufficient context (payment ID,
correlation ID, decline code where available) before raising
the typed application error. `exc_info=True` includes the
stack trace.

## Pattern B: Java SLF4J with MDC

```java
try {
    paymentGateway.charge(paymentId);
} catch (GatewayDeclinedException e) {
    log.warn("payment declined: declineCode={}", e.declineCode(), e);
    throw new PaymentDeclined(paymentId, e.declineCode());
} catch (GatewayTimeoutException e) {
    log.error("payment gateway timeout", e);
    throw new PaymentGatewayUnavailable(paymentId, e);
}
```

The exception is passed as the second argument to log methods,
which SLF4J renders with the full stack trace. MDC (configured
upstream) carries correlation IDs.

## Pattern C: Node.js with pino structured logging

```javascript
try {
  await gateway.charge(paymentId);
} catch (err) {
  if (err instanceof GatewayDeclinedError) {
    logger.warn({
      payment_id: paymentId,
      correlation_id: correlationId,
      decline_code: err.code,
      err,
    }, 'payment declined');
    throw new PaymentDeclined(paymentId, err.code);
  }
  if (err instanceof GatewayTimeoutError) {
    logger.error({
      payment_id: paymentId,
      correlation_id: correlationId,
      err,
    }, 'payment gateway timeout');
    throw new PaymentGatewayUnavailable(paymentId);
  }
  throw err;
}
```

pino serializes the `err` property to include the stack trace.
The structured fields support querying by payment_id or
correlation_id.

## Pattern D: Go slog with structured fields

```go
if err := gateway.Charge(ctx, paymentID); err != nil {
    var declined *gateway.DeclinedError
    if errors.As(err, &declined) {
        slog.WarnContext(ctx, "payment declined",
            "payment_id", paymentID,
            "decline_code", declined.Code,
        )
        return PaymentDeclined{PaymentID: paymentID, Code: declined.Code}
    }
    var timeout *gateway.TimeoutError
    if errors.As(err, &timeout) {
        slog.ErrorContext(ctx, "payment gateway timeout",
            "payment_id", paymentID,
            "err", err,
        )
        return PaymentGatewayUnavailable{PaymentID: paymentID, Cause: err}
    }
    slog.ErrorContext(ctx, "payment gateway unexpected error",
        "payment_id", paymentID,
        "err", err,
    )
    return fmt.Errorf("charge: %w", err)
}
```

`slog.ErrorContext` reads the correlation ID from the context;
the err field preserves the chain for the unexpected case.

## Pattern E: Ruby with Rails logger

```ruby
begin
  gateway.charge(payment_id)
rescue Gateway::Declined => e
  Rails.logger.warn(
    "payment declined: payment_id=#{payment_id} " \
    "correlation_id=#{Current.correlation_id} " \
    "decline_code=#{e.code}"
  )
  raise PaymentDeclined.new(payment_id, e.code)
rescue Gateway::Timeout => e
  Rails.logger.error(
    "payment gateway timeout: payment_id=#{payment_id} " \
    "correlation_id=#{Current.correlation_id}",
    e
  )
  raise PaymentGatewayUnavailable.new(payment_id)
end
```

Rails.logger receives the exception as the second positional
argument; Lograge or the application's logger setup emits the
stack trace.

## Pattern F: Backstop log and re-raise

```python
try:
    return route(request)
except KnownApplicationError:
    raise
except Exception:
    logger.exception(
        "unhandled exception",
        extra={"path": request.path, "correlation_id": cid(request)},
    )
    metrics.increment("dispatch.unhandled_exception")
    raise
```

This is the substrate-acceptable backstop: log with full
context, emit a metric, then re-raise so the framework's
default handler returns the controlled 500. The re-raise is
what satisfies error-handling.no-exception-swallow (the exception is not swallowed)
while the log ensures operational visibility.
