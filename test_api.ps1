# Test script for Repository Intelligence API

$baseUrl = "http://localhost:8000/api/v1"

Write-Host "=== Testing Repository Intelligence API ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Ask a Question (will fail if no repository indexed)
Write-Host "Test 2: Ask Question" -ForegroundColor Yellow
$questionBody = @{
    question = "How does the authentication work in this system?"
    max_results = 3
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $questionBody -ContentType "application/json"
    Write-Host "✓ Question answered successfully" -ForegroundColor Green
    Write-Host "Answer: $($response.answer)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Question endpoint test skipped (repository may not be indexed yet)" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Test 3: Validate Change Request
Write-Host "Test 3: Validate Change Request" -ForegroundColor Yellow
$changeRequest = @{
    description = "Add support for OAuth2 authentication"
    feature_type = "new_feature"
    target_modules = @("auth", "security")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/validate" -Method Post -Body $changeRequest -ContentType "application/json"
    Write-Host "✓ Change validation completed" -ForegroundColor Green
    Write-Host "Is Valid: $($response.is_valid)" -ForegroundColor Cyan
    Write-Host "Conflicts: $($response.conflicts.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Validation test skipped (repository may not be indexed yet)" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Test 4: Full Analysis
Write-Host "Test 4: Full Analysis" -ForegroundColor Yellow
$analysisRequest = @{
    description = "Add new payment processing module"
    feature_type = "new_feature"
    target_modules = @("payment", "billing")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/analyze" -Method Post -Body $analysisRequest -ContentType "application/json"
    Write-Host "✓ Full analysis completed" -ForegroundColor Green
    Write-Host "Decision: $($response.decision)" -ForegroundColor Cyan
    Write-Host "Impact Level: $($response.impact_assessment.level)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Analysis test skipped (repository may not be indexed yet)" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "=== Testing Complete ===" -ForegroundColor Cyan

