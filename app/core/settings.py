import os
from dataclasses import dataclass
from pathlib import Path


def load_env_file(base_dir: Path) -> None:
    env_path = base_dir / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        if key and key not in os.environ:
            os.environ[key] = value


@dataclass(slots=True)
class DatabaseSettings:
    backend: str
    sqlite_path: Path
    mongodb_uri: str
    mongodb_database: str
    mongodb_server_selection_timeout_ms: int
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
        load_env_file(base_dir)

        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        trusted_raw = os.getenv("DB_SQLSERVER_TRUSTED_CONNECTION", "0").strip().lower()

        return cls(
            backend=os.getenv("DB_BACKEND", "sqlite").strip().lower(),
            sqlite_path=Path(os.getenv("DB_SQLITE_PATH", data_dir / "electric_management.db")),
            mongodb_uri=os.getenv("DB_MONGODB_URI", "mongodb://localhost:27017").strip(),
            mongodb_database=os.getenv("DB_MONGODB_DATABASE", "ElectricManagementDemo").strip(),
            mongodb_server_selection_timeout_ms=int(os.getenv("DB_MONGODB_SERVER_SELECTION_TIMEOUT_MS", "10000")),
            sqlserver_host=os.getenv("DB_SQLSERVER_HOST", "localhost").strip(),
            sqlserver_port=int(os.getenv("DB_SQLSERVER_PORT", "1433")),
            sqlserver_database=os.getenv("DB_SQLSERVER_DATABASE", "ElectricManagement").strip(),
            sqlserver_username=os.getenv("DB_SQLSERVER_USERNAME", "sa").strip(),
            sqlserver_password=os.getenv("DB_SQLSERVER_PASSWORD", "").strip(),
            sqlserver_driver=os.getenv("DB_SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server").strip(),
            sqlserver_trusted_connection=trusted_raw in {"1", "true", "yes"},
        )
