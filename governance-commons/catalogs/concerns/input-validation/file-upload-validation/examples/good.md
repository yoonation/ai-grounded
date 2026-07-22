<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: input-validation.file-upload-validation file upload validation

Substrate-original good patterns. Adapt to your stack.

## Pattern A: FastAPI upload with magic-byte verification and size limit

```python
import magic
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()
# Parser-level size limit configured via Starlette / Uvicorn.
# Application also rejects above its own threshold.

ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB

@app.post("/avatars")
async def upload_avatar(file: UploadFile = File(...)):
    # Declared Content-Type allowlist check
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "content-type not permitted")

    # Read with size cap
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "file too large")

    # Magic-byte verification: content must match declaration
    detected = magic.from_buffer(data, mime=True)
    if detected != file.content_type:
        raise HTTPException(400, "content does not match declared type")

    # Server-generated storage key; client filename only in
    # metadata.
    storage_key = f"{uuid.uuid4()}{ALLOWED_TYPES[file.content_type]}"
    await object_storage.put(
        bucket="user-uploads",
        key=storage_key,
        body=data,
        content_type=file.content_type,
        content_disposition=f'attachment; filename="{sanitize_filename(file.filename)}"',
    )
    return {"storage_key": storage_key}

def sanitize_filename(name: str) -> str:
    # Strip path separators, null bytes, control characters.
    clean = re.sub(r"[\x00-\x1f\x7f/\\]", "_", name or "upload")
    return clean[:120]
```

## Pattern B: Express with multer and file-type detection

```javascript
const multer = require('multer');
const FileType = require('file-type');
const crypto = require('crypto');

const ALLOWED_MIME = new Set(['image/jpeg', 'image/png', 'image/webp']);
const MAX_BYTES = 10 * 1024 * 1024;

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: MAX_BYTES },
  fileFilter: (req, file, cb) => {
    if (!ALLOWED_MIME.has(file.mimetype)) {
      return cb(new Error('content-type not permitted'));
    }
    cb(null, true);
  },
});

app.post('/avatars', upload.single('file'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });

  // Magic-byte verification
  const detected = await FileType.fromBuffer(req.file.buffer);
  if (!detected || detected.mime !== req.file.mimetype) {
    return res.status(400).json({ error: 'content mismatch' });
  }

  const storageKey = `${crypto.randomUUID()}.${detected.ext}`;
  await objectStorage.put(storageKey, req.file.buffer, {
    contentType: req.file.mimetype,
    contentDisposition: `attachment; filename="${sanitize(req.file.originalname)}"`,
  });
  res.json({ storage_key: storageKey });
});
```

## Pattern C: Zip extraction with per-entry containment check

```python
import zipfile
from pathlib import Path

def extract_zip_safely(zip_path: Path, dest_dir: Path) -> list[Path]:
    dest_dir = dest_dir.resolve()
    extracted = []
    with zipfile.ZipFile(zip_path) as zf:
        # Reject decompression bombs by total expanded size.
        total = sum(zi.file_size for zi in zf.infolist())
        if total > 100 * 1024 * 1024:  # 100 MB limit
            raise ValueError("expanded size exceeds limit")

        for member in zf.infolist():
            # Reject absolute paths, drive letters, and ..
            target = (dest_dir / member.filename).resolve()
            if not target.is_relative_to(dest_dir):
                raise ValueError(f"zip-slip blocked: {member.filename}")
            # Reject symlinks
            if member.external_attr >> 28 == 0xA:  # symlink
                raise ValueError(f"symlinks not permitted: {member.filename}")
            zf.extract(member, dest_dir)
            extracted.append(target)
    return extracted
```

## Pattern D: Image processing with bounded dimensions (Pillow)

```python
from PIL import Image
from io import BytesIO

MAX_PIXELS = 50_000_000  # 50 megapixels
MAX_DIMENSION = 8000

def resize_image_safely(data: bytes, max_size: tuple[int, int]) -> bytes:
    with Image.open(BytesIO(data)) as img:
        # Reject bombs before any processing.
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            raise ValueError("image dimensions exceed limit")
        if img.width * img.height > MAX_PIXELS:
            raise ValueError("image pixel count exceeds limit")
        img.thumbnail(max_size)
        out = BytesIO()
        img.save(out, format=img.format or "PNG")
        return out.getvalue()
```
