# Global Rule: Orimise Model Routing & Token Safeguards

Tất cả các agent khi sử dụng Orimise API (thông qua skill `orimise-deep-planning` và script `orimise_call.py`) **bắt buộc tuân thủ nghiêm ngặt** các quy tắc định tuyến và an toàn token dưới đây:

---

## 1. Quy Tắc Cốt Lõi Về Claude Opus 5.5 (`claude-opus-5-5`)

Model `claude-opus-5-5` có năng lực suy luận sâu và tỷ lệ p/p rất cao ($4 in / $20 out), nhưng tự động bật **Extended Thinking ngầm** khi gặp bài toán rà soát/đánh giá mã nguồn. Agent phải tuân thủ:

### 🔴 Điều Cấm Kỵ (Tránh Lỗi acc=0 và Cạn Hạn Mức 8.192 Tokens):
- **TUYỆT ĐỐI KHÔNG** gửi prompt gộp nhiều file lớn (>4.000 input tokens) kèm câu hỏi mở như *"review all bugs of these 4 files"* cho Opus 5.5. 
- *Lý do*: Chuỗi suy luận ngầm của Opus 5.5 sẽ vượt quá giới hạn cứng 8.192 output tokens của Orimise (Extended Thinking tokens được tính trực tiếp vào giới hạn output này) và bị ngắt kết nối (`finish: length`), làm mất trắng $0.30 - $0.60 chi phí mà trả về `0 ký tự output` (`acc=0`).

### 🟢 Cách Sử Dụng Đúng & Hiệu Quả:
1. **Quy tắc Staged Review (Từng file độc lập)**:
   - Chia nhỏ bài review: Gửi từng file hoặc từng module logic hẹp (<2.000 input tokens).
2. **Cấu hình trần `--max-tokens 5000` (hoặc 6000)**:
   - Dành ~2.800 tokens cho Opus 5.5 suy luận ngầm rà soát mọi ngóc ngách logic/race condition.
   - Dành ~2.200 tokens còn lại để model xuất bài review hoàn chỉnh (3.000–4.000+ ký tự).
3. **Quy tắc điều khiển Prompt Intent**:
   - **Cần lập plan / tóm tắt nhanh (Không tốn token suy luận)**: Dùng câu lệnh mô tả: *"Explain architecture"*, *"Describe flow"*, *"Draft high-level plan"*. Opus 5.5 sẽ **KHÔNG bật Extended Thinking**, xuất text ngay trong 100–300 tokens.
   - **Cần tìm bug ẩn, logic race condition (Deep Auditing)**: Dùng: *"Review logic bugs, variable scope issues, error handling"*, kèm `--max-tokens 5000` cho 1 file mục tiêu.
4. **Cấm dùng `--resume` khi `acc=0`**:
   - Nếu gặp `exit 2` với `acc=0` (suy luận ngầm ngốn hết token), TUYỆT ĐỐI KHÔNG dùng `--resume`. Chuyển ngay sang `claude-sonnet-4-6` hoặc chia nhỏ file mục tiêu thành block logic < 1.000 tokens.

---

## 2. Quy Tắc Định Tuyến Các Model Khác

| Tình huống tác vụ | Model bắt buộc sử dụng | Cấu hình & Lý do |
|---|---|---|
| **Code Review đa file, rà soát bảo mật toàn diện, Refactor lớn** | `claude-sonnet-4-6` | `--max-tokens 4000 - 6000`. Model mặc định ổn định nhất. Không bị kẹt trần suy luận ngầm, xuất kết quả ngay sau 10–15s. |
| **Tìm bug logic cực khó, thuật toán phức tạp, race condition tinh vi** | `claude-opus-5-5` | **Chỉ gửi 1 file/logic hẹp** (<2k in), đặt `--max-tokens 5000`. Cấm `--resume` nếu `acc=0`. |
| **Câu hỏi đóng, kiểm tra cú pháp, tóm tắt log nhỏ (<10k in)** | `claude-haiku-4-5-20251001` | `--max-tokens 2000`. Siêu rẻ ($1/$5), không phí sàn, phản hồi <5s. Bắt buộc có trường `CONFIDENCE:`. |
| **Nén log thô khổng lồ (>25k tokens sau compact_log)** | `gpt-6-luna` | Chỉ dùng cho chunk `>= 50.000 tokens` (hòa vốn phí sàn $0.05). Log từ 25k–40k tokens gửi trực tiếp cho `claude-sonnet-4-6`. |
| **Escalation cấp cao nhất (khi các model trên đều thất bại)** | `claude-fable-5-1` | **BẮT BUỘC user duyệt trước** (`--allow-premium`), vì giá đắt gấp 2.5x Opus ($10/$50). Lưu ý model nhạy cảm với câu hỏi bảo mật (`content_filter`). |

---

## 3. Tiêu Chuẩn Prompting & Phòng Ngừa Bộ Lọc An Toàn

1. **Tránh từ khóa kích hoạt `content_filter`**:
   - Không dùng: `bypass`, `exploit`, `vulnerability hack`.
   - Dùng: `input validation gaps`, `logic flaws`, `security safeguards review`, `error handling edge-cases`.
2. **Luôn chạy `--dry-run` trước khi gọi thật** để kiểm tra `est_input_tokens`, `worst_case_usd` và đảm bảo các token secret đã được scrub.
