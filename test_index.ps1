# Test script for indexing GitHub repositories and PDFs

$baseUrl = "http://localhost:8000/api/v1"

Write-Host "=== Testing Repository Indexing ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Index GitHub Repository
Write-Host "Test 1: Index GitHub Repository" -ForegroundColor Yellow
$githubBody = @{
    repository_path = "https://github.com/microsoft/vscode"  # Example - replace with your repo
    cleanup = $true
} | ConvertTo-Json

try {
    Write-Host "Indexing GitHub repository (this may take a while)..." -ForegroundColor Gray
    $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $githubBody -ContentType "application/json"
    Write-Host "✓ GitHub repository indexed successfully" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ Failed to index GitHub repository" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Test 2: Index Local PDF File
Write-Host "Test 2: Index PDF File (if you have one)" -ForegroundColor Yellow
Write-Host "To test PDF indexing, use:" -ForegroundColor Gray
Write-Host '  $filePath = "C:\path\to\your\file.pdf"' -ForegroundColor Gray
Write-Host '  $body = @{ repository_path = $filePath } | ConvertTo-Json' -ForegroundColor Gray
Write-Host '  Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $body -ContentType "application/json"' -ForegroundColor Gray
Write-Host ""

# Test 3: Ask a Question (after indexing)
Write-Host "Test 3: Ask Question (after indexing)" -ForegroundColor Yellow
$questionBody = @{
    question = "What is the main purpose of this repository?"
    max_results = 5
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $questionBody -ContentType "application/json"
    Write-Host "✓ Question answered" -ForegroundColor Green
    Write-Host "Answer: $($response.answer)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Question test skipped (repository may not be indexed yet)" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "=== Testing Complete ===" -ForegroundColor Cyan

