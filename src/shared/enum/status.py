from enum import StrEnum, auto

__all__ = ("AccessStatus", "StateStatus", )

class AccessStatus(StrEnum):
    active = auto()
    temporary_ban = auto()
    permanent_ban = auto()
    self_removal = auto()
    forced_removal = auto()

class StateStatus(StrEnum):
    none = auto()
    error = auto()
    access = auto()
    denied = auto()
