<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.correlation-ids correlation IDs

Substrate-original anti-pattern examples for logging.correlation-ids.

## Anti-pattern A: No correlation infrastructure

```python
import logging
log = logging.getLogger(__name__)

@app.route('/api/order')
def create_order():
    log.info("order received")
    order = orders.create(request.get_json())
    log.info("order saved", extra={"order_id": order.id})
    payments.charge(order)
    log.info("payment processed")
    return jsonify({"id": order.id})
```

Why this violates logging.correlation-ids: no correlation field is bound.
Three log records from this single request scatter across the
aggregator with no shared identifier. Incident investigation
must reconstruct the sequence by timestamp proximity, which
fails under concurrent load.

## Anti-pattern B: Thread-local correlation in async code

```python
import logging
import threading

local = threading.local()

class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(local, 'request_id', 'none')
        return True

async def handle_request(request):
    local.request_id = generate_id()
    log.info("processing")
    await asyncio.create_task(background_work())  # ← context lost
    return success()

async def background_work():
    log.info("background started")  # ← request_id is 'none'
```

Why this violates logging.correlation-ids: thread-local storage does not
propagate across asyncio task boundaries. Logs from
background_work lose the correlation. The substrate-
recommended replacement is contextvars (Python) or
AsyncLocalStorage (JavaScript).

## Anti-pattern C: Manual correlation passing that drifts

```javascript
function handleRequest(req, res) {
    const requestId = req.headers['x-request-id'] || uuidv4();
    console.log({ request_id: requestId, msg: 'request received' });
    processOrder(req.body, requestId);
    chargePayment(req.body.payment, requestId);
    res.json({ ok: true });
}

function processOrder(order, requestId) {
    console.log({ request_id: requestId, order: order.id, msg: 'order created' });
    saveToDatabase(order);  // ← requestId not passed to saveToDatabase
}

function saveToDatabase(order) {
    console.log({ msg: 'saving order' });  // ← no correlation
}
```

Why this violates logging.correlation-ids: manual correlation passing
relies on every function call site to thread the request_id
through its arguments. A single missed parameter (saveToDatabase
above) breaks the chain for all logs below that call.

## Anti-pattern D: Correlation only on entry log

```python
@app.route('/api/payment')
def process_payment():
    request_id = request.headers.get('X-Request-ID', generate_id())
    log.info("payment_received", request_id=request_id)
    try:
        charge_card(request.json['card'], request.json['amount'])
        log.info("payment_succeeded")  # ← no request_id
    except PaymentError as e:
        log.error("payment_failed", error=str(e))  # ← no request_id
    return jsonify({"ok": True})
```

Why this violates logging.correlation-ids: the request_id is logged only
on entry. Subsequent log records lack the correlation, so
the success or failure cannot be joined to the entry record
without timestamp guesswork.

## Anti-pattern E: Background job with no correlation

```python
@celery_app.task
def send_welcome_email(user_id):
    log.info("sending welcome email", user_id=user_id)
    user = users.get(user_id)
    send_email(user.email, 'Welcome')
    log.info("welcome email sent")
```

Why this violates logging.correlation-ids: the background job emits log
records with no correlation to the request that triggered
the job. Tracing a user-reported "I never got the welcome
email" issue requires manual correlation by user_id and
timestamp, which fails when many similar jobs run.

## Anti-pattern F: Correlation lost across HTTP service boundaries

```python
@app.route('/api/checkout')
def checkout():
    log.info("checkout_started", request_id=g.request_id)

    response = requests.post(
        'https://inventory.internal/reserve',
        json={'items': request.json['items']},
    )

    log.info("inventory_response", status=response.status_code, request_id=g.request_id)
    return finalize_order()
```

Why this violates logging.correlation-ids: the outbound HTTP request to
inventory.internal does not propagate the request_id (or
trace context). The inventory service logs the reservation
under its own correlation; cross-service tracing requires
manual reconstruction. The substrate-recommended fix is to
propagate W3C Trace Context headers on every outbound call,
which most HTTP client libraries do automatically when
OpenTelemetry instrumentation is enabled.

## Anti-pattern G: Per-worker correlation drift

```python
# gunicorn config: workers=4, prefork mode
import structlog
import uuid

WORKER_ID = uuid.uuid4().hex[:8]  # ← bound at worker start

structlog.configure(
    processors=[
        lambda _, __, event_dict: {**event_dict, 'worker_id': WORKER_ID},
        structlog.processors.JSONRenderer(),
    ]
)
```

Why this violates logging.correlation-ids: each worker has a different
WORKER_ID, but the field is not a per-request correlation.
Records carry worker affinity but no request affinity. A
user's request lands on a random worker; their logs are
tagged with a worker_id that does not correlate to anything
useful for incident response.

## Cross-reference

- Good patterns: examples/logging/correlation-ids-good.md
- Substrate rule: logging.correlation-ids
