<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.no-exception-swallow exception swallow

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Python empty except body

```python
try:
    gateway.charge(payment_id)
except GatewayException:
    pass
```

The exception is suppressed without log. Operations failures
go unnoticed; the payment may have failed and no one knows.

## Antipattern B: Python except with comment instead of log

```python
try:
    gateway.charge(payment_id)
except GatewayException:
    # ignore, we'll retry next time
    pass
```

The comment is not a log entry. The "we'll retry next time"
intent is not implemented; the failure is silently dropped.

## Antipattern C: Java empty catch block

```java
try {
    paymentGateway.charge(paymentId);
} catch (GatewayException e) {
}
```

Same pattern in Java: the exception is caught and dropped. The
SpotBugs DE_MIGHT_IGNORE detector flags this.

## Antipattern D: JavaScript empty catch

```javascript
try {
  await gateway.charge(paymentId);
} catch (err) {}
```

Empty catch in JavaScript. The eslint `no-empty` rule (with
`allowEmptyCatch: false`) flags this; the substrate's L1
binding rejects it.

## Antipattern E: Go err received but ignored

```go
order, err := repo.Load(ctx, id)
if err != nil {
    // do nothing
}
return order
```

The err is checked but no action is taken. The Go-idiomatic
equivalent of swallow: errcheck flags the unused err return,
and the substrate's L1 binding marks the empty conditional
body.

## Antipattern F: Console.log instead of structured log

```javascript
try {
  await gateway.charge(paymentId);
} catch (err) {
  console.log('charge failed');
  return null;
}
```

`console.log` does not satisfy the substrate's log discipline:
no structured fields, no correlation ID, no exception detail.
The operator sees "charge failed" with no way to correlate to
a specific payment or to investigate. Severity is implicit
(stdout vs stderr), not structured.

## Antipattern G: Catch-log-without-context

```python
try:
    gateway.charge(payment_id)
except GatewayException:
    logger.error("error")
```

The log entry has no context: which payment, which gateway,
which correlation ID. The operator cannot use the entry for
investigation. The substrate's L1 binding catches "logger
called in catch" but does not verify context completeness;
error-handling.typed-error-classification review (via the LOG-L2-* rules) catches the
context deficiency.

## Antipattern H: Re-raise without log

```python
try:
    gateway.charge(payment_id)
except GatewayException:
    raise
```

While the exception is re-raised (so it propagates), the lack
of log means the operator's first signal is the outer handler's
log (which may be far from the original site). error-handling.no-exception-swallow
requires the log at the catch site even when re-raising,
because the local context (which call, which parameters) is
most easily captured there.

## Remediation

For each antipattern above, add a structured log call with
correlation ID, operation name, exception detail (including
stack trace via exc_info=True or equivalent), and any
relevant business context (payment_id, user_id, request_id).
Choose severity per the application's logging policy:
typically ERROR for failures that interrupt the request,
WARN for failures the handler recovers from with a fallback,
DEBUG for expected non-failure exceptional paths (file
absent during optional poll).
