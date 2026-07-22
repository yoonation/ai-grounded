---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.input-validation.file-upload-validation-file-upload-validation"
title: "input-validation.file-upload-validation test template: file upload validation"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# input-validation.file-upload-validation test template: file upload validation

## How to use this binding

This binding describes test scenarios for file-upload endpoints.
The tests verify the five validation steps (Content-Type
allowlist, magic-byte check, size limit, storage isolation,
content-processor hardening) operate as designed.

## Scenario 1: Permitted Content-Type with matching content accepted

**Preconditions**
- An upload endpoint with a documented allowlist (e.g.,
  ["image/jpeg", "image/png"])
- A test JPEG file with valid magic bytes

**Action**
- Submit the file with Content-Type: image/jpeg

**Expected**
- HTTP 200 (or the endpoint's success status)
- The file is stored at the documented location
- The storage path uses the server-generated identifier, not
  the client filename

## Scenario 2: Mismatched magic bytes rejected

**Preconditions**
- Same upload endpoint as Scenario 1
- A test file with PE executable magic bytes ("MZ" header)
  renamed to file.jpg and declared as Content-Type: image/jpeg

**Action**
- Submit the file

**Expected**
- HTTP 400 (or the endpoint's rejection status)
- Error message identifies the content-type mismatch
- The file is not persisted
- A rejection log entry exists

## Scenario 3: Disallowed Content-Type rejected

**Preconditions**
- Same upload endpoint with Content-Type allowlist
- A valid PDF file declared as Content-Type: application/pdf
  (assume PDFs are not on the allowlist)

**Action**
- Submit the file

**Expected**
- HTTP 400
- Error message identifies the disallowed content-type
- The file is not persisted

## Scenario 4: Oversized upload rejected at parser

**Preconditions**
- The endpoint has a documented size limit (e.g., 10 MB)
- A test file exceeding the limit (e.g., 50 MB)

**Action**
- Begin streaming the file to the endpoint
- Monitor server memory and CPU during the upload

**Expected**
- HTTP 413 (Payload Too Large) or the framework's equivalent
- The server does NOT buffer the entire payload before
  rejecting (verified by monitoring memory)
- The connection is closed early once the limit is exceeded

## Scenario 5: Path-traversal filename rejected or sanitized

**Preconditions**
- An upload endpoint that uses the client filename in some
  capacity (download metadata, internal logging)

**Action**
- Submit a file with filename "../../etc/passwd" or containing
  null bytes

**Expected**
- The filename is sanitized (stripped to "passwd") or rejected
- The storage path does NOT include the traversal characters
- The server-generated storage key is used regardless of the
  client filename

## Scenario 6: Stored files served with safe Content-Type and Content-Disposition

**Preconditions**
- A previously uploaded file is available for retrieval
- The retrieval endpoint serves the file

**Action**
- Retrieve the file
- Inspect response headers

**Expected**
- Response Content-Type matches the declared and verified type
- Content-Disposition: attachment with the (sanitized) filename
- The retrieval is from a sandboxed origin (separate subdomain
  or object storage) per the storage-isolation requirement

## Scenario 7: Zip-slip rejected on archive uploads (if applicable)

**Preconditions**
- The application accepts archive uploads (zip, tar) and
  extracts them
- A test archive with an entry path "../../etc/evil" is
  constructed

**Action**
- Upload the malicious archive

**Expected**
- Extraction is rejected at the entry-path validation step
- No file is created outside the extraction directory
- A log entry records the rejection

## Scenario 8: Image processing parser bombs rejected (if applicable)

**Preconditions**
- The application processes uploaded images (resize, convert)
- A test "decompression bomb" PNG (small file that expands to
  excessive dimensions when decoded) is constructed

**Action**
- Upload the bomb image

**Expected**
- The image processor rejects the bomb (via dimension limits,
  pixel count limits, or library-provided bomb detection)
- The server's memory consumption does not spike excessively
- The endpoint returns a structured error
