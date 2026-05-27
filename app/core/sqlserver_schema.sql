/*
    Electric Management - SQL Server setup script

    Cach dung:
    1. Mo SQL Server Management Studio hoac Azure Data Studio.
    2. Ket noi vao SQL Server.
    3. Copy toan bo file nay va chay.

    Script nay co the chay lai nhieu lan:
    - Tao database neu chua co.
    - Tao bang neu chua co.
    - Bo sung cot/index neu schema cu thieu.
    - Seed tai khoan Admin, ho dan mau va bieu gia mac dinh.
*/

USE [master];
GO

IF DB_ID(N'ElectricManagement') IS NULL
BEGIN
    CREATE DATABASE [ElectricManagement];
END;
GO

USE [ElectricManagement];
GO

SET NOCOUNT ON;
GO

IF OBJECT_ID(N'dbo.users', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(50) NOT NULL,
        password NVARCHAR(255) NOT NULL,
        role NVARCHAR(50) NOT NULL CONSTRAINT CK_users_role_admin CHECK (role = N'Admin'),
        display_name NVARCHAR(100) NOT NULL,
        is_active BIT NOT NULL CONSTRAINT DF_users_is_active DEFAULT 1,
        CONSTRAINT UQ_users_username UNIQUE (username)
    );
END;
GO

IF OBJECT_ID(N'dbo.customers', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.customers (
        id INT IDENTITY(1,1) PRIMARY KEY,
        customer_code NVARCHAR(50) NOT NULL,
        owner_name NVARCHAR(100) NOT NULL,
        address NVARCHAR(255) NOT NULL,
        phone_number NVARCHAR(20) NOT NULL,
        contract_type NVARCHAR(50) NOT NULL,
        CONSTRAINT UQ_customers_customer_code UNIQUE (customer_code)
    );
END;
GO

IF OBJECT_ID(N'dbo.tariff_configs', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.tariff_configs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        contract_type NVARCHAR(50) NOT NULL,
        fixed_fee INT NOT NULL,
        vat_percent FLOAT NOT NULL,
        peak_multiplier FLOAT NOT NULL,
        base_rate INT NOT NULL,
        formula_note NVARCHAR(MAX) NOT NULL,
        price_tiers NVARCHAR(MAX) NOT NULL CONSTRAINT DF_tariff_configs_price_tiers DEFAULT N'',
        updated_at DATETIME2 NOT NULL CONSTRAINT DF_tariff_configs_updated_at DEFAULT SYSDATETIME(),
        CONSTRAINT UQ_tariff_configs_contract_type UNIQUE (contract_type)
    );
END;
GO

IF OBJECT_ID(N'dbo.meter_readings', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.meter_readings (
        id INT IDENTITY(1,1) PRIMARY KEY,
        customer_code NVARCHAR(50) NOT NULL,
        reading_period NVARCHAR(20) NOT NULL,
        new_index INT NOT NULL,
        note NVARCHAR(500) NOT NULL CONSTRAINT DF_meter_readings_note DEFAULT N'',
        recorded_by_user_id INT NULL,
        created_at DATETIME2 NOT NULL CONSTRAINT DF_meter_readings_created_at DEFAULT SYSDATETIME(),
        updated_by_user_id INT NULL,
        updated_at DATETIME2 NULL,
        CONSTRAINT FK_meter_readings_customers FOREIGN KEY (customer_code) REFERENCES dbo.customers(customer_code),
        CONSTRAINT FK_meter_readings_recorded_users FOREIGN KEY (recorded_by_user_id) REFERENCES dbo.users(id),
        CONSTRAINT FK_meter_readings_updated_users FOREIGN KEY (updated_by_user_id) REFERENCES dbo.users(id),
        CONSTRAINT UQ_meter_readings_customer_period UNIQUE (customer_code, reading_period)
    );
END;
GO

IF OBJECT_ID(N'dbo.invoices', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.invoices (
        id INT IDENTITY(1,1) PRIMARY KEY,
        invoice_code NVARCHAR(50) NOT NULL,
        customer_code NVARCHAR(50) NOT NULL,
        billing_period NVARCHAR(20) NOT NULL,
        consumption_kwh INT NOT NULL CONSTRAINT DF_invoices_consumption_kwh DEFAULT 0,
        fixed_fee INT NOT NULL CONSTRAINT DF_invoices_fixed_fee DEFAULT 0,
        vat_amount INT NOT NULL CONSTRAINT DF_invoices_vat_amount DEFAULT 0,
        amount INT NOT NULL,
        status NVARCHAR(50) NOT NULL,
        issued_by_user_id INT NULL,
        issued_at DATETIME2 NOT NULL CONSTRAINT DF_invoices_issued_at DEFAULT SYSDATETIME(),
        CONSTRAINT UQ_invoices_invoice_code UNIQUE (invoice_code),
        CONSTRAINT UQ_invoices_customer_period UNIQUE (customer_code, billing_period),
        CONSTRAINT FK_invoices_customers FOREIGN KEY (customer_code) REFERENCES dbo.customers(customer_code),
        CONSTRAINT FK_invoices_users FOREIGN KEY (issued_by_user_id) REFERENCES dbo.users(id)
    );
END;
GO

IF OBJECT_ID(N'dbo.payments', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.payments (
        id INT IDENTITY(1,1) PRIMARY KEY,
        receipt_code NVARCHAR(50) NOT NULL,
        invoice_code NVARCHAR(50) NOT NULL,
        paid_amount INT NOT NULL,
        payment_method NVARCHAR(50) NOT NULL,
        payer_name NVARCHAR(100) NOT NULL CONSTRAINT DF_payments_payer_name DEFAULT N'',
        collected_by_user_id INT NOT NULL,
        note NVARCHAR(500) NOT NULL CONSTRAINT DF_payments_note DEFAULT N'',
        paid_at DATETIME2 NOT NULL CONSTRAINT DF_payments_paid_at DEFAULT SYSDATETIME(),
        CONSTRAINT UQ_payments_receipt_code UNIQUE (receipt_code),
        CONSTRAINT FK_payments_invoices FOREIGN KEY (invoice_code) REFERENCES dbo.invoices(invoice_code),
        CONSTRAINT FK_payments_users FOREIGN KEY (collected_by_user_id) REFERENCES dbo.users(id)
    );
END;
GO

IF OBJECT_ID(N'dbo.incidents', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.incidents (
        id INT IDENTITY(1,1) PRIMARY KEY,
        customer_code NVARCHAR(50) NOT NULL,
        incident_type NVARCHAR(100) NOT NULL,
        priority NVARCHAR(50) NOT NULL,
        description NVARCHAR(500) NOT NULL,
        status NVARCHAR(50) NOT NULL,
        received_by_user_id INT NULL,
        received_date DATE NULL,
        CONSTRAINT FK_incidents_customers FOREIGN KEY (customer_code) REFERENCES dbo.customers(customer_code),
        CONSTRAINT FK_incidents_users FOREIGN KEY (received_by_user_id) REFERENCES dbo.users(id)
    );
END;
GO

IF OBJECT_ID(N'dbo.audit_logs', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.audit_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        action NVARCHAR(50) NOT NULL,
        entity_name NVARCHAR(100) NOT NULL,
        entity_key NVARCHAR(100) NOT NULL,
        description NVARCHAR(500) NOT NULL CONSTRAINT DF_audit_logs_description DEFAULT N'',
        created_at DATETIME2 NOT NULL CONSTRAINT DF_audit_logs_created_at DEFAULT SYSDATETIME(),
        CONSTRAINT FK_audit_logs_users FOREIGN KEY (user_id) REFERENCES dbo.users(id)
    );
END;
GO

/* Migration cho database cu */
IF COL_LENGTH(N'dbo.tariff_configs', N'price_tiers') IS NULL
    ALTER TABLE dbo.tariff_configs ADD price_tiers NVARCHAR(MAX) NOT NULL CONSTRAINT DF_tariff_configs_price_tiers DEFAULT N'';
GO

IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = N'dbo'
      AND TABLE_NAME = N'tariff_configs'
      AND COLUMN_NAME = N'formula_note'
      AND CHARACTER_MAXIMUM_LENGTH <> -1
)
    ALTER TABLE dbo.tariff_configs ALTER COLUMN formula_note NVARCHAR(MAX) NOT NULL;
GO

IF COL_LENGTH(N'dbo.meter_readings', N'recorded_by_user_id') IS NULL
    ALTER TABLE dbo.meter_readings ADD recorded_by_user_id INT NULL;
GO

IF COL_LENGTH(N'dbo.meter_readings', N'updated_by_user_id') IS NULL
    ALTER TABLE dbo.meter_readings ADD updated_by_user_id INT NULL;
GO

IF COL_LENGTH(N'dbo.meter_readings', N'updated_at') IS NULL
    ALTER TABLE dbo.meter_readings ADD updated_at DATETIME2 NULL;
GO

IF COL_LENGTH(N'dbo.invoices', N'consumption_kwh') IS NULL
    ALTER TABLE dbo.invoices ADD consumption_kwh INT NOT NULL CONSTRAINT DF_invoices_consumption_kwh DEFAULT 0;
GO

IF COL_LENGTH(N'dbo.invoices', N'fixed_fee') IS NULL
    ALTER TABLE dbo.invoices ADD fixed_fee INT NOT NULL CONSTRAINT DF_invoices_fixed_fee DEFAULT 0;
GO

IF COL_LENGTH(N'dbo.invoices', N'vat_amount') IS NULL
    ALTER TABLE dbo.invoices ADD vat_amount INT NOT NULL CONSTRAINT DF_invoices_vat_amount DEFAULT 0;
GO

IF COL_LENGTH(N'dbo.invoices', N'issued_by_user_id') IS NULL
    ALTER TABLE dbo.invoices ADD issued_by_user_id INT NULL;
GO

IF COL_LENGTH(N'dbo.invoices', N'issued_at') IS NULL
    ALTER TABLE dbo.invoices ADD issued_at DATETIME2 NOT NULL CONSTRAINT DF_invoices_issued_at DEFAULT SYSDATETIME();
GO

IF COL_LENGTH(N'dbo.payments', N'receipt_code') IS NULL
    ALTER TABLE dbo.payments ADD receipt_code NVARCHAR(50) NULL;
GO

IF COL_LENGTH(N'dbo.payments', N'payer_name') IS NULL
    ALTER TABLE dbo.payments ADD payer_name NVARCHAR(100) NOT NULL CONSTRAINT DF_payments_payer_name DEFAULT N'';
GO

IF COL_LENGTH(N'dbo.payments', N'collected_by_user_id') IS NULL
    ALTER TABLE dbo.payments ADD collected_by_user_id INT NULL;
GO

IF COL_LENGTH(N'dbo.payments', N'note') IS NULL
    ALTER TABLE dbo.payments ADD note NVARCHAR(500) NOT NULL CONSTRAINT DF_payments_note DEFAULT N'';
GO

IF COL_LENGTH(N'dbo.incidents', N'received_by_user_id') IS NULL
    ALTER TABLE dbo.incidents ADD received_by_user_id INT NULL;
GO

/* Index */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_meter_readings_customer_period' AND object_id = OBJECT_ID(N'dbo.meter_readings'))
    CREATE INDEX IX_meter_readings_customer_period ON dbo.meter_readings(customer_code, reading_period);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_invoices_customer_period' AND object_id = OBJECT_ID(N'dbo.invoices'))
    CREATE INDEX IX_invoices_customer_period ON dbo.invoices(customer_code, billing_period);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_invoices_status' AND object_id = OBJECT_ID(N'dbo.invoices'))
    CREATE INDEX IX_invoices_status ON dbo.invoices(status);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_payments_invoice_code' AND object_id = OBJECT_ID(N'dbo.payments'))
    CREATE INDEX IX_payments_invoice_code ON dbo.payments(invoice_code);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_incidents_customer_status' AND object_id = OBJECT_ID(N'dbo.incidents'))
    CREATE INDEX IX_incidents_customer_status ON dbo.incidents(customer_code, status);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_audit_logs_user_created_at' AND object_id = OBJECT_ID(N'dbo.audit_logs'))
    CREATE INDEX IX_audit_logs_user_created_at ON dbo.audit_logs(user_id, created_at);
GO

/* Seed du lieu toi thieu */
IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE username = N'admin')
BEGIN
    INSERT INTO dbo.users (username, password, role, display_name, is_active)
    VALUES (
        N'admin',
        N'sha256$240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
        N'Admin',
        N'Quản trị viên',
        1
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.customers WHERE customer_code = N'HD001')
    INSERT INTO dbo.customers (customer_code, owner_name, address, phone_number, contract_type)
    VALUES (N'HD001', N'Nguyễn Văn A', N'Khu A - Tổ 1', N'0901111111', N'Hộ gia đình');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.customers WHERE customer_code = N'HD002')
    INSERT INTO dbo.customers (customer_code, owner_name, address, phone_number, contract_type)
    VALUES (N'HD002', N'Trần Thị B', N'Khu A - Tổ 2', N'0902222222', N'Hộ gia đình');
GO

IF NOT EXISTS (SELECT 1 FROM dbo.customers WHERE customer_code = N'HD003')
    INSERT INTO dbo.customers (customer_code, owner_name, address, phone_number, contract_type)
    VALUES (N'HD003', N'Xưởng May Hòa Phát', N'Khu B - Cụm CN 1', N'0903333333', N'Nhà máy');
GO

DECLARE @household_price_tiers NVARCHAR(MAX) = N'[
  {"from_kwh":0,"to_kwh":50,"rate":1806},
  {"from_kwh":51,"to_kwh":100,"rate":1866},
  {"from_kwh":101,"to_kwh":200,"rate":2167},
  {"from_kwh":201,"to_kwh":300,"rate":2729},
  {"from_kwh":301,"to_kwh":400,"rate":3050},
  {"from_kwh":401,"to_kwh":null,"rate":3151}
]';

IF NOT EXISTS (SELECT 1 FROM dbo.tariff_configs WHERE contract_type = N'Hộ gia đình')
BEGIN
    INSERT INTO dbo.tariff_configs (
        contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate,
        formula_note, price_tiers, updated_at
    )
    VALUES (
        N'Hộ gia đình',
        35000,
        8.0,
        1.0,
        1806,
        N'Biểu giá lũy tiến theo sản lượng tiêu thụ.',
        @household_price_tiers,
        SYSDATETIME()
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.tariff_configs WHERE contract_type = N'Nhà máy')
BEGIN
    INSERT INTO dbo.tariff_configs (
        contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate,
        formula_note, price_tiers, updated_at
    )
    VALUES (
        N'Nhà máy',
        150000,
        8.0,
        1.35,
        2450,
        N'Biểu giá sản xuất theo đơn giá cơ sở và hệ số giờ cao điểm.',
        N'[]',
        SYSDATETIME()
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.audit_logs WHERE entity_name = N'system' AND entity_key = N'sqlserver_schema')
BEGIN
    INSERT INTO dbo.audit_logs (user_id, action, entity_name, entity_key, description)
    SELECT TOP 1
        id,
        N'INIT',
        N'system',
        N'sqlserver_schema',
        N'Khởi tạo database SQL Server bằng script app/core/sqlserver_schema.sql.'
    FROM dbo.users
    WHERE username = N'admin';
END;
GO

SELECT N'Khởi tạo SQL Server database ElectricManagement thành công.' AS message;
GO
