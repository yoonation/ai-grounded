<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.critical-path-coverage critical paths catalogued and covered

Substrate-original good patterns. Adapt to your stack.

## Pattern A: catalog of critical paths

The application's `/docs/critical-paths.md` (referenced from the
testing-strategy.testing-strategy ADR):

```markdown
# Critical Business Paths

## Authentication
- Login (POST /auth/login)
- Logout (POST /auth/logout)
- Password reset request (POST /auth/password-reset)
- Token refresh (POST /auth/refresh)

## Authorization
- Resource ownership check (READ /orders/:id)
- Cross-tenant access prevention (READ /tenants/:tid/data)
- Role-based action authorization (POST /admin/users)

## Payment / State-Changing
- Charge card (POST /payments)
- Refund (POST /payments/:id/refund)
- Bulk export (POST /exports/orders)

## Security Boundary
- Token signature validation
- SSO callback parameter validation
```

Each path has a corresponding test suite directory:
`tests/critical-paths/auth/`, `tests/critical-paths/authz/`,
`tests/critical-paths/payment/`, `tests/critical-paths/security/`.

## Pattern B: per-path test matrix

For each critical path, a test matrix:

```
Path: POST /auth/login
| Happy | Error | Edge | Security Probe |
| ----- | ----- | ---- | -------------- |
| test_login_with_valid_credentials | test_login_with_wrong_password | test_login_with_empty_password | test_login_does_not_enumerate_users |
|       | test_login_with_unknown_user | test_login_with_max_length_password | test_login_resists_timing_oracle |
|       | test_login_when_user_locked | test_login_with_unicode_password | test_login_enforces_rate_limit |
|       | test_login_when_idp_unavailable | test_login_with_special_chars | test_login_rejects_replay_token |
```

```python
# tests/critical-paths/auth/test_login_security_probes.py
import pytest

class TestLoginSecurityProbes:
    """
    Substrate-aligned security probes per authentication.generic-failure-responses (generic
    error messaging) and authentication.no-hardcoded-credentials (timing-based enumeration
    prevention).
    """

    def test_login_does_not_enumerate_users(self, client):
        """authentication.generic-failure-responses: wrong-password and unknown-user paths
        return identical responses (status and body)."""
        wrong_pw = client.post("/auth/login",
                               json={"username": "alice", "password": "wrong"})
        unknown = client.post("/auth/login",
                              json={"username": "nonexistent", "password": "any"})
        assert wrong_pw.status_code == unknown.status_code == 401
        assert wrong_pw.json() == unknown.json()

    def test_login_resists_timing_oracle(self, client, timing_oracle):
        """authentication.no-hardcoded-credentials: response timing for wrong-password vs
        unknown-user is within acceptable variance."""
        wrong_pw_times = timing_oracle.measure(
            lambda: client.post("/auth/login",
                                json={"username": "alice", "password": "wrong"}),
            n=100,
        )
        unknown_times = timing_oracle.measure(
            lambda: client.post("/auth/login",
                                json={"username": "x", "password": "y"}),
            n=100,
        )
        assert timing_oracle.is_indistinguishable(wrong_pw_times, unknown_times)
```

The security probe tests reference substrate L1 rule IDs in
docstrings, making the cross-concern alignment explicit.

## Pattern C: edge case coverage with parametrize

```python
@pytest.mark.parametrize("password,description", [
    ("", "empty"),
    ("a", "single char"),
    ("a" * 128, "max documented length"),
    ("a" * 129, "max length + 1"),
    ("a" * 10000, "very long"),
    ("\x00", "null byte"),
    ("\u202e", "unicode override"),
    ("ümlaut", "non-ascii"),
    ("admin' OR '1'='1", "sql injection probe"),
])
def test_login_handles_password_edge_cases(client, password, description):
    """Edge-case coverage for the login critical path."""
    response = client.post("/auth/login",
                           json={"username": "alice", "password": password})
    assert response.status_code in (401, 400), description
    # The substrate's authentication.generic-failure-responses guarantees no information leakage
    assert "alice" not in response.text
```

The parametrize fixture exercises edge cases as distinct test
cases; each appears in the test report with the description, so
failures are diagnostically rich.

## Pattern D: cross-concern security probe alignment

```python
# tests/critical-paths/payment/test_charge_card_security.py
class TestChargeCardSecurityProbes:
    """
    Critical path: POST /payments
    Substrate alignment: authorization.authz-before-resource-access (authorization before access),
    input-validation.parameterized-queries (parameterized queries), error-handling.no-stack-trace-in-response (no stack
    trace in response).
    """

    def test_charge_requires_authentication(self, client):
        response = client.post("/payments",
                               json={"amount": 100, "card_token": "tok_abc"})
        assert response.status_code == 401

    def test_charge_enforces_ownership(self, client, user_a_token, user_b_card):
        response = client.post("/payments",
                               headers={"Authorization": f"Bearer {user_a_token}"},
                               json={"amount": 100, "card_token": user_b_card})
        assert response.status_code == 403

    def test_charge_with_malformed_amount_rejected_cleanly(self, client, valid_token):
        response = client.post("/payments",
                               headers={"Authorization": f"Bearer {valid_token}"},
                               json={"amount": "'; DROP TABLE payments; --"})
        assert response.status_code == 400
        # error-handling.no-stack-trace-in-response: no stack trace
        assert "Traceback" not in response.text
        assert "at line" not in response.text
```

Each test exercises a substrate L1 rule from an adjacent concern.
The test docstrings cross-reference the L1 IDs, supporting the
substrate's compositional discipline.

## Pattern E: gap tracking when matrix is incomplete

The team maintains a `tests/critical-paths/MATRIX.md` showing
the per-path × test-type matrix. Empty cells are tracked as
issues:

```markdown
| Path | Happy | Error | Edge | Security |
| ---- | ----- | ----- | ---- | -------- |
| /auth/login | ✓ | ✓ | ✓ | ✓ |
| /auth/logout | ✓ | ✓ | ◯ (issue-456) | ✓ |
| /payments | ✓ | ✓ | ✓ | ✓ |
| /payments/refund | ✓ | ◯ (issue-789) | ◯ (issue-790) | ✓ |
```

The MATRIX.md file is the substrate-acceptable interim form
while gaps are remediated; the testing-strategy.critical-path-coverage review catches the
matrix at PR time when new critical paths are added.
