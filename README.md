# Antigravity Team Skills & Rules Repository

Kho lưu trữ tập trung các **Skills** (năng lực / quy trình nghiệp vụ) và **Rules** (tiêu chuẩn / quy tắc cốt lõi) dùng chung cho các AI Agent trong Google Antigravity & Gemini CLI.

> 📖 **Xem thêm**: Đọc [PROJECT.md](file:///e:/Program%20Files/AI%20Skills/Skills/PROJECT.md) để hiểu rõ mục đích dự án, triết lý vận hành và cam kết cải tiến liên tục của team.

---

## 📂 Cấu trúc Repository

```text
Skills/
├── .gitignore
├── README.md
├── sync.ps1                     # Script đồng bộ 1 chạm cho thành viên team
├── skills/                      # Danh mục các AI Skills
│   ├── codegraph/               # Phân tích semantic code & chống trùng lặp code
│   ├── git-clean-workflow/      # Quy chuẩn Git sạch, zero AI watermark, danh tính dev
│   ├── mistake-memory/          # Hệ thống ghi nhớ và phòng ngừa lỗi lặp lại
│   ├── multi-model-orchestration/ # Điều phối phân việc cho 7 model AI
│   ├── orimise-deep-planning/   # Phân tích sâu & lập kế hoạch qua Orimise API
│   └── playwright/              # Kiểm thử E2E & tự động hóa trình duyệt
└── rules/                       # Danh mục các Rules chung
    ├── codegraph-intelligence.md
    ├── destructive-operations-safety.md
    ├── git-author-clean-code.md
    ├── multi-model-orchestration.md
    ├── multi_model_escalation.md
    ├── orimise-model-routing.md
    ├── plan-approval-first.md
    └── project-initialization.md
```

---

## 🛠 Danh mục Skills

| Skill | Mục đích chính | Tệp chính |
| :--- | :--- | :--- |
| **`codegraph`** | Phân tích call graph, callers/callees, blast radius và chống code duplicate bằng SQLite graph cục bộ. | `skills/codegraph/SKILL.md` |
| **`git-clean-workflow`** | Đảm bảo commit sạch, commit conventional, loại bỏ toàn bộ AI attribution tags / watermark. | `skills/git-clean-workflow/SKILL.md` |
| **`mistake-memory`** | Ledger tự học ghi nhận các lỗi coding từng gặp, phân tích nguyên nhân gốc rễ và tự động kiểm tra trước khi code. | `skills/mistake-memory/SKILL.md` |
| **`multi-model-orchestration`** | Bộ điều phối phân bổ công việc tối ưu chi phí & chất lượng giữa 7 mô hình AI (Flash, Pro, Sonnet, Opus...). | `skills/multi-model-orchestration/SKILL.md` |
| **`orimise-deep-planning`** | Ủy quyền phân tích cấp cao và gỡ bug khó qua Orimise API khi agent cục bộ bế tắc. | `skills/orimise-deep-planning/SKILL.md` |
| **`playwright-testing`** | Hướng dẫn agent test giao diện web, cào dữ liệu và E2E testing qua Playwright CLI / MCP / Library. | `skills/playwright/SKILL.md` |

---

## 📜 Danh mục Rules

| Rule | Mô tả |
| :--- | :--- |
| **`codegraph-intelligence.md`** | Bắt buộc kiểm tra symbol hiện có và blast radius trước khi viết hàm mới hoặc refactor. |
| **`destructive-operations-safety.md`** | Tuyệt đối cấm tự ý xóa tệp/thư mục mà không có xác nhận rõ ràng từ lập trình viên. |
| **`git-author-clean-code.md`** | Quy định danh tính author và nghiêm cấm gắn trailer AI (`Co-authored-by`, `Generated-by`). |
| **`multi-model-orchestration.md`** | Phân loại độ phức tạp công việc trước khi giao cho model phù hợp. |
| **`multi_model_escalation.md`** | Cơ chế tự động leo thang lên model tư duy cao cấp (Sonnet/Opus) khi gặp bài toán khó. |
| **`orimise-model-routing.md`** | Các giới hạn an toàn token và định tuyến model khi dùng Orimise API. |
| **`plan-approval-first.md`** | Bắt buộc lập kế hoạch và chờ duyệt trước khi thực thi thay đổi mã nguồn. |
| **`project-initialization.md`** | Quy trình khởi tạo scaffolding (`.agents/`, `AGENTS.md`) khi agent vào dự án mới. |

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng cho Thành viên Team

### Cách 1: Đồng bộ vào máy cá nhân (Global Scope - Khuyên dùng)
Áp dụng cho mọi dự án mở trong Antigravity trên máy của bạn:

Chạy lệnh PowerShell tại thư mục repo này:
```powershell
.\sync.ps1 -Target global
```
*Tất cả skills và rules sẽ được copy trực tiếp vào `~/.gemini/config/skills` và `~/.gemini/config/rules`.*

---

### Cách 2: Đồng bộ vào một Project cụ thể (Project Scope)
Nếu chỉ muốn áp dụng bộ skills/rules cho một repo dự án xác định:

```powershell
.\sync.ps1 -Target project -ProjectPath "D:\Path\To\YourProject"
```
*Tệp sẽ được đồng bộ vào thư mục `YourProject/.agents/skills/` và `YourProject/.agents/rules/`.*

---

## 🔄 Quy trình Đóng góp & Cập nhật (Contribution Workflow)

1. Khi bạn tối ưu một quy trình hoặc bổ sung Skill mới, hãy thêm vào thư mục `skills/<tên-skill>/SKILL.md`.
2. Kiểm tra format YAML Frontmatter:
   ```markdown
   ---
   name: <ten-skill-chu-thuong-gach-noi>
   description: >-
     Mô tả ngắn gọn chức năng của skill và trường hợp agent nên kích hoạt.
   ---
   ```
3. Commit và push lên Git:
   ```bash
   git add .
   git commit -m "feat(skills): add <ten-skill> skill for team"
   git push origin main
   ```
4. Các thành viên khác chỉ cần `git pull` và chạy lại `.\sync.ps1 -Target global` để nhận bản cập nhật mới nhất.
