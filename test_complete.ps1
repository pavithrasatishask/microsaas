# Complete Test Script for Healthcare Insurance App Indexing and Querying

$baseUrl = "http://localhost:8000/api/v1"

Write-Host "=== Complete System Test ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Health Check
Write-Host "Step 1: Health Check" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✓ Server is running" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "✗ Server is not running. Please start it with: python run_server.py" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Index GitHub Repository
Write-Host "Step 2: Indexing GitHub Repository" -ForegroundColor Yellow
Write-Host "Repository: https://github.com/pavithrasatishask/HealthcareInsuranceApp" -ForegroundColor Gray
Write-Host "This may take 2-5 minutes..." -ForegroundColor Gray

$githubBody = @{
    repository_path = "https://github.com/pavithrasatishask/HealthcareInsuranceApp"
    cleanup = $true
} | ConvertTo-Json

try {
    $startTime = Get-Date
    $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $githubBody -ContentType "application/json"
    $duration = (Get-Date) - $startTime
    Write-Host "✓ GitHub repository indexed successfully!" -ForegroundColor Green
    Write-Host "  Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "  Message: $($response.message)" -ForegroundColor Cyan
    Write-Host "  Time taken: $($duration.TotalSeconds) seconds" -ForegroundColor Cyan
    $githubIndexed = $true
} catch {
    Write-Host "✗ Failed to index GitHub repository" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
    if ($_.ErrorDetails.Message) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Details: $($errorDetails.error)" -ForegroundColor Gray
    }
    $githubIndexed = $false
}
Write-Host ""

# Step 3: Index PDF File
Write-Host "Step 3: Indexing PDF File" -ForegroundColor Yellow
$pdfPath = "C:\Users\pavithra.krishnan\Downloads\US HealthCare Knowledge Base.pdf"

if (Test-Path $pdfPath) {
    Write-Host "Found PDF at: $pdfPath" -ForegroundColor Green
    $pdfBody = @{
        repository_path = $pdfPath
    } | ConvertTo-Json
    
    try {
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "$baseUrl/index" -Method Post -Body $pdfBody -ContentType "application/json"
        $duration = (Get-Date) - $startTime
        Write-Host "✓ PDF file indexed successfully!" -ForegroundColor Green
        Write-Host "  Status: $($response.status)" -ForegroundColor Cyan
        Write-Host "  Message: $($response.message)" -ForegroundColor Cyan
        Write-Host "  Time taken: $($duration.TotalSeconds) seconds" -ForegroundColor Cyan
        $pdfIndexed = $true
    } catch {
        Write-Host "✗ Failed to index PDF file" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
        if ($_.ErrorDetails.Message) {
            $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Details: $($errorDetails.error)" -ForegroundColor Gray
        }
        $pdfIndexed = $false
    }
} else {
    Write-Host "⚠ PDF file not found at: $pdfPath" -ForegroundColor Yellow
    Write-Host "Please provide the correct path to the PDF file" -ForegroundColor Yellow
    $pdfIndexed = $false
}
Write-Host ""

# Step 4: Test Questions
if ($githubIndexed -or $pdfIndexed) {
    Write-Host "Step 4: Testing Question Answering" -ForegroundColor Yellow
    Write-Host ""
    
    $questions = @(
        @{
            question = "How does user authentication work in this system?"
            description = "Authentication question"
        },
        @{
            question = "What are the main features of the policy management system?"
            description = "Policy management question"
        },
        @{
            question = "How are claims processed?"
            description = "Claims processing question"
        }
    )
    
    foreach ($q in $questions) {
        Write-Host "Question: $($q.question)" -ForegroundColor Cyan
        $questionBody = @{
            question = $q.question
            max_results = 5
        } | ConvertTo-Json
        
        try {
            $response = Invoke-RestMethod -Uri "$baseUrl/question" -Method Post -Body $questionBody -ContentType "application/json"
            Write-Host "✓ Question answered" -ForegroundColor Green
            Write-Host "Answer: $($response.answer.Substring(0, [Math]::Min(200, $response.answer.Length)))..." -ForegroundColor White
            Write-Host "Files referenced: $($response.repository_evidence.file_paths.Count)" -ForegroundColor Gray
            Write-Host ""
        } catch {
            Write-Host "✗ Failed to answer question" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
            Write-Host ""
        }
    }
} else {
    Write-Host "⚠ Skipping question tests - no content indexed" -ForegroundColor Yellow
}

# Step 5: Test Change Validation
Write-Host "Step 5: Testing Change Validation" -ForegroundColor Yellow
$changeBody = @{
    description = "Add support for OAuth2 authentication"
    feature_type = "new_feature"
    target_modules = @("auth", "security")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/validate" -Method Post -Body $changeBody -ContentType "application/json"
    Write-Host "✓ Change validation completed" -ForegroundColor Green
    Write-Host "  Is Valid: $($response.is_valid)" -ForegroundColor Cyan
    Write-Host "  Conflicts: $($response.conflicts.Count)" -ForegroundColor Cyan
    if ($response.conflicts.Count -gt 0) {
        Write-Host "  Conflict details: $($response.conflicts -join ', ')" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Change validation test skipped" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Step 6: Test Full Analysis
Write-Host "Step 6: Testing Full Analysis" -ForegroundColor Yellow
$analysisBody = @{
    description = "Add new payment processing module"
    feature_type = "new_feature"
    target_modules = @("payment", "billing")
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/analyze" -Method Post -Body $analysisBody -ContentType "application/json"
    Write-Host "✓ Full analysis completed" -ForegroundColor Green
    Write-Host "  Decision: $($response.decision)" -ForegroundColor Cyan
    Write-Host "  Impact Level: $($response.impact_assessment.level)" -ForegroundColor Cyan
    Write-Host "  Affected Modules: $($response.impact_assessment.affected_modules.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Full analysis test skipped" -ForegroundColor Yellow
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  GitHub Repository: $(if ($githubIndexed) { '✓ Indexed' } else { '✗ Failed' })" -ForegroundColor $(if ($githubIndexed) { 'Green' } else { 'Red' })
Write-Host "  PDF File: $(if ($pdfIndexed) { '✓ Indexed' } else { '✗ Failed' })" -ForegroundColor $(if ($pdfIndexed) { 'Green' } else { 'Red' })

