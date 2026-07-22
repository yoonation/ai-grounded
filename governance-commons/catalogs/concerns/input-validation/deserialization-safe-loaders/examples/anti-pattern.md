<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.deserialization-safe-loaders deserialization safe loaders (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: yaml.load on configuration file

```python
import yaml

# FORBIDDEN: yaml.load interprets !!python/object tags and
# constructs arbitrary classes. A configuration file written
# by deployment tooling with templated content can include
# malicious tags.
def load_config_BAD(path):
    with open(path) as f:
        return yaml.load(f)  # missing SafeLoader
```

Why this violates input-validation.deserialization-safe-loaders:
- The "local config file" is not necessarily trustworthy:
  templated YAML, downloaded YAML, CI-generated YAML may
  carry attacker-controlled content
- yaml.load supports tags that produce RCE at load time
- CWE-502 deserialization risk

## Anti-pattern B: No version check on configuration

```python
# FORBIDDEN: load proceeds regardless of schema generation.
# A new field in v2 config may be silently ignored when the
# code expects v1 fields, producing partial functionality.
def load_config_BAD2(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)
    # No version field check; no schema validation.
    return AppConfig(**cfg)  # may accept stale or future schema
```

## Anti-pattern C: PyTorch torch.load with default weights_only=False

```python
import torch

# FORBIDDEN on cross-boundary models: pickle-based load runs
# embedded code at load time. A model file downloaded from
# a registry (Hugging Face, github releases) may be tampered.
def load_model_BAD(path):
    return torch.load(path)  # default weights_only=False
```

## Anti-pattern D: Silent fallback to default on load error

```python
# FORBIDDEN: load failure falls through to defaults. A
# corrupted config file produces a running application with
# unexpected behavior; security-relevant settings may be off.
def load_config_BAD3(path):
    try:
        with open(path) as f:
            return AppConfig(**yaml.safe_load(f))
    except Exception:
        return AppConfig()  # all defaults, no warning
```

## Anti-pattern E: XML loading with external entities enabled

```python
import xml.etree.ElementTree as ET

# FORBIDDEN: stdlib xml.etree is partially safe but historical
# versions and other parsers (lxml.etree.fromstring,
# xml.sax) need explicit hardening.
def parse_xml_BAD(xml_bytes):
    # XXE attack: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    return ET.fromstring(xml_bytes)
```

Use `defusedxml.ElementTree` instead. lxml requires
`lxml.etree.XMLParser(resolve_entities=False, no_network=True)`.

## Anti-pattern F: No schema validation after deserialization

```python
# FORBIDDEN: parsed values flow into AppConfig without schema
# enforcement; type mismatches or unexpected fields are not
# caught at load time.
def load_config_BAD4(path):
    with open(path) as f:
        raw = yaml.safe_load(f)
    # No Pydantic / JSON Schema / equivalent validation.
    return raw  # raw dict; downstream code accesses keys
```

## Anti-pattern G: ML model loaded from arbitrary URL

```python
# FORBIDDEN: model URL is configuration-driven without
# provenance check. Configuration change (or compromise of
# the configuration source) loads attacker model.
def load_model_BAD2(config):
    response = requests.get(config["model_url"])
    return torch.load(BytesIO(response.content))
```

## Anti-pattern H: Pickle-based session storage exposed to client

```python
# FORBIDDEN: pickle-backed session cookie. Client can craft
# any pickle and the server unpickles on every request.
@app.route("/")
def index_BAD():
    session_data = pickle.loads(
        base64.b64decode(request.cookies.get("session", "")))
    return f"hello {session_data.get('user', 'anonymous')}"
```

## Why review identifies these

The input-validation.deserialization-safe-loaders review checklist's seven questions flag:
- yaml.load without SafeLoader at any call site
- No version validation on configuration
- ML model load without provenance check
- Fail-open on configuration error
- No schema validation after deserialization
- XML loading without XXE protection
- Cross-format coverage gaps
