from enum import Enum


class UserRoleEnum(str, Enum):
    """
    Constants for the various roles scoped in the application ecosystem
    """

    USER = "USER"
    ADMIN = "ADMIN"
