<#
.SYNOPSIS
    Non-destructive security and repository-hygiene checker for Aegis ContractLock.
.DESCRIPTION
    Verifies that the repository complies with IBM hackathon security conventions:
    - .bobignore exists
    - .env and .venv are git-ignored
    - .env.example remains trackable
    - No private keys (*.pem, *.key, *.p12, *.pfx) are tracked
    - No caches or virtual environments are tracked
    - No obvious credential patterns in tracked text files
    - No local absolute file:/// links in judge-facing tracked text
    - No C:\Users\ local absolute paths in judge-facing tracked text
    - Avoids scanning .git internals
    - Avoids treating binary screenshots/images as UTF-8 text
    - Does not print credential values upon detection (reports file/path + category only)
#>

$ErrorActionPreference = "Continue"

$repoRoot = $PSScriptRoot
Set-Location $repoRoot

$allPassed = $true
$results = [ordered]@{}

function Record-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details = ""
    )
    $results[$Name] = $Passed
    if (-not $Passed) {
        $script:allPassed = $false
        if ($Details) {
            Write-Host "  [FAIL] $Details" -ForegroundColor Red
        }
    }
}

Write-Host "============================================================"
Write-Host "AEGIS CONTRACTLOCK - SECURITY PREFLIGHT CHECK"
Write-Host "============================================================"
Write-Host ""

# ------------------------------------------------------------------------------
# Check 1: .bobignore exists
# ------------------------------------------------------------------------------
$bobignorePath = Join-Path $repoRoot ".bobignore"
$bobignoreExists = Test-Path $bobignorePath
Record-Check ".bobignore exists" $bobignoreExists "Missing .bobignore in repository root."

# ------------------------------------------------------------------------------
# Check 2: .env is ignored
# ------------------------------------------------------------------------------
& git check-ignore -q .env 2>$null
$envIgnored = ($LASTEXITCODE -eq 0)
Record-Check ".env is ignored" $envIgnored ".env is NOT ignored by git."

# ------------------------------------------------------------------------------
# Check 3: .env.example remains trackable
# ------------------------------------------------------------------------------
$envExamplePath = Join-Path $repoRoot ".env.example"
$envExampleExists = Test-Path $envExamplePath
& git check-ignore -q .env.example 2>$null
$envExampleNotIgnored = ($LASTEXITCODE -ne 0)
$envExampleValid = $envExampleExists -and $envExampleNotIgnored
Record-Check ".env.example trackable" $envExampleValid ".env.example missing or improperly ignored by git."

# ------------------------------------------------------------------------------
# Check 4: .venv is ignored
# ------------------------------------------------------------------------------
& git check-ignore -q .venv 2>$null
$venvIgnored = ($LASTEXITCODE -eq 0)
Record-Check ".venv is ignored" $venvIgnored ".venv is NOT ignored by git."

# ------------------------------------------------------------------------------
# Check 5: No tracked *.pem / *.key / *.p12 / *.pfx
# ------------------------------------------------------------------------------
$trackedKeyFiles = & git ls-files "*.pem" "*.key" "*.p12" "*.pfx" "*.pkcs12" 2>$null
$noTrackedKeys = ([string]::IsNullOrWhiteSpace($trackedKeyFiles))
$keyDetails = if (-not $noTrackedKeys) { "Tracked key/cert files found:`n$trackedKeyFiles" } else { "" }
Record-Check "No tracked private keys/certs" $noTrackedKeys $keyDetails

# ------------------------------------------------------------------------------
# Check 6: No tracked __pycache__, *.pyc, .pytest_cache, .venv
# ------------------------------------------------------------------------------
$trackedNoise = & git ls-files "*__pycache__*" "*.pyc" "*.pyo" "*.pytest_cache*" "*.venv*" 2>$null
$noTrackedNoise = ([string]::IsNullOrWhiteSpace($trackedNoise))
$noiseDetails = if (-not $noTrackedNoise) { "Tracked cache/venv files found:`n$trackedNoise" } else { "" }
Record-Check "No tracked cache/venv noise" $noTrackedNoise $noiseDetails

# ------------------------------------------------------------------------------
# Enumerate candidate text files (tracked + candidate working tree text files)
# Avoid scanning .git directory or binary files.
# ------------------------------------------------------------------------------
$trackedFiles = & git ls-files 2>$null
$untrackedFiles = & git ls-files --others --exclude-standard 2>$null
$candidateFiles = ($trackedFiles + $untrackedFiles) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique

$binaryExtensions = @('.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.pdf', '.bin', '.exe', '.dll', '.so', '.pyc', '.pyo', '.zip', '.tar', '.gz')

function Test-IsBinaryFile {
    param([string]$FilePath)
    $ext = [System.IO.Path]::GetExtension($FilePath).ToLowerInvariant()
    if ($binaryExtensions -contains $ext) {
        return $true
    }
    # Check first 1024 bytes for null byte indicator
    try {
        $stream = [System.IO.File]::OpenRead($FilePath)
        $buffer = New-Object byte[] 1024
        $bytesRead = $stream.Read($buffer, 0, 1024)
        $stream.Close()
        for ($b = 0; $b -lt $bytesRead; $b++) {
            if ($buffer[$b] -eq 0) {
                return $true
            }
        }
    }
    catch {
        return $true
    }
    return $false
}

$textFilesToCheck = @()
foreach ($file in $candidateFiles) {
    # Skip .git directory and security_preflight.ps1 itself (contains pattern definitions)
    if ($file -like ".git/*" -or $file -like ".git\*" -or $file -eq "security_preflight.ps1") {
        continue
    }
    $fullPath = Join-Path $repoRoot $file
    if (Test-Path $fullPath -PathType Leaf) {
        if (-not (Test-IsBinaryFile $fullPath)) {
            $textFilesToCheck += $file
        }
    }
}

# ------------------------------------------------------------------------------
# Check 7: No obvious credential patterns in tracked text files
# Avoid printing credential values if anything suspicious is found.
# Report only file/path + category.
# ------------------------------------------------------------------------------
$credentialViolations = @()

$credentialRules = @(
    @{
        Category = "Private Key Header"
        Pattern  = '-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY'
    },
    @{
        Category = "AWS Access Key"
        Pattern  = '\bAKIA[0-9A-Z]{16}\b'
    },
    @{
        Category = "GitHub Personal Access Token"
        Pattern  = '\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})\b'
    },
    @{
        Category = "Slack Token"
        Pattern  = '\bxox[baprs]-[0-9a-zA-Z-]{10,}\b'
    },
    @{
        Category = "JSON Web Token (JWT)"
        Pattern  = '\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b'
    },
    @{
        Category = "Hardcoded Secret / API Key"
        Pattern  = '(?i)(?:api_key|secret_key|private_key|auth_token)\s*[:=]\s*["''][A-Za-z0-9_\-]{20,}["'']'
    }
)

foreach ($relPath in $textFilesToCheck) {
    $fullPath = Join-Path $repoRoot $relPath
    try {
        $lines = [System.IO.File]::ReadAllLines($fullPath)
        for ($i = 0; $i -lt $lines.Length; $i++) {
            $line = $lines[$i]
            # Ignore safe placeholder examples in templates/docs
            if ($line -match '(?i)(?:PLACEHOLDER|EXAMPLE|YOUR_KEY|DUMMY|<username>)') {
                continue
            }
            foreach ($rule in $credentialRules) {
                if ($line -match $rule.Pattern) {
                    $credentialViolations += [PSCustomObject]@{
                        File     = $relPath
                        Line     = $i + 1
                        Category = $rule.Category
                    }
                }
            }
        }
    }
    catch {}
}

$noCredentials = ($credentialViolations.Count -eq 0)
$credDetails = if (-not $noCredentials) {
    $msgs = @()
    foreach ($v in $credentialViolations) {
        $msgs += "$($v.File):$($v.Line) - Category: $($v.Category)"
    }
    $msgs -join "`n"
} else { "" }

Record-Check "No exposed credentials in text" $noCredentials $credDetails

# ------------------------------------------------------------------------------
# Check 8: No file:/// absolute local links in judge-facing tracked text
# ------------------------------------------------------------------------------
$fileUriViolations = @()

foreach ($relPath in $textFilesToCheck) {
    $fullPath = Join-Path $repoRoot $relPath
    try {
        $lines = [System.IO.File]::ReadAllLines($fullPath)
        for ($i = 0; $i -lt $lines.Length; $i++) {
            $line = $lines[$i]
            if ($line -match '(?i)file:///') {
                $fileUriViolations += "$($relPath):$($i + 1)"
            }
        }
    }
    catch {}
}

$noFileUris = ($fileUriViolations.Count -eq 0)
$fileUriDetails = if (-not $noFileUris) {
    "Found file:/// links in:`n" + ($fileUriViolations -join "`n")
} else { "" }

Record-Check "No file:/// local links in text" $noFileUris $fileUriDetails

# ------------------------------------------------------------------------------
# Check 9: No C:\Users\ absolute local paths in judge-facing tracked text
# ------------------------------------------------------------------------------
$userPathViolations = @()

foreach ($relPath in $textFilesToCheck) {
    $fullPath = Join-Path $repoRoot $relPath
    try {
        $lines = [System.IO.File]::ReadAllLines($fullPath)
        for ($i = 0; $i -lt $lines.Length; $i++) {
            $line = $lines[$i]
            # Allow illustrative documentation tokens like C:\Users\<username>\...
            if ($line -match '(?i)C:[\\/]Users[\\/]<username>') {
                continue
            }
            if ($line -match '(?i)C:[\\/]Users[\\/]') {
                $userPathViolations += "$($relPath):$($i + 1)"
            }
        }
    }
    catch {}
}

$noUserPaths = ($userPathViolations.Count -eq 0)
$userPathDetails = if (-not $noUserPaths) {
    "Found C:\Users\ paths in:`n" + ($userPathViolations -join "`n")
} else { "" }

Record-Check "No C:\Users\ local paths in text" $noUserPaths $userPathDetails

# ------------------------------------------------------------------------------
# Check 10: Sensitive patterns remain ignored inside evidence directories
# ------------------------------------------------------------------------------
$nestedSecretPaths = @(
    "reports/_security_probe.pem",
    "bob_evidence/_security_probe.key",
    "baseline/credentials.json",
    "bob_sessions/final/.env"
)

$nestedSecretsProtected = $true
$nestedFailures = @()

foreach ($probe in $nestedSecretPaths) {
    & git check-ignore -q --no-index $probe 2>$null

    if ($LASTEXITCODE -ne 0) {
        $nestedSecretsProtected = $false
        $nestedFailures += $probe
    }
}

$nestedDetails = if (-not $nestedSecretsProtected) {
    "Sensitive path patterns unexpectedly trackable:`n" +
    ($nestedFailures -join "`n")
}
else {
    ""
}

Record-Check `
    "Secrets ignored inside evidence dirs" `
    $nestedSecretsProtected `
    $nestedDetails

# ------------------------------------------------------------------------------
# Results Summary
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host "SECURITY PREFLIGHT SUMMARY"
Write-Host "------------------------------------------------------------"

foreach ($entry in $results.GetEnumerator()) {
    $status = if ($entry.Value) { "PASS" } else { "FAIL" }
    $color = if ($entry.Value) { "Green" } else { "Red" }
    Write-Host ("{0,-36} {1}" -f $entry.Key, $status) -ForegroundColor $color
}

Write-Host "------------------------------------------------------------"

if ($allPassed) {
    Write-Host "SECURITY PREFLIGHT: PASS" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "SECURITY PREFLIGHT: FAIL" -ForegroundColor Red
    exit 1
}
