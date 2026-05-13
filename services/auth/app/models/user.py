import enum
import uuid
from datetime import datetime, timezone

import uuid6
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, default=None)

    # Profile fields (settings / admin-managed)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True, default=None)
    program: Mapped[str | None] = mapped_column(String(80), nullable=True, default=None)
    year_of_study: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
