from enum import StrEnum, auto

__all__ = ("ServerGamemode",)

class ServerGamemode(StrEnum):
    none = auto()
    sandbox = auto()
    roleplay = auto()
    adventure = auto()
    minigames = auto()
    pvp = auto()
    pve = auto()
    mmo = auto()
