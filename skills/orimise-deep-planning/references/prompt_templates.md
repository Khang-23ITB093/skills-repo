# Mẫu prompt cho `orimise_call.py`

Model được gọi **không biết gì** ngoài prompt. Script đã gắn sẵn system prompt (vai trò, output được agent máy
tiêu thụ, cấm đoán bừa, dòng kết `<<END>>`), nên file prompt chỉ chứa phần riêng của task.
Có thể bọc từng khối bằng thẻ XML (`<task>`, `<context>`, `<scope>`, `<output_format>`) thay cho heading `#`; hai cách tương đương nhau.

## Header chung (mọi kịch bản)

```text
# GOAL
<yêu cầu của user, NGUYÊN VĂN, <=3 câu. Không diễn giải lại>
# WHY THIS CALL
<đã thử gì, kết quả ra sao, cần model quyết định điều gì>
# DONE WHEN
<tiêu chí quan sát được: test X pass / hành vi Y xảy ra / lệnh Z exit 0>
# ENV
<OS, runtime+version, framework, lệnh test/build>
# SCOPE
files_in_scope: <danh sách>   frozen (không được đụng): <danh sách>
```

## A. Plan kiến trúc / tính năng mới

```text
<Header chung>
# STRUCTURE (depth 2, chỉ thư mục liên quan)
<tree>
# INTERFACES (chữ ký hàm/type liên quan, KHÔNG thân hàm)
<signatures>
# NON-GOALS
<điều không được làm>
# OUTPUT FORMAT (Markdown, không gì khác)
## APPROACH (<=5 bullets)
## RISKS (<=3 bullets)
## STEPS (<=12, đúng thứ tự phụ thuộc)
S1 | file: <path> | action: create|modify|delete | detail: <1-2 dòng: làm gì, vì sao> | verify: <1 lệnh đơn>
## MISSING_INFO (hoặc "none")
```

Plan phức tạp (> 5 bước, có luồng phụ thuộc) có thể yêu cầu xuất HTML artifact, xem
[`html_artifacts_guide.md`](../../anthropic-agent-guide/references/html_artifacts_guide.md).

## B. Debug lỗi sâu

```text
<Header chung>
# SYMPTOM
<thông báo lỗi chính xác>
# STACK TRACE (chỉ frame của project + frame thư viện cuối cùng + dòng exception)
<trace>
# REPRO
<các bước>
# ALREADY TRIED (mỗi lần 1 dòng)
1. giả thuyết -> thay đổi -> kết quả (không đổi / lỗi mới: ...)
# CODE (hàm lỗi + caller trực tiếp, kèm path:line)
<code>
# OUTPUT FORMAT
ROOT_CAUSE: <=3 câu
CONFIDENCE: high|medium|low
MISSING_INFO: <danh sách hoặc "none">
VERIFY: <1 lệnh đơn>
PATCH: <unified diff trong fence ```diff, chỉ hunk thay đổi + 3 dòng context>
```

## C. Review mã nguồn

```text
<Header chung>
# CODE TO REVIEW (1 file mục tiêu hoặc diff)
<content>
# FOCUS
Review logic bugs, variable scope issues, error handling edge-cases, input validation gaps.
# OUTPUT FORMAT (Markdown, không gì khác)
## VERDICT
pass | needs-fixes
## FINDINGS (nếu pass ghi "none")
F1 | file: <path:line> | severity: critical|major|minor | issue: <1 dòng: nguyên nhân, hậu quả> | fix: <1-2 dòng>
## MISSING_INFO (hoặc "none")
```

Khi review bảo mật, ưu tiên dùng *control gap, unhandled flow, input validation gap* thay cho *bypass/exploit/hack*.
Kinh nghiệm này có từ model cũ để tránh `content_filter`, chưa đo lại trên model 5.5.

## D. Log pass 1 (`gpt-6-luna`, chỉ khi chunk >= 50k token)

```text
Return ONLY JSON: {"time_range":"","error_groups":[{"signature":"<normalized>","count":0,"sample":""}],"anomalies":[""]}
<chunk log đã qua compact_log.py>
```

Gộp các JSON lại (cộng `count` theo `signature`), rồi gửi bản gộp kèm Header chung cho `claude-sonnet-5-5` ở pass 2.
