# PowerShell script to synchronize Skills and Rules into one or more AI Agent hosts.
#
# Examples:
#   .\sync.ps1 -Target global                                   # Antigravity only (legacy default)
#   .\sync.ps1 -Target global -Hosts all                        # every known host
#   .\sync.ps1 -Target global -Hosts claude,codex               # Claude Code + shared ~/.agents
#   .\sync.ps1 -Target project -ProjectPath "D:\Proj" -Hosts all
#   .\sync.ps1 -Target project -ProjectPath "D:\Proj" -Skill react-patterns -Hosts agents,claude
#   .\sync.ps1 -Target project -ProjectPath "D:\Proj" -Category 08-languages-frameworks -DryRun
#
# Skill install paths (verified 2026-10):
#   antigravity  ~/.gemini/config/skills            rules -> ~/.gemini/config/rules
#   claude       ~/.claude/skills                   rules -> ~/.claude/rules
#   codex        ~/.agents/skills                   (no rule dir; always-on lives in AGENTS.md)
#   cursor       ~/.cursor/skills                   (no rule dir)
#   agents       ~/.agents/skills                   shared by Codex/Cursor/Antigravity-compatible tools
#   dsh          $DSH_HOME/skills (fallback ~/.dsh/skills)
# Project targets always write .agents/skills (+ .claude/skills for the claude host).

param(
    [ValidateSet("global", "project")]
    [string]$Target = "global",

    [string]$ProjectPath = "",

    [string]$Skill = "",

    [string]$Category = "",

    # Host names: antigravity, claude, codex, cursor, agents, dsh, all. Default depends on -Target.
    [string[]]$Hosts = @(),

    # List what would be copied without copying anything.
    [switch]$DryRun,

    # Overwrite an existing skill folder of the same name. Off by default (never clobber silently).
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path $PSScriptRoot -Parent
$AllHosts = @("antigravity", "claude", "codex", "cursor", "agents", "dsh")

# ---------------------------------------------------------------- host helpers
function Resolve-Hosts {
    param([string[]]$Requested)

    if (-not $Requested -or $Requested.Count -eq 0) {
        if ($Target -eq "global") { return @("antigravity") } else { return @("agents") }
    }
    $expanded = @()
    foreach ($h in $Requested) {
        foreach ($part in ($h -split ",")) {
            $name = $part.Trim().ToLowerInvariant()
            if ($name -eq "") { continue }
            if ($name -eq "all") { $expanded += $AllHosts; continue }
            if ($AllHosts -notcontains $name) {
                throw "Unknown host '$name'. Valid: $($AllHosts -join ', '), all"
            }
            $expanded += $name
        }
    }
    return ($expanded | Select-Object -Unique)
}

function Get-GlobalSkillDir {
    param([string]$HostName)
    switch ($HostName) {
        "antigravity" { return (Join-Path $env:USERPROFILE ".gemini\config\skills") }
        "claude"      { return (Join-Path $env:USERPROFILE ".claude\skills") }
        "codex"       { return (Join-Path $env:USERPROFILE ".agents\skills") }
        "cursor"      { return (Join-Path $env:USERPROFILE ".cursor\skills") }
        "agents"      { return (Join-Path $env:USERPROFILE ".agents\skills") }
        "dsh" {
            if ($env:DSH_HOME) { return (Join-Path $env:DSH_HOME "skills") }
            return (Join-Path $env:USERPROFILE ".dsh\skills")
        }
        default { throw "Unknown host '$HostName'" }
    }
}

function Get-GlobalRuleDir {
    param([string]$HostName)
    # Only Antigravity and Claude Code have a native rules directory.
    # Codex / Cursor / DSH express always-on guidance through AGENTS.md instead.
    switch ($HostName) {
        "antigravity" { return (Join-Path $env:USERPROFILE ".gemini\config\rules") }
        "claude"      { return (Join-Path $env:USERPROFILE ".claude\rules") }
        default       { return $null }
    }
}

function Get-ProjectSkillDir {
    param([string]$HostName, [string]$Root)
    if ($HostName -eq "claude") { return (Join-Path $Root ".claude\skills") }
    return (Join-Path $Root ".agents\skills")
}

function Get-ProjectRuleDir {
    param([string]$HostName, [string]$Root)
    if ($HostName -eq "claude") { return (Join-Path $Root ".claude\rules") }
    return (Join-Path $Root ".agents\rules")
}

# ---------------------------------------------------------------- copy helpers
$script:CopiedCount = 0
$script:SkippedCount = 0

function Copy-SkillFlat {
    param([string]$SkillDir, [string]$Destination)

    if (-not (Test-Path (Join-Path $SkillDir "SKILL.md"))) { return }
    $skillName = Split-Path $SkillDir -Leaf
    $targetDir = Join-Path $Destination $skillName

    if (Test-Path $targetDir) {
        if (-not $Force) {
            Write-Host "    = [Skip] $skillName (already exists at $targetDir; use -Force to overwrite)" -ForegroundColor DarkYellow
            $script:SkippedCount++
            return
        }
        if (-not $DryRun) { Remove-Item -Path $targetDir -Recurse -Force }
    }

    if ($DryRun) {
        Write-Host "    ~ [DryRun] $skillName -> $targetDir" -ForegroundColor DarkCyan
    } else {
        $parent = Split-Path $targetDir -Parent
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        Copy-Item -Path $SkillDir -Destination $targetDir -Recurse -Force `
            -Exclude ".env*", "*.key", "*.pem", ".git"
        Write-Host "    + [Skill] $skillName -> $targetDir" -ForegroundColor Gray
    }
    $script:CopiedCount++
}

function Copy-Rules {
    param([string]$Destination, [string]$HostName, [int]$MaxBytes = 24000)

    $rulesRoot = Join-Path $RepoRoot "rules"
    if (-not (Test-Path $rulesRoot)) { return }

    Get-ChildItem -File -Path $rulesRoot | ForEach-Object {
        if ($_.Length -gt $MaxBytes) {
            Write-Warning "    ! Rule '$($_.Name)' is $($_.Length) bytes (> $MaxBytes); Antigravity truncates it."
        }
        if ($DryRun) {
            Write-Host "    ~ [DryRun] rule $($_.Name) -> $Destination" -ForegroundColor DarkCyan
        } else {
            Copy-Item -Path $_.FullName -Destination $Destination -Force `
                -Exclude ".env*", "*.key", "*.pem"
        }
    }
}

# ---------------------------------------------------------------- resolve plan
$ResolvedHosts = Resolve-Hosts -Requested $Hosts

if ($Target -eq "global") {
    $plan = foreach ($h in $ResolvedHosts) {
        [pscustomobject]@{
            Host     = $h
            SkillDir = Get-GlobalSkillDir -HostName $h
            RuleDir  = Get-GlobalRuleDir  -HostName $h
        }
    }
} else {
    if (-not $ProjectPath) {
        Write-Error "Please specify the project path via -ProjectPath <path>"
        exit 1
    }
    if (-not (Test-Path $ProjectPath)) {
        Write-Error "Project path not found: $ProjectPath"
        exit 1
    }
    $plan = foreach ($h in $ResolvedHosts) {
        [pscustomobject]@{
            Host     = $h
            SkillDir = Get-ProjectSkillDir -HostName $h -Root $ProjectPath
            RuleDir  = Get-ProjectRuleDir  -HostName $h -Root $ProjectPath
        }
    }
}

# Several hosts share one directory (codex and agents both use ~/.agents/skills).
# Collapse them so each destination is written once.
$seen = @{}
$plan = @($plan | Where-Object {
    $key = "$($_.SkillDir)|$($_.RuleDir)"
    if ($seen.ContainsKey($key)) { $false } else { $seen[$key] = $true; $true }
})

Write-Host ">>> Target: $Target" -ForegroundColor Cyan
if ($DryRun) { Write-Host ">>> DRY RUN - nothing will be written" -ForegroundColor Yellow }
foreach ($entry in $plan) {
    $ruleNote = if ($entry.RuleDir) { $entry.RuleDir } else { "(no native rule dir; use AGENTS.md)" }
    Write-Host "    $($entry.Host): skills=$($entry.SkillDir) rules=$ruleNote" -ForegroundColor DarkGray
}

# ---------------------------------------------------------------- 1. own skills
# With -Skill, copy only that skill (it may be an own skill). Otherwise copy the whole own set.
$OwnSkillDirs = @(Get-ChildItem -Directory -Path (Join-Path $RepoRoot "skills"))
$OwnMatch = $null
if ($Skill) { $OwnMatch = $OwnSkillDirs | Where-Object { $_.Name -eq $Skill } | Select-Object -First 1 }

Write-Host "--> Syncing own skills..." -ForegroundColor Green
if ($Skill -and -not $OwnMatch) {
    Write-Host "    (skill '$Skill' is not an own skill - skipping the own-skill set)" -ForegroundColor DarkGray
} else {
    $OwnToCopy = if ($OwnMatch) { @($OwnMatch) } else { $OwnSkillDirs }
    foreach ($entry in $plan) {
        if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $entry.SkillDir | Out-Null }
        foreach ($d in $OwnToCopy) {
            Copy-SkillFlat -SkillDir $d.FullName -Destination $entry.SkillDir
        }
    }
}

# ---------------------------------------------------------------- 2. external skills
$ExternalDir = Join-Path $RepoRoot "_external"
if (Test-Path $ExternalDir) {
    Write-Host "--> Syncing external skills..." -ForegroundColor Green

    if ($Skill) {
        Write-Host "    Filtering by skill: $Skill" -ForegroundColor Cyan
        $found = Get-ChildItem -Path $ExternalDir -Filter "SKILL.md" -Recurse |
            Where-Object { $_.Directory.Name -eq $Skill } | Select-Object -First 1
        if (-not $found) {
            if ($OwnMatch) {
                Write-Host "    (owned skill '$Skill' was copied from the skills/ folder)" -ForegroundColor DarkGray
            } else {
                Write-Warning "Skill '$Skill' not found in the _external library or in skills/."
            }
        } else {
            foreach ($entry in $plan) {
                if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $entry.SkillDir | Out-Null }
                Copy-SkillFlat -SkillDir $found.Directory.FullName -Destination $entry.SkillDir
            }
        }
    } elseif ($Category) {
        Write-Host "    Filtering by category: $Category" -ForegroundColor Cyan
        $catPath = Join-Path $ExternalDir $Category
        if (-not (Test-Path $catPath)) {
            Write-Warning "Category '$Category' not found in the _external library."
        } else {
            $matches = Get-ChildItem -Path $catPath -Filter "SKILL.md" -Recurse
            foreach ($entry in $plan) {
                if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $entry.SkillDir | Out-Null }
                foreach ($m in $matches) {
                    Copy-SkillFlat -SkillDir $m.Directory.FullName -Destination $entry.SkillDir
                }
            }
        }
    } elseif ($Target -eq "global") {
        # Global scope stays small on purpose: only portable, low-risk, widely useful skills.
        $GlobalExternal = @("docx", "pptx", "pdf", "xlsx", "skill-creator")
        Write-Host "    Installing the default global bundle: $($GlobalExternal -join ', ')" -ForegroundColor Cyan
        foreach ($entry in $plan) {
            if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $entry.SkillDir | Out-Null }
            foreach ($gSkill in $GlobalExternal) {
                $found = Get-ChildItem -Path $ExternalDir -Filter "SKILL.md" -Recurse |
                    Where-Object { $_.Directory.Name -eq $gSkill } | Select-Object -First 1
                if ($found) {
                    Copy-SkillFlat -SkillDir $found.Directory.FullName -Destination $entry.SkillDir
                } else {
                    Write-Warning "Global external skill '$gSkill' not found in _external."
                }
            }
        }
    } else {
        # Project scope with no filter: the whole library. Usually NOT what you want -
        # prefer the curated set chosen by the project-charter skill.
        Write-Warning "No -Skill or -Category given: copying ALL external skills into the project."
        Write-Warning "This can exceed the project context budget. Prefer -Skill <name> for a curated set."
        $matches = Get-ChildItem -Path $ExternalDir -Filter "SKILL.md" -Recurse
        foreach ($entry in $plan) {
            if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $entry.SkillDir | Out-Null }
            foreach ($m in $matches) {
                Copy-SkillFlat -SkillDir $m.Directory.FullName -Destination $entry.SkillDir
            }
        }
    }
}

# ---------------------------------------------------------------- 3. rules
Write-Host "--> Syncing rules..." -ForegroundColor Green
$ruleHosts = @($plan | Where-Object { $_.RuleDir })
if ($ruleHosts.Count -eq 0) {
    Write-Host "    (no host in this selection reads a native rules directory; always-on rules belong in AGENTS.md)" -ForegroundColor DarkGray
}
foreach ($entry in $ruleHosts) {
    if (-not $DryRun) { New-Item -ItemType Directory -Force -Path $entry.RuleDir | Out-Null }
    Copy-Rules -Destination $entry.RuleDir -HostName $entry.Host
}

# ---------------------------------------------------------------- summary
Write-Host ""
if ($DryRun) {
    Write-Host ">>> Dry run complete: $($script:CopiedCount) would be written, $($script:SkippedCount) skipped." -ForegroundColor Yellow
} else {
    Write-Host ">>> Synchronization completed: $($script:CopiedCount) written, $($script:SkippedCount) skipped." -ForegroundColor Yellow
    Write-Host "    Note: Claude Code does not read .agents/skills/ - include the 'claude' host to mirror skills." -ForegroundColor DarkGray
}
