<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.path-traversal-prevention path traversal prevention (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: os.path.join with user input passed directly to open (Python)

```python
# FORBIDDEN: filename can contain ../ to escape the base dir.
# Attacker submits "../../etc/passwd" and reads it.
def read_upload_BAD(filename):
    path = os.path.join("/var/app/uploads", filename)
    with open(path, "rb") as f:  # no containment check
        return f.read()
```

Why this violates input-validation.path-traversal-prevention:
- os.path.join treats the .. components as ordinary path
  elements
- No canonical resolution; no containment check
- Canonical CWE-22 path traversal

## Anti-pattern B: Flask send_file with request data (Python)

```python
# FORBIDDEN: send_file receives a user-controlled path
# without any containment check.
@app.route("/download/<filename>")
def download_BAD(filename):
    return send_file(f"/var/app/uploads/{filename}")
```

## Anti-pattern C: Node.js path.join with user filename

```javascript
// FORBIDDEN: path.join does not resolve .. and does not
// constrain the result to the base directory.
async function readUploadBAD(filename) {
  const filePath = path.join('/var/app/uploads', filename);
  return await fs.readFile(filePath);
}
```

## Anti-pattern D: Java File constructor without canonicalization

```java
// FORBIDDEN: File constructor accepts the relative path; no
// containment check after construction.
public byte[] readUploadBAD(String filename) throws IOException {
    File f = new File("/var/app/uploads", filename);
    return Files.readAllBytes(f.toPath());
}
```

## Anti-pattern E: Go filepath.Join without containment check

```go
// FORBIDDEN: filepath.Join cleans single-level .. but does
// not prevent escaping the base directory across multiple
// components.
func ReadUploadBAD(filename string) ([]byte, error) {
    p := filepath.Join("/var/app/uploads", filename)
    return os.ReadFile(p)
}
```

## Anti-pattern F: Rails send_file with params-derived path

```ruby
# FORBIDDEN: params[:filename] flows directly into the file
# path. Rails send_file does not enforce containment.
class DownloadsController < ApplicationController
  def show
    send_file "/var/app/uploads/#{params[:filename]}"
  end
end
```

## Anti-pattern G: Containment check applied to the unresolved path

```python
# SUBTLY FORBIDDEN: the containment check operates on the
# constructed (not resolved) path. Encoded traversal
# sequences and symlinks bypass the check.
def read_upload_BAD2(filename):
    base = "/var/app/uploads"
    candidate = os.path.join(base, filename)
    # WRONG ORDER: check before resolve
    if not candidate.startswith(base):
        raise ValueError("blocked")
    candidate = os.path.realpath(candidate)  # too late
    with open(candidate, "rb") as f:
        return f.read()
```

The check must happen AFTER realpath, not before. The pattern
above is a common partial implementation that looks correct.

## Why mechanical detection fires on these patterns

Semgrep registry rules detect:
- open / fs.readFile / File constructor / send_file invocations
  with non-constant path components
- os.path.join with request data flowing into a file operation
  without a realpath check
- Absence of a containment check adjacent to file operations
- Containment check applied before canonicalization (the
  subtle variant)
