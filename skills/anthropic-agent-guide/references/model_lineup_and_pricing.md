# Phân Loại Mô Hình Claude, Bảng Giá & Khả Năng Tương Thích Nền Tảng

Tài liệu này cung cấp ma trận chi tiết về các thế hệ mô hình Anthropic Claude (Claude 5.5, Claude 5 và tiền nhiệm), thông số kỹ thuật, bảng giá chuẩn và trạng thái hỗ trợ trên các nhà cung cấp (Direct Anthropic API, OpenRouter, Orimise Gateway).

---

## 1. Ma Trận Mô Hình (Model Matrix)

Để đảm bảo tính chính xác và tránh ảo giác (Zero-Hallucination), các mã định danh mô hình (Model IDs) được phân loại minh bạch thành hai trạng thái:
- **`[VERIFIED]`**: Đã được kiểm chứng thực tế và đang hoạt động ổn định trên gateway Orimise hiện tại.
- **`[ASSUMED]`**: Model IDs thế hệ mới nhất của Anthropic (đã công bố trên `claude.dev`, hoạt động trên Claude Direct API và OpenRouter, sẵn sàng kích hoạt trên Orimise khi nhà cung cấp mở cổng).

| Tên Mô Hình | API Model ID | Trạng Thái | Giá Input / 1M | Giá Output / 1M | Cache Read / 1M | Khuyến Nghị Sử Dụng |
|---|---|---|---|---|---|---|
| **Claude Sonnet 4.6** | `claude-sonnet-4-6` | `[VERIFIED]` | $3.00 | $15.00 | $0.30 | **Mặc định trên Orimise**: Ngựa chiến ổn định cho Code Review đa file, Refactor kiến trúc lớn. Không bị nghẽn thinking ngầm. |
| **Claude Opus 5.5** | `claude-opus-5-5` | `[VERIFIED]` | $4.00 | $20.00 | $0.20 | **Tìm bug logic sâu, race condition**: Cực kỳ thông minh, tự bật Extended Thinking. Tuân thủ **Quy tắc 2.000 Input Tokens** (chỉ gửi 1 file mục tiêu hẹp). |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001` | `[VERIFIED]` | $1.00 | $5.00 | $0.10 | **Nhiệm vụ nhanh, đóng**: Input < 10k token, kiểm tra cú pháp, trích xuất dữ liệu, câu hỏi Yes/No. Phản hồi siêu nhanh (<5s). |
| **Claude Sonnet 5** | `claude-sonnet-5` | `[VERIFIED]` | $3.00 | $15.00 | $0.30 | **Viết code mới từ đầu**: Thiết kế boilerplate, khung sườn dự án ban đầu. |
| **Claude Fable 5.1** | `claude-fable-5-1` | `[VERIFIED]` (Orimise) | $10.00 | $50.00 | $0.25 | **Cấp cao nhất (Frontier)**: Đắt gấp 2.5 lần Opus 5.5. Chỉ dùng khi có sự đồng thuận của người dùng (`--allow-premium`). |
| **Claude Sonnet 5.5** | `claude-sonnet-5-5` | `[ASSUMED]` (OpenRouter/Direct) | $2.00 | $10.00 | $0.20 | **Thế hệ mới tối ưu nhất**: Nhanh hơn 30%, thông minh hơn, rẻ hơn Sonnet 4.6 (33%). Context 1M native, output 128k. Hỗ trợ `between_tools`. |
| **Claude Haiku 5.5** | `claude-haiku-5-5` | `[ASSUMED]` (Direct API) | $0.80 | $4.00 | $0.08 | **Subagents & High-volume**: Sắp ra mắt cho luồng tự động hóa quy mô lớn. |

---

## 2. Thông Số Kỹ Thuật Thế Hệ Claude 5.5 (Sonnet 5.5 & Opus 5.5)

- **Context Window**: 1.000.000 tokens (1M native), không cần beta header.
- **Max Output Tokens**: 128.000 tokens (lên tới 300k trên Message Batches API với header `output-300k-2026-03-24`).
- **Cơ chế Thinking**:
  - Bật mặc định (Adaptive Thinking). Mô hình tự điều chỉnh độ dài suy luận dựa trên độ phức tạp của bài toán.
  - Output tokens bao gồm cả token suy luận ngầm và text phản hồi.
- **Tùy chọn `between_tools`**:
  - Cho phép tắt thinking mở đầu khi chạy agent với công cụ. Mô hình chỉ suy luận ngắn giữa các lần gọi công cụ, giúp giảm đáng kể thời gian phản hồi mở đầu.
- **Minimum Cacheable Prompt**: Giảm xuống còn **512 tokens** (so với 1.024 tokens trên Sonnet 5), giúp các đoạn system prompt và tool definition ngắn cũng được hưởng lợi từ cache.

---

## 3. Chuyển Đổi Sang Bên Thứ Ba: Cấu Hình OpenRouter

Nếu bạn muốn sử dụng ngay các mô hình mới nhất như `claude-sonnet-5-5` trước khi Orimise cập nhật, bạn có thể chuyển hướng endpoint qua OpenRouter rất dễ dàng:

### 1. Thiết lập biến môi trường
```powershell
# Trỏ URL sang OpenRouter API
$env:ORIMISE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Đặt API Key của OpenRouter vào file hoặc biến
$env:ORIMISE_KEY_FILE = "$env:USERPROFILE\.gemini\config\openrouter_api_key.txt"
```

### 2. Ví dụ Python gọi OpenRouter với đầy đủ Headers bắt buộc:
```python
import urllib.request
import json

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/my-org/my-agent",  # Bắt buộc để xếp hạng trên OpenRouter
    "X-Title": "Antigravity Engineering Agent",             # Bắt buộc nhận diện ứng dụng
}
payload = {
    "model": "anthropic/claude-sonnet-5.5",
    "messages": [{"role": "user", "content": "Analyze this code"}],
    "max_tokens": 4096
}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                             data=json.dumps(payload).encode("utf-8"),
                             headers=headers, method="POST")
```

### 3. Bảng ánh xạ Model ID trên OpenRouter:
- `claude-sonnet-5-5` $\rightarrow$ `anthropic/claude-sonnet-5.5` [PROJECTED / ROADMAP]
- `claude-opus-5-5` $\rightarrow$ `anthropic/claude-opus-5.5` [PROJECTED / ROADMAP]
- `claude-sonnet-4-6` $\rightarrow$ `anthropic/claude-3.5-sonnet` [VERIFIED]

---

## 4. Các Thay Đổi Phá Vỡ Tương Thích Cần Lưu Ý (Breaking Changes)

Khi làm việc với các SDK và endpoint của dòng Claude 5.5:

1. **Không tắt thinking bằng `{"type": "disabled"}`**:
   - Gửi `thinking: {"type": "disabled"}` trên Sonnet 5.5 sẽ trả về lỗi **HTTP 400 Bad Request**.
   - Cách làm đúng: Dùng `thinking: {"type": "between_tools"}` nếu muốn tắt upfront thinking khi dùng tool, hoặc dùng Adaptive Thinking bình thường.
2. **Loại bỏ ép buộc `tool_choice` dạng `tool` hoặc `any`**:
   - `tool_choice: {"type": "tool", "name": "..."}` sẽ bị lỗi 400.
   - Cách làm đúng: Gửi `tool_choice: {"type": "auto"}` kết hợp với đánh dấu công cụ là `"strict": true` (bắt buộc có `"additionalProperties": false` trong schema) và ghi rõ trong prompt khi nào cần dùng.
3. **Đọc văn bản giữa các tool call từ `thinking` blocks**:
   - Khi mô hình ghi nhận tiến độ giữa các tool call, nội dung đó trả về dưới dạng block type `thinking`.
   - Cần duyệt qua mảng `response.content` theo `block.type` thay vì giả định phần tử đầu tiên là text (`content[0].text` sẽ crash nếu block 0 là `thinking`).
   - Sử dụng `thinking.display: "updates"` hoặc `"summarized"` để hiển thị tiến độ thân thiện cho người dùng.
