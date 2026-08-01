from enum import Enum


class UserRole(str, Enum):
    """System Level Role of the user"""

    USER = "user"
    ADMIN = "admin"


class OrganizationRole(str, Enum):
    """Organization Level Role of the user"""

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
