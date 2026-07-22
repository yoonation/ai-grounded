<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.deserialization-safe-loaders deserialization safe loaders

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Configuration with version field and schema validation

```python
import yaml
from pydantic import BaseModel, Field, ValidationError

SUPPORTED_CONFIG_VERSIONS = {"2.0"}

class AppConfig(BaseModel):
    model_config = {"extra": "forbid"}  # reject unknown keys

    version: str
    log_level: str = Field(pattern=r"^(debug|info|warn|error)$")
    listen_port: int = Field(ge=1, le=65535)
    database_url: str

def load_config(path: str) -> AppConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict) or raw.get("version") not in SUPPORTED_CONFIG_VERSIONS:
        raise RuntimeError(
            f"config version not supported: {raw.get('version')}"
        )
    try:
        return AppConfig(**raw)
    except ValidationError as e:
        raise RuntimeError(f"config validation failed: {e}") from e
```

Safe loader (yaml.safe_load), version check, schema validation,
fail-closed on any error.

## Pattern B: PyTorch model load with hash verification and weights_only

```python
import hashlib
import torch

EXPECTED_MODEL_HASH = "sha256:abc123..."  # pinned in source

def load_classifier(model_path: str):
    # Verify hash before load.
    with open(model_path, "rb") as f:
        digest = hashlib.sha256()
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    actual = f"sha256:{digest.hexdigest()}"
    if actual != EXPECTED_MODEL_HASH:
        raise RuntimeError(f"model hash mismatch: {actual}")

    # weights_only=True (PyTorch 1.13+) prevents pickle's code-
    # execution hooks at load time.
    state_dict = torch.load(model_path, weights_only=True)
    model = ClassifierArch()
    model.load_state_dict(state_dict)
    model.eval()
    return model
```

## Pattern C: Safetensors model format (no code execution by design)

```python
from safetensors.torch import load_file

def load_safetensors_model(path: str):
    # safetensors format does not support arbitrary Python
    # code, only tensor data. Loading is structurally safe
    # without weights_only or filter.
    state_dict = load_file(path)
    model = ClassifierArch()
    model.load_state_dict(state_dict)
    return model
```

## Pattern D: XML loading with external entity expansion disabled

```python
from defusedxml import ElementTree as ET

def parse_xml_safely(xml_bytes: bytes) -> ET.Element:
    # defusedxml disables external entity expansion, parameter
    # entity expansion, and DTD retrieval by default.
    return ET.fromstring(xml_bytes)
```

For Java, use `XMLInputFactory.setProperty(
"javax.xml.stream.isSupportingExternalEntities", false)` plus
`setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "")` and
`ACCESS_EXTERNAL_SCHEMA`.

## Pattern E: JSON loading with schema validation (Node.js)

```javascript
const Ajv = require('ajv');
const fs = require('fs');

const configSchema = {
  type: 'object',
  required: ['version', 'log_level', 'listen_port'],
  additionalProperties: false,
  properties: {
    version: { const: '2.0' },
    log_level: { enum: ['debug', 'info', 'warn', 'error'] },
    listen_port: { type: 'integer', minimum: 1, maximum: 65535 },
    database_url: { type: 'string', format: 'uri' },
  },
};

function loadConfig(path) {
  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(configSchema);
  const raw = JSON.parse(fs.readFileSync(path, 'utf8'));
  if (!validate(raw)) {
    throw new Error(`config validation failed: ${JSON.stringify(validate.errors)}`);
  }
  return raw;
}
```

## Pattern F: Fail-closed on load failure

```python
def main():
    try:
        config = load_config("/etc/app/config.yaml")
    except RuntimeError as e:
        # Fail closed: do not start with default or partial config.
        print(f"FATAL: configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    run_application(config)
```
