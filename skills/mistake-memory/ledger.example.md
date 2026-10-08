# Mistake Ledger (Template Mẫu)

> Persistent knowledge base of coding mistakes. Each entry represents a **domain of errors**,
> not a single instance. Entries are append-only: never delete, only add or update.
>
> This ledger is automatically consulted before writing code in any matching context.

---

## [ERR-000] Mẫu Ghi Nhận Lỗi (Template)

- **First Detected**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD
- **Occurrences**: 1
- **Trigger**: [User correction / CI failure / Review]
- **Severity**: [Low / Medium / High / Critical]

### Surface Error
Mô tả vắn tắt lỗi bề mặt xuất hiện trong code.

```
<!-- ❌ WRONG -->
Code sai...

<!-- ✅ CORRECT -->
Code đúng...
```

### Root Cause Domain
Phân tích nguyên nhân gốc rễ và phạm trù lỗi.

### Complete Rule Set
Bảng quy tắc đầy đủ cần tuân thủ.

### Prevention Checklist
- [ ] Checklist kiểm tra trước khi bàn giao code.
