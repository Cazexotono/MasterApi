import re
from typing import Optional
from ipaddress import IPv4Address
from uuid import uuid4, UUID as UUID_TYPE
from datetime import datetime

from ulid import ULID
from pydantic import SecretBytes
from sqlalchemy import (
    CheckConstraint,
    Integer,
    MetaData,
    String,
    Boolean,
    UUID,
    ForeignKey,
    UniqueConstraint,
    Enum,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.asyncio import AsyncAttrs


from core import project
from shared.enum import UserProvider, ServerGamemode

from .mixin import StatusMixin, CreatedAtMixin, TimestampMixin, UpdatedAtMixin
from .custom_type import SecretByteType, ULIDType

__all__ = (
    "Base",
    "User",
    "UserAccount",
    "UserPublicInfo",
    "RefreshToken",
    "Server",
    "ServerPublicInfo",
    "GameSession",
)

# Base Model
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(schema=project.name)

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        name = cls.__name__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

# Core User
class User(Base, StatusMixin, TimestampMixin):
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    account: Mapped["UserAccount"] = relationship(back_populates="user", uselist=False)
    info: Mapped["UserPublicInfo"] = relationship(back_populates="user", uselist=False)
    servers: Mapped[list["Server"]] = relationship(back_populates="owner_user")
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="user", uselist=True)


class UserAccount(Base, UpdatedAtMixin):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{project.name}.user.user_id"), primary_key=True, nullable=False)

    provider: Mapped[UserProvider] = mapped_column(Enum(UserProvider), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[Optional[SecretBytes]] = mapped_column(SecretByteType(128), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reg_ip: Mapped[IPv4Address] = mapped_column(INET, nullable=False)
    last_ip: Mapped[Optional[IPv4Address]] = mapped_column(INET, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="account")
    tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="account")

    __table_args__ = (CheckConstraint(
        "(provider = 'email' AND password_hash IS NOT NULL) OR (provider != 'email')", name="chk_email_requires_password"),
    )

class RefreshToken(Base):
    account_user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{project.name}.user_account.user_id"), nullable=False, primary_key=True)   
    device: Mapped[str] = mapped_column(String(32), nullable=False, primary_key=True)
    
    jti: Mapped[str] = mapped_column(String(26), unique=True, nullable=False)
    token: Mapped[str] = mapped_column(String(1024), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    account: Mapped["UserAccount"] = relationship(back_populates="tokens")
    user: Mapped["User"] = relationship("User", primaryjoin="foreign(RefreshToken.account_user_id) == User.user_id", viewonly=True)

class UserPublicInfo(Base, UpdatedAtMixin):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{project.name}.user.user_id"), primary_key=True, nullable=False)
    
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    locale: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    social_links: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship(back_populates="info", uselist=False)

# Server Core
class Server(Base, StatusMixin, TimestampMixin):
    uuid: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey(f"{project.name}.user.user_id"), nullable=False)

    owner_user: Mapped["User"] = relationship(back_populates="servers")
    credential: Mapped["ServerCredential"] = relationship(back_populates="server")
    info: Mapped["ServerPublicInfo"] = relationship(back_populates="server", uselist=False)
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="server", uselist=True)

class ServerCredential(Base, CreatedAtMixin):
    server_uuid: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{project.name}.server.uuid"), primary_key=True, nullable=False)
    secret_hash: Mapped[SecretBytes] = mapped_column(SecretByteType(128), nullable=False)
    allowed_ips:  Mapped[Optional[IPv4Address]] = mapped_column(INET, nullable=True)
    last_ip: Mapped[Optional[IPv4Address]] = mapped_column(INET, nullable=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    server: Mapped["Server"] = relationship(back_populates="credential")

class ServerPublicInfo(Base, UpdatedAtMixin):
    server_uuid: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{project.name}.server.uuid"), primary_key=True)

    display_name: Mapped[str] = mapped_column(String(32), nullable=False, default="My Server")
    description: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    host: Mapped[IPv4Address] = mapped_column(INET, nullable=False)
    main_port: Mapped[int] = mapped_column(Integer, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    locale: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    gamemode_type: Mapped[ServerGamemode] = mapped_column(Enum(ServerGamemode), default=ServerGamemode.none, nullable=False)
    game_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    visible: Mapped[bool] = mapped_column(Boolean, default=False)
    links: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    server: Mapped["Server"] = relationship(back_populates="info", uselist=False)

    __table_args__ = (UniqueConstraint("host", "main_port", name="uc_host_port"),)

class GameSession(Base, CreatedAtMixin):
    session_id: Mapped[ULID] = mapped_column(ULIDType(26), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{project.name}.user.user_id"), nullable=False)
    server_uuid: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{project.name}.server.uuid"), nullable=False)
    
    session_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    reg_ip: Mapped[IPv4Address] = mapped_column(INET, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="sessions")
    server: Mapped["Server"] = relationship(back_populates="sessions")

class FavoriteServer(Base):
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{project.name}.user.user_id"), primary_key=True)
    server_uuid: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{project.name}.server.uuid"), primary_key=True)
    
    user: Mapped["User"] = relationship()
    server: Mapped["Server"] = relationship()

class ReportServer(Base, TimestampMixin):
    id: Mapped[ULID] = mapped_column(ULIDType(26), primary_key=True)
    reporter_user_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{project.name}.user.user_id"), nullable=False)
    server_uuid: Mapped[UUID_TYPE] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{project.name}.server.uuid"), nullable=False)
    
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String(1024))
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    reporter: Mapped["User"] = relationship()
    server: Mapped["Server"] = relationship()