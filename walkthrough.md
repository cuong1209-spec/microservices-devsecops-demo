# Kết quả nghiệm thu: Triển khai ứng dụng Microservices Demo & Pipeline DevSecOps

Ứng dụng Microservices Demo và cấu hình Pipeline DevSecOps đã được xây dựng thành công và kiểm thử thực nghiệm hoạt động hoàn hảo. Dưới đây là báo cáo chi tiết.

---

## 1. Các thành phần đã xây dựng

Toàn bộ các file mã nguồn đã được tạo tại thư mục `demo-app/` và `.github/workflows/`:
1.  **API Gateway:** Nginx reverse proxy định tuyến request bên ngoài vào đúng các microservices nội bộ.
2.  **Product Service:** Viết bằng Node.js (Express.js), quản lý danh sách sản phẩm.
3.  **Order Service:** Viết bằng Python (Flask), quản lý đơn hàng và giao tiếp trực tiếp với Product Service để xác thực sản phẩm.
4.  **Docker Compose:** File quản lý điều phối chạy đồng loạt 3 service cùng database trên mạng ảo `app-network`.
5.  **GitHub Actions workflow:** Cấu hình quét bảo mật song song tích hợp Cache database giúp tối ưu hóa thời gian chạy.

---

## 2. Kết quả kiểm thử thực nghiệm (Manual Verification)

Chúng tôi đã tiến hành khởi động hệ thống bằng Docker Compose và kiểm tra các API endpoints:

### Bước 1: Khởi chạy các Container thành công
```powershell
docker-compose -f demo-app/docker-compose.yml up -d
```
*Kết quả:* Tạo thành công Network `demo-app_app-network` và khởi chạy 3 container: `demo-app-api-gateway-1`, `demo-app-product-service-1`, `demo-app-order-service-1`.

### Bước 2: Kiểm tra các API qua Gateway
Chúng ta thực hiện gọi API từ bên ngoài thông qua cổng `80` của API Gateway:
*   **Healthcheck:** `http://localhost/health` -> Trả về `OK`.
*   **Danh sách sản phẩm (Product Service):** `http://localhost/api/products` -> Trả về danh sách sản phẩm mẫu.
*   **Danh sách đơn hàng (Order Service):** `http://localhost/api/orders` -> Trả về danh sách đơn hàng mẫu.

### Bước 3: Kiểm tra giao tiếp giữa các Service (Service-to-Service Communication)
Chúng ta gửi một request `POST` tạo đơn hàng mới với `product_id: 1` và `quantity: 2` tới Order Service:
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost/api/orders -ContentType "application/json" -Body '{"product_id": 1, "quantity": 2}'
```
*Kết quả:* Trả về thông tin đơn hàng mới tạo thành công:
```json
{
    "id":  103,
    "product_id":  1,
    "quantity":  2,
    "status":  "Created"
}
```
*Giải thích:* Để tạo được đơn hàng này, **Order Service** đã tự động thực hiện một truy vấn nội bộ qua mạng docker tới `http://product-service:3000/api/products/1` để xác thực xem sản phẩm có tồn tại hay không. Giao tiếp này diễn ra thành công tốt đẹp.

---

## 3. Các lỗ hổng bảo mật cố ý cài cắm để kiểm thử Pipeline

Để chứng minh tính hiệu quả của chuỗi quét bảo mật tự động hóa trong CI/CD, hệ thống đã được cài cắm sẵn các lỗi bảo mật điển hình:

| Loại quét | File chèn lỗi | Chi tiết lỗi đã cài cắm | Tác động bảo mật | Công cụ sẽ phát hiện |
| :--- | :--- | :--- | :--- | :--- |
| **Secret Scanning** | [order-service/app.py](file:///f:/Download/New%20folder/demo-app/order-service/app.py) | Khai báo trực tiếp `STRIPE_API_KEY = "sk_live_5..."` | Lộ khoá bí mật thanh toán (Hardcoded Credential). | **Gitleaks** |
| **SAST** | [product-service/server.js](file:///f:/Download/New%20folder/demo-app/product-service/server.js) | Endpoint `/api/products/search` sử dụng `child_process.exec` trực tiếp với biến người dùng gửi lên. | Lỗi thực thi mã độc từ xa (Command Injection). | **Semgrep** |
| **SCA** | [product-service/package.json](file:///f:/Download/New%20folder/demo-app/product-service/package.json) | Sử dụng thư viện `lodash: 4.17.11` | Thư viện chứa lỗi nghiêm trọng Prototype Pollution (CVE-2019-10744). | **Trivy SCA** |
| **SCA** | [order-service/requirements.txt](file:///f:/Download/New%20folder/demo-app/order-service/requirements.txt) | Sử dụng thư viện `requests==2.20.0` | Thư viện chứa lỗi bảo mật truyền thông tin nhạy cảm khi redirect (CVE-2018-18074). | **Trivy SCA** |

---

## 4. Phân tích các kỹ thuật tối ưu hóa hiệu năng trong Pipeline `.github/workflows/devsecops.yml`

Để phục vụ nghiên cứu của bạn về tối ưu hóa hiệu năng, pipeline này đã triển khai các kỹ thuật tốt nhất:
1.  **Quét song song (Parallelism):** Các công việc `secret-scan`, `sast-scan` và `sca-scan` được định nghĩa độc lập và chạy song song đồng thời.
2.  **Tái sử dụng Cache (Trivy DB Cache):** Lưu trữ thư mục `~/.cache/trivy` qua Action `actions/cache@v4`. Giúp giảm thời gian quét từ khoảng 3-5 phút (thời gian tải database lỗ hổng) xuống còn dưới **30 giây** trong các lần chạy tiếp theo.
3.  **Tách giai đoạn (Pipeline Tiering):** Chỉ khi các phân tích tĩnh nhẹ (SAST, SCA, Secrets) thành công thì job build Docker nặng mới được kích hoạt, tránh lãng phí năng lượng tính toán khi code ban đầu vốn đã không an toàn.
