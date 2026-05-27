/*
    Electric Management - Database SQL Server

    Cach dung:
    1. Mo SQL Server Management Studio.
    2. Mo New Query.
    3. Copy toan bo file nay va bam Execute.

    Ghi chu:
    - File nay viet theo kieu SQL co ban thuong dung trong bai tap/bao cao:
      CREATE DATABASE -> CREATE TABLE -> FOREIGN KEY -> INSERT du lieu mau.
    - Neu muon chay lai tu dau, hay xoa database ElectricManagement thu cong
      trong SSMS truoc, hoac doi ten database o dong CREATE DATABASE.
*/

CREATE DATABASE ElectricManagement;
GO

USE ElectricManagement;
GO

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    role NVARCHAR(50) NOT NULL,
    display_name NVARCHAR(100) NOT NULL,
    is_active BIT NOT NULL DEFAULT 1
);
GO

CREATE TABLE customers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(50) NOT NULL UNIQUE,
    owner_name NVARCHAR(100) NOT NULL,
    address NVARCHAR(255) NOT NULL,
    phone_number NVARCHAR(20) NOT NULL,
    contract_type NVARCHAR(50) NOT NULL
);
GO

CREATE TABLE tariff_configs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    contract_type NVARCHAR(50) NOT NULL UNIQUE,
    fixed_fee INT NOT NULL,
    vat_percent FLOAT NOT NULL,
    peak_multiplier FLOAT NOT NULL,
    base_rate INT NOT NULL,
    formula_note NVARCHAR(MAX) NOT NULL,
    price_tiers NVARCHAR(MAX) NOT NULL DEFAULT N'',
    updated_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

CREATE TABLE meter_readings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(50) NOT NULL,
    reading_period NVARCHAR(20) NOT NULL,
    new_index INT NOT NULL,
    note NVARCHAR(500) NOT NULL DEFAULT N'',
    recorded_by_user_id INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    updated_by_user_id INT NULL,
    updated_at DATETIME2 NULL,

    CONSTRAINT UQ_meter_readings_customer_period UNIQUE (customer_code, reading_period),
    CONSTRAINT FK_meter_readings_customers
        FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
    CONSTRAINT FK_meter_readings_recorded_users
        FOREIGN KEY (recorded_by_user_id) REFERENCES users(id),
    CONSTRAINT FK_meter_readings_updated_users
        FOREIGN KEY (updated_by_user_id) REFERENCES users(id)
);
GO

CREATE TABLE invoices (
    id INT IDENTITY(1,1) PRIMARY KEY,
    invoice_code NVARCHAR(50) NOT NULL UNIQUE,
    customer_code NVARCHAR(50) NOT NULL,
    billing_period NVARCHAR(20) NOT NULL,
    consumption_kwh INT NOT NULL DEFAULT 0,
    fixed_fee INT NOT NULL DEFAULT 0,
    vat_amount INT NOT NULL DEFAULT 0,
    amount INT NOT NULL,
    status NVARCHAR(50) NOT NULL,
    issued_by_user_id INT NULL,
    issued_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

    CONSTRAINT UQ_invoices_customer_period UNIQUE (customer_code, billing_period),
    CONSTRAINT FK_invoices_customers
        FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
    CONSTRAINT FK_invoices_users
        FOREIGN KEY (issued_by_user_id) REFERENCES users(id)
);
GO

CREATE TABLE payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    receipt_code NVARCHAR(50) NOT NULL UNIQUE,
    invoice_code NVARCHAR(50) NOT NULL,
    paid_amount INT NOT NULL,
    payment_method NVARCHAR(50) NOT NULL,
    payer_name NVARCHAR(100) NOT NULL DEFAULT N'',
    collected_by_user_id INT NOT NULL,
    note NVARCHAR(500) NOT NULL DEFAULT N'',
    paid_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

    CONSTRAINT FK_payments_invoices
        FOREIGN KEY (invoice_code) REFERENCES invoices(invoice_code),
    CONSTRAINT FK_payments_users
        FOREIGN KEY (collected_by_user_id) REFERENCES users(id)
);
GO

CREATE TABLE incidents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_code NVARCHAR(50) NOT NULL,
    incident_type NVARCHAR(100) NOT NULL,
    priority NVARCHAR(50) NOT NULL,
    description NVARCHAR(500) NOT NULL,
    status NVARCHAR(50) NOT NULL,
    received_by_user_id INT NULL,
    received_date DATE NULL,

    CONSTRAINT FK_incidents_customers
        FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
    CONSTRAINT FK_incidents_users
        FOREIGN KEY (received_by_user_id) REFERENCES users(id)
);
GO

CREATE TABLE audit_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    action NVARCHAR(50) NOT NULL,
    entity_name NVARCHAR(100) NOT NULL,
    entity_key NVARCHAR(100) NOT NULL,
    description NVARCHAR(500) NOT NULL DEFAULT N'',
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),

    CONSTRAINT FK_audit_logs_users
        FOREIGN KEY (user_id) REFERENCES users(id)
);
GO

CREATE INDEX IX_meter_readings_customer_period
ON meter_readings(customer_code, reading_period);
GO

CREATE INDEX IX_invoices_customer_period
ON invoices(customer_code, billing_period);
GO

CREATE INDEX IX_invoices_status
ON invoices(status);
GO

CREATE INDEX IX_payments_invoice_code
ON payments(invoice_code);
GO

CREATE INDEX IX_incidents_customer_status
ON incidents(customer_code, status);
GO

CREATE INDEX IX_audit_logs_user_created_at
ON audit_logs(user_id, created_at);
GO

INSERT INTO users (username, password, role, display_name, is_active)
VALUES
(
    N'admin',
    N'sha256$240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    N'Admin',
    N'Quản trị viên',
    1
);
GO

INSERT INTO customers (customer_code, owner_name, address, phone_number, contract_type)
VALUES
    (N'HD001', N'Nguyễn Văn A', N'Khu A - Tổ 1', N'0901111111', N'Hộ gia đình'),
    (N'HD002', N'Trần Thị B', N'Khu A - Tổ 2', N'0902222222', N'Hộ gia đình'),
    (N'HD003', N'Xưởng May Hòa Phát', N'Khu B - Cụm công nghiệp 1', N'0903333333', N'Nhà máy'),
    (N'HD004', N'Lê Văn C', N'Khu C - Tổ 3', N'0904444444', N'Hộ gia đình'),
    (N'HD005', N'Cơ sở Gỗ Gia Hưng', N'Khu C - Xưởng 2', N'0905555555', N'Nhà máy');
GO

DECLARE @household_price_tiers NVARCHAR(MAX);

SET @household_price_tiers = N'[
  {"from_kwh":0,"to_kwh":50,"rate":1806},
  {"from_kwh":51,"to_kwh":100,"rate":1866},
  {"from_kwh":101,"to_kwh":200,"rate":2167},
  {"from_kwh":201,"to_kwh":300,"rate":2729},
  {"from_kwh":301,"to_kwh":400,"rate":3050},
  {"from_kwh":401,"to_kwh":null,"rate":3151}
]';

INSERT INTO tariff_configs (
    contract_type,
    fixed_fee,
    vat_percent,
    peak_multiplier,
    base_rate,
    formula_note,
    price_tiers
)
VALUES
(
    N'Hộ gia đình',
    35000,
    8.0,
    1.0,
    1806,
    N'Tính tiền điện hộ gia đình theo bậc thang sản lượng.',
    @household_price_tiers
),
(
    N'Nhà máy',
    150000,
    8.0,
    1.35,
    2450,
    N'Tính tiền điện sản xuất theo đơn giá cơ sở và hệ số giờ cao điểm.',
    N'[]'
);
GO

INSERT INTO meter_readings (customer_code, reading_period, new_index, note, recorded_by_user_id)
VALUES
    (N'HD001', N'01/2026', 120, N'Chỉ số đầu kỳ mẫu', 1),
    (N'HD001', N'02/2026', 310, N'Chỉ số tháng 02', 1),
    (N'HD002', N'01/2026', 80, N'Chỉ số đầu kỳ mẫu', 1),
    (N'HD002', N'02/2026', 245, N'Chỉ số tháng 02', 1),
    (N'HD003', N'01/2026', 1000, N'Chỉ số đầu kỳ mẫu', 1),
    (N'HD003', N'02/2026', 3600, N'Chỉ số tháng 02', 1),
    (N'HD004', N'01/2026', 50, N'Chỉ số đầu kỳ mẫu', 1),
    (N'HD004', N'02/2026', 180, N'Chỉ số tháng 02', 1),
    (N'HD005', N'01/2026', 900, N'Chỉ số đầu kỳ mẫu', 1),
    (N'HD005', N'02/2026', 2100, N'Chỉ số tháng 02', 1);
GO

INSERT INTO invoices (
    invoice_code,
    customer_code,
    billing_period,
    consumption_kwh,
    fixed_fee,
    vat_amount,
    amount,
    status,
    issued_by_user_id
)
VALUES
    (N'HDON-HD001-022026', N'HD001', N'02/2026', 190, 35000, 43346, 585176, N'Chưa thanh toán', 1),
    (N'HDON-HD002-022026', N'HD002', N'02/2026', 165, 35000, 37592, 507492, N'Đã thanh toán', 1),
    (N'HDON-HD003-022026', N'HD003', N'02/2026', 2600, 150000, 708784, 9568584, N'Chưa thanh toán', 1),
    (N'HDON-HD004-022026', N'HD004', N'02/2026', 130, 35000, 29074, 392494, N'Chưa thanh toán', 1),
    (N'HDON-HD005-022026', N'HD005', N'02/2026', 1200, 150000, 337128, 4551228, N'Đã thanh toán', 1);
GO

INSERT INTO payments (
    receipt_code,
    invoice_code,
    paid_amount,
    payment_method,
    payer_name,
    collected_by_user_id,
    note
)
VALUES
    (N'BN-HD002-022026', N'HDON-HD002-022026', 507492, N'Tiền mặt', N'Trần Thị B', 1, N'Thu đủ tiền điện tháng 02/2026'),
    (N'BN-HD005-022026', N'HDON-HD005-022026', 4551228, N'Chuyển khoản', N'Cơ sở Gỗ Gia Hưng', 1, N'Thu đủ tiền điện tháng 02/2026');
GO

INSERT INTO incidents (
    customer_code,
    incident_type,
    priority,
    description,
    status,
    received_by_user_id,
    received_date
)
VALUES
    (N'HD001', N'Mất điện', N'Cao', N'Hộ dân báo mất điện khu A.', N'Đang xử lý', 1, '2026-02-18'),
    (N'HD003', N'Công tơ bất thường', N'Trung bình', N'Cần kiểm tra lại chỉ số công tơ.', N'Mới tiếp nhận', 1, '2026-02-20');
GO

INSERT INTO audit_logs (user_id, action, entity_name, entity_key, description)
VALUES
    (1, N'INIT', N'system', N'sqlserver_schema', N'Tạo database SQL Server bằng script app/core/sqlserver_schema.sql.');
GO

SELECT N'Tạo database ElectricManagement thành công.' AS message;
GO
