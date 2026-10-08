# Ứng Dụng HTML Artifacts & Chuẩn Bảo Mật Giao Tiếp Người - Agent

Tài liệu này hướng dẫn cách khai thác sức mạnh vượt trội của định dạng HTML Artifacts để thay thế các tài liệu Markdown dài dòng, tạo ra các giao diện tương tác hai chiều và bảo đảm an toàn thông tin (CSP Sandbox).

---

## 1. Tại Sao HTML Vượt Trội Hơn Markdown Trong Tác Vụ Phức Tạp?

Markdown là định dạng tuyệt vời cho ghi chú ngắn, nhưng bộc lộ nhiều hạn chế nghiêm trọng khi tài liệu vượt quá 100 dòng:
1. **Mật độ thông tin thấp**: Markdown không thể biểu diễn trực quan các luồng dữ liệu song song, biểu đồ trạng thái, hay các bảng đối chiếu đa chiều mà không phải dùng ký tự ASCII thô sơ.
2. **Khó đọc & Dễ bỏ sót**: Con người rất hiếm khi đọc kỹ một file markdown dài hàng trăm dòng từ đầu đến cuối. Người dùng có xu hướng lướt qua và bỏ sót các rủi ro kiến trúc quan trọng.
3. **Thiếu khả năng tương tác**: Markdown là dữ liệu tĩnh một chiều. HTML cho phép tạo ra các thanh trượt (sliders), nút chọn, tab chuyển đổi nội dung và nút "Copy as prompt" để đưa phản hồi trực tiếp ngược lại cho Agent.

---

## 2. 4 Kịch Bản Ứng Dụng Đỉnh Cao Của HTML Artifacts

### 1. Kế Hoạch Kiến Trúc & Thiết Kế Hệ Thống (Architecture Specs)
- Tổ chức theo các **Tab điều hướng**: `Tổng Quan` | `Sơ Đồ Dữ Liệu` | `Chi Tiết API` | `Các Rủi Ro` | `Kế Hoạch Từng Bước`.
- Sử dụng thẻ `<svg>` để vẽ trực tiếp kiến trúc hệ thống (hộp, mũi tên, luồng dữ liệu) thay vì ASCII art.
- Nhúng các thông số đo lường (latency budget, throughput) dạng callout nổi bật.

### 2. Code Review & Phân Tích Pull Request
- Render trực tiếp khối Diff mã nguồn với màu sắc rõ ràng (đỏ cho dòng xóa, xanh cho dòng thêm).
- **Chú thích bên lề (Margin Annotations)**: Gắn trực tiếp nhận xét vào số dòng cụ thể, phân loại rõ ràng bằng nhãn màu sắc:
  - 🔴 `[BLOCKING]` — Lỗi bảo mật hoặc crash bắt buộc sửa.
  - 🟡 `[MAJOR]` — Điểm nghẽn hiệu năng hoặc thiếu test.
  - 🟢 `[NIT]` — Góp ý nhỏ về phong cách viết mã.

### 3. Tinh Chỉnh Tham Số Giao Diện & Prototype
- Tạo trang HTML độc lập chứa component cần thiết kế kèm các thanh trượt điều chỉnh: padding, bo góc, màu sắc, thời lượng animation.
- Có nút **"Copy Configuration"** để người dùng bấm một nút là sao chép toàn bộ tham số ưng ý dán lại vào chat cho agent áp dụng vào mã nguồn.

### 4. Giao Diện Triage Vé Lỗi & Sắp Xếp Ưu Tiên (Custom Triage Editor)
- Trình bày danh sách 30-50 tickets lỗi dưới dạng bảng kéo thả (Now / Next / Later).
- Người dùng sắp xếp xong bấm nút **"Export Ordering as Prompt"** để gửi lại danh sách đã chốt cho agent xử lý.

---

## 3. Quy Chuẩn An Toàn & Bảo Mật (Security & CSP Sandbox)

Vì HTML Artifacts có thể chứa mã JavaScript, việc render nội dung này bắt buộc phải tuân thủ các quy tắc bảo mật nghiêm ngặt để phòng chống tấn công chéo hoặc rò rỉ dữ liệu:

### Mẫu Khung Nhúng An Toàn (Safe Iframe Pattern):

```html
<iframe 
  srcdoc="<!-- Nội dung HTML sinh ra từ agent -->" 
  sandbox="allow-scripts allow-same-origin"
  csp="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: 'self';"
  style="width: 100%; height: 600px; border: 1px solid #e0e0e0; border-radius: 8px;">
</iframe>
```

### Các Ràng Buộc Bảo Mật Cần Tuân Thủ:
1. 🔒 **Chặn kết nối mạng ngoài (`connect-src 'none'`)**: Tuyệt đối không cho phép mã JS trong artifact gọi lệnh `fetch()` hoặc `XMLHttpRequest` ra bất kỳ máy chủ bên ngoài nào.
2. 🔒 **Cấm `allow-forms`**: Không cho phép submit form ra ngoài môi trường thực thi.
3. 🔒 **Giao tiếp an toàn qua `postMessage`**: Mọi dữ liệu người dùng tương tác trong artifact chỉ được gửi về cửa sổ chính thông qua cơ chế `window.parent.postMessage()`.
