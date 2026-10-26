# Cài đặt và Thiết lập Skills Hub cho Team

Tài liệu này hướng dẫn cài đặt và đồng bộ kho Skills & Rules về môi trường làm việc cá nhân, cho
nhiều AI agent (Antigravity · Claude Code · Codex · Cursor · DeepSeek Harness).

---

## 1. Yêu cầu tiên quyết

- Git
- PowerShell 5.1+ (Windows) hoặc Bash (Linux/macOS). Script bash dùng `rsync` nếu có, tự fallback sang `cp`.
- Ít nhất một AI agent đã cài đặt.

---

## 2. Các bước cài đặt cho thành viên mới

### Bước 1: Clone repository
```bash
git clone <repo-url> skills-repo
cd skills-repo
```

### Bước 2: Đồng bộ Skills và Rules

Windows (PowerShell):
```powershell
# Chỉ Antigravity (mặc định cũ)
.\scripts\sync.ps1 -Target global

# Mọi agent có trên máy
.\scripts\sync.ps1 -Target global -Hosts all

# Chọn cụ thể
.\scripts\sync.ps1 -Target global -Hosts antigravity,claude
```

Linux / macOS:
```bash
chmod +x ./scripts/sync.sh
./scripts/sync.sh --target global --hosts all
```

> 💡 Nếu Windows chặn script (`... is not digitally signed`), chạy một trong hai cách:
> `powershell -ExecutionPolicy Bypass -File .\scripts\sync.ps1 -Target global -Hosts all`
> hoặc `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` trong phiên hiện tại.

### Bước 3: Bảng đường dẫn từng agent

| Host | Skills (global) | Rules (global) | Ghi chú |
| :--- | :--- | :--- | :--- |
| `antigravity` | `~/.gemini/config/skills` | `~/.gemini/config/rules` | Mặc định. CLI dùng `~/.gemini/antigravity-cli/skills` |
| `claude` | `~/.claude/skills` | `~/.claude/rules` | Claude Code **không** đọc `.agents/skills/` |
| `codex` | `~/.agents/skills` | — | Rule always-on nằm trong `AGENTS.md` |
| `cursor` | `~/.cursor/skills` | — | Cursor cũng đọc `.agents/skills/` |
| `agents` | `~/.agents/skills` | — | Thư mục dùng chung; trùng với `codex` nên script tự gộp |
| `dsh` | `$DSH_HOME/skills` (mặc định `~/.dsh/skills`) | — | Đường dẫn skill của DSH chưa được tài liệu hóa chính thức |

Ở project scope (`-Target project`), skill luôn vào `<project>/.agents/skills/`, và mirror thêm vào
`<project>/.claude/skills/` khi chọn host `claude`.

### Bước 4: Cài đặt các kỹ năng bên thứ ba (External Skills)

Kho chứa không commit các kỹ năng bên ngoài để tránh vi phạm bản quyền và lệch phiên bản. Danh sách
phiên bản được khóa tại `skills.lock.md`.

Yêu cầu agent thực thi:
> *"Dùng skill-manager. Cài đặt tất cả các external skills được liệt kê trong file skills.lock.md đúng theo scope đã quy định."*

---

## 3. Khởi tạo một dự án mới (quan trọng nhất)

Sau khi đã có skill `project-charter` ở global scope, chỉ cần mở dự án và nói:

> *"Khởi tạo dự án"* / *"Setup project"* / *"Chuẩn hóa quy trình cho dự án này"*

Agent sẽ tự quét repo, phỏng vấn bạn theo 5 vòng (mục tiêu, kiến trúc, code, **cách làm việc với
bạn**, skill), trình kế hoạch để bạn duyệt, rồi sinh `AGENTS.md` + `.agents/` + cầu nối `CLAUDE.md`.

Kết quả: mọi phiên AI sau đó đều theo đúng quy trình và kiến trúc đã thống nhất.

---

## 4. Quy trình đồng bộ khi repo có bản cập nhật mới

Khi có thông báo cập nhật từ team:

1. `git pull` để kéo skills, rules và `skills.lock.md` mới nhất.
2. Chạy lại sync:
   ```powershell
   .\scripts\sync.ps1 -Target global -Hosts all
   ```
3. Nhờ Agent kiểm tra:
   > *"Dùng skill-manager kiểm tra và cập nhật toàn bộ skills kể cả external skills theo skills.lock.md."*

### Mẹo an toàn

- Thêm `-DryRun` để xem trước những gì sẽ được ghi, không tạo file nào.
- Skill đã tồn tại **không bị ghi đè**; muốn cập nhật phải thêm `-Force`.
- `-Skill <tên>` tìm cả trong `skills/` (nội bộ) lẫn `_external/` (thư viện), nên không cần biết nó ở đâu.
