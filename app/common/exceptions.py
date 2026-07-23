from fastapi import HTTPException, status


class UserAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )


class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Invalid username or password.")