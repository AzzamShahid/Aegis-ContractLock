$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$results = [ordered]@{
    "Engine tests"           = $false
    "Contract coverage"      = $false
    "Behavioral equality"    = $false
    "Architecture"           = $false
    "Mutation gauntlet"      = $false
    "Evidence readiness"     = $false
}

# Verification commands regenerate evidence files.
# Back them up first, then restore them so running this script does not
# permanently dirty the repository.
$evidencePaths = @(
    "baseline\baseline.json",
    "reports\candidate-evidence.json",
    "reports\verification.json",
    "reports\verification.md",
    "reports\contract-coverage.json",
    "reports\contract-coverage.md",
    "reports\gauntlet-report.json",
    "reports\gauntlet-report.md",
    "reports\architecture-comparison.json",
    "reports\architecture-comparison.md",
    "reports\evidence-certificate.json",
    "reports\evidence-certificate.md",
    "reports\dashboard.html",
    "reports\readiness.json",
    "reports\readiness.md"
)

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-verify-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

$existing = @{}

foreach ($relativePath in $evidencePaths) {
    $source = Join-Path $PSScriptRoot $relativePath

    if (Test-Path $source) {
        $existing[$relativePath] = $true

        $backup = Join-Path $tempRoot $relativePath
        $backupDir = Split-Path $backup -Parent

        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        Copy-Item $source $backup -Force
    }
    else {
        $existing[$relativePath] = $false
    }
}

function Run-Step {
    param(
        [string]$Title,
        [scriptblock]$Command,
        [string]$RequiredPattern
    )

    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Title
    Write-Host "============================================================"

    $output = & $Command 2>&1 | Out-String
    $exitCode = $LASTEXITCODE

    Write-Host $output.TrimEnd()

    if ($exitCode -ne 0) {
        throw "$Title failed with exit code $exitCode."
    }

    if ($RequiredPattern -and $output -notmatch $RequiredPattern) {
        throw "$Title completed but expected result was not found: $RequiredPattern"
    }
}

try {
    Run-Step `
        "1/6 - Aegis engine tests" `
        { python -m pytest tests -q } `
        "7 passed"

    $results["Engine tests"] = $true

    Run-Step `
        "2/6 - Legacy behavioral-contract coverage" `
        { python -m aegis.cli coverage } `
        "100\.00%"

    $results["Contract coverage"] = $true

    Run-Step `
        "3/6 - Behavioral equivalence" `
        { python -m aegis.cli verify } `
        "VERDICT:\s+ACCEPTED"

    $results["Behavioral equality"] = $true

    Run-Step `
        "4/6 - Architecture integrity" `
        { python -m aegis.cli architecture } `
        "(?s)Modern legacy imports:\s*0.*Modern cycles\s*:\s*0"

    $results["Architecture"] = $true

    Run-Step `
        "5/6 - Seeded regression audit" `
        { python -m aegis.cli gauntlet } `
        "21"

    $results["Mutation gauntlet"] = $true

    Run-Step `
        "6/6 - Complete submission readiness" `
        { python -m aegis.cli readiness } `
        "SUBMISSION READINESS:\s+READY"

    $results["Evidence readiness"] = $true
}
catch {
    Write-Host ""
    Write-Host "Verification failure:"
    Write-Host $_.Exception.Message
}
finally {
    # Restore evidence exactly as it existed before verification.
    foreach ($relativePath in $evidencePaths) {
        $target = Join-Path $PSScriptRoot $relativePath
        $backup = Join-Path $tempRoot $relativePath

        if ($existing[$relativePath]) {
            $targetDir = Split-Path $target -Parent
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            Copy-Item $backup $target -Force
        }
        elseif (Test-Path $target) {
            Remove-Item $target -Force
        }
    }

    Remove-Item $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "============================================================"
Write-Host "AEGIS CONTRACTLOCK - SUBMISSION VERIFICATION"
Write-Host "============================================================"

foreach ($entry in $results.GetEnumerator()) {
    $status = if ($entry.Value) { "PASS" } else { "FAIL" }
    Write-Host ("{0,-26} {1}" -f $entry.Key, $status)
}

$allPassed = -not ($results.Values -contains $false)

Write-Host "------------------------------------------------------------"

if ($allPassed) {
    Write-Host "FINAL: READY"
    Write-Host "All submission verification gates passed."
    exit 0
}
else {
    Write-Host "FINAL: NOT READY"
    Write-Host "At least one submission verification gate failed."
    exit 1
}
