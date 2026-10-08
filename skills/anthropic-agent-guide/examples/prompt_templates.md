# Mẫu Prompt Chuẩn Hóa Theo Phong Cách Anthropic (XML Structure)

Dưới đây là các mẫu prompt chuẩn mực được thiết kế theo khuyến nghị mới nhất từ Anthropic: sử dụng thẻ XML bản địa, phân định rõ ràng giữa chỉ thị và dữ liệu, loại bỏ sáo rỗng và hướng dẫn bằng lý do (Justification).

---

## 1. Mẫu Lập Kế Hoạch Kiến Trúc & Thiết Kế Tính Năng Mới

```xml
<task>
Thiết kế kiến trúc và lập kế hoạch từng bước triển khai tính năng: {TÊN_TÍNH_NĂNG}.
Hoàn thành khi kế hoạch bao quát đầy đủ data flow, interfaces, các rủi ro bảo mật và lệnh verify cho từng bước.
</task>

<context>
- Môi trường: {NGÔN_NGỮ} / {FRAMEWORK}
- Kiến trúc hiện tại: {TÓM_TẮT_KIẾN_TRÚC}
- Các file liên quan trực tiếp:
{DANH_SÁCH_FILES}
</context>

<instructions>
1. Giữ tính nhất quán: Thiết kế kiểu dữ liệu và cấu trúc khớp với idiom hiện có trong codebase.
2. Phân chia rõ ràng: Tách biệt logic nghiệp vụ khỏi tầng persistence và transport.
3. Đối với từng bước triển khai, cung cấp một lệnh kiểm tra đơn lẻ (đơn lệnh, không dùng pipe shell) để verify ngay sau khi sửa.
</instructions>

<constraints>
- Không thêm dependency mới trừ khi có lý giải bắt buộc.
- Không sửa đổi các file bị đóng băng: {FROZEN_FILES}.
</constraints>

<output_format>
## APPROACH (Tối đa 5 gạch đầu dòng)
## RISKS & MITIGATIONS (Tối đa 3 rủi ro cốt lõi)
## STEPS (Đúng thứ tự phụ thuộc)
S1 | file: <path> | action: create|modify | detail: <1-2 dòng giải thích> | verify: <lệnh kiểm tra>
## MISSING_INFO (Hoặc "none")
</output_format>
```

---

## 2. Mẫu Điều Tra & Sửa Lỗi Sâu (Deep Root-Cause Debugging)

```xml
<task>
Xác định nguyên nhân gốc rễ và đề xuất bản vá tối thiểu cho lỗi sau: {TÊN_LỖI}.
</task>

<symptom>
{THÔNG_BÁO_LỖI_VÀ_EXCEPTION}
</symptom>

<stack_trace>
{STACK_TRACE_RÚT_GỌN}
</stack_trace>

<evidence>
Các bước đã thử nghiệm và kết quả:
1. {GIẢ_THUYẾT_1} -> {KẾT_QUẢ}
2. {GIẢ_THUYẾT_2} -> {KẾT_QUẢ}
</evidence>

<code_snippet path="{ĐƯỜNG_DẪN_FILE}" lines="{DÒNG_BẮT_ĐẦU}-{DÒNG_KẾT_THÚC}">
{NỘI_DUNG_HÀM_GẶP_LỖI}
</code_snippet>

<instructions>
- Tìm nguyên nhân gốc rễ (Root Cause) thay vì chỉ vá phần triệu chứng (Symptom patching).
- Đưa ra bản vá dạng Unified Diff tối thiểu, giữ nguyên phong cách comment và format của code xung quanh.
- Cung cấp một lệnh verify duy nhất để kiểm chứng bản vá mà không tạo tác dụng phụ.
</instructions>

<output_format>
ROOT_CAUSE: <= 3 câu phân tích chính xác cơ chế gây lỗi.
CONFIDENCE: high | medium | low
VERIFY: <lệnh kiểm chứng duy nhất>
PATCH:
```diff
<unified diff hunk>
```
</output_format>
```

---

## 3. Mẫu Code Review Toàn Diện & Phân Loại Mức Độ

```xml
<task>
Thực hiện đánh giá mã nguồn (Code Review) cho thay đổi sau đây.
Tập trung vào: tính đúng đắn của logic, rò rỉ tài nguyên, xử lý biên (edge cases) và bảo mật.
</task>

<diff_to_review>
{NỘI_DUNG_GIT_DIFF}
</diff_to_review>

<instructions>
- Không nhận xét về các quy chuẩn formatting đã được linter tự động kiểm tra.
- Phân loại rõ ràng mọi phát hiện theo 3 mức độ: CRITICAL (lỗi logic/bảo mật bắt buộc chặn), MAJOR (hiệu năng/thiếu test), MINOR (phong cách/tính rõ ràng).
- Với mỗi phát hiện, chỉ rõ dòng code, nguyên nhân, hậu quả và đề xuất cách sửa cụ thể.
</instructions>

<output_format>
## VERDICT
pass | needs-fixes

## FINDINGS (Ghi "none" nếu pass)
F1 | file: <path:line> | severity: critical|major|minor | issue: <nguyên nhân và hậu quả> | fix: <cách sửa>

## MISSING_INFO (hoặc "none")
</output_format>
```
