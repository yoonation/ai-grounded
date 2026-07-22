<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.ssrf-prevention SSRF prevention (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: requests.get(user_url) with no validation

```python
import requests

# FORBIDDEN: user-supplied URL fetched directly. Attacker
# submits http://169.254.169.254/latest/meta-data/iam/...
# and the application returns AWS instance credentials.
@app.route("/fetch")
def fetch_url_BAD():
    target = request.args.get("url")
    return requests.get(target).text
```

Why this violates input-validation.ssrf-prevention:
- No allowlist; any URL is accepted
- No IP resolution check; metadata service is reachable
- Default redirect-follow; redirects to private hosts succeed
- No timeout; slow connections exhaust workers
- Canonical CWE-918 SSRF

## Anti-pattern B: Regex-only URL check (bypassed by redirects)

```javascript
// FORBIDDEN: regex catches some bad URLs but does not handle
// DNS rebinding, IPv6-mapped IPv4, or redirect chains.
function fetchIfPublicBAD(url) {
  if (/^https:\/\/(api|webhook)\.partner\.example\//.test(url)) {
    return axios.get(url);  // default follow-redirects=true
  }
  throw new Error('not allowed');
}
// Attack: partner.example redirects to 10.0.0.5/admin
// Axios follows; SSRF achieved.
```

## Anti-pattern C: Denylist instead of allowlist

```python
# FORBIDDEN: denylist misses internal hosts the operator
# didn't anticipate. New internal services or cloud-provider
# metadata endpoints (Azure, GCP, OCI variants) bypass it.
BLOCKED = {"localhost", "127.0.0.1", "169.254.169.254"}

def fetch_BAD(url):
    host = urlparse(url).hostname
    if host in BLOCKED:
        raise ValueError("blocked")
    return requests.get(url)  # everything else is fair game
```

## Anti-pattern D: Hostname check without IP resolution

```python
# FORBIDDEN: hostname check is bypassed by DNS rebinding.
# Attacker controls a domain that resolves to a public IP at
# validation time and a private IP at request time.
def fetch_BAD(url):
    host = urlparse(url).hostname
    if not host.endswith(".partner.example"):
        raise ValueError("blocked")
    return requests.get(url)
```

## Anti-pattern E: Following redirects without re-validation

```python
# FORBIDDEN: initial URL is allowlisted; redirect target
# is not re-checked. Public 302 service redirects to
# 169.254.169.254 and the metadata is exfiltrated.
def fetch_BAD(url):
    if urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("blocked")
    return requests.get(url, allow_redirects=True)  # no per-hop check
```

## Anti-pattern F: AWS instance with IMDSv1 enabled

```hcl
# FORBIDDEN: http_tokens=optional permits IMDSv1, which does
# not require a session token. An SSRF that reaches
# 169.254.169.254 returns credentials without any token.
resource "aws_instance" "app_BAD" {
  ami           = data.aws_ami.app.id
  instance_type = "t3.medium"

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "optional"  # allows IMDSv1
  }
}
```

## Anti-pattern G: No timeout on outbound calls

```python
# FORBIDDEN: default timeout=None (infinite). A slow internal
# service or attacker-controlled slow-response server holds
# the worker indefinitely.
def fetch_BAD(url):
    if urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("blocked")
    return requests.get(url)  # no timeout argument
```

## Why review identifies these

The input-validation.ssrf-prevention review checklist's seven questions flag:
- No explicit allowlist (or denylist used instead)
- No IP resolution check
- Redirects followed without re-validation
- IMDSv2 / metadata service protection missing
- No outbound timeout
- SSRF defenses not tested
- Rejections not logged for audit
