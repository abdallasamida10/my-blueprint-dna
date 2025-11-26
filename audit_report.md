# Technical Due Diligence Audit
**Project:** MyBlueprint MVP
**Date:** 2025-11-27

## Executive Summary
The current MVP demonstrates functional core logic but contains critical security and scalability flaws that would prevent a successful due diligence process for a SaaS acquisition or investment.

## Critical Findings

### 1. Security Vulnerability: Unrestricted File Upload & Path Traversal
**Severity:** High
**Location:** `server/main.py:26`
```python
file_location = f"uploads/{file.filename}"
```
**Issue:** The application uses the user-provided `filename` directly without sanitization. A malicious actor could upload a file named `../../script.sh` to execute code or overwrite system files (Path Traversal). Additionally, there is no validation of the file content type (magic bytes), allowing executables to be uploaded.
**Remediation:** Generate a unique UUID for the filename (e.g., `uuid.uuid4()`) and validate the file extension/MIME type before saving.

### 2. Security Vulnerability: Permissive CORS Configuration
**Severity:** Medium
**Location:** `server/main.py:14`
```python
allow_origins=["*"]
```
**Issue:** Allowing all origins (`*`) enables Cross-Origin Resource Sharing from any malicious website. This exposes the API to CSRF-like attacks if authentication cookies were added later, and allows unauthorized frontends to consume your API quota.
**Remediation:** Restrict `allow_origins` to the specific Netlify domain (e.g., `["https://my-blueprint.netlify.app"]`) and `localhost` for development.

### 3. Scalability Code Smell: In-Memory File Processing
**Severity:** Medium
**Location:** `server/analysis_engine.py:23`
```python
self.user_df = pd.read_csv(self.file_path, ...)
```
**Issue:** The application loads the entire genomic file into RAM. While acceptable for 23andMe text files (~20MB), full VCF files can be 1GB+. This will cause Out-Of-Memory (OOM) crashes on the Render Free Tier (512MB RAM limit) as user load increases.
**Remediation:** Implement a streaming/chunked processing pipeline. Use `pd.read_csv(chunksize=1000)` to process the file in blocks, filter for relevant markers, and discard the rest immediately, keeping memory usage constant regardless of file size.
