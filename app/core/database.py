import sqlite3
import hashlib
from contextlib import contextmanager
from datetime import datetime
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
        self._mongodb_client = pymongo.MongoClient(
            self.settings.mongodb_uri,
            serverSelectionTimeoutMS=self.settings.mongodb_server_selection_timeout_ms,
        )
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
            self._mongodb_upsert_with_id(
                "tariff_configs",
                {"contract_type": contract_type},
                {
                    "contract_type": contract_type,
                    "fixed_fee": fixed_fee,
                    "vat_percent": vat_percent,
                    "peak_multiplier": peak_multiplier,
                    "base_rate": base_rate,
                    "formula_note": formula_note,
                    "updated_at": datetime.now(),
                },
            )

        self._seed_mongodb_sample_data()

    def _mongodb_upsert_with_id(self, collection_name: str, key: dict[str, Any], payload: dict[str, Any]) -> None:
        collection = self.mongo_collection(collection_name)
        if collection.find_one(key, {"_id": 1}) is not None:
            return
        document = {"id": self.next_sequence(collection_name), **payload}
        collection.insert_one(document)

    def _seed_mongodb_sample_data(self) -> None:
        now = datetime.now()

        customers = [
            ("HD004", "Phạm Minh Tuấn", "Khu A - Tổ 4, Nhà 12", "0904444444", "Hộ gia đình"),
            ("HD005", "Lê Thu Hà", "Khu A - Tổ 5, Nhà 08", "0905555555", "Hộ gia đình"),
            ("HD006", "Đặng Quốc Huy", "Khu C - Tổ 1, Nhà 21", "0906666666", "Hộ gia đình"),
            ("HD007", "Cửa hàng Tạp hóa Minh Anh", "Khu C - Dãy ki-ốt 03", "0907777777", "Hộ gia đình"),
            ("HD008", "Công ty TNHH Cơ khí An Phú", "Khu B - Cụm CN 2", "0908888888", "Nhà máy"),
            ("HD009", "Xưởng Gỗ Gia Hưng", "Khu B - Cụm CN 3", "0909999999", "Nhà máy"),
        ]
        for customer_code, owner_name, address, phone_number, contract_type in customers:
            self._mongodb_upsert_with_id(
                "customers",
                {"customer_code": customer_code},
                {
                    "customer_code": customer_code,
                    "owner_name": owner_name,
                    "address": address,
                    "phone_number": phone_number,
                    "contract_type": contract_type,
                },
            )

        readings = [
            ("HD001", "01/2026", 1180), ("HD001", "02/2026", 1325), ("HD001", "03/2026", 1472), ("HD001", "04/2026", 1615),
            ("HD002", "01/2026", 940), ("HD002", "02/2026", 1058), ("HD002", "03/2026", 1182), ("HD002", "04/2026", 1306),
            ("HD004", "01/2026", 520), ("HD004", "02/2026", 638), ("HD004", "03/2026", 781), ("HD004", "04/2026", 925),
            ("HD005", "01/2026", 760), ("HD005", "02/2026", 852), ("HD005", "03/2026", 951), ("HD005", "04/2026", 1056),
            ("HD006", "01/2026", 410), ("HD006", "02/2026", 506), ("HD006", "03/2026", 612), ("HD006", "04/2026", 735),
            ("HD007", "01/2026", 1280), ("HD007", "02/2026", 1515), ("HD007", "03/2026", 1782), ("HD007", "04/2026", 2054),
            ("HD008", "01/2026", 18400), ("HD008", "02/2026", 20780), ("HD008", "03/2026", 23240), ("HD008", "04/2026", 25810),
            ("HD009", "01/2026", 9650), ("HD009", "02/2026", 11140), ("HD009", "03/2026", 12680), ("HD009", "04/2026", 14390),
        ]
        for customer_code, period, new_index in readings:
            self._mongodb_upsert_with_id(
                "meter_readings",
                {"customer_code": customer_code, "reading_period": period},
                {
                    "customer_code": customer_code,
                    "reading_period": period,
                    "new_index": new_index,
                    "note": "Ghi định kỳ từ đội vận hành",
                    "recorded_by_user_id": 1,
                    "created_at": now,
                },
            )

        invoices = [
            ("HDON-HD001-022026", "HD001", "02/2026", 145, 35000, 355_880, "Đã thanh toán"),
            ("HDON-HD002-022026", "HD002", "02/2026", 118, 35000, 289_960, "Đã thanh toán"),
            ("HDON-HD004-032026", "HD004", "03/2026", 143, 35000, 351_060, "Đã thanh toán"),
            ("HDON-HD005-032026", "HD005", "03/2026", 99, 35000, 246_980, "Chưa thanh toán"),
            ("HDON-HD006-042026", "HD006", "04/2026", 123, 35000, 301_340, "Chưa thanh toán"),
            ("HDON-HD007-042026", "HD007", "04/2026", 272, 35000, 710_380, "Chưa thanh toán"),
            ("HDON-HD008-032026", "HD008", "03/2026", 2460, 150000, 8_979_660, "Đã thanh toán"),
            ("HDON-HD008-042026", "HD008", "04/2026", 2570, 150000, 9_364_950, "Chưa thanh toán"),
            ("HDON-HD009-042026", "HD009", "04/2026", 1710, 150000, 6_360_930, "Chưa thanh toán"),
        ]
        for invoice_code, customer_code, period, consumption, fixed_fee, amount, status in invoices:
            vat_amount = int(amount * 8 / 108)
            self._mongodb_upsert_with_id(
                "invoices",
                {"invoice_code": invoice_code},
                {
                    "invoice_code": invoice_code,
                    "customer_code": customer_code,
                    "billing_period": period,
                    "consumption_kwh": consumption,
                    "fixed_fee": fixed_fee,
                    "vat_amount": vat_amount,
                    "amount": amount,
                    "status": status,
                    "issued_by_user_id": 1,
                    "issued_at": now,
                },
            )

        payments = [
            ("BN-HDON-HD001-022026", "HDON-HD001-022026", 355_880, "Tien mat", "Nguyễn Văn A"),
            ("BN-HDON-HD002-022026", "HDON-HD002-022026", 289_960, "Chuyen khoan", "Trần Thị B"),
            ("BN-HDON-HD004-032026", "HDON-HD004-032026", 351_060, "Tien mat", "Phạm Minh Tuấn"),
            ("BN-HDON-HD008-032026", "HDON-HD008-032026", 8_979_660, "Chuyen khoan", "Công ty TNHH Cơ khí An Phú"),
        ]
        for receipt_code, invoice_code, paid_amount, method, payer_name in payments:
            self._mongodb_upsert_with_id(
                "payments",
                {"receipt_code": receipt_code},
                {
                    "receipt_code": receipt_code,
                    "invoice_code": invoice_code,
                    "paid_amount": paid_amount,
                    "payment_method": method,
                    "payer_name": payer_name,
                    "collected_by_user_id": 1,
                    "note": "Thu tiền điện theo kỳ hóa đơn",
                    "paid_at": now,
                },
            )

        incidents = [
            ("HD004", "Mất điện", "Cao", "Mất điện cục bộ sau mưa lớn, cần kiểm tra aptomat tổng.", "Đang xử lý", "2026-04-18"),
            ("HD005", "Hỏng công tơ", "Trung bình", "Công tơ hiển thị chập chờn, khách hàng yêu cầu kiểm định.", "Đã tiếp nhận", "2026-04-20"),
            ("HD008", "Quá tải đường dây", "Khẩn cấp", "Dây cấp vào xưởng nóng bất thường vào giờ cao điểm.", "Đang xử lý", "2026-04-22"),
            ("HD009", "Chập điện", "Cao", "Tủ điện khu xưởng phát tia lửa, đã cô lập khu vực.", "Hoàn thành", "2026-04-10"),
        ]
        for customer_code, incident_type, priority, description, status, received_date in incidents:
            self._mongodb_upsert_with_id(
                "incidents",
                {"customer_code": customer_code, "incident_type": incident_type, "received_date": received_date},
                {
                    "customer_code": customer_code,
                    "incident_type": incident_type,
                    "priority": priority,
                    "description": description,
                    "status": status,
                    "received_by_user_id": 1,
                    "received_date": received_date,
                },
            )

        audit_logs = [
            ("CREATE", "customers", "HD004", "Thêm hồ sơ hộ dân Phạm Minh Tuấn"),
            ("CREATE", "meter_readings", "04/2026", "Ghi chỉ số công tơ định kỳ tháng 04/2026"),
            ("CREATE", "invoices", "HDON-HD008-042026", "Lập hóa đơn nhà máy kỳ 04/2026"),
            ("CREATE", "payments", "BN-HDON-HD008-032026", "Ghi nhận thanh toán chuyển khoản"),
        ]
        for action, entity_name, entity_key, description in audit_logs:
            self._mongodb_upsert_with_id(
                "audit_logs",
                {"action": action, "entity_name": entity_name, "entity_key": entity_key},
                {
                    "user_id": 1,
                    "action": action,
                    "entity_name": entity_name,
                    "entity_key": entity_key,
                    "description": description,
                    "created_at": now,
                },
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
