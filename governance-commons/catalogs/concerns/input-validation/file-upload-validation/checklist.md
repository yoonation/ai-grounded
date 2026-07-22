---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.file-upload-validation-file-upload-validation"
title: "input-validation.file-upload-validation review checklist: file upload validation"
substrate-rule: "input-validation.file-upload-validation"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add or modify file-upload endpoints"
  - "Code changes that touch multipart parsing or file storage logic"
  - "Code changes that integrate new file-processing libraries (image resize, document parsers, archive extractors)"
  - "Periodic input-validation self-assessment"
---

# input-validation.file-upload-validation review checklist: file upload validation

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block
merge.

This checklist covers the five validation steps that file-upload
endpoints require: Content-Type allowlist, magic-byte content
verification, size limit at the parser, isolated storage location,
and content-processor hardening. Each step defeats a different
attack class; partial implementation leaves exploitable gaps.

## Review questions

### 1. Content-Type allowlist: is there an explicit list of accepted types?

Confirm that the endpoint has an explicit allowlist of accepted
Content-Type values. The allowlist is declared in code or in
schema metadata; it is not implicit in the application's handling.

What good looks like: the upload endpoint declares an allowed set
(e.g., ["image/jpeg", "image/png", "image/webp"] for an avatar
endpoint); requests with other Content-Type values are rejected
with a structured error.

What needs follow-up: the endpoint accepts any Content-Type;
file-type filtering relies on file extension alone; the allowlist
is implicit in the application's downstream processing.

### 2. Magic-byte verification: is declared type cross-checked against content?

Confirm that the actual file content's magic bytes are inspected
and matched against the declared Content-Type. A client cannot
declare Content-Type: image/png while uploading an executable; the
magic-byte check rejects the mismatch.

What good looks like: the endpoint uses libmagic (python-magic),
file-type (Node.js), Apache Tika (Java), or equivalent to detect
the actual format; the detected format must match the declared
Content-Type for the upload to proceed.

What needs follow-up: the application trusts the client's
Content-Type declaration without verification; magic-byte
inspection is missing; type mismatch is detected later by a
downstream processor (or not at all).

### 3. Size limit at parser: is the multipart parser size-bounded?

Confirm that the maximum upload size is enforced at the multipart
parser level rather than at the application level. Parser-level
enforcement rejects oversized streams without buffering them
completely; application-level enforcement requires reading the
full payload into memory before checking.

What good looks like: the framework's max-upload-size configuration
is set (Flask MAX_CONTENT_LENGTH, FastAPI / Starlette upload
limit, Spring multipart.max-file-size, Rails ActiveStorage size
limit); the limit is documented per endpoint where it differs
from the application-wide default.

What needs follow-up: the application reads the entire upload
into memory before checking size; oversized uploads consume
server memory before rejection; the size limit is not enforced
at all.

### 4. Storage isolation: are uploads stored outside web-executable paths?

Confirm that uploaded files are stored in a location that is not
executable as scripts. Object storage (S3, GCS, Azure Blob) with
explicit Content-Type override and Content-Disposition: attachment
is the substrate-recommended pattern. Local file system storage
must be outside any web-server document root.

What good looks like: uploads go to a configured storage backend
(object storage bucket or non-web-served file system path);
served files include Content-Type and Content-Disposition headers
that force download rather than browser rendering of scripts; the
storage path is documented.

What needs follow-up: uploads are stored inside the web root;
uploaded files can be retrieved at their original filename and
rendered as scripts; Content-Type and Content-Disposition are not
explicitly set on the serving response.

### 5. Filename handling: are uploaded filenames sanitized?

Confirm that the client-supplied filename is sanitized before
being used in the storage path or in downstream operations.
Path-traversal characters (../), null bytes, and reserved
characters are stripped or rejected. The substrate-recommended
pattern is to use a server-generated identifier as the storage
key and to preserve the client filename only in metadata.

What good looks like: the storage key is a server-generated UUID
or hash; the client filename is preserved in metadata for
download attribution but not in the file system path; downstream
operations on the filename apply the path-traversal-prevention
pattern (input-validation.path-traversal-prevention).

What needs follow-up: client filenames flow into storage paths
without sanitization; path-traversal characters in filenames can
break storage layout; null bytes truncate the stored filename
unexpectedly.

### 6. Content-processor hardening: are downstream parsers safe?

Confirm that when the application processes uploaded content
(image resize, PDF parsing, archive extraction, document
conversion), the processor is hardened against format-specific
parser exploits. The substrate's review attention is on known
exploit classes: ImageMagick CVE history for image processing,
zip-slip and decompression bombs for archive extraction, parser
exploits for PDF rendering.

What good looks like: image processing uses a substrate-recommended
hardened library (Pillow with explicit format limits, sharp for
Node.js with bounded operations); archive extraction uses a
zip-slip-resistant library or explicit per-entry containment
check; PDF parsing uses a substrate-recommended library and
disables JavaScript execution.

What needs follow-up: image processing uses ImageMagick without
policy.xml hardening; archive extraction uses naive zip-extract
without per-entry containment; PDF parsing uses a library with
JavaScript execution enabled.

### 7. Serving domain: are uploads served from a sandboxed origin?

Confirm that uploaded files are served from a domain or path that
does not share a session with the application origin. This
defends against active-content disclosure: if a user uploads a
file that contains executable content, serving it from the
application origin exposes session cookies.

What good looks like: uploads are served from a separate domain
(uploads.example.com) or from an object storage URL that does
not include application cookies; the serving origin's CORS
policy prevents cross-origin script access to application data.

What needs follow-up: uploads are served from the application
origin with application cookies in scope; an uploaded HTML file
or SVG with embedded script could access session storage.

## Output

Each question receives GOOD, NEEDS FOLLOW-UP, or NOT APPLICABLE
per the standard checklist output convention.
