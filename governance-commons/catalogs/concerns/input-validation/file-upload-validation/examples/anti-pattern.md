<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.file-upload-validation file upload validation (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Trust the file extension

```python
# FORBIDDEN: filename extension is client-controlled.
# Attacker uploads malicious.php renamed as avatar.jpg, then
# accesses /uploads/avatar.jpg via PHP-FPM mapping.
@app.route("/avatars", methods=["POST"])
def upload_avatar_BAD():
    file = request.files["file"]
    if not file.filename.lower().endswith((".jpg", ".png")):
        return "bad extension", 400
    file.save(f"/var/www/html/uploads/{file.filename}")
    return "ok"
```

Why this violates input-validation.file-upload-validation:
- Extension alone is meaningless; client controls it
- Saves into web-executable directory (web root)
- No magic-byte verification
- Client filename used directly in storage path

## Anti-pattern B: Trust Content-Type header alone

```javascript
// FORBIDDEN: Content-Type header is client-set; no magic-
// byte verification.
app.post('/upload', upload.single('file'), (req, res) => {
  if (req.file.mimetype !== 'image/jpeg') {
    return res.status(400).send('only jpeg');
  }
  fs.writeFileSync(`/var/www/uploads/${req.file.originalname}`, req.file.buffer);
  res.send('ok');
});
```

## Anti-pattern C: No size limit at parser

```python
# FORBIDDEN: framework loads the entire payload into memory
# before the handler can check size. A 10 GB upload exhausts
# server memory.
@app.route("/upload", methods=["POST"])
def upload_BAD():
    file = request.files["file"]  # Flask reads to memory or temp
    data = file.read()
    if len(data) > 10 * 1024 * 1024:
        return "too big", 413  # too late
    # ...
```

The substrate-recommended pattern sets the parser-level limit
(Flask MAX_CONTENT_LENGTH) so the framework rejects oversized
streams without buffering.

## Anti-pattern D: Filename flows into storage path

```ruby
# FORBIDDEN: client filename used as storage key. Path-
# traversal characters or null bytes can escape the upload
# directory or truncate the stored name.
def upload_BAD
  uploaded = params[:file]
  File.open("/var/app/uploads/#{uploaded.original_filename}", 'wb') do |f|
    f.write(uploaded.read)
  end
end
```

## Anti-pattern E: Upload directory inside web root

```nginx
# FORBIDDEN: uploads served by the same nginx that may execute
# scripts. An uploaded .php / .jsp / .aspx file becomes
# executable. Even .html with embedded script runs in the
# application origin.
location /uploads/ {
  alias /var/www/html/uploads/;
}
```

## Anti-pattern F: Zip extraction without containment

```python
# FORBIDDEN: zipfile.extractall does not prevent zip-slip.
# An archive entry named "../../etc/cron.d/evil" writes
# outside the destination directory.
def extract_BAD(zip_path, dest):
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)  # no per-entry check
```

## Anti-pattern G: Image processing without bomb defense

```python
# FORBIDDEN: PIL opens the image without dimension or pixel-
# count limits. A 1KB PNG with declared 64000x64000 dimensions
# expands to multi-GB on decode.
def resize_BAD(data):
    img = Image.open(BytesIO(data))
    img.thumbnail((800, 600))
    out = BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
```

PIL's default decompression-bomb warning is non-fatal; the
substrate-recommended posture is explicit dimension limits.

## Anti-pattern H: Served with same-origin cookies in scope

```nginx
# FORBIDDEN: uploads served from the application domain. An
# uploaded SVG with embedded <script> accesses application
# session cookies.
location /uploads/ {
  alias /var/app/uploads/;
  # No Content-Disposition: attachment header
  # No separate domain
}
```

## Why review identifies these

The input-validation.file-upload-validation review checklist's seven questions flag:
- No Content-Type allowlist
- No magic-byte verification
- Size limit not at parser level
- Storage location is web-executable
- Filename flows into storage path without sanitization
- Content processor (ImageMagick / archive / PDF) unhardened
- Uploads served same-origin without download-forcing headers
