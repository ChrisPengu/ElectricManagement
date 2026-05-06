import hashlib

from app.dto.mappers import to_user_dto
from app.dto.requests import LoginRequestDTO
from app.dto.responses import UserDTO
from app.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def authenticate(self, request: LoginRequestDTO) -> UserDTO | None:
        username = request.username.strip()
        password = request.password.strip()

        if not username or not password:
            return None

        account = self.auth_repository.get_by_username(username)
        if account is None:
            return None
        if not account.is_active:
            return None
        if not self._verify_password(password, account.password):
            return None
        if account.role.strip().casefold() != "admin":
            return None
        return to_user_dto(account)

    def _verify_password(self, raw_password: str, stored_password: str) -> bool:
        if stored_password.startswith("sha256$"):
            digest = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
            return stored_password == f"sha256${digest}"
        return stored_password == raw_password
