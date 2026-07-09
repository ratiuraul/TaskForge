from app.common.enums import UserRole
from app.modules.auth.models.user_model import User
from app.modules.auth.repository.user_repository import UserRepository
from app.modules.auth.schemas.user_schema import UserCreate, UserResponse


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.password,
            role=UserRole.USER
        )

        created_user = self.repository.create(user)

        return UserResponse.model_validate(created_user)
