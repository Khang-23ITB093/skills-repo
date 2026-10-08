# Quản Lý Effort, Tối Ưu Chi Phí & Chiến Lược Prompt Caching

Tài liệu này phân tích cơ chế điều phối nỗ lực tính toán (Effort Tuning), bài toán kinh tế giữa số lượt retry và token, cùng các đúc kết thực nghiệm từ benchmark Terminal-Bench 3.0 của Anthropic.

---

## 1. Bản Chất Của "Effort" Là Gì?

**Effort là ngân sách tính toán (compute budget)** mà bạn chỉ định cho mô hình chi tiêu cho mỗi turn: bao gồm độ dài suy luận ngầm (thinking), số lượng công cụ được gọi, và mức độ đào sâu kiểm chứng biên (edge-case testing).

Khi bạn yêu cầu một kỹ sư làm việc:
- Trong **1 giờ** (`low` effort): Họ sẽ đưa ra phương án tối thiểu hoạt động được để bạn xem xét và cùng lặp lại phản hồi nhanh chóng.
- Trong **12 giờ** (`high` / `max` effort): Họ sẽ chủ động viết fuzzer, tái hiện lỗi trên nhiều môi trường, đọc mã nguồn thư viện liên quan và tự kiểm chứng nhiều giả thuyết trước khi báo cáo kết quả.

---

## 2. Chuẩn Mực Mới Nhất Của Anthropic Về Extended Thinking & Effort (2026)

Theo tài liệu chính thức từ Anthropic (`docs.anthropic.com`), cơ chế tư duy của Claude đã có sự chuyển dịch căn bản:

### 2.1 Adaptive Thinking vs Legacy Extended Thinking
* **Legacy Mode (`thinking: {"type": "enabled", "budget_tokens": N}`)**: Là chế độ thủ công cũ. Chế độ này yêu cầu tối thiểu $1.024$ tokens và bắt buộc `budget_tokens` phải nhỏ hơn đáng kể so với `max_tokens`. Chế độ này bị coi là lỗi thời (deprecated) và trả về lỗi `HTTP 400` trên các dòng model mới.
* **Modern Mode (`thinking: {"type": "adaptive"}`)**: Là chuẩn mực mặc định hiện tại. Claude tự động đánh giá độ phức tạp của bài toán để quyết định có cần suy nghĩ hay không và suy nghĩ bao nhiêu.
* **Tham số `effort` ("low" | "medium" | "high")**: Đóng vai trò là núm điều chỉnh **độ sâu tư duy (Reasoning Depth)** trong chế độ Adaptive Thinking, không phải là mode riêng biệt:
  - `effort: "low"`: Thu nhỏ toàn bộ chu trình xử lý, tiết kiệm tối đa độ trễ và chi phí token.
  - `effort: "high"`: Thúc đẩy mô hình tư duy đa chiều và kiểm chứng biên sâu hơn.
* **Đặc tính của Claude Opus 5.5 & Fable 5.1**: **Thinking không thể tắt (Cannot be disabled)** — cơ chế Adaptive Thinking luôn luôn hoạt động ngầm trên mọi request.

---

### 2.2 Khi Nào NÊN DÙNG vs TUYỆT ĐỐI TRÁNH DÙNG

| Tình Huống | Khuyến Nghị Anthropic | Phân Tích Kỹ Thuật |
|---|---|---|
| **Toán học, Logic puzzles, Formal Invariants** | ⭐ **RẤT NÊN DÙNG** | Đòi hỏi nhiều bước suy luận chuỗi (Serial test-time compute) trước khi đưa ra kết luận. |
| **Thiết kế kiến trúc cấp cao (High-Level Architecture)** | ⭐ **RẤT NÊN DÙNG** | Cần mô hình tự cân nhắc trade-offs, phân tích các hướng tiếp cận trước khi chọn ra plan tối ưu. |
| **Tìm lỗi logic ẩn hẹp (Isolated Root-Cause)** | ⭐ **RẤT NÊN DÙNG** (Khi input < 500 tokens) | Giúp mô hình tự phản biện và loại bỏ các giả thuyết sai lầm. |
| **Code Review toàn bộ file hoặc nhiều file lớn** | ❌ **TUYỆT ĐỐI TRÁNH** | **Cạm bẫy cạn kiệt Token Output (`acc=0`)**: Khi context đầu vào lớn, suy luận ngầm của Opus sẽ nuốt chửng toàn bộ ngân sách 5.000–8.000 output tokens, khiến request chạm trần `finish_reason=length` mà không kịp trả về bất kỳ ký tự nào! |
| **Format code, Viết Boilerplate, Linting, Sửa cú pháp** | ❌ **TUYỆT ĐỐI TRÁNH** | Gây lãng phí chi phí token suy luận (tính tiền như output tokens) mà không mang lại bất kỳ cải thiện nào. |
| **Tác vụ tương tác thời gian thực (Streaming UI / Chat)** | ❌ **TUYỆT ĐỐI TRÁNH** | Gây độ trễ (TTFT - Time to First Token) kéo dài từ 30s đến hàng phút. |

---

### 2.3 Quy Tắc Sống Còn: "Try Standard First"

Anthropic khuyến cáo một nguyên tắc bất biến cho mọi nhà phát triển hệ thống Agent:
1. **Luôn bắt đầu bằng mô hình Tiêu chuẩn (Standard Model / Workhorse) trước**: Sử dụng `Claude Sonnet 4.6` hoặc `Claude Sonnet 5` không ép buộc Extended Thinking ngầm cho các tác vụ lập trình, review mã nguồn và refactor.
2. **Chỉ leo thang sang Extended Thinking / High Effort khi và chỉ khi**:
   - Mô hình tiêu chuẩn đã thử nghiệm và bế tắc hoặc đưa ra phương án sai.
   - Bài toán đã được **cô lập hẹp** (chỉ gửi chữ ký hàm, lỗi logic cụ thể hoặc bài toán trừu tượng $< 500 - 1.000$ tokens input).
   - Trần `max_tokens` của môi trường phải đủ lớn ($\ge 16.000$ tokens), hoặc gateway phải hỗ trợ tách biệt luồng thinking stream và content stream.


---

## 3. Đúc Kết Thực Nghiệm Từ Terminal-Bench 3.0

Nghiên cứu được Anthropic công bố trên blog `claude.dev` khi đánh giá năng lực agent trên bộ benchmark Terminal-Bench 3.0 (phát triển bởi Harbor Framework cộng đồng, gồm 70 bài toán thực tế thuộc các lĩnh vực bảo mật, hệ điều hành, khoa học, toán học) chỉ ra:

1. **Effort tạo ra đột phá ở bài toán có nhiều Edge-Cases ẩn**:
   - Bài toán viết bộ lọc chống XSS (`html-js-filter`): Claude Fable ở mức `low` chỉ đạt $1/5$ thành công (viết 1 pass và test thử 1 trang đơn giản). Ở mức `xhigh` đạt $5/5$ thành công (tự động đọc mã nguồn parser, viết fuzzer ngẫu nhiên, test bộ XSS chuẩn).
   - Bài toán fix bug crash storage engine (`mvcc-lsm-compaction`): Claude Opus 5.5 ở mức `low` đạt $0/5$, nhưng ở `xhigh` đạt $4/5$ vì mô hình tự viết test tái hiện lỗi crash trước khi sửa code.
2. **Effort KHÔNG sửa được sai lầm về phương pháp tiếp cận cốt lõi**:
   - Nếu mô hình chọn sai thuật toán hoặc hiểu sai bản chất bài toán, tăng effort chỉ khiến mô hình suy nghĩ lâu hơn về hướng đi sai đó. Khi gặp tình huống này, hãy can thiệp bằng cách điều chỉnh prompt hoặc đổi mô hình.
3. **Vòng lặp phát triển phần mềm lý tưởng**:
   - **Bước 1**: Đưa spec và yêu cầu Claude phỏng vấn làm rõ các điểm thiếu sót.
   - **Bước 2**: Triển khai bản nháp đầu tiên ở mức **`low` effort** (để phản hồi nhanh, giữ người dùng trong vòng lặp).
   - **Bước 3**: Review bản nháp, tinh chỉnh hướng đi.
   - **Bước 4**: Chạy kiểm thử toàn diện và verify ở mức **`high` effort**.

---

## 4. Bài Toán Kinh Tế: Chi Phí Retry vs Chi Phí Nâng Effort

Trên mô hình Claude Opus 5.5:
- Đơn giá Input: **$4.00 / 1M**
- Đơn giá Output (gồm thinking): **$20.00 / 1M** (đắt gấp 5 lần input)
- Đơn giá Cache Read: **$0.20 / 1M** (rẻ bằng $1/100$ so với output)

### So sánh trực quan:
- Giả sử bạn nâng từ `med` lên `high`, mô hình tiêu tốn thêm khoảng **$20.000$ thinking tokens** $\rightarrow$ Chi phí tăng thêm là **$0.40$ USD**.
- Nếu bạn để mức `low`/`med` khiến code bị lỗi, agent phải bước vào một **vòng lặp retry 10 turns** (với context trung bình 100k tokens đã cache + 10k output tokens) $\rightarrow$ Chi phí retry cũng mất khoảng **$0.40 - $0.60$ USD**, chưa kể thời gian chờ đợi và nguy cơ bế tắc.

> [!IMPORTANT]
> **Nguyên Tắc Vàng Trong Điều Phối Chi Phí**:
> **"Nâng Effort trước khi đổi sang Model lớn hơn."**
> Nếu `med` effort trên Sonnet chưa giải quyết được bài toán, hãy thử nâng lên `high` effort. Chỉ khi `high` hoặc `xhigh` vẫn thất bại mới leo thang sang Opus hoặc Fable.

---

## 5. Kinh Tế Của Compaction & Quản Lý Phiên Làm Việc

- **Tại sao turn càng về sau càng đắt?**
  Mỗi turn mới đều phải gửi lại toàn bộ lịch sử trò chuyện phía trước. Dù có cache, đọc 150k token cache vẫn tốn gấp 7.5 lần so với đọc 20k token cache.
- **Thời điểm chạy `/compact` lý tưởng**:
  - Không chạy compact ngay trước khi kết thúc tác vụ (lãng phí token sinh tóm tắt mà không tận dụng được ở các turn sau).
  - Chạy compact tại **điểm ngắt tự nhiên** (khi vừa hoàn thành một milestone lớn) và khi cache vẫn còn ấm (warm cache).
- **Lệnh `/clear`**:
  Dùng `/clear` khi chuyển sang một tác vụ hoàn toàn độc lập. Lệnh này xóa sạch context và hoàn toàn miễn phí, giúp bắt đầu phiên mới với 100% token sạch.
