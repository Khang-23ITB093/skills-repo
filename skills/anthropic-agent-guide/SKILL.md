---
name: anthropic-agent-guide
description: >-
  Hướng dẫn thực chiến toàn diện về cách sử dụng AI và mô hình Claude (thế hệ 5.5: Opus 5.5, Sonnet 5.5,
  Haiku 5.5, Fable 5.1 và thế hệ tiền nhiệm) của Anthropic: Context Engineering ("Unhobbling Claude"),
  bảo tồn Prompt Caching, điều phối mức Effort, thiết kế Dynamic Workflows, kiểm thử Evals & Hillclimbing,
  và tạo HTML Artifacts. Kích hoạt khi cần tối ưu hóa prompt, xây dựng agent harness với Claude, chọn model
  (Direct Anthropic / OpenRouter / Orimise), gỡ lỗi chi phí cache, hoặc lập trình cùng Claude Code.
---

# Anthropic Claude & Agent Engineering Guide

Runbook kỹ thuật chuẩn hóa dành cho AI Agent khi tương tác hoặc xây dựng hệ thống trên nền tảng các mô hình Anthropic Claude.

Tài liệu chi tiết được tách biệt theo nguyên tắc **Progressive Disclosure (Bảo vệ Token)** trong thư mục `references/` và `examples/`. Agent chỉ nạp thêm tài liệu chi tiết khi gặp tình huống tương ứng.

---

## 1. Ma Trận Mô Hình Nhanh (Model Matrix)

Chi tiết đầy đủ xem tại: [`references/model_lineup_and_pricing.md`](references/model_lineup_and_pricing.md).

| Tên Model | API ID | Trạng Thái | Giá (In / Out / Cache Read) | Vai Trò & Điểm Mạnh Thực Chiến |
|---|---|---|---|---|
| **Sonnet 4.6** | `claude-sonnet-4-6` | `[VERIFIED]` | $3 / $15 / $0.30 | **Mặc định trên Orimise**: Ngựa chiến cho Code Review đa file, Refactor kiến trúc lớn. Không bị trần thinking ngầm. |
| **Opus 5.5** | `claude-opus-5-5` | `[VERIFIED]` | $4 / $20 / $0.20 | **Toán học, Logic hẹp, Formal Invariants**: Thông minh nhất, Adaptive Thinking luôn bật ngầm. **Tránh dùng để audit file code dài** để không cạn token output (`acc=0`). Phù hợp input < 500 tokens. |

| **Haiku 4.5** | `claude-haiku-4-5-20251001` | `[VERIFIED]` | $1 / $5 / $0.10 | **Nhiệm vụ nhanh, đóng**: Input < 10k token, check cú pháp, câu hỏi Yes/No. Phản hồi siêu tốc (<5s). |
| **Sonnet 5** | `claude-sonnet-5` | `[VERIFIED]` | $3 / $15 / $0.30 | **Code mới từ đầu**: Sinh boilerplate và khung sườn ứng dụng. |
| **Fable 5.1** | `claude-fable-5-1` | `[VERIFIED]` | $10 / $50 / $0.25 | **Frontier cao nhất**: Đắt gấp 2.5 lần Opus 5.5, cần `--allow-premium` và sự đồng ý của người dùng. |
| **Sonnet 5.5** | `claude-sonnet-5-5` | `[ASSUMED]` | $2 / $10 / $0.20 | **Tối ưu nhất thế hệ 5.5**: Nhanh hơn 30%, rẻ hơn Sonnet 4.6 (33%), 1M context native. Hỗ trợ `between_tools`. |

*(Ghi chú: `[VERIFIED]` = Đang hoạt động trên gateway Orimise hiện tại; `[ASSUMED]` = Model mới của Anthropic, sẵn sàng trên Direct API/OpenRouter và chờ Orimise mở cổng).*

---

## 2. Quy Tắc Vàng Context Engineering ("Unhobbling Claude")

Chi tiết đầy đủ xem tại: [`references/context_engineering.md`](references/context_engineering.md).

1. **Phán đoán thay vì Luật cứng**: Không dùng mệnh lệnh tiêu cực cực đoan ("never write comments"). Hãy chỉ thị: *"Viết code tương thích với phong cách xung quanh: khớp mật độ comment, cách đặt tên và idiom của codebase"*.
2. **Thiết kế Giao diện thay vì Nhồi nhét ví dụ**: Cung cấp schema tham số công cụ rõ ràng (`enum`, `strict: true`, `additionalProperties: false`) thay vì các đoạn văn bản giải thích dài hàng nghìn ký tự.
3. **Cấu trúc Thẻ XML Bản Địa**: Đóng gói nội dung vào các khối `<task>`, `<context>`, `<instructions>`, `<constraints>`, `<output_format>`. (Xem mẫu tại [`examples/prompt_templates.md`](examples/prompt_templates.md)).
4. **Loại bỏ Sáo rỗng (Anti-Patterns)**: Cấm dùng "think step by step", "do not be lazy", "double check everything".
5. **Xây dựng Mục Gotchas**: Luôn lưu lại các điểm mù thực tế của dự án vào mục Gotchas của skill để làm tài sản tái sử dụng.

---

## 3. Quản Lý Effort & Chi Phí Thực Tế

Chi tiết đầy đủ xem tại: [`references/effort_and_cost_tuning.md`](references/effort_and_cost_tuning.md).

Bảng ánh xạ ngân sách token suy luận (`EFFORT_BUDGET`):
- **`low` (1.024 tokens)**: Brainstorming, đổi tên biến, edit cơ học nhanh có người giám sát.
- **`med` (8.192 tokens)**: Mặc định cho phát triển tính năng và lập trình hàng ngày.
- **`high` (16.384 tokens)**: Debug lỗi sâu trong brownfield codebase, security audit, edge cases.
- **`xhigh` (32.768 tokens)**: Các bài toán chứa nhiều điểm mù biên (parser XSS, theorem proving).
- **`max` (lên tới max_tokens)**: Chạy tự trị giải quyết bài toán cực khó.

> [!TIP]
> **Quy Tắc Kinh Tế Cốt Lõi**: Một vòng lặp retry 10 turns tốn kém tương đương chi phí nâng effort từ `med` lên `high`. **Luôn nâng Effort trước khi quyết định đổi sang Model lớn hơn!**

---

## 4. Bảo Tồn Prompt Cache (`CACHE_RULES`)

Prompt Cache giúp giảm tới **90% chi phí** và tăng tốc độ phản hồi. Để tránh phá vỡ cache:
1. **Phân tầng cố định**: Xếp nội dung theo thứ tự: *Base system prompt $\rightarrow$ Hướng dẫn dự án $\rightarrow$ Môi trường session $\rightarrow$ Hội thoại messages*.
2. **Không đổi công cụ giữa phiên**: Định nghĩa toàn bộ công cụ ngay từ turn 1 (dùng `defer_loading` cho công cụ phụ). Cấm thêm/bớt tool giữa phiên.
3. **Cấm đổi Model giữa phiên**: Đổi model sẽ xóa trắng cache của phiên đó.
4. **Quản lý TTL**: Cache trên API hết hạn sau **5 phút**. Sau mỗi 5 phút nhàn rỗi, turn tiếp theo sẽ phải trả phí cache-write.

---

## 5. Dynamic Workflows & Kiến Trúc Đa Agent

Chi tiết đầy đủ xem tại: [`references/dynamic_workflows_harness.md`](references/dynamic_workflows_harness.md) và code mẫu [`examples/workflow_recipes.py`](examples/workflow_recipes.py).

- **6 Mẫu hình**: Classify-and-act, Fan-out and Synthesize, Adversarial Verification, Generate-and-Filter, Pairwise Tournament, Loop-until-Done.
- **Chính sách Partial Failure**: Fan-out $N$ tasks: nếu $>50\%$ worker fail $\rightarrow$ Abort; nếu $\le 50\%$ fail $\rightarrow$ Tiếp tục tổng hợp và gắn nhãn `[INCOMPLETE_DATA]`.
- **Cô lập context**: Dùng Git Worktree độc lập cho từng subagent thực thi song song.

---

## 6. Evals, Hillclimbing & HTML Artifacts

- **Evals & Hillclimbing**: Chi tiết tại [`references/evals_and_hillclimbing.md`](references/evals_and_hillclimbing.md).
  - Snapshot `BASELINE_EVAL` trước khi tối ưu.
  - Chia tách tập Train và Test (Held-out set) để chống hiện tượng học vẹt (Overfitting) vào harness.
- **HTML Artifacts**: Chi tiết tại [`references/html_artifacts_guide.md`](references/html_artifacts_guide.md).
  - Sử dụng HTML thay Markdown khi tài liệu $>100$ dòng hoặc cần trực quan hóa đa chiều (diff margin notes, tabs, interactive knobs).
  - Tuân thủ chuẩn bảo mật an toàn: `<iframe srcdoc="..." sandbox="allow-scripts allow-same-origin" csp="...">`.

---

## 7. Checklist Tiền Kiểm Tra (Pre-flight Checklist)

Trước khi gửi bất kỳ prompt hoặc khởi tạo subagent nào với Claude:
- [ ] Model ID đã được xác thực (`[VERIFIED]` trên Orimise, hoặc trỏ đúng OpenRouter)?
- [ ] Prompt đã được phân tách rõ ràng bằng thẻ XML (`<task>`, `<context>`, `<output_format>`)?
- [ ] Đã xóa bỏ các câu lệnh sáo rỗng ("think step by step", "do not be lazy")?
- [ ] System prompt có nằm trong ngưỡng an toàn token (`MAX_SYSTEM_PROMPT_TOKENS`)?
- [ ] Đã chỉ định đúng mức Effort phù hợp với độ phức tạp của bài toán?
- [ ] Không có file nhạy cảm (`.env*`, `*key*`, `*token*`) nằm trong ngữ cảnh?
