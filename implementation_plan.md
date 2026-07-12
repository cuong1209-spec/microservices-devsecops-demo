# Kế hoạch triển khai: Xây dựng ứng dụng Microservices Demo & Pipeline DevSecOps

Kế hoạch này mô tả cấu trúc thư mục, mã nguồn các dịch vụ microservices mẫu và cấu hình pipeline tích hợp bảo mật (Shift-Left Security) trên GitHub Actions.

## Kiến trúc thư mục đề xuất
Chúng ta sẽ tạo thư mục `demo-app` nằm trong workspace hiện tại với cấu trúc như sau:
```text
demo-app/
├── docker-compose.yml
├── api-gateway/
│   ├── Dockerfile
│   └── nginx.conf
├── product-service/
│   ├── Dockerfile
│   ├── package.json
│   └── server.js
├── order-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── .github/
    └── workflows/
        └── devsecops.yml
```

---

## Các thành phần chi tiết cần xây dựng

### 1. API Gateway (`api-gateway`)
*   Sử dụng **Nginx** làm Reverse Proxy để tiếp nhận các request từ clients.
*   Định tuyến (route):
    *   `/api/products` -> `product-service:3000`
    *   `/api/orders` -> `order-service:5000`

### 2. Product Service (`product-service`)
*   Viết bằng **Node.js (Express.js)**.
*   Cung cấp API lấy danh sách sản phẩm và chi tiết sản phẩm.
*   **Chủ ý chèn lỗ hổng:**
    *   Sử dụng một thư viện cũ trong `package.json` (ví dụ: `lodash` phiên bản cũ có lỗ hổng prototype pollution) để kiểm tra tính năng quét SCA (Trivy).
    *   Lỗi SQL Injection hoặc logic đơn giản để SAST (Semgrep) phát hiện.

### 3. Order Service (`order-service`)
*   Viết bằng **Python (Flask)**.
*   Cung cấp API tạo đơn hàng mới.
*   **Chủ ý chèn lỗ hổng:**
    *   Để lộ một chuỗi API Key giả trong file code (Hardcoded Secret) để kiểm tra Gitleaks/Secret scanning.

### 4. Docker Compose & Mạng nội bộ (`docker-compose.yml`)
*   Cấu hình chạy cả 3 service cùng một lúc.
*   Tạo mạng ảo nội bộ (`app-network`) giúp các service gọi nhau bằng tên service.

### 5. Cấu hình CI/CD Pipeline (`.github/workflows/devsecops.yml`)
*   **Triggers:** Chạy khi push code lên nhánh `main` hoặc tạo Pull Request.
*   **Jobs chạy song song (Parallel execution) để tối ưu hiệu năng:**
    *   `secret-scan`: Chạy Gitleaks phát hiện secret lộ trong commit.
    *   `sast-scan`: Chạy Semgrep quét mã nguồn Node.js và Python.
    *   `sca-scan`: Chạy Trivy quét file dependencies (`package.json`, `requirements.txt`).
*   **Jobs build & scan container:**
    *   `build-and-image-scan`: Chỉ chạy khi các job quét ở trên vượt qua (Passed). Tiến hành build Docker images và quét lỗ hổng của các image bằng Trivy (Container scan).

---

## Kế hoạch kiểm thử & Xác thực (Verification Plan)
1.  **Chạy thử nghiệm local:** Chạy `docker-compose up --build` tại máy local để đảm bảo các service hoạt động bình thường, API Gateway định tuyến chính xác.
2.  **Xác thực Pipeline bảo mật:**
    *   Đẩy mã nguồn lên GitHub.
    *   Quan sát pipeline GitHub Actions tự động kích hoạt.
    *   Kiểm tra xem các công cụ (Gitleaks, Semgrep, Trivy) có phát hiện đúng các lỗ hổng đã cố ý cài cắm hay không.
    *   Kiểm tra thời gian thực thi của từng job để đánh giá hiệu năng.
