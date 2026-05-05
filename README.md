# Electric Management

Phần mềm desktop quản lý dịch vụ cung cấp điện tại khu dân cư, xây dựng bằng `Python` và `PyQt5`. Ứng dụng được định hướng chỉ dành cho `Admin`; hộ dân hoặc đơn vị sử dụng điện không đăng nhập vào phần mềm.

## Mục Tiêu

- Quản lý hồ sơ hộ dân và đơn vị sử dụng điện.
- Ghi nhận chỉ số công tơ theo kỳ.
- Cấu hình biểu giá điện theo loại hợp đồng.
- Lập và quản lý hóa đơn điện.
- Admin ghi nhận giao dịch thu tiền, đối soát công nợ và cập nhật trạng thái hóa đơn.
- Tiếp nhận, phân loại và theo dõi sự cố điện.
- Xem báo cáo tổng quan doanh thu, hóa đơn, công nợ và vận hành.

## Tài Khoản Admin

Tài khoản mẫu khi chạy local:

```text
Username: admin
Password: admin123
Role: Admin
```

`AuthService` chỉ cho phép tài khoản có vai trò `Admin` truy cập hệ thống.

## Cấu Trúc Dự Án

```text
ElectricManagement/
├── main.py
├── app/
│   ├── core/
│   │   ├── database.py
│   │   ├── settings.py
│   │   └── sqlserver_schema.sql
│   ├── dto/
│   ├── models/
│   ├── repositories/
│   └── services/
├── ui/
│   ├── login.py
│   ├── main_window.py
│   ├── hodan.py
│   ├── congto.py
│   ├── hoadon.py
│   ├── thanhtoan.py
│   ├── suco.py
│   ├── report.py
│   └── tariff.py
└── data/
```

## Các Màn Hình Chính

- `Đăng nhập`: cổng đăng nhập dành riêng cho Admin.
- `Quản lý hộ dân`: quản lý hộ dân hoặc đơn vị sử dụng điện.
- `Quản lý công tơ`: ghi nhận chỉ số công tơ mới theo kỳ.
- `Quản lý hóa đơn`: quản lý hóa đơn điện, kỳ hóa đơn và trạng thái công nợ.
- `Quản lý thu tiền`: Admin ghi nhận khoản thu, lập mã biên nhận, đối soát và cập nhật hóa đơn.
- `Quản lý sự cố`: tiếp nhận và theo dõi sự cố điện.
- `Báo cáo - thống kê`: tổng quan doanh thu, hóa đơn, công nợ.
- `Biểu giá & hợp đồng`: cấu hình biểu giá và loại hợp đồng.

## Kiến Trúc

Luồng tổng quát:

```text
UI -> DTO -> Service -> Repository -> DatabaseManager -> SQL Server
```

Vai trò từng tầng:

- `ui/`: hiển thị giao diện PyQt5 và nhận thao tác Admin.
- `app/dto/`: dữ liệu vào/ra giữa UI và service.
- `app/models/`: entity nghiệp vụ.
- `app/repositories/`: truy cập database.
- `app/services/`: xử lý nghiệp vụ.
- `app/core/database.py`: kết nối, tạo schema và seed dữ liệu.

## Database

Database mục tiêu là `SQL Server`. SQLite chỉ dùng fallback khi chạy local hoặc khi máy chưa có SQL Server/ODBC driver.

Các bảng chính:

- `users`: tài khoản quản trị, chỉ vai trò `Admin`.
- `customers`: hộ dân hoặc đơn vị sử dụng điện.
- `tariff_configs`: cấu hình biểu giá.
- `meter_readings`: chỉ số công tơ, có Admin ghi nhận.
- `invoices`: hóa đơn điện, có Admin lập hóa đơn.
- `payments`: giao dịch thu tiền, có Admin ghi nhận khoản thu.
- `incidents`: sự cố điện, có Admin tiếp nhận.
- `audit_logs`: nhật ký thao tác quản trị.

File SQL Server đầy đủ nằm tại:

```text
app/core/sqlserver_schema.sql
```

Một phần schema quan trọng:

```sql
CREATE TABLE payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    receipt_code NVARCHAR(50) UNIQUE NOT NULL,
    invoice_code NVARCHAR(50) NOT NULL,
    paid_amount INT NOT NULL,
    payment_method NVARCHAR(50) NOT NULL,
    payer_name NVARCHAR(100) NOT NULL DEFAULT '',
    collected_by_user_id INT NOT NULL,
    note NVARCHAR(500) NOT NULL DEFAULT '',
    paid_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_payments_invoices FOREIGN KEY (invoice_code) REFERENCES invoices(invoice_code),
    CONSTRAINT FK_payments_users FOREIGN KEY (collected_by_user_id) REFERENCES users(id)
);
```

Thiết kế này thể hiện đúng nghiệp vụ: Admin không phải người thanh toán tiền điện; Admin là người ghi nhận khoản thu và đối soát công nợ.

## Cấu Hình SQL Server

Các biến môi trường hỗ trợ:

```text
DB_BACKEND=sqlserver
DB_SQLSERVER_HOST=localhost
DB_SQLSERVER_PORT=1433
DB_SQLSERVER_DATABASE=ElectricManagement
DB_SQLSERVER_USERNAME=sa
DB_SQLSERVER_PASSWORD=your_password
DB_SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
DB_SQLSERVER_TRUSTED_CONNECTION=0
```

Nếu dùng Windows Authentication:

```text
DB_SQLSERVER_TRUSTED_CONNECTION=1
```

Khi chưa có SQL Server local, có thể dùng:

```text
DB_BACKEND=sqlite
```

## Cách Chạy

Tại thư mục gốc dự án:

```powershell
venv\Scripts\python.exe main.py
```

Không nên chạy trực tiếp các file trong `ui/` trừ khi đang debug riêng từng màn hình.

## Tài Liệu Chi Tiết

Thiết kế class, quan hệ bảng và mã SQL Server đầy đủ được mô tả trong:

```text
DESIGN_README.md
```
