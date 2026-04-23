from app.core.database import DatabaseManager
from app.models import UserAccount


class AuthRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_by_username(self, username: str) -> UserAccount | None:
        row = self.db.fetch_one(
            """
            SELECT id, username, password, role, display_name, is_active
            FROM users
            WHERE username = ?
            """,
            (username,),
        )

        if row is None:
            return None

        return UserAccount(
            id=row["id"],
            username=row["username"],
            password=row["password"],
            role=row["role"],
            display_name=row["display_name"],
            is_active=bool(row["is_active"]),
        )
