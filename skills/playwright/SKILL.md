---
name: playwright-testing
description: >-
  Kỹ năng và tài liệu hướng dẫn cho AI Agent sử dụng Playwright (thông qua MCP, 
  Agent CLI, và thư viện Node.js) để kiểm thử, điều khiển trình duyệt và tự động hóa web.
---

# Kỹ năng Kiểm thử và Tự động hóa với Playwright

Playwright cung cấp ba phương thức chính để con người và AI Agent tương tác với trình duyệt. Tuỳ thuộc vào bối cảnh (code script, chạy lệnh terminal, hay cấu hình server), bạn (AI Agent) cần biết chọn công cụ phù hợp.

## 1. Playwright Library (Thư viện Node.js truyền thống)
Dành cho việc viết kịch bản test (E2E testing) hoặc cào dữ liệu (scraping) bằng code.
*   **Cài đặt:** `npm init playwright@latest`
*   **Cách hoạt động:** Người dùng/Agent viết code Node.js (ví dụ `test.spec.ts`) gọi các hàm API của thư viện Playwright.
*   **Khi nào dùng:** Khi bạn được yêu cầu "viết test E2E", "viết script cào dữ liệu" hoặc tích hợp Playwright vào codebase của người dùng.
*   **Ví dụ Code cơ bản:**
    ```javascript
    const { chromium } = require('playwright');
    (async () => {
      const browser = await chromium.launch();
      const page = await browser.newPage();
      await page.goto('http://localhost:3030');
      await page.fill('#chat-input', 'Hello');
      await page.click('#btn-send');
      await browser.close();
    })();
    ```

## 2. Playwright Agent CLI (Công cụ dòng lệnh cho AI Agent)
Dành riêng cho các Coding Agents (như chính bạn, Claude Code, GitHub Copilot) khi bạn chỉ có quyền truy cập Terminal/Shell để tương tác với web.
*   **Cài đặt:** `npm i -g @playwright/cli@latest`
*   **Cách hoạt động:** Agent thực thi trực tiếp các câu lệnh bash trên terminal thay vì viết code hoặc gọi tool. Cực kỳ tối ưu Token vì nó trả về kết quả qua file nội bộ hệ thống thay vì đẩy toàn bộ DOM vào Context của LLM.
*   **Khi nào dùng:** Khi bạn (Agent) cần tự tay test một UI hoặc thao tác web mà không có sẵn tool `open_browser_url` hoặc khi tool mặc định bị lỗi.
*   **Lệnh cơ bản:**
    *   `playwright-cli open http://localhost:3030`
    *   `playwright-cli click "#btn-settings"`
    *   `playwright-cli type "#chat-input" "Xin chào"`
    *   `playwright-cli snapshot` (để lấy cấu trúc accessibility của trang hiện tại).

## 3. Playwright MCP (Model Context Protocol)
Dành cho việc tích hợp tính năng điều khiển trình duyệt thành Tool trực tiếp cho AI Assistant (như Cursor, Claude Desktop, Antigravity IDE).
*   **Cài đặt:** Thêm vào file cấu hình MCP (`mcp_config.json` hoặc cấu hình tương đương):
    ```json
    {
      "mcpServers": {
        "playwright": {
          "command": "npx",
          "args": ["-y", "@playwright/mcp@latest"]
        }
      }
    }
    ```
*   **Cách hoạt động:** Sau khi cài đặt, Agent sẽ có sẵn các "Tool" (như `playwright_navigate`, `playwright_click`, `playwright_fill`). Mỗi khi gọi tool, trình duyệt ngầm sẽ thực thi và trả về một **Accessibility Snapshot** (Bản đồ cấu trúc truy cập) dưới dạng JSON có cấu trúc rõ ràng.
*   **Khi nào dùng:** Khi bạn cần tương tác với web theo thời gian thực (Real-time), và Agent IDE của bạn hỗ trợ giao thức MCP. Phương pháp này giúp Agent "nhìn" thấy trang web một cách chính xác định dạng (deterministic).

## Tổng kết so sánh cho AI Agent:
| Tính năng | Playwright Agent CLI | Playwright MCP |
| :--- | :--- | :--- |
| **Cơ chế gọi lệnh** | Terminal (Lệnh Bash/Shell) | Cấu hình Server (MCP Tool Calls) |
| **Bảo toàn Context** | Tối ưu cao (Đọc qua File cục bộ) | Tiêu tốn hơn (Gửi snapshot qua Tool Response) |
| **Khuyên dùng khi** | Cần test nhanh, bị giới hạn Token | Có sẵn hệ sinh thái MCP, cần tương tác sâu |

*Ghi chú: Nếu hệ thống giả lập trình duyệt nội bộ của Agent bị lỗi (như lỗi 404 khi tải Driver Playwright), Agent có thể sử dụng `Playwright Agent CLI` như một giải pháp thay thế hoàn hảo ngay trong Terminal để vượt rào.*
