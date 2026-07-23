from app.common.enums import UserRole
from app.common.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models.user_model import User
from app.modules.auth.repository.user_repository import UserRepository
from app.modules.auth.schemas.user_schema import UserCreate, UserLogin, UserResponse


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user:
            raise UserAlreadyExistsError

        hashed_password = hash_password(user_data.password)

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role=UserRole.USER,
        )

        created_user = self.repository.create(user)

        return UserResponse.model_validate(created_user)

    def login(self, user_data: UserLogin):
        user = self.repository.get_by_email(user_data.email)

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(user_data.password, user.hashed_password):
            raise InvalidCredentialsError()

        access_token = create_access_token(data={"sub": str(user.id)})

        return {"access_token": access_token}
