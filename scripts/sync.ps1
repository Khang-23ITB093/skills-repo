# PowerShell script để đồng bộ Skills và Rules vào Antigravity / Gemini CLI
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
    Write-Host ">>> Đang đồng bộ vào cấu hình Global: $DestRoot" -ForegroundColor Cyan
} else {
    if (-not $ProjectPath) {
        Write-Error "Vui lòng truyền đường dẫn dự án qua -ProjectPath <đường dẫn>"
        exit 1
    }
    $DestRoot = Join-Path $ProjectPath ".agents"
    $DestSkills = Join-Path $DestRoot "skills"
    $DestRules = Join-Path $DestRoot "rules"
    Write-Host ">>> Đang đồng bộ vào Project: $DestRoot" -ForegroundColor Cyan
}

# Đảm bảo thư mục đích tồn tại
New-Item -ItemType Directory -Force -Path $DestSkills | Out-Null
New-Item -ItemType Directory -Force -Path $DestRules | Out-Null

# Copy Own Skills
Write-Host "--> Đồng bộ các skills nội bộ..." -ForegroundColor Green
Copy-Item -Path (Join-Path $RepoRoot "skills\*") -Destination $DestSkills -Recurse -Force -Exclude ".env*", "*.key", "*.pem"

# Copy Global External Skills (nếu target là global và có _external)
$ExternalDir = Join-Path $RepoRoot "_external"
if (Test-Path $ExternalDir) {
    Write-Host "--> Đồng bộ các skills external (Global)..." -ForegroundColor Green
    # Các skill external có thể được copy hoặc symlink vào DestSkills
    Get-ChildItem -Directory -Path $ExternalDir | ForEach-Object {
        $skillName = $_.Name
        # Bỏ qua các skill thuần project-scope trừ khi được cấu hình
        Copy-Item -Path $_.FullName -Destination $DestSkills -Recurse -Force
    }
}

# Copy Rules
Write-Host "--> Đồng bộ các rules..." -ForegroundColor Green
Copy-Item -Path (Join-Path $RepoRoot "rules\*") -Destination $DestRules -Recurse -Force -Exclude ".env*", "*.key", "*.pem"

Write-Host ">>> Hoàn tất đồng bộ thành công!" -ForegroundColor Yellow
