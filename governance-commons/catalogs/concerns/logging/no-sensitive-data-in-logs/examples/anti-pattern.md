<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.no-sensitive-data-in-logs sensitive data in logs

Substrate-original anti-pattern examples for logging.no-sensitive-data-in-logs.

## Anti-pattern A: Whole-request logging

```python
@app.route('/api/login', methods=['POST'])
def login():
    log.info("login_attempt", request=request)
    user = authenticate(request.form['username'], request.form['password'])
    return success(user)
```

Why this violates logging.no-sensitive-data-in-logs: request serialization captures
the full body including the password field. Aggregator
ingestion stores the password for the entire retention window.

## Anti-pattern B: Exception stringification with user input

```python
def transfer_funds(amount, account):
    try:
        assert account.balance >= amount, \
            f"Insufficient balance: {account.balance} for transfer of {amount}"
        process_transfer(amount, account)
    except AssertionError as e:
        log.error("transfer_failed", error=str(e))
```

Why this violates logging.no-sensitive-data-in-logs: the assertion message includes
account balance and transfer amount; str(e) carries this into
the log record. Customer financial state is now in logs for
the retention window.

## Anti-pattern C: Debug logging of credentials

```javascript
async function login(username, password) {
    console.log('login attempt:', { username, password });
    const result = await api.authenticate(username, password);
    return result;
}
```

Why this violates logging.no-sensitive-data-in-logs: console.log of the credentials
object captures both username and password. Even if the
console output is redirected to a structured aggregator, the
password is in the structured record.

## Anti-pattern D: Token in URL logging

```python
@app.route('/api/reset', methods=['GET'])
def reset_password():
    log.info("password_reset_link_accessed",
        url=request.url,
        ip=request.remote_addr)
    token = request.args.get('token')
    return reset_form(token)
```

Why this violates logging.no-sensitive-data-in-logs: the reset URL contains the
single-use token in the query string. Logging the full URL
captures the token, which is presumed compromised once
logged.

## Anti-pattern E: User object serialization

```python
def update_profile(user_id, updates):
    user = users.get(user_id)
    log.info("profile_update",
        user_id=user_id,
        user=user.to_dict(),
        updates=updates)
    user.update(updates)
```

Why this violates logging.no-sensitive-data-in-logs: user.to_dict() typically
includes hashed password, session token, SSN if stored, and
other sensitive fields. The model-default serializer is not
log-safe.

## Anti-pattern F: HTTP header dump

```javascript
app.use((req, res, next) => {
    console.log('incoming request:', {
        method: req.method,
        path: req.path,
        headers: req.headers,
        body: req.body
    });
    next();
});
```

Why this violates logging.no-sensitive-data-in-logs: req.headers includes the
Authorization header (bearer tokens, basic auth credentials),
Cookie header (session identifiers), and any custom auth
headers. req.body may include passwords or PII depending on
the endpoint.

## Anti-pattern G: Credit card number in logs

```python
@app.route('/api/checkout', methods=['POST'])
def checkout():
    card = request.form['card_number']
    log.info("checkout_attempt", card=card, amount=request.form['amount'])
    process_payment(card, amount)
```

Why this violates logging.no-sensitive-data-in-logs: the card_number field carries
a Primary Account Number (PAN), prohibited from logs by
PCI DSS Requirement 3.4. Even if encrypted at rest, the log
location is generally accessible to a broader audience than
the PAN's allowed access.

## Cross-reference

- Good patterns: examples/logging/no-sensitive-data-in-logs-good.md
- Substrate rule: logging.no-sensitive-data-in-logs
- Related anti-pattern: secrets-management no-secrets-in-logs-anti-pattern.md
