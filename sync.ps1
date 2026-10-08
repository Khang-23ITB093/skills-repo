# PowerShell script để đồng bộ Skills và Rules vào Antigravity / Gemini CLI
param(
    [ValidateSet("global", "project")]
    [string]$Target = "global",
    [string]$ProjectPath = ""
)

$RepoRoot = $PSScriptRoot

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

# Copy Skills
Write-Host "--> Đồng bộ các skills..." -ForegroundColor Green
Copy-Item -Path (Join-Path $RepoRoot "skills\*") -Destination $DestSkills -Recurse -Force

# Copy Rules
Write-Host "--> Đồng bộ các rules..." -ForegroundColor Green
Copy-Item -Path (Join-Path $RepoRoot "rules\*") -Destination $DestRules -Recurse -Force

Write-Host ">>> Hoàn tất đồng bộ thành công!" -ForegroundColor Yellow
