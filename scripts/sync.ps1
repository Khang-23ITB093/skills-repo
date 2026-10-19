# PowerShell script to synchronize Skills and Rules into Antigravity / Gemini CLI
param(
    [ValidateSet("global", "project")]
    [string]$Target = "global",
    [string]$ProjectPath = "",
    [string]$Skill = "",
    [string]$Category = ""
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

# Helper function to copy a single skill flat into destination
function Copy-SkillFlat($skillDir, $destination) {
    if (Test-Path (Join-Path $skillDir "SKILL.md")) {
        $skillName = Split-Path $skillDir -Leaf
        $targetDir = Join-Path $destination $skillName
        Copy-Item -Path $skillDir -Destination $targetDir -Recurse -Force -Exclude ".env*", "*.key", "*.pem", ".git"
        Write-Host "    + [Skill] $skillName -> $targetDir" -ForegroundColor Gray
    }
}

# 1. Copy Own Skills
Write-Host "--> Syncing own skills..." -ForegroundColor Green
Get-ChildItem -Directory -Path (Join-Path $RepoRoot "skills") | ForEach-Object {
    Copy-SkillFlat $_.FullName $DestSkills
}

# 2. Copy External Skills
$ExternalDir = Join-Path $RepoRoot "_external"
if (Test-Path $ExternalDir) {
    Write-Host "--> Syncing external skills..." -ForegroundColor Green
    
    if ($Skill) {
        # Sync specific skill by name
        Write-Host "    Filtering by skill: $Skill" -ForegroundColor Cyan
        $found = Get-ChildItem -Path $ExternalDir -Filter "SKILL.md" -Recurse | Where-Object { $_.Directory.Name -eq $Skill } | Select-Object -First 1
        if ($found) {
            Copy-SkillFlat $found.Directory.FullName $DestSkills
        } else {
            Write-Warning "Skill '$Skill' not found in _external library."
        }
    } elseif ($Category) {
        # Sync all skills from a specific category folder
        Write-Host "    Filtering by category: $Category" -ForegroundColor Cyan
        $catPath = Join-Path $ExternalDir $Category
        if (Test-Path $catPath) {
            Get-ChildItem -Path $catPath -Filter "SKILL.md" -Recurse | ForEach-Object {
                Copy-SkillFlat $_.Directory.FullName $DestSkills
            }
        } else {
            Write-Warning "Category '$Category' not found in _external library."
        }
    } elseif ($Target -eq "global") {
        # In global mode by default, only sync core global external skills
        $GlobalExternal = @("docx", "pptx", "pdf", "xlsx", "skill-creator")
        foreach ($gSkill in $GlobalExternal) {
            $found = Get-ChildItem -Path $ExternalDir -Filter "SKILL.md" -Recurse | Where-Object { $_.Directory.Name -eq $gSkill } | Select-Object -First 1
            if ($found) {
                Copy-SkillFlat $found.Directory.FullName $DestSkills
            } else {
                Write-Warning "Global external skill '$gSkill' not found in _external."
            }
        }
    } else {
        # In project mode without specific filter, sync all external skills flat
        Write-Host "    Syncing all external skills flat into project scope..." -ForegroundColor Cyan
        Get-ChildItem -Path $ExternalDir -Filter "SKILL.md" -Recurse | ForEach-Object {
            Copy-SkillFlat $_.Directory.FullName $DestSkills
        }
    }
}

# 3. Copy Rules
Write-Host "--> Syncing rules..." -ForegroundColor Green
Get-ChildItem -File -Path (Join-Path $RepoRoot "rules") | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $DestRules -Force -Exclude ".env*", "*.key", "*.pem"
}

Write-Host ">>> Synchronization completed successfully!" -ForegroundColor Yellow
