<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.rate-limiting rate limiting (good patterns)

Substrate-original good-pattern examples for authentication.rate-limiting.

## Pattern A: Flask-Limiter with Redis backend (Python / Flask)

```python
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Rate limiter with Redis backend for shared state across replicas.
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://redis.internal:6379/0",
    default_limits=[],
)

# Per-IP limit on login: 10 attempts per 15 minutes.
@app.route("/login", methods=["POST"])
@limiter.limit("10 per 15 minutes")
def login():
    body = request.get_json()
    username = body.get("username", "")
    password = body.get("password", "")

    # Per-account rate limit tracked separately, using a
    # username-based key.
    account_key = f"login:account:{username}"
    if account_failures.get(account_key, 0) >= 5:
        return generic_auth_failure()

    user = authenticate(username, password)
    if user is None:
        account_failures.incr(account_key, ttl=900)  # 15 min
        return generic_auth_failure()

    account_failures.delete(account_key)
    return issue_session(user)


@app.route("/password-reset", methods=["POST"])
@limiter.limit("5 per hour")
def password_reset():
    # Generic response per authentication.generic-failure-responses.
    return jsonify({"message": "If the email is registered, a reset link has been sent."})


@app.route("/oauth/token", methods=["POST"])
@limiter.limit("30 per minute")
def token_endpoint():
    return handle_token_request()


@app.errorhandler(429)
def rate_limit_handler(e):
    # Generic 429 response. Same shape regardless of whether
    # credentials would have authenticated.
    response = jsonify({"error": "Too many requests"})
    response.status_code = 429
    response.headers["Retry-After"] = "900"
    return response


def generic_auth_failure():
    return jsonify({"error": "Invalid credentials"}), 401
```

Why this satisfies authentication.rate-limiting:
- Coverage: all three auth endpoints (login, password reset, token) rate-limited
- Granularity: per-IP via Flask-Limiter; per-account via separate counter
- Thresholds: 10/15min login, 5/hour reset, 30/min token (within substrate ranges)
- Storage: Redis shared backend
- Response shape: generic 429 with Retry-After
- Account lockout: per-account counter at 5 with 15-minute TTL

## Pattern B: express-rate-limit with Redis backend (Node.js / Express)

```javascript
const express = require("express");
const rateLimit = require("express-rate-limit");
const RedisStore = require("rate-limit-redis");
const {createClient} = require("redis");

const app = express();
const redis = createClient({url: "redis://redis.internal:6379"});
redis.connect();

const loginLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.sendCommand(args),
  }),
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: "draft-7",
  legacyHeaders: false,
  message: {error: "Too many requests"},
  handler: (req, res) => {
    res.status(429).set("Retry-After", "900").json({error: "Too many requests"});
  },
});

const passwordResetLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.sendCommand(args),
  }),
  windowMs: 60 * 60 * 1000,
  max: 5,
  message: {error: "Too many requests"},
});

const tokenLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.sendCommand(args),
  }),
  windowMs: 60 * 1000,
  max: 30,
  message: {error: "Too many requests"},
});

app.post("/login", loginLimiter, async (req, res) => {
  // Per-account check, in addition to per-IP from middleware.
  const accountFailureKey = `login:account:${req.body.username}`;
  const failures = parseInt(await redis.get(accountFailureKey) || "0");
  if (failures >= 5) {
    return res.status(401).json({error: "Invalid credentials"});
  }

  const user = await authenticate(req.body.username, req.body.password);
  if (!user) {
    await redis.incr(accountFailureKey);
    await redis.expire(accountFailureKey, 900);
    return res.status(401).json({error: "Invalid credentials"});
  }

  await redis.del(accountFailureKey);
  return res.json({session: issueSession(user)});
});

app.post("/password-reset", passwordResetLimiter, async (req, res) => {
  return res.json({message: "If the email is registered, a reset link has been sent."});
});

app.post("/oauth/token", tokenLimiter, async (req, res) => {
  return handleTokenRequest(req, res);
});
```

Why this satisfies authentication.rate-limiting:
- Same coverage and granularity as Pattern A in JavaScript
- Redis store via rate-limit-redis library
- Per-endpoint limit configuration via separate limiter middleware
- Generic 429 response with Retry-After

## Pattern C: Django REST framework throttle classes (Python / DRF)

```python
from rest_framework import throttling, status, views
from rest_framework.response import Response

class LoginIPThrottle(throttling.AnonRateThrottle):
    rate = "10/15min"
    scope = "login_ip"

class LoginAccountThrottle(throttling.SimpleRateThrottle):
    rate = "5/15min"
    scope = "login_account"
    def get_cache_key(self, request, view):
        username = request.data.get("username") if hasattr(request, "data") else None
        if not username:
            return None
        return f"throttle_{self.scope}_{username}"

class LoginView(views.APIView):
    throttle_classes = [LoginIPThrottle, LoginAccountThrottle]

    def post(self, request):
        user = authenticate(request.data.get("username"), request.data.get("password"))
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"session": issue_session(user)})


class PasswordResetThrottle(throttling.AnonRateThrottle):
    rate = "5/hour"
    scope = "password_reset"

class PasswordResetView(views.APIView):
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        return Response({"message": "If the email is registered, a reset link has been sent."})
```

DRF settings ensure cache backend is Redis (or other shared
backend) so throttle state is shared across replicas.

```python
# settings.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis.internal:6379/1",
    }
}
```

Why this satisfies authentication.rate-limiting:
- DRF throttle classes provide both per-IP (AnonRateThrottle) and
  per-account (custom scope) granularity
- Cache backend is Redis, shared across replicas
- 429 response is DRF default with Retry-After header

## Pattern D: Spring Security with Bucket4j (Java)

```java
import io.github.bucket4j.Bucket;
import io.github.bucket4j.distributed.proxy.ProxyManager;
import io.github.bucket4j.redis.lettuce.cas.LettuceBasedProxyManager;
import java.time.Duration;

@Component
public class AuthRateLimitFilter extends OncePerRequestFilter {

    private final ProxyManager<String> proxyManager;

    @Override
    protected void doFilterInternal(
        HttpServletRequest request,
        HttpServletResponse response,
        FilterChain chain) throws IOException, ServletException {

        String path = request.getRequestURI();
        String sourceIP = request.getRemoteAddr();

        Bucket bucket;
        if (path.equals("/login")) {
            bucket = perIpBucket(sourceIP, "login", 10, Duration.ofMinutes(15));
        } else if (path.equals("/password-reset")) {
            bucket = perIpBucket(sourceIP, "reset", 5, Duration.ofHours(1));
        } else if (path.equals("/oauth/token")) {
            bucket = perIpBucket(sourceIP, "token", 30, Duration.ofMinutes(1));
        } else {
            chain.doFilter(request, response);
            return;
        }

        if (bucket.tryConsume(1)) {
            chain.doFilter(request, response);
        } else {
            response.setStatus(429);
            response.setHeader("Retry-After", "900");
            response.getWriter().write("{\"error\":\"Too many requests\"}");
        }
    }

    private Bucket perIpBucket(String ip, String scope, long limit, Duration window) {
        String key = scope + ":" + ip;
        return proxyManager.builder().build(key, () -> BucketConfiguration.builder()
            .addLimit(Bandwidth.classic(limit, Refill.intervally(limit, window)))
            .build());
    }
}
```

Why this satisfies authentication.rate-limiting:
- Distributed Bucket4j with Redis-backed ProxyManager
- Per-endpoint limit configuration
- 429 response with Retry-After

## What good patterns have in common

- Rate-limit middleware applied to ALL authentication endpoints
- Both per-IP and per-account granularities
- Substrate-recommended thresholds or stricter
- Shared backend (Redis is the common choice)
- Generic 429 response with Retry-After, identical regardless of
  authentication outcome

## Cross-reference

- Substrate rule: authentication.rate-limiting in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Anti-patterns: examples/authentication/rate-limiting-anti-pattern.md
