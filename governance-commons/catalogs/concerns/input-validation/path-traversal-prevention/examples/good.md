<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.path-traversal-prevention path traversal prevention

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python pathlib with resolve and is_relative_to

```python
from pathlib import Path

BASE_DIR = Path("/var/app/uploads").resolve()

def read_upload(filename: str) -> bytes:
    # Construct the candidate path, resolve to canonical form,
    # then verify containment.
    candidate = (BASE_DIR / filename).resolve()
    if not candidate.is_relative_to(BASE_DIR):
        raise ValueError("path traversal blocked")
    return candidate.read_bytes()
```

`is_relative_to` (Python 3.9+) performs the prefix check
correctly, accounting for the OS separator.

## Pattern B: Python with os.path.realpath plus prefix comparison

```python
import os

BASE_DIR = os.path.realpath("/var/app/uploads")

def read_upload(filename: str) -> bytes:
    candidate = os.path.realpath(os.path.join(BASE_DIR, filename))
    # Compare with the trailing separator to avoid matching
    # paths like "/var/app/uploads_other/...".
    if not candidate.startswith(BASE_DIR + os.sep):
        raise ValueError("path traversal blocked")
    with open(candidate, "rb") as f:
        return f.read()
```

## Pattern C: Node.js with path.resolve and startsWith

```javascript
const path = require('path');
const fs = require('fs/promises');

const BASE_DIR = path.resolve('/var/app/uploads');

async function readUpload(filename) {
  const candidate = path.resolve(BASE_DIR, filename);
  if (!candidate.startsWith(BASE_DIR + path.sep)) {
    throw new Error('path traversal blocked');
  }
  return await fs.readFile(candidate);
}
```

## Pattern D: Java File.getCanonicalPath with prefix check

```java
public class UploadReader {
    private static final File BASE_DIR;
    static {
        try {
            BASE_DIR = new File("/var/app/uploads").getCanonicalFile();
        } catch (IOException e) {
            throw new ExceptionInInitializerError(e);
        }
    }

    public byte[] readUpload(String filename) throws IOException {
        File candidate = new File(BASE_DIR, filename).getCanonicalFile();
        if (!candidate.getPath().startsWith(BASE_DIR.getPath() + File.separator)) {
            throw new SecurityException("path traversal blocked");
        }
        return Files.readAllBytes(candidate.toPath());
    }
}
```

## Pattern E: Go filepath.Clean plus prefix check

```go
import (
    "errors"
    "os"
    "path/filepath"
    "strings"
)

var baseDir, _ = filepath.Abs("/var/app/uploads")

func ReadUpload(filename string) ([]byte, error) {
    candidate := filepath.Join(baseDir, filename)
    resolved, err := filepath.Abs(candidate)
    if err != nil {
        return nil, err
    }
    if !strings.HasPrefix(resolved, baseDir+string(filepath.Separator)) {
        return nil, errors.New("path traversal blocked")
    }
    return os.ReadFile(resolved)
}
```

## Pattern F: Allowlisted file names (strongest control)

```python
ALLOWED_DOWNLOADS = {
    "user-guide": "/var/app/docs/user-guide.pdf",
    "terms": "/var/app/docs/terms.pdf",
    "privacy": "/var/app/docs/privacy.pdf",
}

def download_doc(key: str):
    path = ALLOWED_DOWNLOADS.get(key)
    if path is None:
        raise ValueError(f"unknown document: {key}")
    return send_file(path)
```

When the user input selects from a closed set, the allowlist
match before any path construction is the substrate-recommended
strongest control.
