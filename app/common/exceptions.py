from fastapi import HTTPException, status


class UserAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

class InvalidUserId(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid User id.",
        )


class InvalidCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Invalid username or password.")


class OrgAlreadyExistsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization with this name already exists.",
        )


class InvalidOrgIdError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization with this id does not exists",
        )


class InsufficientPrivilegesError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized for this action",
        )


class NotOrgMember(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this organization.",
        )


class UserIsAlreadyMember(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already member in this organization.",
        )


class ProjectAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project with this name already exists in this organization.",
        )


class InvalidProjectIdError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project with this id does not exists",
        )
