from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth.repository.user_repository import UserRepository
from app.modules.auth.schemas.user_schema import UserCreate, UserLogin, UserResponse, TokenResponse
from app.modules.auth.services.user_service import AuthService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models.user_model import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    service = AuthService(repository)

    return service.create_user(user)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    repository = UserRepository(db)
    service = AuthService(repository)

    user_data = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    return service.login(user_data)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
