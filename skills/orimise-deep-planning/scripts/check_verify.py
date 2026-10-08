#!/usr/bin/env python3
"""
check_verify.py "<lệnh>" - kiểm tra lệnh VERIFY do model ngoài sinh ra.
Exit 0 = nằm trong allowlist (được phép chạy ở thư mục gốc project) | Exit 1 = BỊ CHẶN.
Lưu ý: test/build vẫn chạy code của project, nên diff phải được review trước khi verify.
"""
import re, shlex, sys

BAD_CHARS = re.compile(r"[;&|<>`$(){}\n\r%]")
ALLOW = [
    r"(python3?|py)( -m)? (pytest|unittest|ruff|mypy|flake8|pyright)\b[^;&|<>`$(){}\n\r%]*",
    r"(pytest|mypy|flake8|pyright)\b[^;&|<>`$(){}\n\r%]*",
    r"ruff (check|format --check)\b[^;&|<>`$(){}\n\r%]*",
    r"(npm|pnpm|yarn)( run)? (test|lint|build|typecheck)\b[^;&|<>`$(){}\n\r%]*",
    r"npx (tsc --noEmit|jest|vitest|eslint)\b[^;&|<>`$(){}\n\r%]*",
    r"tsc --noEmit\b[^;&|<>`$(){}\n\r%]*",
    r"go (test|vet|build)\b[^;&|<>`$(){}\n\r%]*",
    r"cargo (test|check|clippy|build)\b[^;&|<>`$(){}\n\r%]*",
    r"dotnet (test|build)\b[^;&|<>`$(){}\n\r%]*",
    r"(mvn|gradle) (test|build|check)\b[^;&|<>`$(){}\n\r%]*",
    r"git (diff|status|apply --check)\b[^;&|<>`$(){}\n\r%]*",
]
BAD_TOKENS = {"-c", "-e", "--eval", "--exec", "--require", "--config-file"}

def check(cmd):
    cmd = cmd.strip()
    if not cmd or len(cmd) > 300: return "rỗng hoặc quá dài"
    if BAD_CHARS.search(cmd): return "chứa ký tự điều khiển shell (; & | < > ` $ ( ) { } %)"
    try: toks = shlex.split(cmd, posix=False)
    except ValueError: return "không parse được"
    for tk in toks:
        t = tk.strip("\"'")
        if ".." in t: return f"token '{tk}' chứa '..'"
        if t.startswith(("/", "~")) or re.match(r"^[A-Za-z]:[\\/]", t): return f"token '{tk}' là đường dẫn tuyệt đối"
        if any(t == b or t.startswith(f"{b}=") or (len(b) == 2 and t.startswith(b)) for b in BAD_TOKENS):
            return f"cờ '{tk}' không được phép"
    if not any(re.fullmatch(rx, cmd) for rx in ALLOW): return "không nằm trong allowlist"
    return None

if __name__ == "__main__":
    reason = check(" ".join(sys.argv[1:]))
    if reason:
        print(f"BLOCKED: {reason}", file=sys.stderr); sys.exit(1)
    print("OK")
