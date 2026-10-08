# PowerShell script to synchronize Skills and Rules into Antigravity / Gemini CLI
param(
    [ValidateSet("global", "project")]
    [string]$Target = "global",
    [string]$ProjectPath = ""
)

$RepoRoot = Split-Path $PSScriptRoot -Parent

if ($Target -eq "global") {
    $DestRoot = Join-Path $env:USERPROFILE ".gemini\config"
    $DestSkills = Join-Path $DestRoot "skills"
    $DestRules = Join-Path $DestRoot "rules"
    Write-Host ">>> Synchronizing to Global config: $DestRoot" -ForegroundColor Cyan
} else {
    if (-not $ProjectPath) {
        Write-Error "Please specify project path via -ProjectPath <path>"
        exit 1
    }
    $DestRoot = Join-Path $ProjectPath ".agents"
    $DestSkills = Join-Path $DestRoot "skills"
    $DestRules = Join-Path $DestRoot "rules"
    Write-Host ">>> Synchronizing to Project: $DestRoot" -ForegroundColor Cyan
}

# Ensure destination directories exist
New-Item -ItemType Directory -Force -Path $DestSkills | Out-Null
New-Item -ItemType Directory -Force -Path $DestRules | Out-Null

# 1. Copy Own Skills
Write-Host "--> Syncing own skills..." -ForegroundColor Green
Get-ChildItem -Directory -Path (Join-Path $RepoRoot "skills") | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $DestSkills -Recurse -Force -Exclude ".env*", "*.key", "*.pem"
}

# 2. Copy Global External Skills
$ExternalDir = Join-Path $RepoRoot "_external"
if (Test-Path $ExternalDir) {
    Write-Host "--> Syncing external skills..." -ForegroundColor Green
    # In global mode, only sync global-scope external skills
    $GlobalExternal = @("docx", "pptx", "pdf", "xlsx", "skill-creator")
    Get-ChildItem -Directory -Path $ExternalDir | ForEach-Object {
        if ($Target -eq "global") {
            if ($GlobalExternal -contains $_.Name) {
                Copy-Item -Path $_.FullName -Destination $DestSkills -Recurse -Force
            }
        } else {
            # In project mode, can copy all or project-specific
            Copy-Item -Path $_.FullName -Destination $DestSkills -Recurse -Force
        }
    }
}

# 3. Copy Rules
Write-Host "--> Syncing rules..." -ForegroundColor Green
Get-ChildItem -File -Path (Join-Path $RepoRoot "rules") | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $DestRules -Force -Exclude ".env*", "*.key", "*.pem"
}

Write-Host ">>> Synchronization completed successfully!" -ForegroundColor Yellow
