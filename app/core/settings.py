import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DatabaseSettings:
    backend: str
    sqlite_path: Path
    sqlserver_host: str
    sqlserver_port: int
    sqlserver_database: str
    sqlserver_username: str
    sqlserver_password: str
    sqlserver_driver: str
    sqlserver_trusted_connection: bool

    @classmethod
    def from_env(cls) -> "DatabaseSettings":
        base_dir = Path(__file__).resolve().parents[2]
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        trusted_raw = os.getenv("DB_SQLSERVER_TRUSTED_CONNECTION", "0").strip().lower()

        return cls(
            backend=os.getenv("DB_BACKEND", "sqlite").strip().lower(),
            sqlite_path=Path(os.getenv("DB_SQLITE_PATH", data_dir / "electric_management.db")),
            sqlserver_host=os.getenv("DB_SQLSERVER_HOST", "localhost").strip(),
            sqlserver_port=int(os.getenv("DB_SQLSERVER_PORT", "1433")),
            sqlserver_database=os.getenv("DB_SQLSERVER_DATABASE", "ElectricManagement").strip(),
            sqlserver_username=os.getenv("DB_SQLSERVER_USERNAME", "sa").strip(),
            sqlserver_password=os.getenv("DB_SQLSERVER_PASSWORD", "").strip(),
            sqlserver_driver=os.getenv("DB_SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server").strip(),
            sqlserver_trusted_connection=trusted_raw in {"1", "true", "yes"},
        )
