<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.account-lockout lockout policy (good patterns)

## Pattern A: Time-bounded lockout with Redis (Python)

```python
import redis
from datetime import datetime, timedelta

class LockoutTracker:
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    COUNTER_WINDOW = timedelta(minutes=15)

    def __init__(self, redis_client):
        self.redis = redis_client

    def record_failure(self, account_id):
        key = f"lockout:failures:{account_id}"
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, int(self.COUNTER_WINDOW.total_seconds()))
        if count >= self.LOCKOUT_THRESHOLD:
            self._set_lockout(account_id)

    def record_success(self, account_id):
        self.redis.delete(f"lockout:failures:{account_id}")
        self.redis.delete(f"lockout:active:{account_id}")

    def is_locked(self, account_id):
        return self.redis.exists(f"lockout:active:{account_id}")

    def _set_lockout(self, account_id):
        key = f"lockout:active:{account_id}"
        self.redis.set(
            key,
            datetime.utcnow().isoformat(),
            ex=int(self.LOCKOUT_DURATION.total_seconds()),
        )
        audit_log.lockout_triggered(
            account_id=account_id,
            duration_minutes=self.LOCKOUT_DURATION.total_seconds() / 60,
        )

# Usage in login handler
def login(username, password):
    user = lookup_user(username)
    if user is None:
        # Verify against dummy hash to time-equalize per authentication.generic-failure-responses
        password_hasher.verify(DUMMY_HASH, password)
        return generic_auth_failure()

    if lockout_tracker.is_locked(user.id):
        # Lockout response is identical to standard failure per
        # authentication.generic-failure-responses (does not signal lockout state to client).
        return generic_auth_failure()

    try:
        password_hasher.verify(user.password_hash, password)
    except VerifyMismatchError:
        lockout_tracker.record_failure(user.id)
        return generic_auth_failure()

    lockout_tracker.record_success(user.id)
    return issue_session(user)


def password_reset_complete(reset_token, new_password):
    user = consume_reset_token(reset_token)
    if user is None:
        return generic_failure()
    user.password_hash = hash_password(new_password)
    # Password reset clears any lockout state.
    lockout_tracker.record_success(user.id)
    db.commit()
    return success_response()
```

Why this satisfies authentication.account-lockout:
- Lockout duration is 15 minutes (within substrate range)
- Counter window expires independently (sliding window)
- Successful password reset clears lockout
- Lockout response is identical to standard auth failure
- Audit logging on lockout events

## Pattern B: Lockout with progressive escalation (Node.js)

```javascript
class LockoutPolicy {
  constructor(redis) {
    this.redis = redis;
  }

  // Substrate-recommended baseline; tune per risk profile
  async recordFailure(accountId) {
    const key = `lockout:fail:${accountId}`;
    const count = await this.redis.incr(key);
    if (count === 1) await this.redis.expire(key, 900);

    let lockoutMinutes = 0;
    if (count === 5) lockoutMinutes = 15;
    else if (count === 10) lockoutMinutes = 30;
    else if (count >= 15) lockoutMinutes = 60;  // ceiling per substrate

    if (lockoutMinutes > 0) {
      await this.redis.set(
        `lockout:active:${accountId}`,
        Date.now(),
        "EX", lockoutMinutes * 60,
      );
      await auditLog.lockoutTriggered({accountId, durationMinutes: lockoutMinutes});
    }
  }

  async clearOnSuccess(accountId) {
    await this.redis.del(`lockout:fail:${accountId}`);
    await this.redis.del(`lockout:active:${accountId}`);
  }

  async isLocked(accountId) {
    return Boolean(await this.redis.exists(`lockout:active:${accountId}`));
  }
}
```

Why this satisfies authentication.account-lockout:
- Bounded lockout durations (15/30/60 minutes)
- Even at maximum, the lockout self-clears within an hour
- Successful auth or password reset clears state

## Pattern C: Spring Security with custom AuthenticationFailureHandler (Java)

```java
@Component
public class LockoutAwareAuthenticationFailureHandler implements AuthenticationFailureHandler {
    private static final int THRESHOLD = 5;
    private static final Duration LOCKOUT = Duration.ofMinutes(15);

    private final StringRedisTemplate redis;
    private final AuditLog auditLog;

    @Override
    public void onAuthenticationFailure(
        HttpServletRequest request,
        HttpServletResponse response,
        AuthenticationException exception
    ) throws IOException {
        String username = request.getParameter("username");
        if (username != null) {
            String failKey = "lockout:fail:" + username;
            Long count = redis.opsForValue().increment(failKey);
            redis.expire(failKey, LOCKOUT);

            if (count >= THRESHOLD) {
                String lockKey = "lockout:active:" + username;
                redis.opsForValue().set(lockKey, Instant.now().toString(), LOCKOUT);
                auditLog.lockoutTriggered(username, LOCKOUT.toMinutes());
            }
        }

        // Send generic 401 response per authentication.generic-failure-responses
        response.sendError(HttpStatus.UNAUTHORIZED.value(), "Invalid credentials");
    }
}
```

Why this satisfies authentication.account-lockout:
- Redis-backed state shared across replicas
- Generic 401 response
- Audit logging

## Cross-reference

- Substrate rule: authentication.account-lockout in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Anti-patterns: examples/authentication/lockout-policy-anti-pattern.md
