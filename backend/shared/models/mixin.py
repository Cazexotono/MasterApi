from typing import Optional

from datetime import datetime

from sqlalchemy import TIMESTAMP, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.enum import AccessStatus

__all__ = ("StatusMixin", "CreatedAtMixin", "UpdatedAtMixin", "TimestampMixin",)

class StatusMixin:
    __abstract__ = True
    
    status: Mapped[AccessStatus] = mapped_column(Enum(AccessStatus), default=AccessStatus.active, nullable=False)
    status_timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    status_description: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

class CreatedAtMixin:
    __abstract__ = True
    create: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class UpdatedAtMixin:
    __abstract__ = True
    update: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    __abstract__ = True
