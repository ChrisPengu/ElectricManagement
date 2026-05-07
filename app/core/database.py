import sqlite3
import hashlib
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator

from app.core.settings import DatabaseSettings


class DatabaseManager:
    def __init__(self, settings: DatabaseSettings | None = None):
        self.settings = settings or DatabaseSettings.from_env()
        self.backend = self.settings.backend
        self.db_path = self.settings.sqlite_path
        self._sqlserver_module = None
        self._mongodb_client = None
        self._mongodb_database = None

        if self.backend == "sqlite":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        if self.backend == "sqlserver":
            return self._connect_sqlserver()
        if self.backend == "mongodb":
            return self.mongo_database
        return self._connect_sqlite()

    @contextmanager
    def session(self) -> Iterator[Any]:
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        if self.backend == "mongodb":
            raise RuntimeError("MongoDB backend uses repository collection APIs, not SQL fetch_one.")
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_dict(cursor, row)

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if self.backend == "mongodb":
            raise RuntimeError("MongoDB backend uses repository collection APIs, not SQL fetch_all.")
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        if self.backend == "mongodb":
            raise RuntimeError("MongoDB backend uses repository collection APIs, not SQL execute.")
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()

    def executemany(self, query: str, params_list: Iterable[tuple[Any, ...]]) -> None:
        if self.backend == "mongodb":
            raise RuntimeError("MongoDB backend uses repository collection APIs, not SQL executemany.")
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.executemany(query, list(params_list))
            connection.commit()

    def has_column(self, table_name: str, column_name: str) -> bool:
        if self.backend == "mongodb":
            return True
        if self.backend == "sqlserver":
            row = self.fetch_one(
                """
                SELECT 1 AS found
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
                """,
                (table_name, column_name),
            )
            return row is not None

        rows = self.fetch_all(f"PRAGMA table_info({table_name})")
        return any(row["name"] == column_name for row in rows)

    def initialize(self) -> None:
        if self.backend == "mongodb":
            self._initialize_mongodb()
            return
        try:
            with self.session() as connection:
                cursor = connection.cursor()
                for statement in self._schema_statements():
                    cursor.execute(statement)
                if self.backend == "sqlite":
                    self._migrate_sqlite_schema(cursor)
                self._seed_default_data(cursor)
                connection.commit()
        except sqlite3.OperationalError as exc:
            if self.backend == "sqlite" and "readonly" in str(exc).lower():
                self._validate_readonly_sqlite()
                return
            raise

    def _connect_sqlite(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @property
    def mongo_database(self):
        if self._mongodb_database is None:
            self._mongodb_database = self._connect_mongodb()
        return self._mongodb_database

    def mongo_collection(self, name: str):
        return self.mongo_database[name]

    def next_sequence(self, name: str) -> int:
        result = self.mongo_collection("counters").find_one_and_update(
            {"_id": name},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=self._mongo_return_document().AFTER,
        )
        return int(result["value"])

    def _connect_mongodb(self):
        pymongo = self._import_pymongo()
        self._mongodb_client = pymongo.MongoClient(self.settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        self._mongodb_client.admin.command("ping")
        return self._mongodb_client[self.settings.mongodb_database]

    def _import_pymongo(self):
        try:
            import pymongo  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "MongoDB backend requires `pymongo`. "
                "Install it with `venv\\Scripts\\python.exe -m pip install pymongo`, "
                "or set DB_BACKEND=sqlite."
            ) from exc
        return pymongo

    def _mongo_return_document(self):
        pymongo = self._import_pymongo()
        return pymongo.ReturnDocument

    def _connect_sqlserver(self):
        pyodbc = self._import_pyodbc()
        settings = self.settings

        if settings.sqlserver_trusted_connection:
            connection_string = (
                f"DRIVER={{{settings.sqlserver_driver}}};"
                f"SERVER={settings.sqlserver_host},{settings.sqlserver_port};"
                f"DATABASE={settings.sqlserver_database};"
                "Trusted_Connection=yes;"
            )
        else:
            connection_string = (
                f"DRIVER={{{settings.sqlserver_driver}}};"
                f"SERVER={settings.sqlserver_host},{settings.sqlserver_port};"
                f"DATABASE={settings.sqlserver_database};"
                f"UID={settings.sqlserver_username};"
                f"PWD={settings.sqlserver_password};"
            )

        return pyodbc.connect(connection_string)

    def _import_pyodbc(self):
        if self._sqlserver_module is not None:
            return self._sqlserver_module

        try:
            import pyodbc  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "SQL Server backend requires `pyodbc`. "
                "Install pyodbc and an ODBC driver, or set DB_BACKEND=sqlite for local development."
            ) from exc

        self._sqlserver_module = pyodbc
        return pyodbc

    def _row_to_dict(self, cursor, row) -> dict[str, Any]:
        columns = [column[0] for column in cursor.description]
        if isinstance(row, sqlite3.Row):
            return {column: row[column] for column in columns}
        return dict(zip(columns, row))

    def _validate_readonly_sqlite(self) -> None:
        required_tables = {
            "users",
            "customers",
            "tariff_configs",
            "meter_readings",
            "invoices",
            "payments",
            "incidents",
        }

        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
            existing_tables = {row[0] for row in cursor.fetchall()}

        missing_tables = sorted(required_tables - existing_tables)
        if missing_tables:
            missing_list = ", ".join(missing_tables)
            raise RuntimeError(
                "SQLite database is read-only and cannot be initialized. "
                f"Missing required tables: {missing_list}."
            )

    def _migrate_sqlite_schema(self, cursor) -> None:
        migrations = {
            "meter_readings": [
                ("recorded_by_user_id", "ALTER TABLE meter_readings ADD COLUMN recorded_by_user_id INTEGER"),
            ],
            "invoices": [
                ("consumption_kwh", "ALTER TABLE invoices ADD COLUMN consumption_kwh INTEGER NOT NULL DEFAULT 0"),
                ("fixed_fee", "ALTER TABLE invoices ADD COLUMN fixed_fee INTEGER NOT NULL DEFAULT 0"),
                ("vat_amount", "ALTER TABLE invoices ADD COLUMN vat_amount INTEGER NOT NULL DEFAULT 0"),
                ("issued_by_user_id", "ALTER TABLE invoices ADD COLUMN issued_by_user_id INTEGER"),
                ("issued_at", "ALTER TABLE invoices ADD COLUMN issued_at TEXT NOT NULL DEFAULT ''"),
            ],
            "payments": [
                ("receipt_code", "ALTER TABLE payments ADD COLUMN receipt_code TEXT"),
                ("payer_name", "ALTER TABLE payments ADD COLUMN payer_name TEXT NOT NULL DEFAULT ''"),
                ("collected_by_user_id", "ALTER TABLE payments ADD COLUMN collected_by_user_id INTEGER"),
                ("note", "ALTER TABLE payments ADD COLUMN note TEXT NOT NULL DEFAULT ''"),
            ],
            "incidents": [
                ("received_by_user_id", "ALTER TABLE incidents ADD COLUMN received_by_user_id INTEGER"),
            ],
        }

        for table, column_migrations in migrations.items():
            cursor.execute(f"PRAGMA table_info({table})")
            existing_columns = {row[1] for row in cursor.fetchall()}
            for column_name, statement in column_migrations:
                if column_name not in existing_columns:
                    cursor.execute(statement)

    def _schema_statements(self) -> Iterable[str]:
        if self.backend == "sqlserver":
            return self._sqlserver_schema_statements()
        return self._sqlite_schema_statements()

    def _sqlite_schema_statements(self) -> Iterable[str]:
        return [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                display_name TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT UNIQUE NOT NULL,
                owner_name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                contract_type TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tariff_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_type TEXT UNIQUE NOT NULL,
                fixed_fee INTEGER NOT NULL,
                vat_percent REAL NOT NULL,
                peak_multiplier REAL NOT NULL,
                base_rate INTEGER NOT NULL,
                formula_note TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS meter_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT NOT NULL,
                reading_period TEXT NOT NULL,
                new_index INTEGER NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                recorded_by_user_id INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
                FOREIGN KEY (recorded_by_user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_code TEXT UNIQUE NOT NULL,
                customer_code TEXT NOT NULL,
                billing_period TEXT NOT NULL,
                consumption_kwh INTEGER NOT NULL DEFAULT 0,
                fixed_fee INTEGER NOT NULL DEFAULT 0,
                vat_amount INTEGER NOT NULL DEFAULT 0,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL,
                issued_by_user_id INTEGER,
                issued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
                FOREIGN KEY (issued_by_user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_code TEXT UNIQUE NOT NULL,
                invoice_code TEXT NOT NULL,
                paid_amount INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                payer_name TEXT NOT NULL DEFAULT '',
                collected_by_user_id INTEGER NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_code) REFERENCES invoices(invoice_code),
                FOREIGN KEY (collected_by_user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                received_by_user_id INTEGER,
                received_date TEXT,
                FOREIGN KEY (customer_code) REFERENCES customers(customer_code),
                FOREIGN KEY (received_by_user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                entity_name TEXT NOT NULL,
                entity_key TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
        ]

    def _sqlserver_schema_statements(self) -> Iterable[str]:
        return [
            """
            IF OBJECT_ID('users', 'U') IS NULL
            CREATE TABLE users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                username NVARCHAR(50) UNIQUE NOT NULL,
                password NVARCHAR(255) NOT NULL,
                role NVARCHAR(50) NOT NULL CONSTRAINT CK_users_role_admin CHECK (role = N'Admin'),
                display_name NVARCHAR(100) NOT NULL,
                is_active BIT NOT NULL DEFAULT 1
            )
            """,
            """
            IF OBJECT_ID('customers', 'U') IS NULL
            CREATE TABLE customers (
                id INT IDENTITY(1,1) PRIMARY KEY,
                customer_code NVARCHAR(50) UNIQUE NOT NULL,
                owner_name NVARCHAR(100) NOT NULL,
                address NVARCHAR(255) NOT NULL,
                phone_number NVARCHAR(20) NOT NULL,
                contract_type NVARCHAR(50) NOT NULL
            )
            """,
            """
            IF OBJECT_ID('tariff_configs', 'U') IS NULL
            CREATE TABLE tariff_configs (
                id INT IDENTITY(1,1) PRIMARY KEY,
                contract_type NVARCHAR(50) UNIQUE NOT NULL,
                fixed_fee INT NOT NULL,
                vat_percent FLOAT NOT NULL,
                peak_multiplier FLOAT NOT NULL,
                base_rate INT NOT NULL,
                formula_note NVARCHAR(500) NOT NULL,
                updated_at DATETIME2 NOT NULL
            )
            """,
            """
            IF OBJECT_ID('meter_readings', 'U') IS NULL
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
            )
            """,
            """
            IF OBJECT_ID('invoices', 'U') IS NULL
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
            )
            """,
            """
            IF OBJECT_ID('payments', 'U') IS NULL
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
            )
            """,
            """
            IF OBJECT_ID('incidents', 'U') IS NULL
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
            )
            """,
            """
            IF OBJECT_ID('audit_logs', 'U') IS NULL
            CREATE TABLE audit_logs (
                id INT IDENTITY(1,1) PRIMARY KEY,
                user_id INT NOT NULL,
                action NVARCHAR(50) NOT NULL,
                entity_name NVARCHAR(100) NOT NULL,
                entity_key NVARCHAR(100) NOT NULL,
                description NVARCHAR(500) NOT NULL DEFAULT '',
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
                CONSTRAINT FK_audit_logs_users FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            IF COL_LENGTH('meter_readings', 'recorded_by_user_id') IS NULL
            ALTER TABLE meter_readings ADD recorded_by_user_id INT NULL
            """,
            """
            IF COL_LENGTH('invoices', 'consumption_kwh') IS NULL
            ALTER TABLE invoices ADD consumption_kwh INT NOT NULL CONSTRAINT DF_invoices_consumption_kwh DEFAULT 0
            """,
            """
            IF COL_LENGTH('invoices', 'fixed_fee') IS NULL
            ALTER TABLE invoices ADD fixed_fee INT NOT NULL CONSTRAINT DF_invoices_fixed_fee DEFAULT 0
            """,
            """
            IF COL_LENGTH('invoices', 'vat_amount') IS NULL
            ALTER TABLE invoices ADD vat_amount INT NOT NULL CONSTRAINT DF_invoices_vat_amount DEFAULT 0
            """,
            """
            IF COL_LENGTH('invoices', 'issued_by_user_id') IS NULL
            ALTER TABLE invoices ADD issued_by_user_id INT NULL
            """,
            """
            IF COL_LENGTH('invoices', 'issued_at') IS NULL
            ALTER TABLE invoices ADD issued_at DATETIME2 NOT NULL CONSTRAINT DF_invoices_issued_at DEFAULT SYSDATETIME()
            """,
            """
            IF COL_LENGTH('payments', 'receipt_code') IS NULL
            ALTER TABLE payments ADD receipt_code NVARCHAR(50) NULL
            """,
            """
            IF COL_LENGTH('payments', 'payer_name') IS NULL
            ALTER TABLE payments ADD payer_name NVARCHAR(100) NOT NULL CONSTRAINT DF_payments_payer_name DEFAULT ''
            """,
            """
            IF COL_LENGTH('payments', 'collected_by_user_id') IS NULL
            ALTER TABLE payments ADD collected_by_user_id INT NULL
            """,
            """
            IF COL_LENGTH('payments', 'note') IS NULL
            ALTER TABLE payments ADD note NVARCHAR(500) NOT NULL CONSTRAINT DF_payments_note DEFAULT ''
            """,
            """
            IF COL_LENGTH('incidents', 'received_by_user_id') IS NULL
            ALTER TABLE incidents ADD received_by_user_id INT NULL
            """,
        ]

    def _seed_default_data(self, cursor) -> None:
        if self.backend == "sqlserver":
            self._seed_sqlserver(cursor)
        else:
            self._seed_sqlite(cursor)

    def _initialize_mongodb(self) -> None:
        db = self.mongo_database
        db.users.create_index("username", unique=True)
        db.customers.create_index("customer_code", unique=True)
        db.tariff_configs.create_index("contract_type", unique=True)
        db.meter_readings.create_index([("customer_code", 1), ("reading_period", 1)], unique=True)
        db.invoices.create_index("invoice_code", unique=True)
        db.invoices.create_index([("customer_code", 1), ("billing_period", 1)], unique=True)
        db.payments.create_index("receipt_code", unique=True)

        if db.users.count_documents({"username": "admin"}) == 0:
            db.users.insert_one(
                {
                    "id": self.next_sequence("users"),
                    "username": "admin",
                    "password": self._hash_password("admin123"),
                    "role": "Admin",
                    "display_name": "Quản trị viên",
                    "is_active": True,
                }
            )

        customer_rows = [
            ("HD001", "Nguyễn Văn A", "Khu A - Tổ 1", "0901111111", "Hộ gia đình"),
            ("HD002", "Trần Thị B", "Khu A - Tổ 2", "0902222222", "Hộ gia đình"),
            ("HD003", "Xưởng May Hòa Phát", "Khu B - Cụm CN 1", "0903333333", "Nhà máy"),
        ]
        for customer_code, owner_name, address, phone_number, contract_type in customer_rows:
            db.customers.update_one(
                {"customer_code": customer_code},
                {
                    "$setOnInsert": {
                        "id": self.next_sequence("customers"),
                        "customer_code": customer_code,
                        "owner_name": owner_name,
                        "address": address,
                        "phone_number": phone_number,
                        "contract_type": contract_type,
                    }
                },
                upsert=True,
            )

        tariff_rows = [
            ("Hộ gia đình", 35000, 8.0, 1.0, 1806, "Biểu giá lũy tiến theo sản lượng tiêu thụ."),
            ("Nhà máy", 150000, 8.0, 1.35, 2450, "Biểu giá sản xuất theo khung giờ và hệ số cao điểm."),
        ]
        for contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate, formula_note in tariff_rows:
            db.tariff_configs.update_one(
                {"contract_type": contract_type},
                {
                    "$setOnInsert": {
                        "id": self.next_sequence("tariff_configs"),
                        "contract_type": contract_type,
                        "fixed_fee": fixed_fee,
                        "vat_percent": vat_percent,
                        "peak_multiplier": peak_multiplier,
                        "base_rate": base_rate,
                        "formula_note": formula_note,
                        "updated_at": __import__("datetime").datetime.now(),
                    }
                },
                upsert=True,
            )

    def _seed_sqlite(self, cursor) -> None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (username, password, role, display_name, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", self._hash_password("admin123"), "Admin", "Quản trị viên", 1),
        )

        cursor.executemany(
            """
            INSERT OR IGNORE INTO customers (customer_code, owner_name, address, phone_number, contract_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("HD001", "Nguyễn Văn A", "Khu A - Tổ 1", "0901111111", "Hộ gia đình"),
                ("HD002", "Trần Thị B", "Khu A - Tổ 2", "0902222222", "Hộ gia đình"),
                ("HD003", "Xưởng May Hòa Phát", "Khu B - Cụm CN 1", "0903333333", "Nhà máy"),
            ],
        )

        cursor.executemany(
            """
            INSERT OR IGNORE INTO tariff_configs (
                contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate, formula_note, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            [
                ("Hộ gia đình", 35000, 8.0, 1.0, 1806, "Biểu giá lũy tiến theo sản lượng tiêu thụ."),
                ("Nhà máy", 150000, 8.0, 1.35, 2450, "Biểu giá sản xuất theo khung giờ và hệ số cao điểm."),
            ],
        )

    def _seed_sqlserver(self, cursor) -> None:
        cursor.execute(
            """
            IF NOT EXISTS (SELECT 1 FROM users WHERE username = ?)
            INSERT INTO users (username, password, role, display_name, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", "admin", self._hash_password("admin123"), "Admin", "Quản trị viên", 1),
        )

        customer_rows = [
            ("HD001", "Nguyễn Văn A", "Khu A - Tổ 1", "0901111111", "Hộ gia đình"),
            ("HD002", "Trần Thị B", "Khu A - Tổ 2", "0902222222", "Hộ gia đình"),
            ("HD003", "Xưởng May Hòa Phát", "Khu B - Cụm CN 1", "0903333333", "Nhà máy"),
        ]
        for customer in customer_rows:
            cursor.execute(
                """
                IF NOT EXISTS (SELECT 1 FROM customers WHERE customer_code = ?)
                INSERT INTO customers (customer_code, owner_name, address, phone_number, contract_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (customer[0], *customer),
            )

        tariff_rows = [
            ("Hộ gia đình", 35000, 8.0, 1.0, 1806, "Biểu giá lũy tiến theo sản lượng tiêu thụ."),
            ("Nhà máy", 150000, 8.0, 1.35, 2450, "Biểu giá sản xuất theo khung giờ và hệ số cao điểm."),
        ]
        for tariff in tariff_rows:
            cursor.execute(
                """
                IF NOT EXISTS (SELECT 1 FROM tariff_configs WHERE contract_type = ?)
                INSERT INTO tariff_configs (
                    contract_type, fixed_fee, vat_percent, peak_multiplier, base_rate, formula_note, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, SYSDATETIME())
                """,
                (tariff[0], *tariff),
            )

    def _hash_password(self, password: str) -> str:
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return f"sha256${digest}"
