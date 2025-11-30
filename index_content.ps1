# Simple script to index GitHub repository and PDF files
# Usage: .\index_content.ps1

$baseUrl = "http://localhost:8000/api/v1"

Write-Host "=== Repository Intelligence - Content Indexing ===" -ForegroundColor Cyan
Write-Host ""

# Get GitHub URL from user
Write-Host "Enter GitHub Repository URL (or press Enter to skip):" -ForegroundColor Yellow
$githubUrl = Read-Host
if ($githubUrl) {
    Write-Host "Indexing GitHub repository: $githubUrl" -ForegroundColor Gray
    Write-Host "This may take a few minutes..." -ForegroundColor Gray
    
    $body = @{
        repository_path = $githubUrl
        cleanup = $true
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $body -ContentType "application/json"
        Write-Host "✓ GitHub repository indexed successfully!" -ForegroundColor Green
        $response | ConvertTo-Json
    } catch {
        Write-Host "✗ Failed to index GitHub repository" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Get PDF file path from user
Write-Host "Enter PDF file path (or press Enter to skip):" -ForegroundColor Yellow
$pdfPath = Read-Host
if ($pdfPath) {
    if (Test-Path $pdfPath) {
        Write-Host "Indexing PDF file: $pdfPath" -ForegroundColor Gray
        
        $body = @{
            repository_path = $pdfPath
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $body -ContentType "application/json"
            Write-Host "✓ PDF file indexed successfully!" -ForegroundColor Green
            $response | ConvertTo-Json
        } catch {
            Write-Host "✗ Failed to index PDF file" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ File not found: $pdfPath" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=== Indexing Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now ask questions using:" -ForegroundColor Yellow
Write-Host '  $body = @{ question = "Your question here"; max_results = 5 } | ConvertTo-Json' -ForegroundColor Gray
Write-Host '  Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $body -ContentType "application/json"' -ForegroundColor Gray

