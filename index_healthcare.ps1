# Index Healthcare Insurance App Repository and PDF
# GitHub: https://github.com/pavithrasatishask/HealthcareInsuranceApp
# PDF: US HealthCare Knowledge Base.pdf

$baseUrl = "http://localhost:8000/api/v1"

Write-Host "=== Indexing Healthcare Insurance Content ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Index GitHub Repository
Write-Host "Step 1: Indexing GitHub Repository..." -ForegroundColor Yellow
Write-Host "Repository: https://github.com/pavithrasatishask/HealthcareInsuranceApp" -ForegroundColor Gray
Write-Host "This may take a few minutes depending on repository size..." -ForegroundColor Gray
Write-Host ""

$githubBody = @{
    repository_path = "https://github.com/pavithrasatishask/HealthcareInsuranceApp"
    cleanup = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $githubBody -ContentType "application/json"
    Write-Host "✓ GitHub repository indexed successfully!" -ForegroundColor Green
    Write-Host "  Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "  Message: $($response.message)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "✗ Failed to index GitHub repository" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Step 2: Index PDF File
Write-Host "Step 2: Indexing PDF File..." -ForegroundColor Yellow
Write-Host "Looking for: US HealthCare Knowledge Base.pdf" -ForegroundColor Gray
Write-Host ""

# Try to find the PDF in common locations
$pdfPaths = @(
    ".\US HealthCare Knowledge Base.pdf",
    ".\US_HealthCare_Knowledge_Base.pdf",
    "$env:USERPROFILE\Downloads\US HealthCare Knowledge Base.pdf",
    "$env:USERPROFILE\Documents\US HealthCare Knowledge Base.pdf"
)

$pdfFound = $false
foreach ($pdfPath in $pdfPaths) {
    if (Test-Path $pdfPath) {
        Write-Host "Found PDF at: $pdfPath" -ForegroundColor Green
        $pdfBody = @{
            repository_path = (Resolve-Path $pdfPath).Path
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $pdfBody -ContentType "application/json"
            Write-Host "✓ PDF file indexed successfully!" -ForegroundColor Green
            Write-Host "  Status: $($response.status)" -ForegroundColor Cyan
            Write-Host "  Message: $($response.message)" -ForegroundColor Cyan
            $pdfFound = $true
            break
        } catch {
            Write-Host "✗ Failed to index PDF file" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
            break
        }
    }
}

if (-not $pdfFound) {
    Write-Host "⚠ PDF file not found in common locations." -ForegroundColor Yellow
    Write-Host "Please provide the full path to the PDF file:" -ForegroundColor Yellow
    $customPath = Read-Host
    if ($customPath -and (Test-Path $customPath)) {
        $pdfBody = @{
            repository_path = (Resolve-Path $customPath).Path
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $pdfBody -ContentType "application/json"
            Write-Host "✓ PDF file indexed successfully!" -ForegroundColor Green
            Write-Host "  Status: $($response.status)" -ForegroundColor Cyan
            Write-Host "  Message: $($response.message)" -ForegroundColor Cyan
        } catch {
            Write-Host "✗ Failed to index PDF file" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ Invalid path or file not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Indexing Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now ask questions about the Healthcare Insurance App!" -ForegroundColor Green
Write-Host ""
Write-Host "Example questions:" -ForegroundColor Yellow
Write-Host '  $body = @{ question = "How does user authentication work?"; max_results = 5 } | ConvertTo-Json' -ForegroundColor Gray
Write-Host '  Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $body -ContentType "application/json"' -ForegroundColor Gray
Write-Host ""
Write-Host '  $body = @{ question = "What are the policy management features?"; max_results = 5 } | ConvertTo-Json' -ForegroundColor Gray
Write-Host '  Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $body -ContentType "application/json"' -ForegroundColor Gray

