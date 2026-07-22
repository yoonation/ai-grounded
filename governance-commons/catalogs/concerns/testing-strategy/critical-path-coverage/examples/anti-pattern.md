<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.critical-path-coverage happy-path-only coverage

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: 95% line coverage with zero security probes

```python
# tests/test_auth.py
def test_login_succeeds():
    response = client.post("/auth/login",
                           json={"username": "alice", "password": "correct"})
    assert response.status_code == 200
    assert "token" in response.json()

def test_logout_succeeds():
    response = client.post("/auth/logout", headers={"Authorization": "Bearer ..."})
    assert response.status_code == 204

# coverage.py reports 95% line coverage on the auth module
```

The line coverage metric is high; the actual coverage of failure
modes is zero. Wrong-password, locked-account, expired-token,
malformed-payload, missing-CSRF, user-enumeration, timing-
oracle, and rate-limit cases are not tested.

The substrate's L2 review surfaces this state: "happy only" cells
fill every row of the per-path matrix; no security probe tests
exist; coverage metric agrees with structural exercise but
disagrees with the critical-path catalog.

## Anti-pattern B: no critical path catalog

The team's testing strategy says "test critical functionality
thoroughly." Each contributor interprets this differently:

- Team A tests authentication flows extensively
- Team B tests their payment service unit-by-unit but skips
  integration
- Team C tests UI components but not the underlying API

No catalog exists. New team members do not know which paths are
critical. When a contractor joins, they cannot identify the
security-sensitive surfaces. Audit time: the security
architect cannot point to a single document describing critical
paths.

## Anti-pattern C: tests exist but do not align with substrate L1 rules

```python
# tests/test_validation.py
def test_input_validation_handles_long_strings():
    result = validate_input("a" * 1000)
    assert result.is_valid is True or result.is_valid is False

def test_database_query_works():
    user = User.query.get(1)
    assert user is not None
```

The first test makes no specific claim about behavior. The
second exercises the database query but does not probe
input-validation.parameterized-queries (parameterized queries). Neither test would catch
the SQL injection vulnerability the substrate-aligned probe
test would catch.

## Anti-pattern D: edge cases tested in isolation, not on critical paths

```python
# tests/unit/test_string_utils.py
def test_truncate_empty_string():
    assert truncate("", 10) == ""

def test_truncate_unicode():
    assert truncate("héllo", 4) == "héll"

# tests/unit/test_validator.py
def test_validator_handles_unicode():
    assert validator.validate("héllo") is True
```

The string-utility and validator modules are tested for edge
cases in isolation. The critical paths that use these utilities
(login, payment, profile update) are tested only with happy
inputs. The substrate-aligned coverage tests the edge cases
through the critical path, not just at the utility layer.

## Anti-pattern E: security probes only at security-test boundary

```python
# tests/security/test_owasp_top_10.py
def test_application_resists_sql_injection():
    """One blanket test of one endpoint."""
    response = client.post("/search",
                           json={"q": "' OR '1'='1"})
    assert response.status_code in (400, 422)
```

A single "security tests" file tests one endpoint against one
attack vector. Every other endpoint that handles user input is
untested for SQL injection. The substrate-acceptable form
applies security probes to every critical path, not as a
separate one-off file.

## Anti-pattern F: matrix tracked but never reconciled with reality

The team has a `MATRIX.md` showing per-path × test-type
coverage. The matrix has not been updated since six months ago.
New critical paths have been added but not catalogued; existing
critical paths have had tests removed but the matrix still shows
them as covered.

The substrate-aligned remediation: treat the matrix as code
under version control with a PR-time check that each new
critical-path-touching change either updates the matrix or
flags the path as not requiring matrix coverage with rationale.

## Anti-pattern G: gap tracking without remediation

```markdown
| Path | Happy | Error | Edge | Security |
| ---- | ----- | ----- | ---- | -------- |
| /auth/login | ✓ | ◯ (issue-12) | ◯ (issue-13) | ◯ (issue-14) |
| /auth/logout | ✓ | ◯ (issue-25) | ◯ (issue-26) | ◯ (issue-27) |
| /payments | ✓ | ◯ (issue-40) | ◯ (issue-41) | ◯ (issue-42) |
```

Issues 12-42 were opened a year ago. None has been resolved.
The matrix's "gap tracking" has degraded into a stale ticket
list. The substrate-aligned response: issues with target dates;
quarterly review of stale gap tickets; a forcing function that
prevents indefinite ◯ accumulation.

## Why these forms appear

- Coverage metrics are easy to optimize for; critical-path
  coverage is qualitative and requires discipline.
- Happy paths are easier to write than error paths.
- Security probes require understanding the substrate's L1 rules
  and the application's threat model.
- Edge cases multiply by combinatorial explosion; teams choose
  representative cases without a systematic approach.

## Substrate-aligned remediation pattern

For each critical path: identify the substrate L1 rules from
adjacent concerns that apply; author at least one test per
(path, applicable L1 rule); catalog the path; track the matrix
as code; review the matrix at PR time when critical paths
change.
