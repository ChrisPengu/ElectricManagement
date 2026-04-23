import sqlite3
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

        if self.backend == "sqlite":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        if self.backend == "sqlserver":
            return self._connect_sqlserver()
        return self._connect_sqlite()

    @contextmanager
    def session(self) -> Iterator[Any]:
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_dict(cursor, row)

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()

    def executemany(self, query: str, params_list: Iterable[tuple[Any, ...]]) -> None:
        with self.session() as connection:
            cursor = connection.cursor()
            cursor.executemany(query, list(params_list))
            connection.commit()

    def initialize(self) -> None:
        with self.session() as connection:
            cursor = connection.cursor()
            for statement in self._schema_statements():
                cursor.execute(statement)
            self._seed_default_data(cursor)
            connection.commit()

    def _connect_sqlite(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

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
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_code TEXT UNIQUE NOT NULL,
                customer_code TEXT NOT NULL,
                billing_period TEXT NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_code TEXT NOT NULL,
                paid_amount INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                paid_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
                received_date TEXT
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
                role NVARCHAR(50) NOT NULL,
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
                created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
            )
            """,
            """
            IF OBJECT_ID('invoices', 'U') IS NULL
            CREATE TABLE invoices (
                id INT IDENTITY(1,1) PRIMARY KEY,
                invoice_code NVARCHAR(50) UNIQUE NOT NULL,
                customer_code NVARCHAR(50) NOT NULL,
                billing_period NVARCHAR(20) NOT NULL,
                amount INT NOT NULL,
                status NVARCHAR(50) NOT NULL
            )
            """,
            """
            IF OBJECT_ID('payments', 'U') IS NULL
            CREATE TABLE payments (
                id INT IDENTITY(1,1) PRIMARY KEY,
                invoice_code NVARCHAR(50) NOT NULL,
                paid_amount INT NOT NULL,
                payment_method NVARCHAR(50) NOT NULL,
                paid_at DATETIME2 NOT NULL DEFAULT SYSDATETIME()
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
                received_date DATE NULL
            )
            """,
        ]

    def _seed_default_data(self, cursor) -> None:
        if self.backend == "sqlserver":
            self._seed_sqlserver(cursor)
        else:
            self._seed_sqlite(cursor)

    def _seed_sqlite(self, cursor) -> None:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (username, password, role, display_name, is_active)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("admin", "admin123", "Admin", "Quản trị viên", 1),
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
            ("admin", "admin", "admin123", "Admin", "Quản trị viên", 1),
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
