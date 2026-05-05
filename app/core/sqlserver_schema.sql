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
