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


class TaskStatus(str, Enum):
    """Allowed task statuses"""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    "Allowed task priorites"

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
