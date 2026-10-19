#!/usr/bin/env bash
# Script đồng bộ Skills và Rules vào Antigravity / Gemini CLI trên Linux / macOS
set -e

TARGET="${1:-global}"
PROJECT_PATH="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

if [ "$TARGET" = "global" ]; then
    DEST_ROOT="$HOME/.gemini/config"
    DEST_SKILLS="$DEST_ROOT/skills"
    DEST_RULES="$DEST_ROOT/rules"
    echo ">>> Đang đồng bộ vào cấu hình Global: $DEST_ROOT"
else
    if [ -z "$PROJECT_PATH" ]; then
        echo "Lỗi: Vui lòng truyền đường dẫn dự án: ./sync.sh project /path/to/project"
        exit 1
    fi
    DEST_ROOT="$PROJECT_PATH/.agents"
    DEST_SKILLS="$DEST_ROOT/skills"
    DEST_RULES="$DEST_ROOT/rules"
    echo ">>> Đang đồng bộ vào Project: $DEST_ROOT"
fi

mkdir -p "$DEST_SKILLS"
mkdir -p "$DEST_RULES"

echo "--> Đồng bộ các skills nội bộ..."
rsync -av --exclude=".*" --exclude="*.key" --exclude="*.pem" "$REPO_ROOT/skills/" "$DEST_SKILLS/"

if [ -d "$REPO_ROOT/_external" ]; then
    echo "--> Đồng bộ các skills external..."
    if [ "$TARGET" = "global" ]; then
        # Mặc định ở global mode chỉ đồng bộ các core external skills
        GLOBAL_EXTERNAL=("docx" "pptx" "pdf" "xlsx" "skill-creator")
        for gSkill in "${GLOBAL_EXTERNAL[@]}"; do
            found_dir=$(find "$REPO_ROOT/_external" -type d -name "$gSkill" | head -n 1)
            if [ -n "$found_dir" ] && [ -f "$found_dir/SKILL.md" ]; then
                echo "    + [Skill] $gSkill -> $DEST_SKILLS/$gSkill"
                rsync -av --exclude=".*" --exclude="*.key" --exclude="*.pem" "$found_dir/" "$DEST_SKILLS/$gSkill/"
            fi
        done
    else
        # Ở project mode: sao chép phẳng từng skill vào destination
        find "$REPO_ROOT/_external" -name "SKILL.md" | while read -r skill_file; do
            s_dir="$(dirname "$skill_file")"
            s_name="$(basename "$s_dir")"
            rsync -av --exclude=".*" --exclude="*.key" --exclude="*.pem" "$s_dir/" "$DEST_SKILLS/$s_name/"
        done
    fi
fi

echo "--> Đồng bộ các rules..."
rsync -av --exclude=".*" --exclude="*.key" --exclude="*.pem" "$REPO_ROOT/rules/" "$DEST_RULES/"

echo ">>> Hoàn tất đồng bộ thành công!"
