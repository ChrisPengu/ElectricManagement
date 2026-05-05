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
        if account.password != password:
            return None
        if account.role.strip().casefold() != "admin":
            return None
        return to_user_dto(account)
