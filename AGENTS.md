# AI Agent Guidelines — Team Skills & Rules Hub

Chào mừng Agent. Bạn đang làm việc trong repository **Single Source of Truth (SSOT)** chứa toàn bộ các **Skills** và **Rules** chuẩn hóa của đội ngũ kỹ thuật.

Mọi hành động tạo mới, cập nhật hoặc sửa đổi nội dung trong workspace này **bắt buộc tuân thủ nghiêm ngặt** các quy chuẩn dưới đây:

---

## 1. Bản chất & Vai trò của Workspace này

- Đây **không phải** là một dự án phần mềm ứng dụng thông thường. Đây là **kho tri thức và quy chuẩn hành vi (Meta-knowledge & Engineering Standards)** cho các AI Agent.
- Bất kỳ thay đổi nào trong repository này sẽ ảnh hưởng trực tiếp đến hành vi của AI Agent trên toàn bộ các dự án khác của team sau khi đồng bộ.
- Yêu cầu cốt lõi: **Chính xác, cô đọng, bảo mật và loại bỏ hoàn toàn ảo giác (Zero-Hallucination).**

---

## 2. Quy chuẩn bắt buộc khi Tạo mới hoặc Cập nhật Skill

Mọi skill mới hoặc được tinh chỉnh trong thư mục `skills/<skill_name>/` phải tuân theo cấu trúc chuẩn của Antigravity:

### 2.1 Cấu trúc thư mục Skill
```text
skills/<skill_name>/
├── SKILL.md             # (Bắt buộc) File chỉ dẫn chính với YAML Frontmatter
├── scripts/             # (Tùy chọn) Script tự động hóa có thể chạy được (Python, Bash, PS1)
├── references/          # (Tùy chọn) Tài liệu tra cứu chi tiết, framework, bảng so sánh
└── examples/            # (Tùy chọn) Mẫu code minh họa hoặc template
```

### 2.2 Quy chuẩn `SKILL.md` và YAML Frontmatter
* Phần đầu file bắt buộc có block YAML Frontmatter:
  ```markdown
  ---
  name: <ten-skill-chu-thuong-gach-noi>
  description: >-
    Mô tả rõ ràng: (1) Skill này làm gì, (2) KHI NÀO agent cần kích hoạt skill này.
    Dùng ngôi thứ ba (Third-person).
  ---
  ```
* **Trường `description` là quan trọng nhất**: Agent dựa vào mô tả này để quyết định có kích hoạt skill hay không. Phải ghi rõ điều kiện kích hoạt cụ thể (trigger scenarios).

### 2.3 Nguyên tắc Progressive Disclosure (Bảo vệ Token)
* **Tuyệt đối không** dồn tài liệu dài hàng nghìn dòng vào `SKILL.md`.
* `SKILL.md` chỉ đóng vai trò là "Runbook": tóm tắt quy trình các bước (Workflow steps), lệnh mẫu và điều kiện kiểm chứng.
* Các tài liệu chuyên sâu, bảng đối chiếu dài phải tách sang thư mục `references/<doc_name>.md` và tạo link markdown trỏ tới. Agent chỉ đọc file reference khi thực sự cần.

---

## 3. Quy chuẩn khi Tạo mới hoặc Sửa đổi Rule

* Các file rule đặt trong thư mục `rules/<rule-name>.md`.
* Ngắn gọn, có tính bắt buộc cao (Declarative constraints), chỉ nêu rõ:
  * **Luật cứng (Hard constraints)**: Điều cấm làm (P0).
  * **Hành vi chuẩn (Standard behavior)**: Trình tự xử lý đúng.
  * **Biện pháp phòng ngừa (Safeguards)**.

---

## 3b. Tính Portable Đa Agent (Antigravity · Claude Code · Codex · Cursor · DSH)

Mọi skill/rule trong repo này phải chạy được trên nhiều agent, không chỉ Antigravity:

1. **Chỉ dùng 6 khóa frontmatter portable**: `name`, `description`, `license`, `compatibility`,
   `metadata`, `allowed-tools`. TUYỆT ĐỐI không dùng khóa riêng của Claude Code
   (`disable-model-invocation`, `user-invocable`, `paths`, `context`, `agent`, `hooks`, `model`,
   `argument-hint`, `when_to_use`…) — chúng bị bỏ qua hoặc gây lỗi cứng khi đóng gói.
2. **Không dùng biến thay thế riêng của Claude** trong khối lệnh: `${CLAUDE_SKILL_DIR}`,
   `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `$ARGUMENTS`.
3. **Không phụ thuộc slash command, hook, subagent hay MCP** cho luồng chính — mỗi agent định nghĩa
   chúng khác nhau. Cơ chế kích hoạt portable duy nhất là khớp `description`.
4. **`name` phải trùng tên thư mục**, ≤ 64 ký tự, chữ thường + gạch nối. Đặt tên duy nhất để tránh
   xung đột thứ tự ưu tiên (các agent quy định khác nhau).
5. **Giới hạn kích thước**: `SKILL.md` < 500 dòng; mỗi file rule ≤ 24 KB; `.agents/rules/` phẳng
   1 cấp; tổng rule always-on dưới 20.000 token.
6. **Trong dự án**, rule bất biến phải nằm ở `AGENTS.md` gốc — file duy nhất mọi agent đều đọc.
   Chi tiết tách vào `.agents/rules/*.md`. Nếu phục vụ Claude Code thì thêm `CLAUDE.md` chứa đúng
   `@AGENTS.md` (import, **không** symlink) và mirror skill sang `.claude/skills/`.

Chi tiết đầy đủ + bảng đường dẫn từng host: `skills/project-charter/references/project-layout.md`.

---

## 4. Bảo mật & An toàn Dữ liệu (Security P0)

1. **Tuyệt đối không lưu trữ Secret**:
   * Nghiêm cấm commit API keys (`sk-...`, `AIza...`), tokens, mật khẩu, file `.env`, chứng chỉ private keys vào git.
   * File cấu hình chạy thử phải dùng placeholder hoặc đọc từ biến môi trường / đường dẫn người dùng (`~/.gemini/config/...`).
2. **Quy tắc An toàn Thao tác (Destructive Operations)**:
   * Không bao giờ tự ý chạy các lệnh xóa file hàng loạt (`Remove-Item`, `rm -rf`, `git clean -fd`) mà không hỏi ý kiến người dùng.

---

## 5. Quy chuẩn Git Sạch (Zero AI Footprint)

Khi commit hoặc push mã nguồn trong repository này:
- **Tác giả (Author)**: Đảm bảo sử dụng danh tính người dùng (`git config user.name` và `user.email`).
- **Commit Message**: Tuân thủ chuẩn Conventional Commits:
  - `feat(skill): add <name> skill ...`
  - `fix(rules): update safety checks for ...`
  - `docs: update contribution guide in README`
- **Zero AI Watermarks**: Nghiêm cấm chèn:
  - ❌ `// Generated by AI` / `/* Antigravity */`
  - ❌ `Co-authored-by: Antigravity <...>`
  - ❌ `Signed-off-by: AI Assistant`

---

## 6. Vòng lặp Cải tiến Liên tục (Continuous Improvement)

Mỗi khi người dùng chỉnh sửa hoặc góp ý về một sai lầm mà AI mắc phải:
1. Xác định nguyên nhân gốc rễ và phân loại lỗi.
2. Cập nhật ngay vào [`skills/mistake-memory/ledger.md`](file:///e:/Program%20Files/AI%20Skills/Skills/skills/mistake-memory/ledger.md).
3. Đề xuất cập nhật lại `SKILL.md` tương ứng để ngăn chặn triệt để lỗi này trong tương lai.
