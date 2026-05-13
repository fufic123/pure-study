import re
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserStatus

_NAME_RE = re.compile(r"^[A-Za-zА-Яа-яЁё .'\-]{2,120}$")


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=120)
    program: str = Field(..., min_length=1, max_length=80)
    year_of_study: int = Field(..., ge=1, le=10)
    status: UserStatus = UserStatus.ACTIVE

    @field_validator("full_name")
    @classmethod
    def _full_name_valid(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError("Full name may contain letters, spaces, dots, apostrophes and hyphens only")
        return v.strip()


class UserUpdateRequest(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    program: str | None = Field(default=None, min_length=1, max_length=80)
    year_of_study: int | None = Field(default=None, ge=1, le=10)
    status: UserStatus | None = None

    @field_validator("full_name")
    @classmethod
    def _full_name_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not _NAME_RE.match(v):
            raise ValueError("Full name may contain letters, spaces, dots, apostrophes and hyphens only")
        return v.strip()


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    program: str | None
    year_of_study: int | None
    status: UserStatus
    created_at: datetime

    @classmethod
    def from_orm_user(cls, u) -> "UserResponse":
        return cls(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            program=u.program,
            year_of_study=u.year_of_study,
            status=u.status,
            created_at=u.created_at,
        )
