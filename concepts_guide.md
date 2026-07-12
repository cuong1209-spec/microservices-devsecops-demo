# Hướng Dẫn Cơ Bản: CI/CD Pipeline & Kiến Trúc Ứng Dụng Microservices Demo

Tài liệu này được biên soạn để giúp bạn nắm chắc các khái niệm cốt lõi trước khi đi vào xây dựng hệ thống thực tế.

---

## 1. CI/CD Pipeline Là Gì?

Hãy tưởng tượng **CI/CD Pipeline** giống như một **dây chuyền lắp ráp ô tô tự động** trong nhà máy:
*   **Trước đây (Thủ công):** Thợ cơ khí tự tay lắp ráp, tự chạy thử xe, tự lái xe ra showroom. Rất dễ xảy ra sai sót và tốn thời gian.
*   **Hiện nay (Tự động hóa - CI/CD):** Mỗi khi có linh kiện mới (code mới), dây chuyền tự động kiểm tra kích thước (chạy Unit Test), robot tự động sơn và lắp ráp (Build Docker Image), băng chuyền tự động chuyển xe đến bãi chạy thử (Deploy lên Staging) và kiểm tra an toàn (Security Scanning).

```
[ Developer ] --( Commit & Push Code )--> [ GitHub Repository ]
                                                   │
                                            (Tự động kích hoạt)
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CI/CD PIPELINE                                        │
│                                                                                         │
│  1. Kiểm tra (CI)     2. Kiểm tra bảo mật    3. Đóng gói (Build)   4. Triển khai (CD)   │
│  ┌──────────────┐     ┌─────────────────┐    ┌──────────────┐      ┌──────────────┐     │
│  │ - Lint Code  │ ──> │ - Quét Secrets  │ ──>│ - Build      │ ──>  │ - Deploy lên │     │
│  │ - Unit Test  │     │ - Quét Lỗ Hổng  │    │   Docker     │      │   Docker/VM  │     │
│  └──────────────┘     └─────────────────┘    └──────────────┘      └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

*   **CI (Continuous Integration - Tích hợp liên tục):** Là quá trình tự động kiểm tra code của các lập trình viên ngay khi họ đẩy lên server chung. Mục tiêu là phát hiện lỗi sớm.
*   **CD (Continuous Delivery / Deployment - Chuyển giao/Triển khai liên tục):** Là quá trình tự động đóng gói ứng dụng (thành Docker image) và đưa nó lên chạy thử hoặc chạy thật.

---

## 2. Ứng Dụng Microservices Demo Hoạt Động Thế Nào?

Để thực hành, chúng ta sẽ chọn một ứng dụng bán hàng đơn giản gồm **3 dịch vụ (Microservices)** chạy độc lập:

```
                          ┌────────────────────────┐
                          │   Frontend (Giao diện) │
                          │     (React / HTML5)    │
                          └───────────┬────────────┘
                                      │ (Gửi các HTTP Request)
                                      ▼
                          ┌────────────────────────┐
                          │  API Gateway (Nginx)   │ (Cổng đón tiếp duy nhất)
                          └─────┬────────────┬─────┘
                                │            │
            ┌───────────────────┘            └───────────────────┐
            ▼                                                    ▼
┌───────────────────────┐                            ┌───────────────────────┐
│    Product Service    │                            │     Order Service     │
│    (Node.js / Express)│                            │    (Python / Flask)   │
├───────────────────────┤                            ├───────────────────────┤
│    Database: MongoDB  │                            │ Database: PostgreSQL  │
└───────────────────────┘                            └───────────────────────┘
```

### Cơ chế hoạt động của Demo:
1.  **Frontend (Giao diện):** Người dùng lướt web, bấm xem sản phẩm hoặc bấm mua hàng.
2.  **API Gateway:** Nhận mọi yêu cầu từ trình duyệt. Nếu người dùng xem sản phẩm, nó sẽ chuyển tiếp yêu cầu đến **Product Service**. Nếu người dùng đặt hàng, nó chuyển yêu cầu đến **Order Service**.
3.  **Product Service (Node.js):** Quản lý sản phẩm. Kết nối với MongoDB để lấy dữ liệu sản phẩm gửi về cho người dùng.
4.  **Order Service (Python):** Quản lý đơn hàng. Kết nối với database PostgreSQL để lưu thông tin mua hàng.

### Cách chạy ứng dụng này:
Chúng ta sử dụng **Docker** và **Docker Compose**. 
*   Mỗi service và database sẽ chạy trong một **Docker Container** (giống như một máy ảo thu nhỏ, nhẹ và độc lập).
*   File `docker-compose.yml` sẽ định nghĩa cách các container này kết nối mạng (`network`) nội bộ với nhau. Chỉ cần gõ lệnh `docker-compose up` là cả hệ thống 5 container (Frontend, Gateway, Product, Order, 2 Databases) tự động chạy lên và kết nối với nhau.

---

## 3. Tại Sao Phải Tập Trung Vào "Hiệu Năng Pipeline"?

Trong môi trường thực tế, tốc độ phát triển phần mềm rất nhanh. Nếu một lượt chạy CI/CD mất **30 phút**, lập trình viên sẽ phải ngồi chơi xơ nước chờ đợi. Họ sẽ cảm thấy phiền phức và có xu hướng "tắt bớt" các bước kiểm tra bảo mật.

### Nguyên nhân gây chậm khi tích hợp quét bảo mật:
1.  **Tải dữ liệu lỗ hổng (Vulnerability DB):** Các công cụ như *Trivy* cần tải database chứa danh sách hàng vạn lỗ hổng trên thế giới về để đối chiếu. File này nặng khoảng 100MB - 300MB, tải đi tải lại ở mỗi commit sẽ cực kỳ chậm.
2.  **Phân tích mã nguồn tĩnh (SAST):** Phân tích cú pháp từng dòng code để tìm logic lỗi rất tốn RAM và CPU.
3.  **Quét động (DAST):** *OWASP ZAP* sẽ gửi hàng nghìn request thử tấn công (SQL Injection, brute force) vào web đang chạy. Bước này có thể mất từ 15 phút đến vài tiếng.

### Giải pháp tối ưu hiệu năng (Chủ đề chính đồ án của bạn):
Để giải quyết bài toán này, đồ án của bạn sẽ cấu hình Pipeline theo các chiến lược:

*   **Chiến lược 1: Cache Cơ Sở Dữ Liệu (Vulnerability DB Caching)**
    Cấu hình GitHub Actions lưu lại cache thư mục dữ liệu của Trivy. Lần chạy sau Trivy chỉ cần tải các bản cập nhật nhỏ thay vì tải lại toàn bộ.
*   **Chiến lược 2: Chạy Song Song (Parallel Execution)**
    Thay vì chạy tuần tự: *Quét Secret -> Quét SAST -> Quét SCA*, chúng ta cấu hình cho GitHub Actions chạy các job này song song trên các runner khác nhau.
*   **Chiến lược 3: Phân Phối Tần Suất Quét (Pipeline Tiering)**
    *   **Quét nhanh (SAST, SCA, Secret):** Chạy ở **mọi commit** (mất dưới 3 phút).
    *   **Quét trung bình (Container Scan):** Chỉ chạy khi code được merge vào nhánh `main` và build Docker Image chuẩn bị deploy (mất dưới 5 phút).
    *   **Quét sâu và chậm (DAST):** Không chạy ở mỗi commit. Chỉ chạy định kỳ hàng đêm (Nightly Build) hoặc khi chuẩn bị ra phiên bản lớn (Release).
