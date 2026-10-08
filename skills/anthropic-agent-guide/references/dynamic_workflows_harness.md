# Dynamic Workflows: Kiến Trúc Đa Agent Tự Động Hóa Của Claude Code

Tài liệu này hướng dẫn chi tiết về cơ chế Dynamic Workflows — khả năng tự tạo lập và điều phối harness đa agent theo thời gian thực — cùng 6 mẫu hình (patterns) thực chiến và chính sách xử lý sự cố.

---

## 1. Tại Sao Cần Dynamic Workflows?

Khi một AI Agent làm việc trong một context window duy nhất qua thời gian dài, nó sẽ đối mặt với 3 tử huyệt cố hữu:
1. **Agentic Laziness (Lười biếng agentic)**: Agent dừng lại khi mới hoàn thành được một phần công việc (ví dụ: chỉ sửa 35/50 lỗi bảo mật được báo cáo) và vội vã tuyên bố hoàn tất.
2. **Self-Preferential Bias (Thiên vị giải pháp bản thân)**: Khi được yêu cầu tự đánh giá hoặc kiểm tra lại code của chính mình, agent có xu hướng bỏ qua lỗi logic do chính nó vừa viết ra.
3. **Goal Drift (Lạc mục tiêu)**: Sau nhiều vòng tóm tắt (compaction), các chi tiết ràng buộc nhỏ ("không được sửa file X", "bảo đảm backward compatibility") bị rơi rụng dần.

**Dynamic Workflows** giải quyết triệt để vấn đề này bằng cách phân bổ công việc cho các **subagents độc lập**, mỗi agent sở hữu context window sạch riêng biệt và mục tiêu chuyên biệt.

---

## 2. 6 Mẫu Hình Kiến Trúc Đa Agent (Workflow Patterns)

```mermaid
graph TD
    subgraph FanoutSynthesize [1. Fan-out & Synthesize]
        P1[Task lớn] --> S1[Worker 1]
        P1 --> S2[Worker 2]
        P1 --> S3[Worker N]
        S1 --> SYN[Synthesizer tổng hợp]
        S2 --> SYN
        S3 --> SYN
    end

    subgraph Adversarial [2. Adversarial Verification]
        W[Worker Agent] -->|Output| V[Skeptic Verifier Agent]
        V -->|Feedback| W
    end

    subgraph Tournament [3. Tournament Ranking]
        C1[Phương án A] vs C2[Phương án B] --> J1[Judge 1]
        C3[Phương án C] vs C4[Phương án D] --> J2[Judge 2]
        J1 --> F[Chung kết]
        J2 --> F
    end
```

### 1. Classify-and-Act (Phân loại rồi hành động)
Dùng một agent phân loại tác vụ (dựa trên mức độ phức tạp, ngôn ngữ, rủi ro) để định tuyến sang prompt hoặc model phù hợp (Haiku, Sonnet hoặc Opus).

### 2. Fan-out and Synthesize (Phân tán song song & Tổng hợp)
Chia nhỏ một tác vụ lớn (như refactor 20 files, phân tích 50 logs) thành các task con độc lập. Chạy song song từng task trên một context window sạch để tránh nhiễm chéo ngữ cảnh. Sau đó, một agent tổng hợp (Synthesizer) sẽ đứng tại rào chắn (barrier) để gộp kết quả.

### 3. Adversarial Verification (Kiểm chứng phản biện)
Đối với mỗi kết quả do worker sinh ra, chỉ định một **Skeptic Agent (Agent hoài nghi)** với tiêu chí khắt khe (rubric) độc lập để phản biện và tìm lỗ hổng trước khi cho phép áp dụng.

### 4. Generate-and-Filter (Sinh phương án & Sàng lọc)
Sinh ra một tập hợp nhiều ý tưởng/giải pháp khác nhau, sau đó chạy qua bộ lọc tự động (chạy test, đo benchmark, đối chiếu quy tắc) để chỉ giữ lại những phương án đạt chất lượng cao nhất.

### 5. Tournament (Thi đấu đối đầu xếp hạng)
Khi cần xếp hạng danh sách dài (như chọn tên hàm hay nhất, xếp hạng 50 ứng viên): việc chấm điểm tuyệt đối từ 1 đến 5 thường thiếu ổn định. Hãy tổ chức thi đấu theo cặp (pairwise tournament), trong đó mỗi trận đấu do một judge agent độc lập quyết định.

### 6. Loop-until-Done (Lặp cho tới khi hoàn tất)
Thay vì quy định số bước lặp cố định, agent tiếp tục chạy vòng lặp kiểm tra cho đến khi đạt được điều kiện dừng khách quan (như test suite exit code 0, hoặc log hệ thống không còn exception).

---

## 3. Chính Sách Xử Lý Lỗi Từng Phần (`PARTIAL_FAILURE_POLICY`)

Khi chạy fan-out $N$ subagents song song, nguy cơ một vài subagent gặp sự cố (timeout, rate limit, parse error) là điều không thể tránh khỏi. Cần áp dụng chính sách xử lý lỗi chuẩn mực:

1. **Chuẩn Hóa Kết Quả Trả Về Của Mọi Worker**:
   Mọi worker agent phải trả về cấu trúc dữ liệu JSON nhất quán:
   ```json
   {
     "task_id": "file_auth_jwt.py",
     "status": "ok", // hoặc "error"
     "result": { "findings": [...] },
     "error_msg": null
   }
   ```
2. **Quy Tắc Ngưỡng Thất Bại**:
   - **Nếu tỷ lệ lỗi $> 50\%$**: Toàn bộ quá trình tổng hợp bị hủy bỏ (`abort`), workflow ném ra ngoại lệ và báo cho người dùng kiểm tra lại môi trường.
   - **Nếu tỷ lệ lỗi $\le 50\%$**: Cho phép Synthesizer tiếp tục tổng hợp các kết quả thành công, nhưng **bắt buộc đánh dấu nhãn `[INCOMPLETE_DATA]`** tại tiêu đề báo cáo và liệt kê các task bị lỗi vào mục `MISSING_INFO`.

---

## 4. Cô Lập Môi Trường Bằng Git Worktree

Khi các subagents thực hiện sửa đổi mã nguồn song song, nếu cùng ghi vào một working directory sẽ gây ra xung đột file (race conditions).

**Giải pháp chuẩn của Claude Code**:
- Mỗi subagent thực thi trên một **Git Worktree riêng biệt**:
  ```bash
  git worktree add -b subtask-worker-1 ../worktree-worker-1 HEAD
  ```
- Sau khi worker hoàn tất và vượt qua bài kiểm tra kiểm chứng, thay đổi mới được merge về nhánh chính.
- Xóa bỏ worktree sau khi hoàn tất để giải phóng tài nguyên đĩa:
  ```bash
  git worktree remove ../worktree-worker-1 --force
  ```

---

## 5. Mô Hình Vùng Cách Ly (Quarantine Zone Pattern)

Khi xây dựng agent xử lý dữ liệu đầu vào công khai từ bên ngoài (như xử lý vé hỗ trợ, đọc nội dung website, bug report từ khách hàng):
- **Vùng cách ly (Untrusted Zone)**: Sử dụng các `Reader Agents` chỉ có quyền đọc (Read-only tools). Các agent này bóc tách dữ liệu, chuẩn hóa cấu trúc và tóm tắt thông tin.
- **Vùng tin cậy (Trusted Zone)**: Sử dụng `Actor Agents` có quyền thao tác thực tế (ghi file, chạy lệnh). Actor Agent **chỉ bao giờ nhìn thấy bản tóm tắt đã qua kiểm duyệt** từ Reader Agent, triệt tiêu hoàn toàn nguy cơ Prompt Injection từ dữ liệu người dùng lạ.

---

## 6. Giám Sát & Ghi Log Cấu Trúc (Structured Observability)

Trong các workflow đa agent phức tạp, việc truy vết lỗi và kiểm soát chi phí từng bước (step-level cost tracking) là yếu tố sống còn:

1. **Chuẩn Log JSONLINES Cho Từng Turn Của Agent**:
   Mọi turn gọi LLM hoặc tool execution nên được ghi log cấu trúc:
   ```json
   {
     "trace_id": "wf_20261007_001",
     "span_id": "step_verifier_4",
     "agent_role": "skeptic_verifier",
     "model": "claude-sonnet-4-6",
     "timestamp": "2026-10-07T23:15:00Z",
     "usage": {
       "prompt_tokens": 12450,
       "completion_tokens": 2310,
       "cached_tokens": 11800,
       "cost_usd": 0.0435
     },
     "decision": "REVISE_REQUIRED",
     "reason": "Missing validation for negative integers"
   }
   ```
2. **Sổ Cái Chi Phí (Cost Ledger)**:
   Mọi workflow phải duy trì một ledger cục bộ (như `scratch/orimise_ledger.json`) cập nhật sau mỗi call để ngăn chặn hiện tượng runaway loops (vòng lặp vô tận tiêu hao ngân sách).

