# Antigravity Team Skills & Rules Repository

Kho lưu trữ tập trung các **Skills** (năng lực / quy trình nghiệp vụ) và **Rules** (tiêu chuẩn / quy tắc cốt lõi) dùng chung cho các AI Agent: Google Antigravity & Gemini CLI, Claude Code, Codex, Cursor, và DeepSeek Harness (DSH).

> 📖 **Xem thêm**: Đọc [PROJECT.md](docs/PROJECT.md) để hiểu rõ mục đích dự án, triết lý vận hành và cam kết cải tiến liên tục của team.

---

## 📂 Cấu trúc Repository

```text
skills-repo/
├── .gitignore
├── LICENSE                          # Giấy phép MIT
├── README.md                        # Giới thiệu & hướng dẫn chung
├── AGENTS.md                        # Quy chuẩn hoạt động cho AI Agent
├── INSTALL.md                       # Hướng dẫn chi tiết cài đặt & đồng bộ cho team
├── REGISTRY.md                      # Sổ đăng ký trạng thái & phạm vi toàn bộ skills
├── skills.lock.md                   # Khóa commit & manifest của external skills
├── scripts/
│   ├── sync.ps1                     # Script đồng bộ 1 chạm (PowerShell)
│   └── sync.sh                      # Script đồng bộ 1 chạm (Bash)
├── docs/
│   └── PROJECT.md                   # Mục đích, kiến trúc và triết lý vận hành
├── skills/                          # Danh mục AI Skills nội bộ (Own skills)
│   ├── anthropic-agent-guide/       # Hướng dẫn thực chiến Claude & Context Engineering
│   ├── codegraph/                   # Phân tích semantic code & chống trùng lặp code
│   ├── git-clean-workflow/          # Quy chuẩn Git sạch, zero AI watermark, danh tính dev
│   ├── mistake-memory/              # Hệ thống ghi nhớ và phòng ngừa lỗi lặp lại
│   ├── multi-model-orchestration/   # Điều phối phân việc cho 7 model AI
│   ├── orimise-deep-planning/       # Phân tích sâu & lập kế hoạch qua Orimise API
│   ├── playwright/                  # Kiểm thử E2E & tự động hóa trình duyệt
│   ├── project-charter/             # Khởi tạo dự án: phỏng vấn, hiến pháp AGENTS.md, chọn skill
│   └── skill-manager/               # Quản lý vòng đời, audit, cài đặt skills
├── rules/                           # Danh mục các Rules chung
│   ├── model-routing.md             # Quy tắc điều phối & leo thang model hợp nhất
│   ├── codegraph-intelligence.md
│   ├── destructive-operations-safety.md
│   ├── git-author-clean-code.md
│   ├── multi-model-orchestration.md
│   ├── multi_model_escalation.md
│   ├── orimise-model-routing.md
│   ├── plan-approval-first.md
│   ├── project-charter.md
│   └── project-initialization.md
├── _external/                       # Thư viện 412 external skills (12 phân loại chức năng)
│   ├── 01-documents/                # Văn phòng (Word, Excel, PowerPoint, PDF)
│   ├── 02-video-multimedia/         # Video summary (BibiGPT, YouTube), Remotion, Manim
│   ├── 03-frontend-ui/              # Thiết kế UI, tokens, themes, web artifacts
│   ├── 04-engineering-workflow/     # TDD, review, superpowers, mattpocock, debugging
│   ├── 05-security-compliance/      # Rà soát bảo mật, audit smart contracts, HIPAA/PHI
│   ├── 06-devops-cloud/             # Docker, K8s, mạng homelab/BGP/VPN, canary
│   ├── 07-agentic-systems/          # Harness AI, autonomous loops, Claude API, MCP
│   ├── 08-languages-frameworks/     # React, Next.js, Vue, Python, Rust, SpringBoot
│   ├── 09-research-analytics/       # Deep research, Exa, OSINT, tài liệu học thuật
│   ├── 10-productivity-meta/        # Tạo skill, /grill-me, /handoff, ops, GitHub
│   ├── 11-business-marketing/       # SEO, viết bài, pitch deck, market intelligence
│   ├── 12-specialized-domains/      # Machine Learning, Logistics/Supply chain, Compute
│   ├── README.md                    # Hướng dẫn chọn & kích hoạt external skill
│   └── CATALOG.md                   # Bảng tra cứu chi tiết toàn bộ 412 skills
└── scratch/                         # Vùng chạy thử tạm thời (gitignored)
```

---

## 🛠 Danh mục Skills

| Skill | Mục đích chính | Tệp chính |
| :--- | :--- | :--- |
| **`project-charter`** | Khởi tạo dự án: quét repo, phỏng vấn về mục tiêu/kiến trúc/code/cách làm việc, sinh `AGENTS.md` + `.agents/` + cầu nối `CLAUDE.md`, và chọn skill cho dự án. | `skills/project-charter/SKILL.md` |
| **`skill-manager`** | Quản lý vòng đời, audit bảo mật, cài đặt và đồng bộ skills theo bundle. | `skills/skill-manager/SKILL.md` |
| **`anthropic-agent-guide`** | Hướng dẫn tối ưu prompt, context engineering, dynamic workflows và chi phí cho Claude. | `skills/anthropic-agent-guide/SKILL.md` |
| **`codegraph`** | Phân tích call graph, callers/callees, blast radius và chống code duplicate bằng SQLite graph cục bộ. | `skills/codegraph/SKILL.md` |
| **`git-clean-workflow`** | Đảm bảo commit sạch, commit conventional, loại bỏ toàn bộ AI attribution tags / watermark. | `skills/git-clean-workflow/SKILL.md` |
| **`mistake-memory`** | Ledger tự học ghi nhận các lỗi coding từng gặp, phân tích nguyên nhân gốc rễ và tự động kiểm tra trước khi code. | `skills/mistake-memory/SKILL.md` |
| **`multi-model-orchestration`** | Bộ điều phối phân bổ công việc tối ưu chi phí & chất lượng giữa 7 mô hình AI (Flash, Pro, Sonnet, Opus...). | `skills/multi-model-orchestration/SKILL.md` |
| **`orimise-deep-planning`** | Ủy quyền phân tích cấp cao và gỡ bug khó qua Orimise API khi agent cục bộ bế tắc. | `skills/orimise-deep-planning/SKILL.md` |
| **`playwright`** | Hướng dẫn agent test giao diện web, cào dữ liệu và E2E testing qua Playwright CLI / MCP / Library. | `skills/playwright/SKILL.md` |

---

## 📜 Danh mục Rules

| Rule | Mô tả |
| :--- | :--- |
| **`project-charter.md`** | Bắt buộc mọi dự án phải có Project Charter trước khi code; quy định layout đa host (`AGENTS.md`, `.agents/`, cầu nối Claude). |
| **`model-routing.md`** | Hợp nhất phân tầng model (Workhorse/Economy/Reasoning/Elite), trần token và chỉ thị leo thang. |
| **`codegraph-intelligence.md`** | Bắt buộc kiểm tra symbol hiện có và blast radius trước khi viết hàm mới hoặc refactor. |
| **`destructive-operations-safety.md`** | Tuyệt đối cấm tự ý xóa tệp/thư mục mà không có xác nhận rõ ràng từ lập trình viên. |
| **`git-author-clean-code.md`** | Quy định danh tính author và nghiêm cấm gắn trailer AI (`Co-authored-by`, `Generated-by`). |
| **`multi-model-orchestration.md`** | Phân loại độ phức tạp công việc trước khi giao cho model phù hợp. |
| **`multi_model_escalation.md`** | Cơ chế tự động leo thang lên model tư duy cao cấp (Sonnet/Opus) khi gặp bài toán khó. |
| **`orimise-model-routing.md`** | Các giới hạn an toàn token và định tuyến model khi dùng Orimise API. |
| **`plan-approval-first.md`** | Bắt buộc lập kế hoạch và chờ duyệt trước khi thực thi thay đổi mã nguồn. |
| **`project-initialization.md`** | Quy trình khởi tạo scaffolding (`.agents/`, `AGENTS.md`) khi agent vào dự án mới. |

---

## 🧭 Quy trình Khởi tạo Dự án (`project-charter`)

Đây là quy trình chuẩn để **mọi phiên AI làm việc trên một dự án đều theo cùng một quy trình, kiến trúc và cách cộng tác**. Chạy một lần khi bắt đầu dự án; các phiên sau chỉ cần đọc lại charter.

**Cách kích hoạt:** chỉ cần nói *"khởi tạo dự án"*, *"setup project"*, *"chuẩn hóa quy trình cho dự án này"*, hoặc mở một repo chưa có `AGENTS.md`. Không cần slash command — skill tự khớp theo mô tả nên chạy được trên mọi agent.

**6 pha:**

| Pha | Nội dung |
| :--- | :--- |
| 0. Recon | Tự quét stack, git, tài liệu sẵn có, host đang dùng. **Không hỏi những gì repo đã trả lời được.** |
| 1. Phỏng vấn | 5 vòng: mục tiêu & phạm vi → kiến trúc → code & chất lượng → **cách làm việc với bạn** → skill & host. Mỗi câu đều có đề xuất mặc định. |
| 2. Kế hoạch | Trình danh sách file sẽ tạo + bảng skill đề xuất (kèm lý do, bằng chứng, nguồn, giấy phép). **Dừng và chờ duyệt.** |
| 3. Sinh file | `AGENTS.md`, `.agents/rules/*.md`, `.agents/context/*`, cầu nối `CLAUDE.md`, cài skill đã duyệt. |
| 4. Kiểm tra | Chạy `validate_charter.py` + checklist trong `references/validation.md`. Báo cáo trung thực, không tuyên bố PASS khống. |
| 5. Bàn giao | Tóm tắt + câu lệnh mở phiên mới: *"Đọc `AGENTS.md` và `.agents/context/charter.md` rồi tiếp tục."* |

**Kiểm tra charter tự động:**

```powershell
python skills/project-charter/scripts/validate_charter.py <duong-dan-project>
python skills/project-charter/scripts/validate_charter.py <duong-dan-project> --claude   # kiểm thêm mirror .claude/
python skills/project-charter/scripts/validate_charter.py <duong-dan-project> --json     # cho CI
```

Script kiểm: sự tồn tại và độ dài `AGENTS.md`, frontmatter skill, mirror `.claude/`, secret lọt vào charter, đường dẫn tuyệt đối cá nhân, placeholder chưa điền, và **`.gitignore` có che mất charter hay không**.

> Về kiểm tra `.gitignore`: khi project là git repo, script hỏi thẳng `git check-ignore --no-index` nên kết quả trùng git. Khi không có git, script dùng fallback mô phỏng quy tắc glob của git; fallback xử lý đúng các pattern thường dùng (`.agents/skills/*`, `!.agents/skills/REGISTRY.md`, `.agents/`, `skills/`, `/AGENTS.md`), nhưng **chưa mô phỏng chính xác dạng `dir/**/`** và sẽ cảnh báo `WARN Ignore check` khi phải dùng fallback.

**Cấu trúc sinh ra trong dự án:**

```text
<project>/
├── AGENTS.md                  # Hiến pháp: bất biến + mục lục (mọi agent đều đọc)
├── CLAUDE.md                  # Chỉ chứa "@AGENTS.md" (chỉ khi dùng Claude Code)
└── .agents/
    ├── rules/*.md             # Rule luôn bật, phẳng, có frontmatter
    ├── context/charter.md     # Câu trả lời phỏng vấn
    ├── context/architecture.md# Kiến trúc + nhật ký quyết định
    ├── skills/                # Skill đã chọn (KHÔNG commit)
    ├── skills/REGISTRY.md
    └── skills.manifest.json
```

**Hỗ trợ đa agent** (Antigravity · Claude Code · Codex · Cursor · DeepSeek Harness):

| Host | Đọc skill từ | Rule đọc từ |
| :--- | :--- | :--- |
| `antigravity` | `~/.gemini/config/skills` | `~/.gemini/config/rules` |
| `agents` (dùng chung) | `.agents/skills/` | `.agents/rules/` |
| `claude` | `.claude/skills/` (mirror) | `.agents/rules/` + `CLAUDE.md` |
| `codex` | `.agents/skills/` | `AGENTS.md` |
| `cursor` | `.agents/skills/` | `AGENTS.md` |
| `dsh` | `$DSH_HOME/skills` (mặc định `~/.dsh/skills`) | — |

- `AGENTS.md` ở gốc là file duy nhất **mọi agent đều đọc** → rule bất biến nằm ở đây.
- `.agents/skills/` được Codex/Cursor/Antigravity/DSH đọc; **Claude Code không đọc** → script mirror thêm sang `.claude/skills/`.
- Frontmatter chỉ dùng 6 khóa portable: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
- Không phụ thuộc slash command, hook hay subagent — vì các agent định nghĩa chúng khác nhau.
- Đường dẫn skill của DSH **chưa được tài liệu hóa chính thức**; script đọc `$DSH_HOME` nếu có, nếu không dùng `~/.dsh/skills`.

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng cho Thành viên Team

Xem hướng dẫn đầy đủ tại [`INSTALL.md`](INSTALL.md).

### Cách 1: Đồng bộ vào máy cá nhân (Global Scope - Khuyên dùng)
Áp dụng cho mọi dự án trên máy của bạn:

```powershell
# Chỉ Antigravity (mặc định, giữ tương thích cũ)
.\scripts\sync.ps1 -Target global

# Hoặc mọi agent đã cài trên máy
.\scripts\sync.ps1 -Target global -Hosts all
```

*Mặc định ghi vào `~/.gemini/config/skills` và `~/.gemini/config/rules`.*

---

### Cách 2: Đồng bộ vào một Project cụ thể (Project Scope)
Nếu chỉ muốn áp dụng bộ skills/rules cho một repo dự án xác định:

```powershell
.\scripts\sync.ps1 -Target project -ProjectPath "D:\Path\To\YourProject" -Hosts all
```
*Tệp sẽ được đồng bộ vào `YourProject/.agents/skills/` + `.agents/rules/`, và mirror sang `.claude/skills/` khi chọn host `claude`.*

---

### Cách 3: Kích hoạt Kỹ năng Chuyên biệt từ Thư viện `_external/`
Tra cứu danh mục tại [`_external/CATALOG.md`](_external/CATALOG.md) và kích hoạt chính xác kỹ năng cần thiết:

```powershell
# Kích hoạt 1 skill cụ thể (ví dụ: react-patterns) - không cần biết nó ở skills/ hay _external/
.\scripts\sync.ps1 -Target project -ProjectPath "D:\Path\To\YourProject" -Skill "react-patterns" -Hosts agents,claude

# Hoặc kích hoạt toàn bộ 1 danh mục (ví dụ: 05-security-compliance)
.\scripts\sync.ps1 -Target project -ProjectPath "D:\Path\To\YourProject" -Category "05-security-compliance"
```

> 💡 Thêm `-DryRun` để xem trước sẽ ghi những gì mà không tạo file. Skill cũ **không bao giờ bị ghi đè** trừ khi bạn thêm `-Force`.

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
4. Các thành viên khác chỉ cần `git pull` và chạy lại `.\scripts\sync.ps1 -Target global` để nhận bản cập nhật mới nhất.
