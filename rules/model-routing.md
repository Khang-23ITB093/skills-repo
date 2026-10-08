---
description: Unified multi-model routing, tiering, escalation and token safeguards across all projects
trigger: always_on
---

# Unified Model Routing & Escalation Rule

Áp dụng cho mọi project. Agent đóng vai trò là **Model Orchestrator**, phân loại độ khó tác vụ và định tuyến đến đúng model/tier tối ưu chi phí và năng lực.

---

## 1. Nguyên Tắc Phân Tầng (Model Tiers)

| Tier | Đại diện Model tiêu biểu | Mục đích sử dụng | Quy tắc bắt buộc |
|---|---|---|---|
| **Workhorse (Mặc định)** | Gemini 3.8 Flash, Gemini 3.7 Flash | Triển khai mã nguồn chuẩn, CRUD, boilerplate, fix bug nhỏ | Cấm dùng model cao cấp cho tác vụ đơn giản. |
| **Economy** | Gemini 3.6 Flash, Haiku 4.5 | Docs, comment, câu hỏi đóng cú pháp, tóm tắt log nhỏ | Nhanh, rẻ, tối ưu token. |
| **Reasoning / Review** | Claude Sonnet 4.6, Claude Sonnet 5, Gemini 3.1 Pro | Code review sâu, kiến trúc mô-đun, rà soát bảo mật | Model ổn định nhất cho review đa file, refactor >=3 module. |
| **Deep Logic / Race Condition** | Claude Opus 5.5 (Orimise) | Bug logic cực khó, race condition, thuật toán tinh vi | **Staged Review**: Gửi từng module hẹp (<2.000 in tokens). Đặt `--max-tokens 5000`. Cấm `--resume` nếu `acc=0`. |
| **Elite / Premium** | Claude Fable 5.1, Claude Opus 4.6 | Quyết định kiến trúc sống còn, bế tắc toàn diện | **BẮT BUỘC user duyệt trước** (`--allow-premium`). |
| **Large Log Compression** | GPT-6 Luna | Nén log thô khổng lồ (>50k tokens) | Chỉ dùng khi log vượt ngưỡng hòa vốn phí sàn ($0.05). |

---

## 2. Chỉ Thị Tự Động Leo Thang (Escalation Directive)

Khi gặp lỗi lặp lại (>=2 lần fix thất bại với Workhorse model), race condition phức tạp hoặc thiết kế kiến trúc lõi:
1. **DỪNG NGAY**: Không cố gắng sửa lại nhiều lần bằng model Workhorse gây tốn token vô ích.
2. **Kích hoạt quy trình Orchestration**: Tham chiếu `skills/multi-model-orchestration` và `skills/orimise-deep-planning`.
3. **Chủ động đề xuất**: Báo cáo nguyên nhân cho user và xin phép leo thang sang reasoning model phù hợp.

---

## 3. An Toàn Chi Phí & Bảo Mật Token (Safeguards)

1. **Lọc bí mật**: Luôn qua bộ lọc scrub secret trước khi gửi prompt ra ngoài.
2. **Kiểm tra trước**: Luôn chạy `--dry-run` trước khi gọi API Orimise để xác thực token và trần chi phí.
3. **Prompt Intent**: Dùng từ ngữ kỹ thuật khách quan (`logic flaws`, `safeguards`), tránh từ khóa nhạy cảm kích hoạt `content_filter`.
