<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.no-unsafe-deserialization no unsafe deserialization (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: pickle.loads on request data (Python / Flask)

```python
import pickle

# FORBIDDEN: pickle.loads on bytes from outside the trust
# boundary. Attacker submits a pickle that constructs an
# arbitrary class with __reduce__ producing os.system("...").
@app.route("/import", methods=["POST"])
def import_data_BAD():
    data = pickle.loads(request.get_data())  # RCE at load time
    return jsonify({"imported": True})
```

Why this violates input-validation.no-unsafe-deserialization:
- pickle's serialized format permits __reduce__ tuples that
  invoke arbitrary callables at load time
- Known gadget chains (PyYAML, Twisted, NumPy) produce RCE
- This is canonical CWE-502

## Anti-pattern B: yaml.load without SafeLoader (Python)

```python
import yaml

# FORBIDDEN: yaml.load (without SafeLoader) interprets the
# !!python/object tag and constructs arbitrary classes.
def load_config_BAD(path):
    with open(path) as f:
        return yaml.load(f)  # accepts !!python/object/apply
```

The PyYAML !!python/object/apply tag constructs an arbitrary
Python object via a class lookup; an attacker producing the
YAML file (configuration via supply chain, templated YAML)
gains RCE.

## Anti-pattern C: ObjectInputStream without filter (Java)

```java
// FORBIDDEN: ObjectInputStream.readObject on untrusted bytes.
// Java deserialization gadget chains (Commons Collections,
// Spring, Hibernate) produce RCE from carefully crafted
// streams.
public Object deserializeBAD(byte[] data) throws Exception {
    try (ObjectInputStream ois = new ObjectInputStream(
            new ByteArrayInputStream(data))) {
        return ois.readObject();  // no filter; RCE risk
    }
}
```

## Anti-pattern D: Marshal.load on user data (Ruby)

```ruby
# FORBIDDEN: Marshal.load constructs arbitrary Ruby objects
# from the byte stream. Same risk profile as pickle.
def import_session_BAD(data)
  Marshal.load(data)
end
```

## Anti-pattern E: PHP unserialize on request data

```php
<?php
// FORBIDDEN: unserialize triggers __wakeup, __destruct, and
// other magic methods on the deserialized objects. Known
// gadget chains across major PHP frameworks produce RCE.
function importSessionBAD($data) {
    return unserialize($data);
}
?>
```

## Anti-pattern F: node-serialize (Node.js)

```javascript
const serialize = require('node-serialize');

// FORBIDDEN: node-serialize.unserialize evaluates embedded
// JavaScript function bodies.
function loadSessionBAD(data) {
    return serialize.unserialize(data);  // arbitrary JS eval
}
```

## Anti-pattern G: torch.load without weights_only (Python ML)

```python
import torch

# FORBIDDEN on cross-boundary models: PyTorch's default load
# uses pickle internally, so arbitrary code can execute when
# loading a model from an untrusted source. weights_only=True
# (PyTorch 1.13+) prevents this; the default is unsafe.
def load_model_BAD(path):
    return torch.load(path)  # implicit weights_only=False
```

## Why mechanical detection fires on all of these

Semgrep registry rules detect:
- pickle.load, pickle.loads call sites
- yaml.load without SafeLoader argument
- ObjectInputStream.readObject without preceding setObjectInputFilter
- Marshal.load with non-constant inputs
- unserialize call sites in PHP
- node-serialize.unserialize invocations
- torch.load without weights_only=True (newer rule)
