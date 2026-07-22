<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.no-remote-execution-in-build remote-execution patterns

Substrate-rejected patterns. Detection by the supply-chain.no-remote-execution-in-build
binding flags each.

## Anti-pattern A: curl-pipe-shell installer

```dockerfile
# Substrate-rejected: code fetched and executed in one step
RUN curl -fsSL https://example.com/install.sh | sh
```

The remote endpoint can substitute the script bytes between two
otherwise-identical builds. The build environment executes
whatever the endpoint returns.

## Anti-pattern B: eval of fetched payload

```bash
# Substrate-rejected: eval-curl variant
eval "$(curl -fsSL https://example.com/setup.sh)"

# Substrate-rejected: bash -c variant
bash -c "$(curl -fsSL https://example.com/init.sh)"
```

## Anti-pattern C: GitHub Actions run block with curl-pipe-shell

```yaml
jobs:
  build:
    steps:
      # Substrate-rejected: pattern executes in privileged CI runner
      - name: Install tool
        run: |
          curl -fsSL https://example.com/tool-installer.sh | sh
          tool build
```

The CI runner typically has access to deployment credentials,
signing keys, and source repositories; substrate-rejected
patterns expose all of these to the network endpoint.

## Anti-pattern D: download-and-execute without integrity check

```bash
# Substrate-rejected: no checksum verification between download
# and execute
curl -fsSL https://example.com/tool -o tool
chmod +x tool
./tool
```

## Anti-pattern E: PowerShell irm-pipe-iex

```powershell
# Substrate-rejected: PowerShell variant of curl-pipe-shell
irm https://example.com/install.ps1 | iex
```

## Anti-pattern F: Python exec-of-fetched-code in build script

```python
# Substrate-rejected: build script fetches and executes Python
# from a remote URL
import urllib.request
exec(urllib.request.urlopen("https://example.com/configure.py").read())
```

## Why these patterns fail

The remote endpoint becomes part of the consumer's trust chain
implicitly. Endpoint compromise (DNS hijack, account takeover,
infrastructure breach) substitutes attacker-controlled code into
the build environment. The substrate-rejected patterns produce
no source-tree evidence of the substitution; the only trail is
in the network logs of the build, which are typically not
retained.
