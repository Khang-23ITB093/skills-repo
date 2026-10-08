# Cài đặt và Thiết lập Skills Hub cho Team (Antigravity)

Tài liệu này hướng dẫn các thành viên trong đội ngũ cài đặt và đồng bộ kho Skills & Rules về môi trường làm việc cá nhân.

---

## 1. Yêu cầu tiên quyết
- Git
- PowerShell (Windows) hoặc Bash (Linux/macOS)
- Google Antigravity / Gemini CLI đã cài đặt (thư mục cấu hình: `~/.gemini/config`)

---

## 2. Các bước cài đặt cho thành viên mới

### Bước 1: Clone repository
```bash
git clone <repo-url> skills-repo
cd skills-repo
```

### Bước 2: Đồng bộ các skills và rules nội bộ vào Antigravity
Trên Windows (PowerShell):
```powershell
.\scripts\sync.ps1 -Target global
```
Trên Linux / macOS (Bash):
```bash
chmod +x ./scripts/sync.sh
./scripts/sync.sh global
```

### Bước 3: Cài đặt các kỹ năng bên thứ ba (External Skills)
Kho chứa không commit các kỹ năng bên ngoài để tránh vi phạm bản quyền và lệch phiên bản. Danh sách phiên bản được khóa tại `skills.lock.md`.

Yêu cầu Antigravity Agent thực thi lệnh sau:
> *"Dùng skill-manager. Cài đặt tất cả các external skills được liệt kê trong file skills.lock.md đúng theo scope đã quy định."*

---

## 3. Quy trình đồng bộ khi repo có bản cập nhật mới
Khi có thông báo cập nhật từ team:
1. Chạy `git pull` để kéo các skills, rules và `skills.lock.md` mới nhất về.
2. Chạy `.\scripts\sync.ps1 -Target global` để đồng bộ vào Antigravity.
3. Nhờ Agent kiểm tra:
   > *"Dùng skill-manager kiểm tra và cập nhật toàn bộ skills kể cả external skills theo skills.lock.md."*
