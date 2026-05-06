from app.core.database import DatabaseManager


class AuditLogRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def record(self, user_id: int, action: str, entity_name: str, entity_key: str, description: str = "") -> None:
        self.db.execute(
            """
            INSERT INTO audit_logs (user_id, action, entity_name, entity_key, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, action, entity_name, entity_key, description),
        )
