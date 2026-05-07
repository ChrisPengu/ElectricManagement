from app.core.database import DatabaseManager


class AuditLogRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def record(self, user_id: int, action: str, entity_name: str, entity_key: str, description: str = "") -> None:
        if self.db.backend == "mongodb":
            self.db.mongo_collection("audit_logs").insert_one(
                {
                    "id": self.db.next_sequence("audit_logs"),
                    "user_id": user_id,
                    "action": action,
                    "entity_name": entity_name,
                    "entity_key": entity_key,
                    "description": description,
                }
            )
            return

        self.db.execute(
            """
            INSERT INTO audit_logs (user_id, action, entity_name, entity_key, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, action, entity_name, entity_key, description),
        )
