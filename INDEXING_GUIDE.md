# Indexing Guide - GitHub Repositories and PDF Files

This guide shows you how to index GitHub repositories and PDF files for analysis.

## Prerequisites

- Server must be running: `python run_server.py`
- Supabase database schema must be set up (run `schema.sql`)

## Method 1: Index GitHub Repository via API

### Using PowerShell

```powershell
$baseUrl = "http://localhost:8000/api/v1"

# Index a GitHub repository
$body = @{
    repository_path = "https://github.com/username/repository"
    cleanup = $true  # Clean up cloned repo after indexing
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $body -ContentType "application/json"
```

### Using curl

```bash
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "https://github.com/username/repository",
    "cleanup": true
  }'
```

### Example GitHub URLs Supported

- `https://github.com/microsoft/vscode`
- `https://github.com/user/repo.git`
- `https://github.com/user/repo` (without .git)

## Method 2: Index PDF File

### Option A: Local PDF File Path

```powershell
$body = @{
    repository_path = "C:\path\to\your\document.pdf"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $body -ContentType "application/json"
```

### Option B: Upload PDF File (Multipart)

```powershell
$filePath = "C:\path\to\your\document.pdf"
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileName = [System.IO.Path]::GetFileName($filePath)

$boundary = [System.Guid]::NewGuid().ToString()
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: application/pdf",
    "",
    [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes),
    "--$boundary--"
) -join "`r`n"

Invoke-RestMethod -Uri "$baseUrl/index/file" -Method Post `
    -ContentType "multipart/form-data; boundary=$boundary" `
    -Body ([System.Text.Encoding]::GetEncoding('iso-8859-1').GetBytes($bodyLines))
```

## Method 3: Index Local Repository

```powershell
$body = @{
    repository_path = "C:\path\to\local\repository"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $body -ContentType "application/json"
```

## Testing After Indexing

### 1. Ask a Question

```powershell
$questionBody = @{
    question = "What is the main architecture of this system?"
    max_results = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $questionBody -ContentType "application/json"
```

### 2. Validate a Change Request

```powershell
$changeBody = @{
    description = "Add support for OAuth2 authentication"
    feature_type = "new_feature"
    target_modules = @("auth", "security")
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/validate" -Method Post -Body $changeBody -ContentType "application/json"
```

### 3. Full Analysis

```powershell
$analysisBody = @{
    description = "Add new payment processing module"
    feature_type = "new_feature"
    target_modules = @("payment", "billing")
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/analyze" -Method Post -Body $analysisBody -ContentType "application/json"
```

## Response Format

All indexing endpoints return:

```json
{
  "status": "success",
  "message": "Successfully indexed: https://github.com/user/repo",
  "source": "GitHub URL"
}
```

## Notes

- **GitHub Cloning**: Large repositories may take several minutes to clone and index
- **PDF Files**: PDFs are automatically parsed and chunked for embedding
- **Cleanup**: Set `cleanup: true` to automatically remove cloned repositories after indexing
- **Multiple Indexes**: You can index multiple repositories/PDFs - they will all be stored in the same vector database

## Troubleshooting

### "Failed to clone repository"
- Check your internet connection
- Verify the GitHub URL is correct and public
- Ensure Git is installed on your system

### "No documents found to index"
- Check that the repository contains code files
- Verify file permissions
- Check server logs for specific errors

### "Failed to index PDF"
- Ensure the PDF is not password-protected
- Check that the file path is correct
- Verify the PDF is not corrupted

## Quick Test Script

Run the test script:

```powershell
.\test_index.ps1
```

This will test indexing a sample GitHub repository (you can modify the URL in the script).

