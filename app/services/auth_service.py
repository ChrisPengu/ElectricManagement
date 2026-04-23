from app.dto.mappers import to_user_dto
from app.dto.requests import LoginRequestDTO
from app.dto.responses import UserDTO
from app.repositories.auth_repository import AuthRepository


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def authenticate(self, request: LoginRequestDTO) -> UserDTO | None:
        account = self.auth_repository.get_by_username(request.username)
        if account is None:
            return None
        if not account.is_active:
            return None
        if account.password != request.password:
            return None
        return to_user_dto(account)
