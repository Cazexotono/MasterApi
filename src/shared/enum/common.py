from enum import StrEnum, auto

__all__ = ("Environment", "ClientEnum")


class Environment(StrEnum):
    dev = auto()
    staging = auto()
    production = auto()

class ClientEnum:
    guest = auto()
    user = auto()
    admin = auto()
