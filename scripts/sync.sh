#!/usr/bin/env bash
# Synchronize Skills and Rules into one or more AI Agent hosts (Linux / macOS).
#
# Usage:
#   ./sync.sh                                    # Antigravity global (legacy default)
#   ./sync.sh --target global --hosts all
#   ./sync.sh --target global --hosts claude,codex
#   ./sync.sh --target project --project /path/to/proj --hosts all
#   ./sync.sh --target project --project /path/to/proj --skill react-patterns --hosts agents,claude
#   ./sync.sh --target project --project /path/to/proj --category 08-languages-frameworks --dry-run
#
# Skill install paths (verified 2026-10):
#   antigravity  ~/.gemini/config/skills            rules -> ~/.gemini/config/rules
#   claude       ~/.claude/skills                   rules -> ~/.claude/rules
#   codex        ~/.agents/skills                   (no rule dir; always-on lives in AGENTS.md)
#   cursor       ~/.cursor/skills                   (no rule dir)
#   agents       ~/.agents/skills                   shared by Codex/Cursor/Antigravity-compatible tools
#   dsh          $DSH_HOME/skills (fallback ~/.dsh/skills)
# Project targets always write .agents/skills (+ .claude/skills for the claude host).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

TARGET="global"
PROJECT_PATH=""
SKILL=""
CATEGORY=""
HOSTS=""
DRY_RUN=0
FORCE=0

ALL_HOSTS=("antigravity" "claude" "codex" "cursor" "agents" "dsh")

usage() {
    sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 0
}

# ------------------------------------------------------------------ arg parsing
while [ $# -gt 0 ]; do
    case "$1" in
        --target)   TARGET="${2:-}"; shift 2 ;;
        --project)  PROJECT_PATH="${2:-}"; shift 2 ;;
        --skill)    SKILL="${2:-}"; shift 2 ;;
        --category) CATEGORY="${2:-}"; shift 2 ;;
        --hosts)    HOSTS="${2:-}"; shift 2 ;;
        --dry-run)  DRY_RUN=1; shift ;;
        --force)    FORCE=1; shift ;;
        -h|--help)  usage ;;
        # legacy positional form: ./sync.sh global|project [project-path]
        global|project)
            TARGET="$1"
            if [ "$TARGET" = "project" ] && [ $# -ge 2 ]; then PROJECT_PATH="$2"; shift; fi
            shift ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

if [ "$TARGET" != "global" ] && [ "$TARGET" != "project" ]; then
    echo "Error: --target must be 'global' or 'project'" >&2
    exit 1
fi

# ------------------------------------------------------------------ host helpers
resolve_hosts() {
    local requested="$1" out=()
    if [ -z "$requested" ]; then
        if [ "$TARGET" = "global" ]; then echo "antigravity"; else echo "agents"; fi
        return
    fi
    IFS=',' read -r -a parts <<< "$requested"
    for p in "${parts[@]}"; do
        p="$(echo "$p" | tr '[:upper:]' '[:lower:]' | xargs)"
        if [ -z "$p" ]; then continue; fi
        if [ "$p" = "all" ]; then out+=("${ALL_HOSTS[@]}"); continue; fi
        local known=0
        for h in "${ALL_HOSTS[@]}"; do if [ "$h" = "$p" ]; then known=1; fi; done
        if [ "$known" -eq 0 ]; then
            echo "Error: unknown host '$p'. Valid: ${ALL_HOSTS[*]}, all" >&2
            exit 1
        fi
        out+=("$p")
    done
    printf '%s\n' "${out[@]}" | awk '!seen[$0]++'
}

global_skill_dir() {
    case "$1" in
        antigravity) echo "$HOME/.gemini/config/skills" ;;
        claude)      echo "$HOME/.claude/skills" ;;
        codex)       echo "$HOME/.agents/skills" ;;
        cursor)      echo "$HOME/.cursor/skills" ;;
        agents)      echo "$HOME/.agents/skills" ;;
        dsh)         if [ -n "${DSH_HOME:-}" ]; then echo "$DSH_HOME/skills"; else echo "$HOME/.dsh/skills"; fi ;;
    esac
}

global_rule_dir() {
    # Only Antigravity and Claude Code have a native rules directory.
    case "$1" in
        antigravity) echo "$HOME/.gemini/config/rules" ;;
        claude)      echo "$HOME/.claude/rules" ;;
        *)           echo "" ;;
    esac
}

project_skill_dir() {
    if [ "$1" = "claude" ]; then echo "$2/.claude/skills"; else echo "$2/.agents/skills"; fi
}

project_rule_dir() {
    if [ "$1" = "claude" ]; then echo "$2/.claude/rules"; else echo "$2/.agents/rules"; fi
}

# ------------------------------------------------------------------ copy helpers
COPIED=0
SKIPPED=0

copy_tree() {
    # copy_tree <src-dir> <dest-dir>
    local src="$1" dest="$2"
    mkdir -p "$dest"
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude='.git' --exclude='.env*' --exclude='*.key' --exclude='*.pem' \
            "$src/" "$dest/"
    else
        rm -rf "$dest"
        mkdir -p "$dest"
        cp -R "$src/." "$dest/"
        find "$dest" \( -name '.git' -o -name '.env*' -o -name '*.key' -o -name '*.pem' \) \
            -prune -exec rm -rf {} + 2>/dev/null || true
    fi
}

copy_skill() {
    # copy_skill <skill-dir> <dest-root>
    local skill_dir="$1" dest_root="$2"
    [ -f "$skill_dir/SKILL.md" ] || return 0
    local name target_dir
    name="$(basename "$skill_dir")"
    target_dir="$dest_root/$name"

    if [ -e "$target_dir" ]; then
        if [ "$FORCE" -eq 0 ]; then
            echo "    = [Skip] $name (already exists at $target_dir; use --force to overwrite)"
            SKIPPED=$((SKIPPED + 1))
            return 0
        fi
        if [ "$DRY_RUN" -eq 0 ]; then rm -rf "$target_dir"; fi
    fi

    if [ "$DRY_RUN" -eq 1 ]; then
        echo "    ~ [DryRun] $name -> $target_dir"
    else
        copy_tree "$skill_dir" "$target_dir"
        echo "    + [Skill] $name -> $target_dir"
    fi
    COPIED=$((COPIED + 1))
}

copy_rules() {
    # copy_rules <dest-dir>
    local dest="$1"
    [ -d "$REPO_ROOT/rules" ] || return 0
    if [ "$DRY_RUN" -eq 0 ]; then mkdir -p "$dest"; fi
    for f in "$REPO_ROOT"/rules/*; do
        [ -f "$f" ] || continue
        local base size
        base="$(basename "$f")"
        size=$(wc -c < "$f" | tr -d ' ')
        if [ "$size" -gt 24000 ]; then
            echo "    ! Rule '$base' is $size bytes (> 24000); Antigravity truncates it." >&2
        fi
        if [ "$DRY_RUN" -eq 1 ]; then
            echo "    ~ [DryRun] rule $base -> $dest"
        else
            cp -f "$f" "$dest/$base"
        fi
    done
}

# ------------------------------------------------------------------ resolve plan
# Validate in the parent shell: resolve_hosts runs inside a process substitution,
# so an `exit` there would only kill the subshell and the script would do nothing.
validate_hosts() {
    local requested="$1"
    if [ -z "$requested" ]; then return 0; fi
    local parts=() p known h
    IFS=',' read -r -a parts <<< "$requested"
    for p in "${parts[@]}"; do
        p="$(echo "$p" | tr '[:upper:]' '[:lower:]' | xargs)"
        if [ -z "$p" ]; then continue; fi
        if [ "$p" = "all" ]; then continue; fi
        known=0
        for h in "${ALL_HOSTS[@]}"; do if [ "$h" = "$p" ]; then known=1; fi; done
        if [ "$known" -eq 0 ]; then
            echo "Error: unknown host '$p'. Valid: ${ALL_HOSTS[*]}, all" >&2
            exit 1
        fi
    done
}
validate_hosts "$HOSTS"

# bash 3.2 (macOS default) has no mapfile, so read the hosts line by line.
RESOLVED=()
while IFS= read -r _line; do
    if [ -n "$_line" ]; then RESOLVED+=("$_line"); fi
done < <(resolve_hosts "$HOSTS")
if [ "${#RESOLVED[@]}" -eq 0 ]; then
    echo "Error: no target hosts resolved." >&2
    exit 1
fi

if [ "$TARGET" = "project" ] && [ -z "$PROJECT_PATH" ]; then
    echo "Error: --project <path> is required for --target project" >&2
    exit 1
fi
if [ "$TARGET" = "project" ] && [ ! -d "$PROJECT_PATH" ]; then
    echo "Error: project path not found: $PROJECT_PATH" >&2
    exit 1
fi

echo ">>> Target: $TARGET"
if [ "$DRY_RUN" -eq 1 ]; then echo ">>> DRY RUN - nothing will be written"; fi

declare -a SKILL_DIRS=() RULE_DIRS=() HOST_NAMES=()
for h in "${RESOLVED[@]}"; do
    if [ "$TARGET" = "global" ]; then
        sd="$(global_skill_dir "$h")"; rd="$(global_rule_dir "$h")"
    else
        sd="$(project_skill_dir "$h" "$PROJECT_PATH")"; rd="$(project_rule_dir "$h" "$PROJECT_PATH")"
    fi
    # Several hosts share one directory (codex and agents both use ~/.agents/skills).
    # Collapse them so each destination is written once.
    # (Indexed while-loop instead of "${!arr[@]}": that form breaks under `set -u` on bash 3.2.)
    dup=0
    j=0
    while [ "$j" -lt "${#SKILL_DIRS[@]}" ]; do
        if [ "${SKILL_DIRS[$j]}" = "$sd" ] && [ "${RULE_DIRS[$j]}" = "$rd" ]; then dup=1; break; fi
        j=$((j + 1))
    done
    if [ "$dup" -eq 1 ]; then continue; fi
    HOST_NAMES+=("$h"); SKILL_DIRS+=("$sd"); RULE_DIRS+=("$rd")
    echo "    $h: skills=$sd rules=${rd:-(no native rule dir; use AGENTS.md)}"
done

# ------------------------------------------------------------------ 1. own skills
# With --skill, copy only that skill (it may be an own skill). Otherwise copy the whole own set.
OWN_MATCH=""
if [ -n "$SKILL" ] && [ -d "$REPO_ROOT/skills/$SKILL" ]; then OWN_MATCH="$REPO_ROOT/skills/$SKILL"; fi

echo "--> Syncing own skills..."
if [ -n "$SKILL" ] && [ -z "$OWN_MATCH" ]; then
    echo "    (skill '$SKILL' is not an own skill - skipping the own-skill set)"
else
    if [ -n "$OWN_MATCH" ]; then
        OWN_LIST=("$OWN_MATCH")
    else
        OWN_LIST=("$REPO_ROOT"/skills/*/)
    fi
    for dest in "${SKILL_DIRS[@]}"; do
        for d in "${OWN_LIST[@]}"; do
            [ -d "$d" ] || continue
            copy_skill "${d%/}" "$dest"
        done
    done
fi

# ------------------------------------------------------------------ 2. external skills
if [ -d "$REPO_ROOT/_external" ]; then
    echo "--> Syncing external skills..."
    if [ -n "$SKILL" ]; then
        echo "    Filtering by skill: $SKILL"
        found="$(find "$REPO_ROOT/_external" -type d -name "$SKILL" | head -n 1 || true)"
        if [ -z "$found" ] || [ ! -f "$found/SKILL.md" ]; then
            if [ -n "$OWN_MATCH" ]; then
                echo "    (owned skill '$SKILL' was copied from the skills/ folder)"
            else
                echo "    ! Skill '$SKILL' not found in the _external library or in skills/." >&2
            fi
        else
            for dest in "${SKILL_DIRS[@]}"; do copy_skill "$found" "$dest"; done
        fi
    elif [ -n "$CATEGORY" ]; then
        echo "    Filtering by category: $CATEGORY"
        cat_path="$REPO_ROOT/_external/$CATEGORY"
        if [ ! -d "$cat_path" ]; then
            echo "    ! Category '$CATEGORY' not found in the _external library." >&2
        else
            while IFS= read -r sf; do
                sdir="$(dirname "$sf")"
                for dest in "${SKILL_DIRS[@]}"; do copy_skill "$sdir" "$dest"; done
            done < <(find "$cat_path" -name 'SKILL.md')
        fi
    elif [ "$TARGET" = "global" ]; then
        GLOBAL_EXTERNAL=("docx" "pptx" "pdf" "xlsx" "skill-creator")
        echo "    Installing the default global bundle: ${GLOBAL_EXTERNAL[*]}"
        for g in "${GLOBAL_EXTERNAL[@]}"; do
            found="$(find "$REPO_ROOT/_external" -type d -name "$g" | head -n 1 || true)"
            if [ -n "$found" ] && [ -f "$found/SKILL.md" ]; then
                for dest in "${SKILL_DIRS[@]}"; do copy_skill "$found" "$dest"; done
            else
                echo "    ! Global external skill '$g' not found in _external." >&2
            fi
        done
    else
        echo "    ! No --skill or --category given: copying ALL external skills into the project." >&2
        echo "    ! Prefer --skill <name> for a curated set chosen by the project-charter skill." >&2
        while IFS= read -r sf; do
            sdir="$(dirname "$sf")"
            for dest in "${SKILL_DIRS[@]}"; do copy_skill "$sdir" "$dest"; done
        done < <(find "$REPO_ROOT/_external" -name 'SKILL.md')
    fi
fi

# ------------------------------------------------------------------ 3. rules
echo "--> Syncing rules..."
any_rules=0
k=0
while [ "$k" -lt "${#HOST_NAMES[@]}" ]; do
    rd="${RULE_DIRS[$k]}"
    if [ -n "$rd" ]; then any_rules=1; copy_rules "$rd"; fi
    k=$((k + 1))
done
if [ "$any_rules" -eq 0 ]; then
    echo "    (no host in this selection reads a native rules directory; always-on rules belong in AGENTS.md)"
fi

# ------------------------------------------------------------------ summary
echo ""
if [ "$DRY_RUN" -eq 1 ]; then
    echo ">>> Dry run complete: $COPIED would be written, $SKIPPED skipped."
else
    echo ">>> Synchronization completed: $COPIED written, $SKIPPED skipped."
    echo "    Note: Claude Code does not read .agents/skills/ - include the 'claude' host to mirror skills."
fi
