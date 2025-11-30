# API Documentation

Complete API documentation for the Repository Intelligence Backend service.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Endpoints

### 1. Index Repository

Index a GitHub repository, local repository, or file path for analysis.

**Endpoint:** `POST /api/v1/index`

**Content-Type:** `application/json`

#### Request Body

```json
{
  "repository_path": "string (required)",
  "cleanup": "boolean (optional, default: true)"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repository_path` | string | Yes | Path to repository or file. Can be:<br>- GitHub URL: `https://github.com/user/repo`<br>- Local directory: `C:\path\to\repo`<br>- Local file: `C:\path\to\file.pdf` |
| `cleanup` | boolean | No | Whether to cleanup temporary directories after indexing (default: `true`) |

#### Supported Repository Path Formats

1. **GitHub Repository URLs:**
   - `https://github.com/microsoft/vscode`
   - `https://github.com/user/repo.git`
   - `https://github.com/user/repo` (`.git` extension optional)

2. **Local File Paths:**
   - `C:\path\to\document.pdf`
   - `/path/to/document.pdf` (Unix-style)
   - Any supported file format (PDF, text files, etc.)

3. **Local Directory Paths:**
   - `C:\path\to\repository`
   - `/path/to/repository` (Unix-style)

#### Success Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "Successfully indexed: https://github.com/user/repo",
  "source": "GitHub URL"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"success"` for successful requests |
| `message` | string | Descriptive message about what was indexed |
| `source` | string | Type of source: `"GitHub URL"`, `"PDF file"`, or `"Local path"` |

#### Error Responses

**Status Code:** `400 Bad Request`

```json
{
  "error": "repository_path is required"
}
```

```json
{
  "error": "Path does not exist: /invalid/path",
  "hint": "Please provide a valid file or directory path"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "error": "Failed to index repository. Check logs for details.",
  "hint": "Ensure the path is correct and contains indexable files"
}
```

```json
{
  "error": "Indexing failed: <error message>",
  "details": "Check server logs for more information"
}
```

#### Example Requests

**GitHub Repository:**

```bash
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "https://github.com/microsoft/vscode",
    "cleanup": true
  }'
```

**PowerShell:**

```powershell
$body = @{
    repository_path = "https://github.com/microsoft/vscode"
    cleanup = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/index" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**Local PDF File:**

```bash
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "C:\\path\\to\\document.pdf"
  }'
```

**Local Repository:**

```bash
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "C:\\path\\to\\repository"
  }'
```

---

### 2. Index File Upload

Upload and index a file (e.g., PDF) via multipart form data.

**Endpoint:** `POST /api/v1/index/file`

**Content-Type:** `multipart/form-data`

#### Request Body

Form data with a file field:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | The file to upload and index (PDF, text files, etc.) |

#### Success Response

**Status Code:** `200 OK`

```json
{
  "status": "success",
  "message": "Successfully indexed file: document.pdf"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"success"` for successful requests |
| `message` | string | Descriptive message with the filename that was indexed |

#### Error Responses

**Status Code:** `400 Bad Request`

```json
{
  "error": "No file provided"
}
```

```json
{
  "error": "No file selected"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "error": "Failed to index file"
}
```

```json
{
  "error": "Failed to index file: <error message>"
}
```

#### Example Requests

**Using curl:**

```bash
curl -X POST http://localhost:8000/api/v1/index/file \
  -F "file=@/path/to/document.pdf"
```

**Using PowerShell:**

```powershell
$filePath = "C:\path\to\document.pdf"
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

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/index/file" `
    -Method Post `
    -ContentType "multipart/form-data; boundary=$boundary" `
    -Body ([System.Text.Encoding]::GetEncoding('iso-8859-1').GetBytes($bodyLines))
```

**Using Python requests:**

```python
import requests

url = "http://localhost:8000/api/v1/index/file"
files = {'file': open('document.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

**Using JavaScript (fetch):**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/v1/index/file', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## How It Works

### GitHub Repository Indexing Flow

1. **Request received** at `/api/v1/index` endpoint
2. **URL validation** - Checks if the path is a GitHub URL
3. **Repository cloning** - Clones the GitHub repository to a temporary directory using GitPython
4. **Document loading** - Uses `RepositoryLoader` to load and parse all code files
5. **Embedding generation** - Creates vector embeddings for all documents
6. **Vector storage** - Stores embeddings in Supabase vector database
7. **Cleanup** - Removes temporary cloned repository (if `cleanup: true`)

### File Upload Indexing Flow

1. **Request received** at `/api/v1/index/file` endpoint
2. **File extraction** - Extracts uploaded file from multipart form data
3. **Temporary storage** - Saves file to a temporary directory
4. **Document loading** - Uses `RepositoryLoader` to load and parse the file
5. **Embedding generation** - Creates vector embeddings for document chunks
6. **Vector storage** - Stores embeddings in Supabase vector database
7. **Cleanup** - Removes temporary file after indexing

### Backend Components

- **Route Handler:** `src/api/routes.py`
  - `index_repository()` - Handles `/api/v1/index` endpoint
  - `index_file()` - Handles `/api/v1/index/file` endpoint

- **Service Layer:** `src/services/repository_service.py`
  - `RepositoryService.index_repository()` - Core indexing logic

- **GitHub Utilities:** `src/utils/github_clone.py`
  - `clone_github_repo()` - Clones GitHub repositories
  - `is_github_url()` - Detects GitHub URLs

- **Document Loading:** `src/loaders/repository_loader.py`
  - `RepositoryLoader.load_repository()` - Loads and chunks documents

---

## Notes and Best Practices

### GitHub Repository Indexing

- **Large repositories** may take several minutes to clone and index
- **Public repositories** are supported without authentication
- **Private repositories** require authentication (not currently supported)
- The `.git` extension in URLs is optional
- Cloned repositories are stored in temporary directories and cleaned up automatically

### File Upload

- **Supported formats:** PDF, text files, and other formats supported by the document loader
- **File size:** Consider server memory limits for very large files
- **Temporary storage:** Files are automatically cleaned up after indexing
- **Multiple files:** You can upload multiple files sequentially - they will all be indexed to the same vector database

### General

- **Multiple indexes:** You can index multiple repositories/files - they will all be stored in the same vector database
- **Cleanup option:** Set `cleanup: true` (default) to automatically remove temporary files/directories after indexing
- **Error handling:** Check server logs for detailed error messages if indexing fails
- **Vector database:** All indexed content is stored in Supabase vector database for later retrieval

---

## Troubleshooting

### Common Issues

#### "Failed to clone repository"

**Possible causes:**
- No internet connection
- Invalid GitHub URL
- Repository is private (authentication required)
- Git is not installed on the server

**Solutions:**
- Verify the GitHub URL is correct and public
- Check internet connectivity
- Ensure Git is installed: `git --version`

#### "No documents found to index"

**Possible causes:**
- Repository is empty
- No supported file types in repository
- File permissions issue

**Solutions:**
- Verify the repository contains code files
- Check file permissions
- Review server logs for specific errors

#### "Failed to index file"

**Possible causes:**
- File is password-protected (PDF)
- File is corrupted
- Unsupported file format
- File path is incorrect

**Solutions:**
- Ensure the file is not password-protected
- Verify the file is not corrupted
- Check that the file format is supported
- Verify the file path is correct

#### "Path does not exist"

**Possible causes:**
- Incorrect file path
- Path uses wrong path separators
- File/directory doesn't exist

**Solutions:**
- Use absolute paths
- Use correct path separators for your OS (`\` for Windows, `/` for Unix)
- Verify the file/directory exists before indexing

---

## Related Endpoints

After indexing, you can use these endpoints to interact with the indexed content:

- **`POST /api/v1/question`** - Ask questions about the indexed repository
- **`POST /api/v1/validate`** - Validate change requests
- **`POST /api/v1/impact`** - Analyze impact of changes
- **`POST /api/v1/analyze`** - Perform full analysis (validation + impact + decision)
- **`GET /api/v1/health`** - Health check endpoint

For more information about these endpoints, see the main `README.md` file.

---

## Version

**API Version:** `v1`

**Last Updated:** 2024

