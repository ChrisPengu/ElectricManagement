# Thiết Kế Class Và Database SQL Server

Tài liệu này mô tả thiết kế kỹ thuật của phần mềm quản lý dịch vụ cung cấp điện tại khu dân cư. Phần mềm chỉ dành cho `Admin`; người dân hoặc đơn vị sử dụng điện không đăng nhập vào hệ thống.

## 1. Kiến Trúc Tổng Quan

```text
UI (PyQt5)
  -> DTO
  -> Service
  -> Repository
  -> DatabaseManager
  -> SQL Server
```

Vai trò:

- `UI`: hiển thị giao diện, nhận thao tác của Admin.
- `DTO`: chuẩn hóa dữ liệu đi vào và đi ra giữa UI và service.
- `Service`: xử lý nghiệp vụ và kiểm tra điều kiện.
- `Repository`: đọc/ghi database.
- `Model`: biểu diễn dữ liệu nghiệp vụ.
- `DatabaseManager`: quản lý kết nối, schema, seed dữ liệu.

## 2. Module Chính

```text
app/
├── core/
│   ├── database.py
│   ├── settings.py
│   └── sqlserver_schema.sql
├── dto/
│   ├── requests.py
│   ├── responses.py
│   └── mappers.py
├── models/
├── repositories/
└── services/

ui/
├── login.py
├── main_window.py
├── hodan.py
├── congto.py
├── hoadon.py
├── thanhtoan.py
├── suco.py
├── report.py
└── tariff.py
```

## 3. Thiết Kế Nghiệp Vụ Admin-Only

Admin thực hiện các nghiệp vụ quản lý:

- Tạo và cập nhật hồ sơ hộ dân/đơn vị sử dụng điện.
- Ghi nhận chỉ số công tơ.
- Lập hóa đơn điện.
- Ghi nhận khoản thu từ hóa đơn và đối soát công nợ.
- Tiếp nhận sự cố.
- Cấu hình biểu giá.
- Xem báo cáo và nhật ký thao tác.

Admin không phải là người thanh toán tiền điện. Vì vậy bảng `payments` không mô tả “Admin thanh toán”, mà mô tả “Admin ghi nhận khoản thu”.

## 4. Entity Chính

### `UserAccount`

Tài khoản quản trị hệ thống.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `id` | Khóa chính |
| `username` | Tên đăng nhập |
| `password` | Mật khẩu demo hiện đang lưu dạng text |
| `role` | Vai trò, hiện chỉ hợp lệ là `Admin` |
| `display_name` | Tên hiển thị |
| `is_active` | Trạng thái hoạt động |

### `Customer`

Hộ dân hoặc đơn vị sử dụng điện.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `customer_code` | Mã hộ/đơn vị |
| `owner_name` | Chủ hộ hoặc đại diện đơn vị |
| `address` | Địa chỉ sử dụng điện |
| `phone_number` | Số điện thoại |
| `contract_type` | Loại hợp đồng |

### `TariffConfig`

Cấu hình biểu giá.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `contract_type` | Loại hợp đồng |
| `fixed_fee` | Phí cố định mỗi kỳ |
| `vat_percent` | VAT |
| `peak_multiplier` | Hệ số giờ cao điểm hoặc hệ số sản xuất |
| `base_rate` | Đơn giá cơ sở |
| `formula_note` | Ghi chú công thức |
| `updated_at` | Thời điểm cập nhật |

### `MeterReading`

Chỉ số công tơ theo kỳ.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `customer_code` | Hộ/đơn vị được ghi chỉ số |
| `reading_period` | Kỳ ghi chỉ số |
| `new_index` | Chỉ số mới |
| `note` | Ghi chú |
| `recorded_by_user_id` | Admin ghi nhận |
| `created_at` | Thời điểm tạo |

### `Invoice`

Hóa đơn điện.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `invoice_code` | Mã hóa đơn |
| `customer_code` | Hộ/đơn vị được lập hóa đơn |
| `billing_period` | Kỳ hóa đơn |
| `consumption_kwh` | Sản lượng tiêu thụ |
| `fixed_fee` | Phí cố định |
| `vat_amount` | Tiền VAT |
| `amount` | Tổng tiền |
| `status` | Trạng thái công nợ |
| `issued_by_user_id` | Admin lập hóa đơn |
| `issued_at` | Thời điểm lập |

### `Payment`

Giao dịch thu tiền do Admin ghi nhận.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `receipt_code` | Mã biên nhận |
| `invoice_code` | Hóa đơn được thu tiền |
| `paid_amount` | Số tiền đã thu |
| `payment_method` | Kênh thu: tiền mặt, chuyển khoản... |
| `payer_name` | Người nộp tiền |
| `collected_by_user_id` | Admin ghi nhận khoản thu |
| `note` | Ghi chú đối soát |
| `paid_at` | Thời điểm thu |

### `Incident`

Sự cố điện.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `customer_code` | Hộ/đơn vị liên quan |
| `incident_type` | Loại sự cố |
| `priority` | Mức ưu tiên |
| `description` | Mô tả |
| `status` | Trạng thái xử lý |
| `received_by_user_id` | Admin tiếp nhận |
| `received_date` | Ngày tiếp nhận |

### `AuditLog`

Nhật ký thao tác quản trị.

| Thuộc tính | Ý nghĩa |
| --- | --- |
| `user_id` | Admin thực hiện |
| `action` | Hành động |
| `entity_name` | Tên bảng/nghiệp vụ |
| `entity_key` | Khóa dữ liệu bị tác động |
| `description` | Mô tả thao tác |
| `created_at` | Thời điểm ghi log |

## 5. Quan Hệ Database

- `customers.customer_code` -> `meter_readings.customer_code`
- `customers.customer_code` -> `invoices.customer_code`
- `customers.customer_code` -> `incidents.customer_code`
- `invoices.invoice_code` -> `payments.invoice_code`
- `users.id` -> `meter_readings.recorded_by_user_id`
- `users.id` -> `invoices.issued_by_user_id`
- `users.id` -> `payments.collected_by_user_id`
- `users.id` -> `incidents.received_by_user_id`
- `users.id` -> `audit_logs.user_id`

## 6. Database SQL Server

Database mục tiêu: `ElectricManagement`

File schema dùng trực tiếp:

```text
app/core/sqlserver_schema.sql
```

Mã SQL Server:

```sql
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL CONSTRAINT CK_users_role_admin CHECK (role = N'Admin'),
    display_name NVARCHAR(100) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1
);

CREATE TABLE customers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(50) UNIQUE NOT NULL,
    owner_name NVARCHAR(100) NOT NULL,
    address NVARCHAR(255) NOT NULL,
    phone_number NVARCHAR(20) NOT NULL,
    contract_type NVARCHAR(50) NOT NULL
);

CREATE TABLE tariff_configs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    contract_type NVARCHAR(50) UNIQUE NOT NULL,
    fixed_fee INT NOT NULL,
    vat_percent FLOAT NOT NULL,
    peak_multiplier FLOAT NOT NULL,
    base_rate INT NOT NULL,
    formula_note NVARCHAR(500) NOT NULL,
    updated_at DATETIME2 NOT NULL
);

CREATE TABLE meter_readings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(50) NOT NULL,
    reading_period NVARCHAR(20) NOT NULL,
    new_index INT NOT NULL,
    note NVARCHAR(500) NOT NULL DEFAULT '',
    recorded_by_user_id INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_meter_readings_customers FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
    CONSTRAINT FK_meter_readings_users FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
);

CREATE TABLE invoices (
    id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_code NVARCHAR(50) UNIQUE NOT NULL,
    customer_code NVARCHAR(50) NOT NULL,
    billing_period NVARCHAR(20) NOT NULL,
    consumption_kwh INT NOT NULL DEFAULT 0,
    fixed_fee INT NOT NULL DEFAULT 0,
    vat_amount INT NOT NULL DEFAULT 0,
    amount INT NOT NULL,
    status NVARCHAR(50) NOT NULL,
    issued_by_user_id INT NULL,
    issued_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_invoices_customers FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
    CONSTRAINT FK_invoices_users FOREIGN KEY (issued_by_user_id) REFERENCES users(id)
);

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

CREATE TABLE incidents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(50) NOT NULL,
    incident_type NVARCHAR(100) NOT NULL,
    priority NVARCHAR(50) NOT NULL,
    description NVARCHAR(500) NOT NULL,
    status NVARCHAR(50) NOT NULL,
    received_by_user_id INT NULL,
    received_date DATE NULL,
    CONSTRAINT FK_incidents_customers FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
    CONSTRAINT FK_incidents_users FOREIGN KEY (received_by_user_id) REFERENCES users(id)
);

CREATE TABLE audit_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    entity_name NVARCHAR(100) NOT NULL,
    entity_key NVARCHAR(100) NOT NULL,
    description NVARCHAR(500) NOT NULL DEFAULT '',
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_audit_logs_users FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IX_meter_readings_customer_period ON meter_readings(customer_code, reading_period);
CREATE INDEX IX_invoices_customer_period ON invoices(customer_code, billing_period);
CREATE INDEX IX_invoices_status ON invoices(status);
CREATE INDEX IX_payments_invoice_code ON payments(invoice_code);
CREATE INDEX IX_incidents_customer_status ON incidents(customer_code, status);
CREATE INDEX IX_audit_logs_user_created_at ON audit_logs(user_id, created_at);
```

## 7. Cấu Hình Kết Nối

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

SQLite vẫn được giữ làm fallback local:

```text
DB_BACKEND=sqlite
```

## 8. Hướng Mở Rộng

- Thêm repository/service cho `meter_readings`, `invoices`, `payments`, `incidents`.
- Tự động lập hóa đơn từ chỉ số công tơ.
- Cập nhật trạng thái hóa đơn sau khi Admin ghi nhận khoản thu.
- Ghi `audit_logs` cho mọi thao tác thêm/sửa/xóa/đối soát.
- Mã hóa mật khẩu Admin thay vì lưu text.
- Xuất báo cáo Excel/PDF.
