<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.ssrf-prevention SSRF prevention

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Allowlist + IP resolution check (Python)

```python
import ipaddress
import socket
from urllib.parse import urlparse
import httpx

ALLOWED_HOSTS = {
    "api.payments.example.com",
    "webhook.partner.example",
}

# All private/link-local/loopback/CGNAT ranges across IPv4 + IPv6.
BLOCKED_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # includes IMDS
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),   # CGNAT
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

def assert_outbound_url_safe(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("scheme not permitted")
    host = parsed.hostname
    if host not in ALLOWED_HOSTS:
        raise ValueError(f"host not on allowlist: {host}")
    # Resolve and check every returned address.
    try:
        infos = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise ValueError(f"dns resolution failed: {e}")
    for family, _, _, _, sockaddr in infos:
        ip = ipaddress.ip_address(sockaddr[0])
        for blocked in BLOCKED_RANGES:
            if ip in blocked:
                raise ValueError(f"resolved to blocked range: {ip}")
    return url

def safe_fetch(url: str, timeout_s: float = 5.0) -> httpx.Response:
    assert_outbound_url_safe(url)
    # Disable redirects so each hop can be re-validated.
    with httpx.Client(follow_redirects=False, timeout=timeout_s) as client:
        return client.get(url)

def follow_with_revalidation(url: str, max_redirects: int = 3) -> httpx.Response:
    for _ in range(max_redirects + 1):
        resp = safe_fetch(url)
        if resp.is_redirect:
            url = resp.headers["location"]
            # Loop back to assert_outbound_url_safe on the new URL.
            continue
        return resp
    raise ValueError("too many redirects")
```

## Pattern B: Node.js outbound with allowlist (axios + custom agent)

```javascript
const dns = require('dns').promises;
const net = require('net');
const ipaddr = require('ipaddr.js');
const axios = require('axios');

const ALLOWED_HOSTS = new Set([
  'api.payments.example.com',
  'webhook.partner.example',
]);

function isPrivate(ip) {
  const addr = ipaddr.parse(ip);
  const range = addr.range();
  return ['private', 'loopback', 'linkLocal', 'uniqueLocal',
    'reserved', 'carrierGradeNat'].includes(range);
}

async function assertOutboundUrlSafe(rawUrl) {
  const url = new URL(rawUrl);
  if (!['http:', 'https:'].includes(url.protocol)) {
    throw new Error('scheme not permitted');
  }
  if (!ALLOWED_HOSTS.has(url.hostname)) {
    throw new Error(`host not allowlisted: ${url.hostname}`);
  }
  const records = await dns.lookup(url.hostname, { all: true });
  for (const { address } of records) {
    if (isPrivate(address)) {
      throw new Error(`resolved to private: ${address}`);
    }
  }
  return rawUrl;
}

async function safeFetch(url, opts = {}) {
  await assertOutboundUrlSafe(url);
  return axios.get(url, {
    maxRedirects: 0,
    timeout: 5000,
    ...opts,
  });
}
```

## Pattern C: AWS IMDSv2 enforcement at instance level

```hcl
# Terraform: require IMDSv2 (session token) on all EC2 instances.
# Prevents SSRF-driven access to instance metadata even if
# application-layer URL filtering is bypassed.
resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = "t3.medium"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"   # IMDSv2 only
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }
}
```

## Pattern D: Java outbound with SSRFGuard pattern

```java
public class SafeHttpClient {
    private static final Set<String> ALLOWED_HOSTS = Set.of(
        "api.payments.example.com",
        "webhook.partner.example"
    );

    public HttpResponse<String> get(String urlStr) throws Exception {
        URI uri = URI.create(urlStr);
        if (!Set.of("http", "https").contains(uri.getScheme())) {
            throw new SecurityException("scheme not permitted");
        }
        if (!ALLOWED_HOSTS.contains(uri.getHost())) {
            throw new SecurityException("host not allowlisted");
        }
        InetAddress[] addrs = InetAddress.getAllByName(uri.getHost());
        for (InetAddress addr : addrs) {
            if (addr.isAnyLocalAddress() || addr.isLoopbackAddress()
                || addr.isLinkLocalAddress() || addr.isSiteLocalAddress()
                || addr.getHostAddress().startsWith("169.254")) {
                throw new SecurityException("resolved to blocked range");
            }
        }
        HttpClient client = HttpClient.newBuilder()
            .followRedirects(HttpClient.Redirect.NEVER)
            .connectTimeout(Duration.ofSeconds(5))
            .build();
        return client.send(HttpRequest.newBuilder(uri)
            .timeout(Duration.ofSeconds(10))
            .build(), HttpResponse.BodyHandlers.ofString());
    }
}
```
