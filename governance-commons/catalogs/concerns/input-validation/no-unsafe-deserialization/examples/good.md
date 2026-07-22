<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.no-unsafe-deserialization no unsafe deserialization

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python yaml.safe_load for cross-boundary YAML

```python
import yaml

def load_user_config(path: str) -> dict:
    with open(path, "r") as f:
        # safe_load uses the SafeLoader, which does not include
        # code-execution tags.
        return yaml.safe_load(f)
```

## Pattern B: JSON-only contract for HTTP boundaries (Python)

```python
import json
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

@app.post("/users")
def create_user(request: CreateUserRequest):
    # Body is JSON; Pydantic parses into the typed model.
    # No pickle, no Marshal, no language-native deserialization.
    return UserService.create(request)
```

The wire format is JSON; the parser produces typed values
without invoking any application code.

## Pattern C: Java ObjectInputFilter (JEP 290) when ObjectInputStream is required

```java
import java.io.*;
import java.util.Set;

public class SafeDeserialization {
    private static final ObjectInputFilter FILTER =
        ObjectInputFilter.allowFilter(
            cls -> {
                Set<String> allowed = Set.of(
                    "com.app.dto.AuditEvent",
                    "com.app.dto.UserRecord",
                    "java.util.ArrayList",
                    "java.util.HashMap",
                    "java.lang.String",
                    "java.lang.Long"
                );
                return allowed.contains(cls.getName());
            },
            ObjectInputFilter.Status.REJECTED
        );

    public static Object deserialize(InputStream is) throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(is)) {
            ois.setObjectInputFilter(FILTER);
            return ois.readObject();
        }
    }
}
```

When ObjectInputStream cannot be replaced (legacy interface),
ObjectInputFilter constrains the deserializable class set to an
explicit allowlist.

## Pattern D: Ruby Psych 4+ YAML.load is safe by default

```ruby
require 'yaml'

def load_user_config(path)
  # Psych 4+ (Ruby 3.1+) YAML.load behaves as safe_load by
  # default; older versions need YAML.safe_load explicitly.
  YAML.safe_load(File.read(path), permitted_classes: [Date, Time])
end
```

## Pattern E: PyTorch weights_only loading

```python
import torch

def load_model(path: str):
    # weights_only=True (PyTorch 1.13+) prevents pickle's
    # code-execution hooks from running during load.
    state_dict = torch.load(path, weights_only=True)
    model = ModelArchitecture()
    model.load_state_dict(state_dict)
    return model
```

For PyTorch checkpoints, weights_only=True is the substrate-
recommended pattern. Safetensors format (where the model
producer can choose it) is even stronger: safetensors does not
support arbitrary code execution.

## Pattern F: Node.js JSON-only via Express

```javascript
const express = require('express');
const app = express();

// express.json() parses JSON bodies safely; no node-serialize.
app.use(express.json({ limit: '1mb' }));

app.post('/users', (req, res) => {
  // req.body is a JS object parsed from JSON.
  // Validate with Joi or Zod before use.
  const { error, value } = createUserSchema.validate(req.body);
  if (error) return res.status(400).json({ error: error.message });
  // ... handle creation
});
```
