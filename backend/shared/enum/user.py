from enum import StrEnum, auto

__all__ = ("UserProvider", "UserPrivacy",)

class UserProvider(StrEnum):
    email = auto()
    discord = auto()


class UserPrivacy(StrEnum):
    all = auto()
    users = auto()
    self = auto()