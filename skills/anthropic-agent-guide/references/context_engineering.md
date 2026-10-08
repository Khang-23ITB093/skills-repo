# Context Engineering cho Mô Hình Claude & AI Agent

Tài liệu này đúc kết toàn diện các nguyên lý kỹ thuật ngữ cảnh (Context Engineering) mới nhất từ đội ngũ kỹ thuật Anthropic và quá trình phát triển Claude Code, thay thế các thói quen "prompt engineering" truyền thống.

---

## 1. Triết Lý Cốt Lõi: CPU vs RAM

Trong kiến trúc AI Agent hiện đại:
- **LLM đóng vai trò như CPU**: Xử lý suy luận, logic, ra quyết định và tạo sinh.
- **Context Window đóng vai trò như RAM**: Chứa toàn bộ dữ liệu đang hoạt động tại thời điểm tính toán (system prompt, công cụ, lịch sử hội thoại, tài liệu tra cứu).

Nhiệm vụ cốt lõi của kỹ sư không phải là "viết câu lệnh ma thuật", mà là **quản lý và tối ưu hóa lượng dữ liệu nạp vào RAM tại từng turn**:
- **Tránh Context Rot (Thối rữa ngữ cảnh)**: Khi context window quá đầy hoặc chứa nhiều thông tin mâu thuẫn, khả năng chú ý và độ chính xác của mô hình suy giảm nhanh chóng.
- **Giới hạn độ dài prompt**: Đa số prompt hiệu quả nhất nằm trong khoảng **80 – 200 từ**. Vượt quá 300 từ thường bổ sung nhiễu làm phân tán sự tập trung của mô hình.

---

## 2. "Unhobbling Claude" — 6 Bước Chuyển Dịch Căn Bản

Anthropic đã loại bỏ hơn **80%** độ dài của system prompt trong Claude Code cho thế hệ Claude 5/5.5 mà không làm suy giảm điểm chuẩn coding nhờ 6 chuyển dịch:

| Trước đây (Then) | Hiện nay (Now) | Nguyên lý kỹ thuật |
|---|---|---|
| **Áp đặt luật cứng (Give Claude rules)** | **Để Claude dùng phán đoán (Let Claude use judgement)** | Thay vì cấm đoán cực đoan ("không được viết comment", "không được tạo file plan"), hướng dẫn mô hình: *"Viết code tương thích với phong cách xung quanh: khớp mật độ comment, cách đặt tên và idiom của codebase"*. |
| **Nhồi nhét ví dụ (Give Claude examples)** | **Thiết kế giao diện công cụ (Design interfaces)** | Hàng nghìn ký tự ví dụ mẫu (worked examples) thường giam cầm mô hình vào một không gian suy diễn hẹp. Hãy thiết kế schema công cụ sắc nét: đặt tên tham số biểu cảm, dùng `enum` rõ ràng (vd: `status: [pending, in_progress, completed]`), bật `strict: true`. |
| **Nạp tất cả lên đầu (Put it all upfront)** | **Tiết lộ tăng dần (Use progressive disclosure)** | Không dồn toàn bộ hướng dẫn, runbook vào system prompt. Chia nhỏ tri thức thành cây thư mục files/skills để mô hình tra cứu và nạp khi thực sự cần. |
| **Lặp lại chỉ dẫn (Repeat yourself)** | **Mô tả công cụ đơn giản (Simple tool descriptions)** | Không lặp lại cách dùng công cụ trong system prompt và tool description. Chỉ cần ghi rõ mục đích và cách dùng ngay trong `description` của chính công cụ đó. |
| **Lưu nhớ thủ công vào file phẳng** | **Bộ nhớ tự động & Quản lý vòng đời** | Tránh biến `CLAUDE.md` hay file hướng dẫn thành bãi rác ghi nhớ. Giữ file cấu hình dưới 200 dòng, chỉ lưu các "gotchas" thực sự dị biệt của dự án. |
| **Tài liệu phẳng (Simple specs)** | **Tài liệu tham chiếu phong phú (Rich references)** | Thay vì markdown thuần túy, cung cấp cho Claude: test suites có thể chạy được, mockups HTML/UI trực quan, hoặc các bản tiêu chí đánh giá (rubrics) để mô hình tự kiểm chứng. |

---

## 3. Cấu Trúc Prompt Chuẩn với Thẻ XML Bản Địa

Mô hình Claude được huấn luyện chuyên biệt để phân tích cú pháp bằng các thẻ XML. Sử dụng thẻ XML giúp phân định ranh giới dữ liệu và chỉ thị, loại bỏ hoàn toàn hiện tượng nhầm lẫn giữa dữ liệu người dùng và mệnh lệnh hệ thống.

### Cấu Trúc Khung Khuyến Nghị:

```xml
<task>
Mô tả rõ ràng mục tiêu cần hoàn thành trong 1-3 câu. Nêu rõ tiêu chí nghiệm thu (Done condition).
</task>

<context>
Thông tin nền tảng, kiến trúc hệ thống, các ràng buộc môi trường runtime.
</context>

<instructions>
Các chỉ thị thực hiện. Giải thích lý do (Justification) tại sao lại có ràng buộc đó thay vì chỉ cấm đoán.
</instructions>

<constraints>
- Không sửa đổi các file ngoài phạm vi được chỉ định.
- Bảo toàn tương thích ngược của API hiện tại.
</constraints>

<output_format>
Định dạng đầu ra mong muốn (JSON schema, diff hunk, markdown table).
</output_format>
```

### 3 Điều Cần Loại Bỏ Hoàn Toàn (Anti-Patterns):
1. ❌ **Không dùng sáo rỗng CoT**: Bỏ các câu "think step by step", "take a deep breath", "work carefully". Các mô hình Claude hiện đại (đặc biệt là dòng hỗ trợ thinking) đã tự động suy luận ngầm hoặc theo luồng adaptive thinking; việc lặp lại câu này chỉ làm tốn token và tăng độ trễ.
2. ❌ **Không dùng lời đe dọa / nịnh nọt**: Bỏ "I'll tip you $200" hoặc "do not be lazy".
3. ❌ **Không ra lệnh lặp kép**: Bỏ các chỉ thị "verify twice", "double check everything" nếu bạn không cung cấp cho mô hình một công cụ hoặc lệnh test cụ thể để chạy.

---

## 4. Bảng Định Mức Token Cho System Prompt (`MAX_SYSTEM_PROMPT_TOKENS`)

System prompt được gửi trong mọi turn của phiên làm việc. Đặt system prompt quá dài sẽ làm suy giảm hiệu năng và đẩy chi phí lên cao.

| Phân hạng Model | Ngưỡng an toàn (Safe Limit) | Trần tối đa (Hard Limit) | Hiện tượng khi vượt trần |
|---|---|---|---|
| **Claude Haiku** | $\le 16.000$ tokens | $32.000$ tokens | Suy giảm chất lượng tuân thủ chỉ dẫn, dễ quên ràng buộc cuối |
| **Claude Sonnet** | $\le 32.000$ tokens | $64.000$ tokens | Độ trễ bắt đầu phản hồi (Time-to-First-Token) tăng cao |
| **Claude Opus** | $\le 64.000$ tokens | $128.000$ tokens | Cần đo đạc cẩn trọng, nguy cơ nghẽn token suy luận ngầm |

---

## 5. Bộ Quy Tắc Bảo Tồn Prompt Cache (`CACHE_RULES`)

Prompt Caching hoạt động theo nguyên tắc **so khớp tiền tố (prefix matching)**: API lưu vào bộ nhớ đệm mọi token từ đầu yêu cầu cho đến điểm ngắt `cache_control`.

- **RULE C1 — Thứ tự phân tầng tĩnh $\rightarrow$ động**:
  1. Base system prompt & định nghĩa công cụ (Tĩnh toàn cục $\rightarrow$ Được cache dùng chung cho mọi phiên).
  2. Hướng dẫn dự án / quy chuẩn repo (Tĩnh theo dự án).
  3. Phiên làm việc (Môi trường, cấu hình session).
  4. Lịch sử hội thoại (Động $\rightarrow$ Tăng dần theo từng turn).
  *Bất kỳ sự xáo trộn nào ở phần tĩnh (như chèn timestamp vào system prompt, tráo đổi thứ tự công cụ) sẽ phá vỡ toàn bộ cache!*
- **RULE C2 — Vị trí đặt Breakpoint**:
  Đặt điểm ngắt `cache_control: {"type": "ephemeral"}` tại vị trí **cuối cùng** của khối nội dung ổn định nhất.
- **RULE C3 — Quản lý TTL (Thời gian sống của cache)**:
  - Cache trên API / Gateway: TTL là **5 phút**. Mỗi lần cache hit sẽ reset bộ đếm thời gian 5 phút. Nếu nghỉ giữa chừng $> 5$ phút, lượt gọi tiếp theo sẽ phải trả phí cache write (gấp 1.25 lần phí input thông thường).
  - Cache trên Claude Subscription: TTL là **1 giờ**.
- **RULE C4 — Kiểm chứng Cache Hit trong Response**:
  Luôn theo dõi `usage.cache_read_input_tokens` trong response metadata:
  ```json
  "usage": {
    "input_tokens": 450,
    "output_tokens": 1200,
    "cache_read_input_tokens": 15400,
    "cache_creation_input_tokens": 0
  }
  ```
  Nếu `cache_read_input_tokens > 0`, bạn chỉ phải trả khoảng 5% đến 10% đơn giá input cho khối dữ liệu đó!

---

## 6. Xây Dựng Mục "Gotchas" — Vũ Khí Tối Thượng Trong Skill

Theo kinh nghiệm phát triển hàng trăm skill nội bộ tại Anthropic, phần mang lại tín hiệu giá trị cao nhất cho mô hình trong một Skill không phải là phần mô tả chung chung, mà là **Mục Gotchas (Điểm mù & cạm bẫy)**.

Một mục Gotchas xuất sắc phải chứa những thông tin thực chiến mà mô hình không thể tự suy luận ra chỉ bằng cách đọc code:
- *"Bảng subscriptions là append-only. Bản ghi có hiệu lực là bản ghi có version cao nhất, không phải created_at mới nhất."*
- *"Trường này được gọi là `@request_id` ở API Gateway nhưng lại gọi là `trace_id` trong Billing Service. Chúng có cùng giá trị."*
- *"Môi trường Staging luôn trả về HTTP 200 ngay cả khi Stripe webhook chưa xử lý xong. Hãy kiểm tra bảng payment_events để biết trạng thái thực tế."*
