from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository = audit_log_repository

    def record(self, user_id: int | None, action: str, entity_name: str, entity_key: str, description: str = "") -> None:
        if user_id is None:
            return
        self.audit_log_repository.record(user_id, action, entity_name, entity_key, description)
