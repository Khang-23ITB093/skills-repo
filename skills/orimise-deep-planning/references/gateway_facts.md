# Orimise Gateway — dữ liệu đã kiểm chứng

> Ảnh chụp ngày **2026-10-23** bằng request thật. Danh mục model **thay đổi theo gói tài khoản**:
> luôn chạy `orimise_call.py <model> --probe` trước khi dùng. Mục nào chưa xác minh được thì ghi rõ.

## 1. Model dùng được (allowlist của `orimise_call.py`)

| Model | Route script dùng | Context / Input max | Output max | Effort (thinking) | Prompt cache | Giá vào/ra mỗi 1M | Phí sàn |
|---|---|---|---|---|---|---|---|
| `claude-haiku-5-5` | `/v1/messages` | 300k / 300k | **128.000** | low/med/high/max ✅ | ✅ | $1 / $5 `[ASSUMED]` | không |
| `claude-sonnet-5-5` | `/v1/messages` | 300k / 300k | **128.000** | low/med/high/max ✅ | ✅ | $2 / $10 `[ASSUMED]` | không |
| `claude-opus-5-5` | `/v1/messages` | 300k / 300k | **128.000** | low/med/high/max ✅ | ✅ | $4 / $20 `[kế thừa]` | không |
| `gpt-6-luna` | `/v1/chat/completions` | 600k / 600k | chưa xác minh | ❌ bị nuốt im lặng | ❌ | $0.10 / $0.50 `[kế thừa]` | **$0.05 / request** |

Tài khoản còn mở `gpt-5.6-terra`, `gpt-6-astra`, `gpt-6.1-sol` (600k context) nhưng **chưa có giá**, nên không nằm trong allowlist.

**Bị khoá (`403 MODEL_DISABLED_FOR_USER`)**: `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-sonnet-5`,
`claude-fable-5`, `claude-fable-5-1`, `claude-opus-4-x`, `claude-opus-5`, `gemini-*`, `gpt-5.5`, `gpt-5.6-luna/sol`, `gpt-6-sol`.
`GET /models` vẫn liệt kê cả model bị khoá, nên chỉ một request thật mới phát hiện được 403.

## 2. Sự thật quan trọng (đã đo)

1. **Trần output Claude = 128.000** (`max_tokens:128001` → 400). Field `max_tokens: 8192` trong `/v1/models` là **sai**.
   Ghi chú cũ "trần 8.192" đã lỗi thời. Không cần cắt file < 2k token hay ép `--max-tokens 5000` nữa.
2. **Thinking nằm TRONG `max_tokens`**. Nếu `max_tokens` quá nhỏ, thinking ăn hết chỗ → không có text
   (`stop_reason=max_tokens`, script trả `reason=thinking_exhausted`). Đo được: opus, effort max, max_tokens 1100 → 1100 token thinking, 0 text.
3. Thinking chỉ có tác dụng trên `/v1/messages` (`thinking:{type:"adaptive"}` + `output_config.effort`).
   Trên `/v1/chat/completions` field `thinking` **không được chứng minh là có tác dụng** (gateway nhận field lạ, vẫn trả 200).
4. Adaptive thinking: với prompt ngắn/dễ, Claude **tự chọn không nghĩ** ở mọi mức effort. Đây là hành vi đúng, không phải lỗi.
5. Prompt cache chạy trên `/v1/messages`: lần 2 đọc lại ~100% prefix. Gateway mặc định ghi cache **1h**. GPT không có cache.
6. GPT: **mỗi request tối thiểu $0.05**, kể cả `max_tokens:1`. Không dùng GPT để probe, benchmark hay thử tham số
   (đã từng mất ~$0.70 vì binary-search `max_tokens` trên GPT).
7. **Không có endpoint số dư/giá** (`/v1/me`, `/v1/balance`… đều 404). `est_cost_usd` chỉ là ước lượng; giá cache tính bảo thủ = giá input.
8. Ước lượng token: Claude 5.5 ~2.2 ký tự ASCII/token. Hệ số trong script đã chỉnh theo số đo này.

## 3. API

| Mục | Giá trị |
|---|---|
| Base | `https://api.orimise.com` (đổi bằng env `ORIMISE_BASE_URL`) |
| Messages | `POST /v1/messages`: `x-api-key` + `anthropic-version: 2023-06-01` |
| Chat | `POST /v1/chat/completions`: `Authorization: Bearer` |
| Danh mục (miễn phí) | `GET /models` → `{"models":[{"slug","context_window","supported_reasoning_levels":[{"effort"}]}]}` |
| Health | `GET /health` |

### error_code → hành vi script

| HTTP | `error_code` | Script |
|---|---|---|
| 403 | `MODEL_DISABLED_FOR_USER` | exit 4 `reason=model_unavailable`, **hoàn lượt** ledger, không retry |
| 404 | `MODEL_NOT_FOUND` | exit 4 `reason=model_unavailable`, hoàn lượt |
| 401 | `API_KEY_REQUIRED` / `INVALID_API_KEY` | exit 1 `reason=auth`, hoàn lượt |
| 400 | message chứa `max_tokens ... maximum allowed` | exit 1 `reason=max_tokens_invalid` |

## 4. Hòa vốn `gpt-6-luna` (phí sàn $0.05)

Chỉ tính phần input: so với haiku ($1/M) hòa vốn ≈ **55k token**; so với sonnet-5-5 ($2/M) ≈ **26k token** (giá `[ASSUMED]`).
Quy tắc thống nhất: **chunk < 50k token → KHÔNG dùng Luna**, gửi thẳng Claude. Claude nhận được 300k input nên thường không cần chia chunk.

## 5. Chưa xác minh (đừng coi là sự thật)

| Điều | Trạng thái |
|---|---|
| Giá từng model | ❓ không có endpoint giá |
| Trần output GPT | ❓ gateway nhận `max_tokens: 2.000.000` mà không báo lỗi |
| Effort `xhigh` qua `/v1/messages` | ❓ `/models` liệt kê cho sonnet-5-5 nhưng chưa gọi thử, nên script không cho dùng |
| Từ khoá kích hoạt `content_filter` trên model 5.5 | ❓ kinh nghiệm từ model cũ, chưa đo lại |
| Số dư / log | chỉ xem được qua MCP `orimise-user` |
