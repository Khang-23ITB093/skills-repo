# Global Rule: Orimise Model Routing & Token Safeguards

Áp dụng cho mọi agent dùng Orimise API qua skill `orimise-deep-planning` / script `orimise_call.py`.
Số liệu gốc và các điểm chưa xác minh: `skills/orimise-deep-planning/references/gateway_facts.md` (ảnh chụp 2026-10-23).

---

## 1. Luật cứng (P0)

- **Chỉ dùng model trong allowlist**: `claude-haiku-5-5`, `claude-sonnet-5-5` (mặc định), `claude-opus-5-5`, `gpt-6-luna`.
  `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-sonnet-5`, `claude-fable-5-1` đều trả **403 `MODEL_DISABLED_FOR_USER`** nên KHÔNG dùng.
- **Không dùng GPT để probe, benchmark hay thử tham số**: mỗi request tối thiểu **$0.05**, kể cả `max_tokens:1`.
- **Không dùng `gpt-6-luna` cho chunk < 50.000 token**: gửi thẳng `claude-sonnet-5-5`.
- **Không `--resume` khi `reason=thinking_exhausted`** (thinking ăn hết `--max-tokens`, 0 ký tự text). Tăng `--max-tokens` x2 hoặc hạ `--effort` rồi gọi lại.
- **Không dựa vào "trần 8.192 token"**: con số này sai. Trần output thật của Claude là **128.000**, và thinking nằm **trong** `--max-tokens`.

## 2. Hành vi chuẩn

| Tình huống | Model | Cấu hình |
|---|---|---|
| Code review đa file, security audit, refactor lớn, plan | `claude-sonnet-5-5` | `--effort med --max-tokens 16000` |
| Bug logic cực khó, race condition (leo thang) | `claude-opus-5-5` | `--effort high --max-tokens 24000` |
| Câu hỏi đóng, cú pháp, log < 10k | `claude-haiku-5-5` | `--effort low --max-tokens 2000`, bắt buộc `CONFIDENCE:` |
| Log > 50k token sau `compact_log` | Pass 1 `gpt-6-luna` → Pass 2 `claude-sonnet-5-5` | Pass 1 `--max-tokens 4000` |

Thang leo thang: `haiku-5-5 → sonnet-5-5 → opus-5-5 → DỪNG, hỏi user`. Không còn nấc premium.

## 3. Biện pháp phòng ngừa

1. Đầu phiên chạy `--probe` với model sắp dùng, vì danh mục model thay đổi theo gói tài khoản.
2. Luôn `--dry-run` trước khi gọi thật để kiểm `est_input_tokens`, `worst_case_usd` (đã gồm thinking) và số secret đã scrub.
3. Muốn suy luận sâu hơn: tăng `--effort` (chỉ Claude). Effort chỉ có tác dụng trên `/v1/messages`, nơi script tự định tuyến Claude.
4. Review bảo mật: ưu tiên *input validation gaps, logic flaws, control gap* thay cho *bypass/exploit/hack*.
   Kinh nghiệm này có từ model cũ để tránh `content_filter`, **chưa xác minh lại trên model 5.5**.
5. Chia review theo từng file vì lý do **chất lượng**, không phải vì giới hạn token.
