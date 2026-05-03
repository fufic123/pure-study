import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: str | None = None,
        google_id: str | None = None,
    ) -> User:
        user = User(email=email, hashed_password=hashed_password, google_id=google_id)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_google_id(self, user_id: uuid.UUID, google_id: str) -> User:
        user = await self.get_by_id(user_id)
        user.google_id = google_id  # type: ignore[union-attr]
        await self.session.flush()
        return user  # type: ignore[return-value]
